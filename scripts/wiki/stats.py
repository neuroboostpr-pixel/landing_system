"""Агрегация wiki routing событий и генерация отчёта.

CLI:
    python -m scripts.wiki.stats                       # summary в терминал
    python -m scripts.wiki.stats --report              # пишет wiki/routing-report.md
    python -m scripts.wiki.stats --days=30             # за месяц
    python -m scripts.wiki.stats --exact-tokens        # точный подсчёт через Anthropic API (требует ANTHROPIC_API_KEY)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.wiki import config


@dataclass
class StatsResult:
    queries: int = 0
    direct_reads: int = 0
    est_tokens_saved: int = 0
    est_tokens_spent_bypass: int = 0
    bypass_rate: float = 0.0
    top_bypass: list[dict] = field(default_factory=list)
    by_date: list[dict] = field(default_factory=list)
    by_model: list[dict] = field(default_factory=list)


def compute_stats(events: list[dict[str, Any]], since_days: int = 7) -> StatsResult:
    if not events:
        return StatsResult()

    queries = 0
    direct_reads = 0
    est_saved = 0
    est_bypass = 0
    bypass_map: dict[str, dict] = defaultdict(lambda: {"count": 0, "had_prior_query_count": 0})
    by_date_map: dict[str, dict] = defaultdict(
        lambda: {"queries": 0, "direct_reads": 0, "est_saved": 0}
    )
    by_model_map: dict[str, dict] = defaultdict(
        lambda: {"queries": 0, "direct_reads": 0, "thinking_tokens_total": 0}
    )

    for e in events:
        ts_str = e.get("ts", "")
        try:
            date_key = ts_str[:10]
        except (TypeError, IndexError):
            date_key = "unknown"

        model = e.get("model") or "unknown"
        thinking = e.get("thinking_tokens", 0)

        if e.get("type") == "wiki_query":
            queries += 1
            est_saved += e.get("est_tokens_saved", 0)
            by_date_map[date_key]["queries"] += 1
            by_date_map[date_key]["est_saved"] += e.get("est_tokens_saved", 0)
            by_model_map[model]["queries"] += 1
            by_model_map[model]["thinking_tokens_total"] += thinking

        elif e.get("type") == "direct_read":
            direct_reads += 1
            est_bypass += e.get("est_tokens", 0)
            path = e.get("path", "unknown")
            bypass_map[path]["count"] += 1
            if e.get("had_prior_query"):
                bypass_map[path]["had_prior_query_count"] += 1
            by_date_map[date_key]["direct_reads"] += 1
            by_model_map[model]["direct_reads"] += 1
            by_model_map[model]["thinking_tokens_total"] += thinking

    total = queries + direct_reads
    bypass_rate = direct_reads / total if total > 0 else 0.0

    top_bypass = sorted(
        [{"path": k, **v} for k, v in bypass_map.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:10]

    by_date = sorted(
        [{"date": k, **v} for k, v in by_date_map.items()],
        key=lambda x: x["date"],
        reverse=True,
    )

    by_model = []
    for m, v in by_model_map.items():
        m_total = v["queries"] + v["direct_reads"]
        m_bypass = v["direct_reads"] / m_total if m_total > 0 else 0.0
        m_events = v["queries"] + v["direct_reads"]
        avg_thinking = v["thinking_tokens_total"] // m_events if m_events > 0 else 0
        by_model.append({
            "model": m,
            "queries": v["queries"],
            "direct_reads": v["direct_reads"],
            "bypass_rate": m_bypass,
            "avg_thinking_tokens": avg_thinking,
        })
    by_model.sort(key=lambda x: x["queries"] + x["direct_reads"], reverse=True)

    return StatsResult(
        queries=queries,
        direct_reads=direct_reads,
        est_tokens_saved=est_saved,
        est_tokens_spent_bypass=est_bypass,
        bypass_rate=bypass_rate,
        top_bypass=top_bypass,
        by_date=by_date,
        by_model=by_model,
    )


def one_line_summary(stats: StatsResult, days: int = 7) -> str:
    bypass_pct = int(stats.bypass_rate * 100)
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    spent = f"{stats.est_tokens_spent_bypass:,}".replace(",", " ")
    return (
        f"Вики-граф ({days}д): {stats.queries} запросов к вики · "
        f"{stats.direct_reads} обходов вики · "
        f"~{saved} токенов сэкономлено · ~{spent} токенов потрачено в обход · доля обходов {bypass_pct}%"
    )


def generate_report(stats: StatsResult, since_days: int = 7) -> str:
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=since_days - 1)
    lines = [
        f"# Отчёт по использованию вики-графа ({start} — {end})",
        "",
        "| Дата | Запросов к вики | Обходов вики | Сэкономлено ~токенов | Доля обходов |",
        "|------|-----------------|--------------|----------------------|--------------|",
    ]
    for row in stats.by_date:
        total = row["queries"] + row["direct_reads"]
        bp = int(row["direct_reads"] / total * 100) if total > 0 else 0
        lines.append(
            f"| {row['date']} | {row['queries']} | {row['direct_reads']} "
            f"| {row['est_saved']:,} | {bp}% |"
        )
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    spent = f"{stats.est_tokens_spent_bypass:,}".replace(",", " ")
    bypass_pct = int(stats.bypass_rate * 100)
    lines += [
        "",
        f"**Итого за {since_days} дней:** {stats.queries} запросов к вики · "
        f"{stats.direct_reads} обходов · ~{saved} токенов сэкономлено · ~{spent} токенов потрачено в обход",
        f"**Доля обходов:** {bypass_pct}%",
        "",
        "## Топ файлов читаемых в обход",
        "",
        "| Файл | Всего обходов | Агент знал про вики | Агент не обращался к вики |",
        "|------|---------------|---------------------|---------------------------|",
    ]
    for b in stats.top_bypass:
        prior = b["had_prior_query_count"]
        not_prior = b["count"] - prior
        lines.append(f"| {b['path']} | {b['count']} | {prior} | {not_prior} |")

    if stats.by_model:
        lines += [
            "",
            "## По моделям",
            "",
            "| Модель | Запросов к вики | Обходов вики | Доля обходов | Среднее токенов размышления |",
            "|--------|-----------------|--------------|--------------|------------------------------|",
        ]
        for m in stats.by_model:
            bp = int(m["bypass_rate"] * 100)
            lines.append(
                f"| {m['model']} | {m['queries']} | {m['direct_reads']} "
                f"| {bp}% | {m['avg_thinking_tokens']} |"
            )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Wiki routing stats")
    parser.add_argument("--report", action="store_true", help="Write wiki/routing-report.md")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--exact-tokens", action="store_true",
                        help="Use Anthropic count_tokens API for exact token counts (requires ANTHROPIC_API_KEY)")
    args = parser.parse_args()

    from scripts.wiki import routing_log
    events = routing_log.read_events(since_days=args.days)

    if args.exact_tokens:
        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY not set. Use size-based estimate instead.", file=sys.stderr)
            return 1
        events = _enrich_with_exact_tokens(events, api_key)

    result = compute_stats(events, since_days=args.days)
    suffix = " (exact)" if args.exact_tokens else " (~est ±30%)"
    print(one_line_summary(result, days=args.days) + suffix)

    if args.report:
        md = generate_report(result, since_days=args.days)
        report_path = config.WIKI_DIR / "routing-report.md"
        report_path.write_text(md, encoding="utf-8")
        print(f"Report written to {report_path}")

    return 0


def _enrich_with_exact_tokens(events: list[dict], api_key: str) -> list[dict]:
    """Replaces est_tokens with exact values via Anthropic API. Hash-cached."""
    import hashlib
    import urllib.request
    cache_path = config.REPO_ROOT / "logs" / "token-cache.json"
    cache: dict[str, int] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    def count_file_tokens(file_path: str) -> int:
        p = config.REPO_ROOT / file_path if not file_path.startswith("/") else Path(file_path)
        try:
            content = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return 0
        key = hashlib.md5(content.encode()).hexdigest()
        if key in cache:
            return cache[key]
        body = json.dumps({"model": "claude-haiku-4-5-20251001",
                           "messages": [{"role": "user", "content": content}]}).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages/count_tokens",
            data=body,
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        tokens = result.get("input_tokens", 0)
        cache[key] = tokens
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache), encoding="utf-8")
        return tokens

    enriched = []
    for e in events:
        e = dict(e)
        if e.get("type") == "direct_read" and e.get("path"):
            e["est_tokens"] = count_file_tokens(e["path"])
        enriched.append(e)
    return enriched


if __name__ == "__main__":
    sys.exit(main())

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
    context_injects: dict[str, int] = field(default_factory=dict)  # category → tokens
    leaks: list[dict] = field(default_factory=list)                 # can_be_wiki=True items
    query_details: list[dict] = field(default_factory=list)         # per wiki_query: ts/stage/type/slug/hits/tokens
    launches: list[dict] = field(default_factory=list)              # stage_start/agent_call/skill_call events
    run_summaries: list[dict] = field(default_factory=list)         # per run_id: run_id/date/total/via_wiki/leaks


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
    inject_map: dict[str, int] = defaultdict(int)
    leaks: list[dict] = []
    query_details: list[dict] = []
    result_launches: list[dict] = []

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
            f = e.get("filters") or {}
            query_details.append({
                "ts": ts_str,
                "agent": e.get("agent") or "",
                "stage": f.get("stage") or "",
                "type": f.get("type") or "",
                "slug": f.get("slug") or "",
                "hits": ", ".join(e.get("hits") or []),
                "est_tokens_saved": e.get("est_tokens_saved", 0),
            })

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
            # direct_read — всегда утечка
            leaks.append({
                "source_label": path,
                "est_tokens": e.get("est_tokens", 0),
                "had_prior_query": e.get("had_prior_query", False),
            })

        elif e.get("type") in ("stage_start", "agent_call", "skill_call"):
            result_launches.append(e)

        elif e.get("type") == "context_inject":
            category = e.get("source_category", "unknown")
            tokens = e.get("est_tokens", 0)
            inject_map[category] += tokens
            if e.get("can_be_wiki"):
                leaks.append({
                    "source_label": e.get("source_label", ""),
                    "est_tokens": tokens,
                    "had_prior_query": False,
                })

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

    # Группировка запусков по run_id
    run_map: dict[str, dict] = {}
    for e in events:
        if e.get("type") not in ("stage_start", "agent_call", "skill_call"):
            continue
        rid = e.get("session_id") or "unknown"
        if rid not in run_map:
            run_map[rid] = {
                "run_id": rid,
                "date": e.get("ts", "")[:16].replace("T", " "),
                "total": 0,
                "via_wiki": 0,
                "leaks": 0,
            }
        run_map[rid]["total"] += 1
        if e.get("via_wiki"):
            run_map[rid]["via_wiki"] += 1
        else:
            run_map[rid]["leaks"] += 1
    run_summaries = sorted(run_map.values(), key=lambda x: x["date"], reverse=True)

    return StatsResult(
        queries=queries,
        direct_reads=direct_reads,
        est_tokens_saved=est_saved,
        est_tokens_spent_bypass=est_bypass,
        bypass_rate=bypass_rate,
        top_bypass=top_bypass,
        by_date=by_date,
        by_model=by_model,
        context_injects=dict(inject_map),
        leaks=leaks,
        query_details=query_details,
        launches=result_launches,
        run_summaries=run_summaries,
    )


def one_line_summary(stats: StatsResult, days: int = 7) -> str:
    bypass_pct = int(stats.bypass_rate * 100)
    saved = f"{stats.est_tokens_saved:,}".replace(",", " ")
    spent = f"{stats.est_tokens_spent_bypass:,}".replace(",", " ")

    leak_tokens = sum(l["est_tokens"] for l in stats.leaks)
    leak_str = f" · ⚠️ {leak_tokens:,} токенов в обход".replace(",", " ") if leak_tokens > 0 else ""

    return (
        f"Вики-граф ({days}д): {stats.queries} запросов к вики · "
        f"{stats.direct_reads} обходов вики · "
        f"~{saved} токенов сэкономлено · ~{spent} токенов потрачено в обход · "
        f"доля обходов {bypass_pct}%{leak_str}"
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
        saved_row = f"{row['est_saved']:,}".replace(",", " ")
        lines.append(
            f"| {row['date']} | {row['queries']} | {row['direct_reads']} "
            f"| {saved_row} | {bp}% |"
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
        p = b["path"]
        name = Path(p).name if p else p
        link = f"[{name}](../{p})" if p else name
        lines.append(f"| {link} | {b['count']} | {prior} | {not_prior} |")

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

    has_budget_data = stats.queries > 0 or stats.direct_reads > 0 or bool(stats.context_injects)
    if has_budget_data:
        CLAUDE_MD_TOKENS = 10_231  # fixed overhead: 35809 bytes / 3.5
        lines += [
            "",
            "## Token Budget по категориям (7д)",
            "",
            "| Категория | Событий | ~Токенов | Можно на вики? |",
            "|-----------|---------|----------|----------------|",
            f"| wiki_query | {stats.queries} | -{stats.est_tokens_saved:,} | -- |".replace(",", " "),
        ]

        category_order = ["direct_read", "session_start", "framework_load", "bash_stdout"]
        can_be_wiki_labels = {
            "direct_read": "⚠️ да",
            "session_start": "нет",
            "framework_load": "нет",
            "bash_stdout": "нет",
        }

        if stats.direct_reads > 0:
            lines.append(
                f"| direct_read (legacy) | {stats.direct_reads} "
                f"| +{stats.est_tokens_spent_bypass:,} | ⚠️ да |".replace(",", " ")
            )

        for cat in category_order:
            tokens = stats.context_injects.get(cat, 0)
            if tokens == 0:
                continue
            can_wiki = can_be_wiki_labels.get(cat, "нет")
            lines.append(f"| {cat} | -- | +{tokens:,} | {can_wiki} |".replace(",", " "))

        lines.append(f"| [CLAUDE.md](../CLAUDE.md) | -- | ~{CLAUDE_MD_TOKENS:,} | нет (fixed) |".replace(",", " "))

        if stats.query_details:
            lines += [
                "",
                "### Детали wiki_query",
                "",
                "| Время | Агент | Stage | Type | Slug | Hits | ~Токенов сэкономлено |",
                "|-------|-------|-------|------|------|------|----------------------|",
            ]
            for q in stats.query_details:
                lines.append(
                    f"| {q['ts'][11:16]} | {q['agent'] or '—'} | {q['stage'] or '—'} "
                    f"| {q['type'] or '—'} | {q['slug'] or '—'} | {q['hits'] or '—'} "
                    f"| -{q['est_tokens_saved']} |"
                )

    if stats.run_summaries:
        lines.append("\n## Запуски (сводка)\n")
        lines.append("| run_id | Дата | Агентов/этапов | Через вики | Утечки |")
        lines.append("|--------|------|----------------|------------|--------|")
        for s in stats.run_summaries:
            lines.append(
                f"| {s['run_id']} | {s['date']} | {s['total']} "
                f"| {s['via_wiki']} | {s['leaks']} |"
            )

    if stats.launches:
        lines.append("\n## Запуски vs вики (7д)\n")
        lines.append("| Время | run_id | Тип | Имя | Stage | via_wiki | Утечка? |")
        lines.append("|-------|--------|-----|-----|-------|----------|---------|")
        for e in stats.launches:
            ts_str = e.get("ts", "")
            ts = ts_str[11:16] if len(ts_str) >= 16 else ts_str
            etype = e.get("type", "")
            if etype == "stage_start":
                name = e.get("stage", "")
                tname = "stage"
            elif etype == "agent_call":
                name = e.get("agent", "")
                tname = "agent"
            else:
                name = e.get("skill", "")
                tname = "skill"
            stage = e.get("stage", "")
            via = "✅" if e.get("via_wiki") else "❌"
            leak = "⚠️" if not e.get("via_wiki") else ""
            rid = e.get("session_id", "")
            rid_short = rid.replace("landing-", "") if rid.startswith("landing-") else rid
            lines.append(f"| {ts} | {rid_short} | {tname} | {name} | {stage} | {via} | {leak} |")

    if stats.leaks:
        lines += [
            "",
            "## Утечки -- читается напрямую вместо вики",
            "",
            "| Файл | ~Токенов | Агент знал про вики |",
            "|------|----------|---------------------|",
        ]
        for leak in stats.leaks:
            knew = "да ⚠️" if leak.get("had_prior_query") else "нет"
            label = leak["source_label"]
            name = Path(label).name if label else label
            link = f"[{name}](../{label})" if label else name
            lines.append(f"| {link} | {leak['est_tokens']} | {knew} |")

    return "\n".join(lines) + "\n"


# Alias for backwards compatibility and test usage
render_report = generate_report


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

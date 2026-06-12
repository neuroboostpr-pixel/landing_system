"""Линтер wiki — 7 проверок здоровья.

Структурные проверки (бесплатно):
1. Битые wikilinks
2. Сирые страницы
3. Некомпилированные daily logs
4. Устаревшие концепты
5. Пропущенные обратные ссылки
6. Пустые концепты

LLM-проверка (платно, по флагу --llm-check):
7. Противоречия между концептами
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from scripts.wiki import utils

WIKILINK_RE = re.compile(r"\[\[([^\]\|]+?)(\|[^\]]*)?\]\]")

STALE_DAYS = 30
MIN_WORDS = 50  # «пустой» концепт


def _collect_concepts(wiki_dir: Path) -> dict[str, Path]:
    """Возвращает {file_stem: path} для всех md в concepts/."""
    concepts_dir = wiki_dir / "concepts"
    if not concepts_dir.exists():
        return {}
    return {p.stem: p for p in concepts_dir.rglob("*.md")}


def _wikilinks_in(text: str) -> set[str]:
    """Множество wikilink-имён (без anchor/alias)."""
    return {m.group(1).strip() for m in WIKILINK_RE.finditer(text)}


def run_checks(wiki_dir: Path, llm_check: bool = False) -> dict:
    """Выполняет все структурные проверки. Возвращает словарь по типам."""
    concepts = _collect_concepts(wiki_dir)
    issues = {
        "broken_links": [],
        "orphans": [],
        "uncompiled_daily": [],
        "stale": [],
        "missing_backlinks": [],
        "empty": [],
        "contradictions": [],
    }

    # Для каждого концепта — собрать body и links
    bodies: dict[str, str] = {}
    links_from: dict[str, set[str]] = {}
    for name, path in concepts.items():
        text = path.read_text(encoding="utf-8")
        _, body = utils.parse_frontmatter(text)
        bodies[name] = body
        links_from[name] = _wikilinks_in(body)

    referenced: set[str] = set()
    for name, lset in links_from.items():
        referenced.update(lset)

    # 1. Битые ссылки
    for name, lset in links_from.items():
        for target in lset:
            if target not in concepts:
                issues["broken_links"].append(f"{name} → [[{target}]]")

    # 2. Сирые страницы (никто не ссылается, не считая index/log)
    for name in concepts:
        if name in ("index", "log"):
            continue
        if name not in referenced:
            issues["orphans"].append(name)

    # 3. Daily logs не скомпилированы
    daily = wiki_dir.parent / "memory" / "daily" if wiki_dir.name == "wiki" else None
    if daily and daily.exists():
        compiled = wiki_dir.parent / "memory" / "compiled" / "concepts"
        if not compiled.exists() or not list(compiled.glob("*.md")):
            for f in sorted(daily.glob("*.md")):
                issues["uncompiled_daily"].append(f.name)

    # 4. Устаревшие
    stale_threshold = date.today() - timedelta(days=STALE_DAYS)
    for name, path in concepts.items():
        text = path.read_text(encoding="utf-8")
        meta, _ = utils.parse_frontmatter(text)
        updated = meta.get("updated")
        if isinstance(updated, str):
            try:
                ud = datetime.fromisoformat(updated).date()
                if ud < stale_threshold:
                    issues["stale"].append(f"{name} ({updated})")
            except ValueError:
                pass
        elif isinstance(updated, date):
            if updated < stale_threshold:
                issues["stale"].append(f"{name} ({updated})")

    # 5. Missing backlinks: A→B, но B не упоминает A
    for a, lset in links_from.items():
        for b in lset:
            if b in concepts and a not in links_from.get(b, set()):
                issues["missing_backlinks"].append(f"{a} ↔ {b}")

    # 6. Пустые
    for name, body in bodies.items():
        word_count = len(body.split())
        if word_count < MIN_WORDS:
            issues["empty"].append(f"{name} ({word_count} слов)")

    # 7. LLM — противоречия (опционально)
    if llm_check:
        try:
            from scripts.wiki import sdk_client
            combined = "\n\n---\n\n".join(
                f"# {n}\n\n{bodies[n][:500]}" for n in concepts
            )
            prompt = (
                "Ты ищешь противоречия в wiki. На вход — все концепты. "
                "Найди пары противоречащих утверждений. "
                "Формат ответа: список '- <concept-a> vs <concept-b>: <что противоречит>'. "
                "Если противоречий нет — верни 'нет'."
            )
            result = sdk_client.generate(system=prompt, user=combined)
            if "нет" not in result.lower()[:20]:
                issues["contradictions"] = [
                    line.strip("- ").strip()
                    for line in result.splitlines() if line.strip().startswith("-")
                ]
        except Exception as e:
            issues["contradictions"].append(f"LLM check failed: {e}")

    # New: index.yaml ref checks.
    index_yaml = wiki_dir / "index.yaml"
    if index_yaml.exists():
        import yaml as _yaml
        try:
            data = _yaml.safe_load(index_yaml.read_text(encoding="utf-8")) or {}
        except _yaml.YAMLError:
            data = {}
        ref_issues = check_index_refs(data)
        for key, items in ref_issues.items():
            issues.setdefault(key, []).extend(items)

    return issues


# Required frontmatter fields per concept type.
_REQUIRED_FIELDS_BY_TYPE = {
    "stage": ("stage",),
    "agent": (),
    "command": (),
    "skill": (),
    "rule": (),
    "catalog": (),
}

# Frontmatter fields that should reference existing slugs.
_REF_FIELDS = ("related", "pre_reqs", "invoked_by", "uses_skills")


def check_index_refs(index_data: dict) -> dict[str, list[str]]:
    """Проверяет валидность ссылок и обязательных полей в index.yaml.

    Returns:
        {'broken_refs': [...], 'dup_slugs': [...], 'missing_required': [...],
         'low_confidence': [...], 'orphan_cards': []}.
    """
    issues: dict[str, list[str]] = {
        "broken_refs": [],
        "dup_slugs": [],
        "missing_required": [],
        "low_confidence": [],
        "orphan_cards": [],
    }
    concepts = index_data.get("concepts", [])
    slugs: set[str] = set()
    seen: set[str] = set()

    for c in concepts:
        slug = c.get("slug")
        if not slug:
            continue
        if slug in seen:
            issues["dup_slugs"].append(slug)
        seen.add(slug)
        slugs.add(slug)

    for c in concepts:
        slug = c.get("slug", "?")
        if c.get("incomplete"):
            continue
        type_ = c.get("type", "unknown")
        for required in _REQUIRED_FIELDS_BY_TYPE.get(type_, ()):
            if not c.get(required):
                issues["missing_required"].append(
                    f"{slug} ({type_}): missing '{required}' stage field"
                )
        for field in _REF_FIELDS:
            for target in c.get(field) or []:
                if target not in slugs:
                    issues["broken_refs"].append(f"{slug}.{field} → {target}")
        confidence = c.get("confidence") or {}
        for field, level in confidence.items():
            if level == "low":
                issues["low_confidence"].append(f"{slug}.{field}")

    return issues


# Issue categories that are warn-only (don't fail compile).
_WARN_ONLY_KEYS = {"low_confidence", "stale", "missing_backlinks", "empty", "orphans"}


def compute_exit_code(issues: dict) -> int:
    """0 если только warn-only issues, 1 если есть критические.

    Override через env WIKI_LINT_STRICT=0 — всё становится warn-only.
    """
    if os.environ.get("WIKI_LINT_STRICT", "1") == "0":
        return 0
    for key, items in issues.items():
        if key in _WARN_ONLY_KEYS:
            continue
        if items:
            return 1
    return 0


def format_report(issues: dict) -> str:
    lines = ["# Wiki Lint Report", ""]
    for k, v in issues.items():
        if not v:
            continue
        lines.append(f"## {k} ({len(v)})")
        for item in v[:20]:
            lines.append(f"- {item}")
        if len(v) > 20:
            lines.append(f"- ... ещё {len(v) - 20}")
        lines.append("")
    if all(not v for v in issues.values()):
        lines.append("✅ Все проверки прошли.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default="wiki", help="Папка wiki/")
    parser.add_argument("--llm-check", action="store_true", help="Включить LLM-проверку противоречий")
    parser.add_argument("--structural-only", action="store_true", help="Только структурные проверки")
    args = parser.parse_args()

    wiki_dir = Path(args.wiki).resolve()
    if not wiki_dir.exists():
        print(f"ERROR: wiki dir not found: {wiki_dir}", file=sys.stderr)
        return 2

    llm_check = args.llm_check and not args.structural_only
    issues = run_checks(wiki_dir, llm_check=llm_check)
    print(format_report(issues))
    return compute_exit_code(issues)


if __name__ == "__main__":
    sys.exit(main())

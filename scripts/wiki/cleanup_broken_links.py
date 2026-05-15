#!/usr/bin/env python3
"""Удаляет [[wikilinks]] на несуществующие концепты.

[[gate-check]] → gate-check (текст остаётся, ссылка снимается)
[[landing-orchestrator]] → [[landing-orchestrator]] (живая ссылка остаётся)

Запуск:
  python3 -m scripts.wiki.cleanup_broken_links --wiki wiki [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]\|]+?)(\|[^\]]*)?\]\]")


def collect_concept_stems(wiki_dir: Path) -> set[str]:
    concepts_dir = wiki_dir / "concepts"
    if not concepts_dir.exists():
        return set()
    return {p.stem for p in concepts_dir.rglob("*.md")}


def fix_file(path: Path, valid_stems: set[str], dry_run: bool = False) -> int:
    text = path.read_text(encoding="utf-8")
    fixed = 0

    def replace(m: re.Match) -> str:
        nonlocal fixed
        target = m.group(1).strip()
        if target in valid_stems:
            return m.group(0)  # живая — оставляем
        fixed += 1
        alias = m.group(2)
        if alias:
            return alias[1:]  # alias-текст
        return target  # просто имя как текст

    new_text = WIKILINK_RE.sub(replace, text)
    if fixed > 0 and not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default="wiki")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    wiki = Path(args.wiki).resolve()
    valid = collect_concept_stems(wiki)
    print(f"Валидных стемов в wiki: {len(valid)}")

    total_fixed = 0
    total_files = 0
    for md in (wiki / "concepts").rglob("*.md"):
        n = fix_file(md, valid, dry_run=args.dry_run)
        if n > 0:
            total_fixed += n
            total_files += 1
            print(f"  {md.relative_to(wiki)}: убрано {n} битых ссылок")

    # index.md тоже почистить
    idx = wiki / "index.md"
    if idx.exists():
        n = fix_file(idx, valid, dry_run=args.dry_run)
        if n > 0:
            print(f"  index.md: убрано {n} битых ссылок")
            total_fixed += n

    print(f"\nИтого: {total_fixed} битых ссылок в {total_files} файлах {'(dry-run)' if args.dry_run else 'удалено'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

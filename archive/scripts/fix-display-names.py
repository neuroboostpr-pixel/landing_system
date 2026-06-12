#!/usr/bin/env python3
"""Унифицирует display_name_ru во ВСЕХ блоках в технический формат.

Старый codex-импорт писал длинные русские авто-описания, часто обрезанные на
полуслове («…яркой к»). В карточках галереи нужно короткое техническое имя
БЕЗ русского описания. Формат:

    «<id> (<layout_pattern>)»

напр. «header-cinematic-split-portfolio-kdm1-ru-0 (split)».
Если layout_pattern пуст — просто «<id>».

Применяется ко ВСЕМ блокам библиотеки (кроме служебных папок).

Использование:
  python scripts/fix-display-names.py [--dry-run]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB = REPO_ROOT / "block-library"
SKIP_DIRS = {"_patterns", "_shapes", "_styles", "references"}


def make_name(block_id: str, layout_pattern: str) -> str:
    """Техническое имя карточки: id (+ layout_pattern в скобках)."""
    lp = (layout_pattern or "").strip()
    return f"{block_id} ({lp})" if lp else block_id


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    changed: list[tuple[str, str, str]] = []  # (id, old, new)

    for catdir in sorted(LIB.iterdir()):
        if not catdir.is_dir() or catdir.name.startswith((".", "_")) or catdir.name in SKIP_DIRS:
            continue
        for bd in sorted(catdir.iterdir()):
            mp = bd / "meta.yaml"
            if not mp.exists():
                continue
            meta = yaml.safe_load(mp.read_text(encoding="utf-8")) or {}
            block_id = str(meta.get("id", bd.name))
            old = str(meta.get("display_name_ru", ""))
            new = make_name(block_id, meta.get("layout_pattern", ""))
            if old == new:
                continue
            changed.append((bd.name, old, new))
            if not args.dry_run:
                meta["display_name_ru"] = new
                mp.write_text(
                    yaml.dump(meta, default_flow_style=False, sort_keys=False, allow_unicode=True),
                    encoding="utf-8",
                )

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Переименовано: {len(changed)}")
    for bid, old, new in changed[:15]:
        shown_old = (old[:30] + "…") if len(old) > 30 else old
        print(f"  {bid}: '{shown_old}' → '{new}'")
    if len(changed) > 15:
        print(f"  … ещё {len(changed) - 15}")


if __name__ == "__main__":
    main()

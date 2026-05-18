#!/usr/bin/env python3
"""Регенерирует block-library/catalog.yaml на основе ВСЕХ существующих папок блоков
(старые ru-* + новые imported)."""
import yaml
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "block-library"
CATALOG = LIB / "catalog.yaml"


def main():
    blocks = []
    for cat_dir in sorted(LIB.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith("_") or cat_dir.name.startswith("."):
            continue
        for block_dir in sorted(cat_dir.iterdir()):
            if not block_dir.is_dir():
                continue
            meta_file = block_dir / "meta.yaml"
            if meta_file.exists():
                try:
                    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8")) or {}
                except Exception:
                    meta = {}
            else:
                meta = {}

            entry = {
                "id": block_dir.name,
                "path": f"{cat_dir.name}/{block_dir.name}/",
                "category": cat_dir.name,
            }

            # Унаследовать use_cases от meta (старый формат)
            if "use_cases" in meta:
                entry["use_cases"] = meta["use_cases"]

            # Унаследовать niches_suitable (новый формат) — конвертим в use_cases
            if "niches_suitable" in meta:
                niches = meta["niches_suitable"]
                if isinstance(niches, list):
                    entry["use_cases"] = niches  # же hub

            # style_mood / layout_pattern (новый формат) — оставляем
            for key in ["style_mood", "layout_pattern", "display_name_ru"]:
                if key in meta:
                    entry[key] = meta[key]

            blocks.append(entry)

    catalog = {"version": 2, "updated": "2026-05-16", "blocks": blocks}
    CATALOG.write_text(yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"✅ Catalog refreshed: {len(blocks)} blocks, {len(set(b['category'] for b in blocks))} categories")

    # Распределение
    from collections import Counter
    cats = Counter(b["category"] for b in blocks)
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()

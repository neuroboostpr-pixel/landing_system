#!/usr/bin/env python3
"""Обновляет block-library/catalog.yaml после импорта."""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml не установлен. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--added-from", required=True)
    args = parser.parse_args()

    library = Path(args.library)
    catalog = library / "catalog.yaml"
    if catalog.exists():
        data = yaml.safe_load(catalog.read_text(encoding="utf-8")) or {}
    else:
        data = {"version": 1, "blocks": []}

    blocks = data.setdefault("blocks", [])
    existing_ids = {b.get("id") for b in blocks if isinstance(b, dict)}

    added = json.loads(Path(args.added_from).read_text(encoding="utf-8"))
    new = 0
    for b in added:
        if b["slug"] in existing_ids:
            continue
        try:
            rel_path = str(Path(b["path"]).resolve().relative_to(library.resolve())) + "/"
        except ValueError:
            rel_path = b["path"]
        blocks.append({
            "id": b["slug"],
            "path": rel_path,
            "category": b["category"],
        })
        new += 1

    catalog.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Catalog обновлён: {catalog} (+{new})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

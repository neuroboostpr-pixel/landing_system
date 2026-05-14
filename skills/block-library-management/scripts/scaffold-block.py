#!/usr/bin/env python3
"""Scaffold a new block in block-library/ from the template-source dir.

Usage:
  scaffold-block.py --id <kebab-id> --category <cat> --library <path> --template-source <path>
"""
import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

VALID_CATEGORIES = {
    "hero", "features", "social-proof", "process",
    "pricing", "trust", "cta", "faq", "quiz",
}
KEBAB = re.compile(r"^[a-z][a-z0-9-]*$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--category", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template-source", required=True)
    p.add_argument("--use-cases", default="services,b2c,local",
                   help="comma-separated; default all")
    args = p.parse_args()

    if not KEBAB.match(args.id):
        fail(f"id must be kebab-case: {args.id!r}")
    if args.category not in VALID_CATEGORIES:
        fail(f"invalid category: {args.category!r}")

    lib = Path(args.library)
    target = lib / args.category / args.id
    if target.exists():
        fail(f"block already exists: {target}")

    catalog_path = lib / "catalog.yaml"
    if not catalog_path.exists():
        fail(f"catalog.yaml not found in {lib}")
    catalog = yaml.safe_load(catalog_path.read_text())
    for b in catalog.get("blocks", []):
        if b["id"] == args.id:
            fail(f"id already exists in catalog: {args.id}")

    src = Path(args.template_source)
    if not src.exists():
        fail(f"template source not found: {src}")

    shutil.copytree(src, target)

    # Fill in meta.yaml
    meta_path = target / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text())
    meta["id"] = args.id
    meta["category"] = args.category
    meta["use_cases"] = [u.strip() for u in args.use_cases.split(",")]
    meta["created"] = date.today().isoformat()
    meta_path.write_text(yaml.dump(meta, sort_keys=False, allow_unicode=True))

    # Replace {{block_id}} placeholders in templates
    for html_name in ("template.html", "template-mobile.html"):
        html_path = target / "assets" / html_name
        text = html_path.read_text()
        text = text.replace("{{block_id}}", args.id)
        html_path.write_text(text)

    # Update SKILL.md placeholder
    skill_path = target / "SKILL.md"
    text = skill_path.read_text()
    text = text.replace("<block-id>", args.id)
    skill_path.write_text(text)

    # Update catalog
    catalog.setdefault("blocks", []).append({
        "id": args.id,
        "path": f"{args.category}/{args.id}/",
        "category": args.category,
        "use_cases": meta["use_cases"],
    })
    catalog["updated"] = date.today().isoformat()
    catalog_path.write_text(yaml.dump(catalog, sort_keys=False, allow_unicode=True))

    print(f"OK: scaffolded {target}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render brand-kit.html from brand-kit.md frontmatter."""
import argparse
import re
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.html.render import render
from tools.logger import success, error


def load_brand_kit(project_dir: str) -> dict:
    md_path = Path(project_dir) / "04_БРЕНД" / "brand-kit.md"
    if not md_path.exists():
        raise FileNotFoundError(f"brand-kit.md not found: {md_path}")
    content = md_path.read_text(encoding="utf-8")
    # Extract YAML frontmatter between first two ---
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        raise ValueError("brand-kit.md has no YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    return data.get("brand_kit", data)


def render_brand_kit(project_dir: str) -> Path:
    brand = load_brand_kit(project_dir)
    html = render("brand-kit.html.j2", {"brand": brand})
    out = Path(project_dir) / "04_БРЕНД" / "brand-kit.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        out = render_brand_kit(args.project_dir)
        success(f"Wrote {out}")
        return 0
    except Exception as exc:
        error(f"render failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

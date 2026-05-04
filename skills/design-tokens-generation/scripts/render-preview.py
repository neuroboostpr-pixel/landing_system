#!/usr/bin/env python3
"""Render design-preview.html from 05_ДИЗАЙН-СИСТЕМА/tokens.json.

CLI: python3 render-preview.py <project-dir>
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.html.render import render
from tools.logger import success, warn, error


def load_tokens(project_dir: Path) -> dict:
    """Load tokens.json, returning empty dict if absent."""
    tokens_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    if not tokens_path.exists():
        warn(f"tokens.json not found: {tokens_path} — using empty tokens")
        return {}
    return json.loads(tokens_path.read_text(encoding="utf-8"))


def main(argv: list) -> int:
    p = argparse.ArgumentParser(description="Render design-preview.html from tokens.json.")
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        project_dir = Path(args.project_dir)
        tokens = load_tokens(project_dir)
        out_path = project_dir / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        html = render("design-preview.html.j2", {"tokens": tokens})
        out_path.write_text(html, encoding="utf-8")
        success(f"Wrote {out_path}")
        return 0
    except Exception as exc:
        error(f"render-preview failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

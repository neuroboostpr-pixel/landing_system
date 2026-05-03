#!/usr/bin/env python3
"""Render moodboard.html from 03_РЕФЕРЕНСЫ/index.yaml.

CLI: python3 render.py <refs-dir> [--narrative <path-to-md>] [--project <name>]
"""
import argparse
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.html.render import render
from tools.logger import success, error


def render_moodboard(refs_dir: str, narrative_md: str = "", project_name: str = "Project") -> Path:
    refs = Path(refs_dir)
    idx = refs / "index.yaml"
    if not idx.exists():
        raise FileNotFoundError(f"no index.yaml in {refs_dir}")
    data = yaml.safe_load(idx.read_text(encoding="utf-8")) or {"references": []}
    all_refs = data["references"]
    approved = [r for r in all_refs if r["status"] == "approved"]
    rejected = [r for r in all_refs if r["status"] == "rejected"]

    narrative_html = ""
    if narrative_md:
        narrative_path = Path(narrative_md)
        if narrative_path.exists():
            # Lightweight md -> html: just paragraphs
            narrative_html = "<p>" + narrative_path.read_text(encoding="utf-8").replace("\n\n", "</p><p>") + "</p>"

    html = render("moodboard.html.j2", {
        "approved": approved,
        "rejected": rejected,
        "narrative": narrative_html,
        "project_name": project_name,
    })
    out = refs / "moodboard.html"
    out.write_text(html, encoding="utf-8")
    return out


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("refs_dir")
    p.add_argument("--narrative", default="")
    p.add_argument("--project", default="Project")
    args = p.parse_args(argv[1:])
    try:
        out = render_moodboard(args.refs_dir, args.narrative, args.project)
        success(f"Wrote {out}")
        return 0
    except Exception as exc:
        error(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

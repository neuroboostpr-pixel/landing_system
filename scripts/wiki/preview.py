"""Генерит wiki/preview.html для глазного просмотра."""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.wiki import utils

TEMPLATES = Path(__file__).parent / "templates"


def _load_concepts(wiki_dir: Path) -> list[dict]:
    concepts = []
    cdir = wiki_dir / "concepts"
    if not cdir.exists():
        return concepts
    for p in sorted(cdir.rglob("*.md")):
        text = p.read_text(encoding="utf-8")
        meta, body = utils.parse_frontmatter(text)
        concepts.append({
            "slug": p.stem,
            "name": meta.get("name", p.stem),
            "type": meta.get("type", "unknown"),
            "body": body.strip()[:3000],
        })
    return concepts


def render(wiki_dir: Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("preview.html.j2")
    styles = (TEMPLATES / "styles.css").read_text(encoding="utf-8")

    concepts = _load_concepts(wiki_dir)
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in concepts:
        groups[c["type"]].append({"slug": c["slug"], "name": c["name"], "type": c["type"]})

    html = template.render(
        title=f"{wiki_dir.parent.name} wiki",
        updated=date.today().isoformat(),
        total=len(concepts),
        styles=styles,
        groups=dict(groups),
        concepts=concepts,
    )

    out = wiki_dir / "preview.html"
    utils.atomic_write(out, html)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default="wiki")
    args = parser.parse_args()
    out = render(Path(args.wiki).resolve())
    print(f"Generated: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

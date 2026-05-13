#!/usr/bin/env python3
"""Render static HTML preview of the built WP theme.

CLI: python3 render-build-preview.py <project-dir>
Stdout: path to build-preview.html
"""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success
from tools.html import render


def _find_project_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "08_КОД" / "wp-theme" / "style.css").exists():
            return parent
    raise FileNotFoundError("08_КОД/wp-theme/style.css not found — run /landing-build first")


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        project = _find_project_root(cwd)
    except FileNotFoundError as e:
        error(str(e))
        return 1

    tokens_path = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
    tokens = json.loads(tokens_path.read_text(encoding="utf-8")) if tokens_path.exists() else {}

    stack_path = project / "06_СТЕК" / "design-stack.yaml"
    stack = yaml.safe_load(stack_path.read_text(encoding="utf-8")) if stack_path.exists() else {}

    # Lazy Blocks era: block-spec.yaml is source of truth for controls,
    # and blocks live under wp-theme/blocks/lazyblock-<slug>/.
    spec_path = project / "08_КОД" / "block-spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    lazy_blocks_spec = spec.get("blocks", []) if isinstance(spec, dict) else []

    theme_dir = project / "08_КОД" / "wp-theme"
    blocks_dir = theme_dir / "blocks"
    lazy_blocks = []
    if blocks_dir.exists():
        lazy_blocks = sorted(
            d.name for d in blocks_dir.iterdir()
            if d.is_dir() and d.name.startswith("lazyblock-")
        )

    context = {
        "project_name": project.name,
        "tokens": tokens,
        "stack": stack,
        "lazy_blocks": lazy_blocks,
        "lazy_blocks_spec": lazy_blocks_spec,
    }

    html = render.render("build-preview.html.j2", context)
    out = project / "08_КОД" / "build-preview.html"
    out.write_text(html, encoding="utf-8")

    success(f"Build preview: {out}")
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

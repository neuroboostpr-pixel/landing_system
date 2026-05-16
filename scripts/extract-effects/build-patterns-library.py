#!/usr/bin/env python3
"""Из extracted patterns создаёт reusable HTML+CSS снипеты в _patterns/.

Каждый снипет — папка с index.html (демо) + styles.css (стили) + meta.yaml.

Usage:
    build-patterns-library.py <findings.json>
    cat findings.json | build-patterns-library.py

Env:
    PATTERNS_DIR_OVERRIDE — путь до _patterns/, иначе block-library/_patterns
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import date


DEFAULT_PATTERNS_DIR = (
    Path(__file__).resolve().parents[2] / "block-library" / "_patterns"
)


def patterns_dir() -> Path:
    override = os.environ.get("PATTERNS_DIR_OVERRIDE")
    if override:
        return Path(override)
    return DEFAULT_PATTERNS_DIR


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "x"


def write_pattern(
    base_dir: Path, slug: str, name: str, css_snippet: str, html_demo: str, description: str
) -> bool:
    pattern_dir = base_dir / slug
    if pattern_dir.exists():
        return False  # skip existing
    pattern_dir.mkdir(parents=True)
    (pattern_dir / "styles.css").write_text(css_snippet, encoding="utf-8")
    (pattern_dir / "index.html").write_text(html_demo, encoding="utf-8")
    (pattern_dir / "meta.yaml").write_text(
        f"""id: {slug}
type: pattern
name: {name}
description: "{description}"
imported_at: "{date.today().isoformat()}"
import_method: css-pattern-extraction
""",
        encoding="utf-8",
    )
    return True


def main():
    findings_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"
    if findings_path == "/dev/stdin":
        data = json.loads(sys.stdin.read())
    else:
        data = json.loads(Path(findings_path).read_text())

    base_dir = patterns_dir()
    base_dir.mkdir(parents=True, exist_ok=True)
    added = 0

    # Hover patterns
    for i, hover in enumerate(data.get("hover_states", [])[:10]):
        if isinstance(hover, (list, tuple)) and len(hover) >= 2:
            selector, body = str(hover[0]), str(hover[1])
        else:
            selector, body = f".item-{i}", str(hover)
        sel_clean = selector.strip()
        first_class_root = sel_clean.lstrip(".").split()[0] if sel_clean else f"item-{i}"
        slug = f"hover-effect-{i:02d}-{slugify(sel_clean[:20])}"
        css = (
            f"{sel_clean} {{\n  transition: all 0.3s ease;\n}}\n\n"
            f"{sel_clean}:hover {{\n{body.strip()}\n}}"
        )
        html = f'<div class="{first_class_root}">Hover me</div>'
        if write_pattern(base_dir, slug, f"Hover {i}", css, html, "Hover effect extracted from real site"):
            added += 1

    # Keyframe animations
    for i, kf in enumerate(data.get("keyframes", [])[:10]):
        if isinstance(kf, (list, tuple)) and kf:
            name = str(kf[0])
        elif isinstance(kf, str):
            name = kf
        else:
            name = f"anim-{i}"
        slug = f"animation-{i:02d}-{slugify(name)}"
        css = (
            f"@keyframes {name} {{\n  /* extracted from real site */\n}}\n"
            f".anim-{i:02d} {{\n  animation: {name} 1.2s ease forwards;\n}}"
        )
        html = f'<div class="anim-{i:02d}">Animated</div>'
        if write_pattern(base_dir, slug, f"Animation {name}", css, html, f"Keyframe animation: {name}"):
            added += 1

    # Backdrop-filter (glassmorphism)
    for i, bf in enumerate(data.get("backdrop_filter", [])[:5]):
        slug = f"glass-{i:02d}"
        bf_value = bf if isinstance(bf, str) else " ".join(str(x) for x in bf)
        css = (
            f".glass-{i:02d} {{\n"
            f"  background: rgba(255,255,255,0.1);\n"
            f"  backdrop-filter: {bf_value};\n"
            f"  -webkit-backdrop-filter: {bf_value};\n"
            f"  border: 1px solid rgba(255,255,255,0.2);\n"
            f"  border-radius: 12px;\n}}"
        )
        html = f'<div class="glass-{i:02d}">Glass card</div>'
        if write_pattern(base_dir, slug, f"Glass {i}", css, html, "Glassmorphism with backdrop-filter"):
            added += 1

    # Complex gradients
    for i, gr in enumerate(data.get("gradient_complex", [])[:5]):
        slug = f"gradient-mesh-{i:02d}"
        gr_value = gr if isinstance(gr, str) else " ".join(str(x) for x in gr)
        css = (
            f".gradient-{i:02d} {{\n"
            f"  background: {gr_value};\n"
            f"  background-size: 200% 200%;\n"
            f"  animation: gradient-flow 8s ease infinite;\n}}\n"
            f"@keyframes gradient-flow {{\n"
            f"  0%, 100% {{ background-position: 0 0; }}\n"
            f"  50% {{ background-position: 100% 100%; }}\n}}"
        )
        html = f'<div class="gradient-{i:02d}">Mesh gradient</div>'
        if write_pattern(base_dir, slug, f"Gradient mesh {i}", css, html, "Animated complex gradient"):
            added += 1

    print(f"✅ Added {added} new patterns to {base_dir}")


if __name__ == "__main__":
    main()

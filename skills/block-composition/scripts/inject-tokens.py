#!/usr/bin/env python3
"""Replace CSS custom properties in a template.html with values from tokens.json + mood CSS.

Mapping convention:
  tokens.json key "color.accent" → CSS var --color-accent
  tokens.json key "font.display" → CSS var --font-display
  tokens.json key "spacing.lg"   → CSS var --spacing-lg

CSS vars NOT covered in tokens.json are preserved verbatim.

PR-S: --mood parameter loads mood palette.css and injects before tokens.

Usage: inject-tokens.py <template.html> <tokens.json> <output.html> [--mood <name>]
"""
import argparse
import json
import re
import sys
from pathlib import Path


def flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in d.items():
        key = f"{prefix}-{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = str(v)
    return out


def extract_css_vars_from_file(css_path: Path) -> dict[str, str]:
    """Extract CSS custom properties from a palette.css file."""
    vars_dict = {}
    if not css_path.exists():
        return vars_dict
    content = css_path.read_text(encoding="utf-8")
    # Match :root { --var: value; } patterns
    pattern = re.compile(r"--([a-z0-9-]+):\s*([^;]+);")
    for match in pattern.finditer(content):
        var_name = match.group(1)
        var_value = match.group(2).strip()
        vars_dict[var_name] = var_value
    return vars_dict


def main(in_html: str, tokens_path: str, out_html: str, mood: str = None) -> None:
    html_text = Path(in_html).read_text(encoding="utf-8")
    tokens = json.loads(Path(tokens_path).read_text(encoding="utf-8"))
    flat = flatten(tokens)

    # PR-S: Load mood CSS vars if mood specified (NEW)
    mood_vars = {}
    if mood:
        # Assuming this script is in skills/block-composition/scripts/
        # So we traverse up to skills/ then to block-library/_styles/{mood}/palette.css
        script_dir = Path(__file__).parent
        library_root = script_dir.parent.parent / "block-library"
        mood_palette = library_root / "_styles" / mood / "palette.css"
        mood_vars = extract_css_vars_from_file(mood_palette)

    def repl(match: re.Match) -> str:
        name = match.group(1)
        # Check mood vars first (they should override tokens)
        if mood_vars and name in mood_vars:
            return f"--{name}: {mood_vars[name]};"
        if name in flat:
            return f"--{name}: {flat[name]};"
        return match.group(0)

    pattern = re.compile(r"--([\w-]+):\s*[^;]+;")
    new_text = pattern.sub(repl, html_text)
    Path(out_html).write_text(new_text, encoding="utf-8")
    print(f"OK: wrote {out_html}" + (f" (with mood: {mood})" if mood else ""))


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Inject tokens.json and optional mood CSS into HTML template"
    )
    p.add_argument("in_html", help="Input HTML template")
    p.add_argument("tokens_path", help="Path to tokens.json")
    p.add_argument("out_html", help="Output HTML file")
    p.add_argument("--mood", help="Optional mood name (PR-S)")
    args = p.parse_args()
    main(args.in_html, args.tokens_path, args.out_html, mood=args.mood)

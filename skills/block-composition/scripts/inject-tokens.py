#!/usr/bin/env python3
"""Replace CSS custom properties in a template.html with values from tokens.json.

Mapping convention:
  tokens.json key "color.accent" → CSS var --color-accent
  tokens.json key "font.display" → CSS var --font-display
  tokens.json key "spacing.lg"   → CSS var --spacing-lg

CSS vars NOT covered in tokens.json are preserved verbatim.

Usage: inject-tokens.py <template.html> <tokens.json> <output.html>
"""
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


def main(in_html: str, tokens_path: str, out_html: str) -> None:
    html_text = Path(in_html).read_text(encoding="utf-8")
    tokens = json.loads(Path(tokens_path).read_text(encoding="utf-8"))
    flat = flatten(tokens)

    def repl(match: re.Match) -> str:
        name = match.group(1)
        if name in flat:
            return f"--{name}: {flat[name]};"
        return match.group(0)

    pattern = re.compile(r"--([\w-]+):\s*[^;]+;")
    new_text = pattern.sub(repl, html_text)
    Path(out_html).write_text(new_text, encoding="utf-8")
    print(f"OK: wrote {out_html}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: inject-tokens.py <in.html> <tokens.json> <out.html>", file=sys.stderr)
        sys.exit(2)
    main(*sys.argv[1:])

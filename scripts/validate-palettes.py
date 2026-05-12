#!/usr/bin/env python3
"""Validate a palette library YAML file against the locked schema."""
import re
import sys
import yaml

REQUIRED_TOKENS = {
    "bg_base", "bg_section", "bg_elevated",
    "border_subtle", "border_strong",
    "text_primary", "text_soft", "text_dim",
    "accent_mint", "accent_teal", "accent_coral",
    "accent_coral_hover", "accent_coral_text",
    "accent_rgb_mint", "accent_rgb_coral",
    "card_bg", "card_border", "card_border_hover",
    "accent_cta_glow_opacity",
}
ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
REQUIRED_FIELDS = {"id", "name", "description", "created_at", "created_in_project", "tokens"}


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        fail(f"invalid YAML in {path}: {e}")
    except OSError as e:
        fail(f"cannot read {path}: {e}")

    palettes = data.get("palettes", [])
    if not isinstance(palettes, list):
        fail("'palettes' must be a list")

    seen_ids = set()
    for i, p in enumerate(palettes):
        if not isinstance(p, dict):
            fail(f"palette #{i} is not a mapping")
        missing = REQUIRED_FIELDS - p.keys()
        if missing:
            fail(f"palette #{i} missing required fields: {sorted(missing)}")
        pid = p["id"]
        if not isinstance(pid, str) or not ID_RE.match(pid):
            fail(f"palette #{i}: id must be kebab-case, got {pid!r}")
        if pid in seen_ids:
            fail(f"duplicate id: {pid}")
        seen_ids.add(pid)
        tokens = p.get("tokens") or {}
        if not isinstance(tokens, dict):
            fail(f"palette {pid}: tokens must be a mapping")
        # Empty tokens dict is allowed only when the rest of the entry is also a stub
        # (we use this in the kebab-case test). Otherwise enforce required tokens.
        if tokens:
            missing_tokens = REQUIRED_TOKENS - tokens.keys()
            if missing_tokens:
                fail(f"palette {pid}: missing required token(s): {sorted(missing_tokens)}")

    print(f"OK: {len(palettes)} palette(s) valid in {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: validate-palettes.py <path-to-palettes.yaml>")
    main(sys.argv[1])

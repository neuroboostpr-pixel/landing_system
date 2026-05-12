#!/usr/bin/env python3
"""Parse body.theme-h/i/j/k blocks from main.css → 04_БРЕНД/palettes.yaml."""
import argparse
import os
import re
import sys
import yaml

# Map letter → migration id and name.
LETTER_MAP = {
    "h": ("nu-paper", "Бумажный"),
    "i": ("nu-quiet-dark", "Тихий-тёмный"),
    "j": ("nu-beige", "Бежевый"),
    "k": ("nu-iqido", "IQIDO Guideline"),
}

# CSS-var → yaml token key.
VAR_TO_KEY = {
    "--bg-base": "bg_base",
    "--bg-section": "bg_section",
    "--bg-elevated": "bg_elevated",
    "--border-subtle": "border_subtle",
    "--border-strong": "border_strong",
    "--text-primary": "text_primary",
    "--text-soft": "text_soft",
    "--text-dim": "text_dim",
    "--accent-mint": "accent_mint",
    "--accent-teal": "accent_teal",
    "--accent-coral": "accent_coral",
    "--accent-coral-hover": "accent_coral_hover",
    "--accent-coral-text": "accent_coral_text",
    "--accent-rgb-mint": "accent_rgb_mint",
    "--accent-rgb-coral": "accent_rgb_coral",
    "--card-bg": "card_bg",
    "--card-border": "card_border",
    "--card-border-hover": "card_border_hover",
    "--accent-cta-glow-opacity": "accent_cta_glow_opacity",
}


def parse_block(css, letter):
    pattern = re.compile(
        r"body\.theme-" + letter + r"\s*\{(.*?)\}",
        re.DOTALL,
    )
    m = pattern.search(css)
    if not m:
        print(f"ERROR: theme-{letter} block not found in CSS", file=sys.stderr)
        sys.exit(1)
    body = m.group(1)
    tokens = {}
    for var, key in VAR_TO_KEY.items():
        vm = re.search(re.escape(var) + r"\s*:\s*([^;]+?)\s*;", body)
        if not vm:
            print(f"ERROR: theme-{letter} missing {var}", file=sys.stderr)
            sys.exit(1)
        tokens[key] = vm.group(1).strip()
    return tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--css", required=True)
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    with open(args.css, "r", encoding="utf-8") as f:
        css = f.read()

    palettes = []
    for letter, (pid, pname) in LETTER_MAP.items():
        tokens = parse_block(css, letter)
        palettes.append({
            "id": pid,
            "name": pname,
            "description": f"Migrated from neuroupgrade-v2 theme-{letter}.",
            "created_at": "2026-05-12",
            "created_in_project": "neuroupgrade-v2",
            "tokens": tokens,
        })

    dest_dir = os.path.join(args.project, "04_БРЕНД")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "palettes.yaml")
    with open(dest, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Project palette snapshot (migrated from theme CSS)\n")
        yaml.safe_dump({"palettes": palettes}, f, sort_keys=False, allow_unicode=True)
    # Mirror to design-system folder so /landing-design's export hook picks them up.
    ds_dir = os.path.join(args.project, "05_ДИЗАЙН-СИСТЕМА")
    os.makedirs(ds_dir, exist_ok=True)
    with open(os.path.join(ds_dir, "palettes.yaml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("# Mirror of 04_БРЕНД/palettes.yaml for design-system traceability.\n")
        yaml.safe_dump({"palettes": palettes}, f, sort_keys=False, allow_unicode=True)
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()

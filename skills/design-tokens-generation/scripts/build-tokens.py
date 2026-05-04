#!/usr/bin/env python3
"""Build DESIGN.md and tokens.json from 04_БРЕНД/brand-kit.md.

CLI: python3 build-tokens.py <project-dir>
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import success, warn, error

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{3,8}$')
_FAMILY_RE = re.compile(r'[^a-zA-Z0-9 _\-]')


def _safe_hex(value: str) -> str:
    return value if _HEX_RE.match(str(value)) else "#000000"


def _safe_family(value: str) -> str:
    return _FAMILY_RE.sub('', str(value)).strip() or "sans-serif"


def _load_brand_kit(project_dir: Path) -> dict:
    md_path = project_dir / "04_БРЕНД" / "brand-kit.md"
    if not md_path.exists():
        warn(f"brand-kit.md not found: {md_path} — using defaults")
        return {}
    content = md_path.read_text(encoding="utf-8")
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        warn("brand-kit.md has no YAML frontmatter — using defaults")
        return {}
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        return {}
    return data.get("brand_kit", data)


def _extract_colors(bk: dict) -> dict:
    src = bk.get("colors", {})
    if not isinstance(src, dict):
        src = {}

    def _entry(role: str) -> dict:
        c = src.get(role, {})
        if isinstance(c, dict):
            return {"hex": _safe_hex(c.get("hex", "#000000")), "source": c.get("source", "brand-kit.md")}
        return {"hex": _safe_hex(str(c)), "source": "brand-kit.md"}

    return {
        "primary": _entry("primary"),
        "secondary": _entry("secondary"),
        "accent": _entry("accent"),
        "text": {"hex": "#1a1a2e", "source": "generated"},
        "bg": {"hex": "#ffffff", "source": "generated"},
    }


def _extract_typography(bk: dict) -> dict:
    src = bk.get("typography", {})
    if not isinstance(src, dict):
        src = {}

    def _entry(role: str, default_family: str, weight: int) -> dict:
        t = src.get(role, {})
        if isinstance(t, dict):
            return {
                "family": _safe_family(t.get("family", default_family)),
                "weight": weight,
                "source": t.get("source", "brand-kit.md"),
            }
        return {"family": _safe_family(str(t)), "weight": weight, "source": "brand-kit.md"}

    return {
        "display": _entry("display", "sans-serif", 700),
        "body": _entry("body", "sans-serif", 400),
        "sizes": {
            "h1": "clamp(2.5rem, 6vw, 5rem)",
            "h2": "clamp(1.75rem, 4vw, 3rem)",
            "h3": "clamp(1.25rem, 3vw, 2rem)",
            "base": "1rem",
            "sm": "0.875rem",
        },
    }


def build_tokens(bk: dict) -> dict:
    return {
        "colors": _extract_colors(bk),
        "typography": _extract_typography(bk),
        "spacing": {
            "xs": "0.5rem", "sm": "1rem", "md": "1.5rem",
            "lg": "2rem", "xl": "3rem", "2xl": "4rem", "3xl": "6rem",
        },
        "grid": {"columns": 12, "gap": "24px", "max_width": "1200px"},
        "radius": {"sm": "4px", "md": "8px", "lg": "16px", "full": "9999px"},
        "shadow": {
            "sm": "0 1px 3px rgba(0,0,0,0.1)",
            "md": "0 4px 12px rgba(0,0,0,0.1)",
            "lg": "0 16px 40px rgba(0,0,0,0.15)",
        },
        "breakpoints": {"mobile": "375px", "tablet": "768px", "desktop": "1440px"},
        "motion": {
            "duration_fast": "200ms",
            "duration_base": "300ms",
            "duration_slow": "500ms",
            "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
        },
    }


def _write_design_md(project_dir: Path, tokens: dict) -> None:
    design_dir = project_dir / "05_ДИЗАЙН-СИСТЕМА"
    design_dir.mkdir(parents=True, exist_ok=True)

    colors = tokens["colors"]
    typo = tokens["typography"]
    spacing = tokens["spacing"]
    motion = tokens["motion"]
    grid = tokens["grid"]

    frontmatter = yaml.dump({"tokens": tokens}, allow_unicode=True, default_flow_style=False)

    md = f"---\n{frontmatter}---\n\n# Design System\n\n"
    md += "## Цвета\n\n| Токен | Hex | Источник |\n|---|---|---|\n"
    for name, color in colors.items():
        md += f"| `--color-{name}` | `{color['hex']}` | {color['source']} |\n"
    md += "\n## Типографика\n\n| Токен | Значение | Источник |\n|---|---|---|\n"
    md += f"| `--font-display` | {typo['display']['family']} | {typo['display']['source']} |\n"
    md += f"| `--font-body` | {typo['body']['family']} | {typo['body']['source']} |\n"
    for size_name, size_val in typo["sizes"].items():
        md += f"| `--size-{size_name}` | {size_val} | generated |\n"
    md += "\n## Отступы\n\n| Токен | Значение |\n|---|---|\n"
    for name, val in spacing.items():
        md += f"| `--space-{name}` | {val} |\n"
    md += f"\n## Сетка\n\n- Колонки: {grid['columns']}\n- Gap: {grid['gap']}\n- Max-width: {grid['max_width']}\n"
    md += "\n## Motion\n\n| Токен | Значение |\n|---|---|\n"
    for name, val in motion.items():
        md += f"| `--{name.replace('_', '-')}` | {val} |\n"

    (design_dir / "DESIGN.md").write_text(md, encoding="utf-8")


def _write_tokens_json(project_dir: Path, tokens: dict) -> None:
    design_dir = project_dir / "05_ДИЗАЙН-СИСТЕМА"
    design_dir.mkdir(parents=True, exist_ok=True)
    (design_dir / "tokens.json").write_text(
        json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv: list) -> int:
    p = argparse.ArgumentParser(description="Build DESIGN.md and tokens.json from brand-kit.md.")
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        project_dir = Path(args.project_dir)
        bk = _load_brand_kit(project_dir)
        tokens = build_tokens(bk)
        _write_design_md(project_dir, tokens)
        _write_tokens_json(project_dir, tokens)
        success(f"DESIGN.md + tokens.json → {project_dir / '05_ДИЗАЙН-СИСТЕМА'}")
        return 0
    except Exception as exc:
        error(f"build-tokens failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

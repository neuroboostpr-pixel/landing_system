#!/usr/bin/env python3
"""Synthesize brand-kit.md from extracted style data with full provenance."""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

import yaml

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{3,8}$')
_FAMILY_RE = re.compile(r'[^a-zA-Z0-9 _\-]')


def _safe_hex(value: str) -> str:
    """Return value if it looks like a CSS hex color, else '#000000'."""
    return value if _HEX_RE.match(value) else "#000000"


def _safe_family(value: str) -> str:
    """Strip non-CSS-safe characters from a font-family name."""
    return _FAMILY_RE.sub('', value).strip() or "sans-serif"

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.logger import success, warn, error


def _load_yaml(path: Path) -> dict:
    """Load a YAML file, returning empty dict if absent or non-dict."""
    if not path.exists():
        warn(f"Missing: {path} — using defaults")
        return {}
    result = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        warn(f"Malformed YAML (expected dict, got {type(result).__name__}): {path} — using defaults")
        return {}
    return result


def _load_text_first_line(path: Path, default: str) -> str:
    """Return first non-empty line from a text file, or default."""
    if not path.exists():
        return default
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            return line
    return default


def _count_approved_refs(index_path: Path) -> int:
    """Count refs with status == 'approved' in index.yaml."""
    data = _load_yaml(index_path)
    refs = data.get("refs", [])
    if not isinstance(refs, list):
        return 0
    return sum(1 for r in refs if isinstance(r, dict) and r.get("status") == "approved")


def load_legal_input(project_dir):
    """Load legal: input from 04_БРЕНД/extracted/legal.yaml if exists."""
    legal_path = Path(project_dir) / '04_БРЕНД' / 'extracted' / 'legal.yaml'
    if not legal_path.exists():
        return None
    try:
        with open(legal_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError):
        return None


def build_legal_section(legal_input):
    """Build the ## Legal section from input dict.

    If legal_input is None or missing — emits TODO_LEGAL placeholders.

    Args:
        legal_input: dict with 7 keys (company_name, entity_type, inn, ogrn,
                     legal_address, contact_email, dpo_email) or None.

    Returns:
        Markdown string with '## Legal' header and YAML block.
    """
    if not legal_input:
        legal_input = {
            'company_name': 'TODO_LEGAL',
            'entity_type': 'TODO_LEGAL',
            'inn': 'TODO_LEGAL',
            'ogrn': 'TODO_LEGAL',
            'legal_address': 'TODO_LEGAL',
            'contact_email': 'TODO_LEGAL',
            'dpo_email': 'TODO_LEGAL',
        }

    lines = ['## Legal', '', '```yaml']
    if any(v == 'TODO_LEGAL' for v in legal_input.values()):
        lines.append('# TODO_LEGAL: заполнить до прод-деплоя — без этого лендинг не может запускаться в РФ')

    for key in ['company_name', 'entity_type', 'inn', 'ogrn',
                'legal_address', 'contact_email', 'dpo_email']:
        val = legal_input.get(key, 'TODO_LEGAL')
        # Quote string values to preserve special chars
        lines.append(f"{key}: '{val}'")

    lines.append('```')
    lines.append('')
    return '\n'.join(lines)


def build_brand_kit(project_dir: str) -> Path:
    base = Path(project_dir)
    extracted = base / "04_БРЕНД" / "extracted"

    # --- Load inputs ---
    palette_data = _load_yaml(extracted / "palette.yaml")
    fonts_data = _load_yaml(extracted / "fonts.yaml")
    icons_data = _load_yaml(extracted / "icons.yaml")
    motion_note = _load_text_first_line(extracted / "motion.md", "Subtle transitions, 200-400ms")
    grid_note = _load_text_first_line(extracted / "grid.md", "12-column, 24px gap")
    refs_count = _count_approved_refs(base / "03_РЕФЕРЕНСЫ" / "index.yaml")

    project_name = base.name
    today = date.today().isoformat()

    # --- Colors ---
    palette_list = palette_data.get("palette", [])
    source_image = palette_data.get("source_image", "unknown")

    def _color_entry(idx: int, role: str) -> dict:
        if idx < len(palette_list):
            entry = palette_list[idx]
            pixel = entry.get("source_pixel", [])
            source = f"{source_image}@{pixel}" if pixel else source_image
            return {
                "hex": _safe_hex(entry.get("hex", "#000000")),
                "role": role,
                "source": source,
                "extracted_by": "color-thief",
            }
        return {"hex": "#000000", "role": role, "source": "default", "extracted_by": "color-thief"}

    colors = {
        "primary": _color_entry(0, "primary"),
        "secondary": _color_entry(1, "secondary"),
        "accent": _color_entry(2, "accent"),
    }

    # --- Typography ---
    candidates = fonts_data.get("candidates", [])

    def _font_entry(idx: int) -> dict:
        if idx < len(candidates):
            c = candidates[idx]
            return {
                "family": _safe_family(c.get("family", "sans-serif")),
                "confidence": c.get("confidence", 0.0),
                "source": c.get("source", "unknown"),
            }
        # Fall back to first candidate if only one exists
        if candidates:
            c = candidates[0]
            return {
                "family": _safe_family(c.get("family", "sans-serif")),
                "confidence": c.get("confidence", 0.0),
                "source": c.get("source", "unknown"),
            }
        return {"family": "sans-serif", "confidence": 0.0, "source": "default"}

    typography = {
        "display": _font_entry(0),
        "body": _font_entry(1),
    }

    # --- Icons ---
    results = icons_data.get("results", [])
    library = icons_data.get("recommended_library", "lucide")
    selected_icons = []
    if results:
        first = results[0]
        selected_icons.append({"id": first.get("id", "lucide:circle"), "name": first.get("name", "circle")})

    icons = {
        "library": library,
        "selected": selected_icons,
    }

    # --- Motion & Grid ---
    motion = {"notes": motion_note}
    grid = {"notes": grid_note}

    # --- Build YAML frontmatter ---
    brand_kit = {
        "brand_kit": {
            "meta": {
                "project": project_name,
                "created": today,
                "references_used": refs_count,
            },
            "colors": colors,
            "typography": typography,
            "icons": icons,
            "motion": motion,
            "grid": grid,
        }
    }

    yaml_block = yaml.dump(brand_kit, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # --- Build human-readable Markdown section ---
    primary = colors["primary"]
    secondary = colors["secondary"]
    accent = colors["accent"]
    display = typography["display"]
    body = typography["body"]
    icon_ids = ", ".join(i["id"] for i in selected_icons) if selected_icons else "(none)"

    md_body = f"""# Brand Kit — {project_name}

Generated: {today}

## Colors

- **Primary**: `{primary['hex']}` — primary CTA (source: {primary['source']})
- **Secondary**: `{secondary['hex']}` — secondary (source: {secondary['source']})
- **Accent**: `{accent['hex']}` — accent (source: {accent['source']})

## Typography

- **Display**: {display['family']} (confidence: {display['confidence']}, source: {display['source']})
- **Body**: {body['family']} (confidence: {body['confidence']}, source: {body['source']})

## Icons

Library: {library}
Selected: {icon_ids}

## Motion

{motion_note}

## Grid

{grid_note}
"""

    legal_section = build_legal_section(load_legal_input(project_dir))
    content = f"---\n{yaml_block}---\n\n{md_body}\n{legal_section}"

    out = base / "04_БРЕНД" / "brand-kit.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def main(argv: list) -> int:
    p = argparse.ArgumentParser(description="Build brand-kit.md from extracted style data.")
    p.add_argument("project_dir")
    args = p.parse_args(argv[1:])
    try:
        out = build_brand_kit(args.project_dir)
        success(f"Wrote {out}")
        return 0
    except Exception as exc:
        error(f"build failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

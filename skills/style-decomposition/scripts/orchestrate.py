#!/usr/bin/env python3
"""Style extraction orchestrator — ties palette, fonts, and icons together.

Produces 5 outputs to <refs_dir>/04_БРЕНД/extracted/:
  palette.yaml  fonts.yaml  icons.yaml  grid.md  motion.md

CLI: python3 orchestrate.py <refs-dir> [--images img1 img2] [--url https://...]
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.logger import success, warn, error

# Import library functions from sibling scripts
_SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS))

import importlib.util as _ilu


def _import_script(name: str):
    path = _SCRIPTS / name
    spec = _ilu.spec_from_file_location(name.replace("-", "_").replace(".py", ""), path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_palette_mod = _import_script("extract-palette.py")
_fonts_mod = _import_script("identify-fonts.py")
_icons_mod = _import_script("match-icons.py")

# Re-export for mocking in tests
extract = _palette_mod.extract
identify_url = _fonts_mod.identify_url
match_icons = _icons_mod.match_icons

_DEFAULT_NEEDED_ICONS = ["check", "arrow-right", "user", "x", "sparkles", "shield"]

_GRID_PLACEHOLDER = """# Grid

<!-- Placeholder: to be filled by brand-architect after style review -->

## Base unit
- 8px

## Layout
- Max width: 1280px
- Columns: 12
- Gutter: 24px
- Margin: 40px
"""

_MOTION_PLACEHOLDER = """# Motion

<!-- Placeholder: to be filled by brand-architect after style review -->

## Transitions
- Duration: 200ms (micro), 350ms (elements), 500ms (page)
- Easing: ease-out (enter), ease-in (exit), ease-in-out (transform)

## Principles
- Purposeful: motion guides attention
- Restrained: avoid decorative animation
"""


def run_style_extraction(
    refs_dir: str,
    image_paths: List[str],
    reference_url: Optional[str] = None,
) -> Dict[str, str]:
    """Run complete style extraction and write 5 files.

    Args:
        refs_dir: project root (04_БРЕНД/extracted/ is written here)
        image_paths: list of reference image paths to extract palette from
        reference_url: optional URL for font identification

    Returns dict mapping output keys to their file paths.
    """
    out_dir = Path(refs_dir) / "04_БРЕНД" / "extracted"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Palette ---
    all_colors = []
    for img_path in image_paths:
        try:
            colors = extract(img_path, count=5)
            all_colors.extend(colors)
        except Exception as exc:
            warn(f"Palette extraction failed for {img_path}: {exc}")

    palette_path = out_dir / "palette.yaml"
    palette_path.write_text(
        yaml.safe_dump({
            "source_images": image_paths,
            "palette": all_colors,
        }, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    success(f"Wrote palette.yaml ({len(all_colors)} colors)")

    # --- Fonts ---
    fonts_path = out_dir / "fonts.yaml"
    if reference_url:
        try:
            identify_url(reference_url, str(fonts_path))
            success("Wrote fonts.yaml via DOM inspection")
        except Exception as exc:
            warn(f"Font identification failed: {exc}")
            fonts_path.write_text(
                yaml.safe_dump({
                    "source_url": reference_url,
                    "candidates": [],
                    "manual_review_required": True,
                    "error": str(exc),
                }, allow_unicode=True),
                encoding="utf-8",
            )
    else:
        fonts_path.write_text(
            yaml.safe_dump({
                "source_url": None,
                "candidates": [],
                "manual_review_required": True,
                "note": "No reference URL provided — identify fonts manually",
            }, allow_unicode=True),
            encoding="utf-8",
        )

    # --- Icons ---
    icons_path = out_dir / "icons.yaml"
    try:
        icons_data = match_icons(_DEFAULT_NEEDED_ICONS, str(icons_path))
        # Ensure file is always written (match_icons may skip if mocked)
        if not icons_path.exists():
            icons_path.write_text(
                yaml.safe_dump(icons_data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
        success("Wrote icons.yaml")
    except Exception as exc:
        warn(f"Icon matching failed: {exc}")
        icons_path.write_text(
            yaml.safe_dump({
                "needed": _DEFAULT_NEEDED_ICONS,
                "matches": {},
                "recommendation": {"library": "lucide", "reason": "default (matching failed)"},
                "error": str(exc),
            }, allow_unicode=True),
            encoding="utf-8",
        )

    # --- Grid (placeholder) ---
    grid_path = out_dir / "grid.md"
    if not grid_path.exists():
        grid_path.write_text(_GRID_PLACEHOLDER, encoding="utf-8")
        success("Wrote grid.md (placeholder)")

    # --- Motion (placeholder) ---
    motion_path = out_dir / "motion.md"
    if not motion_path.exists():
        motion_path.write_text(_MOTION_PLACEHOLDER, encoding="utf-8")
        success("Wrote motion.md (placeholder)")

    return {
        "palette": str(palette_path),
        "fonts": str(fonts_path),
        "icons": str(icons_path),
        "grid": str(grid_path),
        "motion": str(motion_path),
    }


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("refs_dir")
    p.add_argument("--images", nargs="*", default=[], dest="images")
    p.add_argument("--url", default=None)
    args = p.parse_args(argv[1:])
    try:
        result = run_style_extraction(args.refs_dir, args.images, args.url)
        success(f"Style extraction complete: {list(result.keys())}")
        return 0
    except Exception as exc:
        error(f"orchestration failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

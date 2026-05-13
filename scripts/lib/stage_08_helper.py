#!/usr/bin/env python3
"""Stage-08 structural check for the Lazy Blocks pipeline.

Called from gate-check.sh as type=script. Validates that the project has the
required Lazy Blocks artifacts (no longer ACF Blocks JSON / template-parts /
gutenberg-blocks/<slug>/block.json — those belong to the deprecated pipeline).

Required artifacts (hard fail if missing/invalid):
  - 08_КОД/block-spec.yaml exists and validates via block_spec.load + validate
  - 08_КОД/wp-theme/functions.php contains both `lzb/init` and
    `lazyblocks()->add_block(`
  - 08_КОД/wp-theme/blocks/ exists and contains AT LEAST one
    lazyblock-*/block.php
  - 08_КОД/page-content.html exists

Soft (warn-only):
  - if block-spec.yaml has any section-card blocks, the AUTO-GENERATED
    lzb-inner-blocks marker should be present in assets/css/main.css.

Exit 0 = pass. Exit 1 = hard fail.

Usage: python stage_08_helper.py <project-root>
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
# block_spec lives inside the wp-gutenberg-block-builder skill
sys.path.insert(
    0,
    str(REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"),
)


def check(project: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # Legacy bypass
    state = project / ".landing-state.yaml"
    if state.exists() and "legacy: true" in state.read_text(encoding="utf-8"):
        print("stage-08: legacy:true — skipping hard checks", file=sys.stderr)
        return 0

    code_dir = project / "08_КОД"

    # 1. block-spec.yaml exists + validates
    spec_path = code_dir / "block-spec.yaml"
    spec = None
    if not spec_path.exists():
        errors.append("block-spec.yaml missing at 08_КОД/block-spec.yaml")
    else:
        try:
            from block_spec import load as spec_load, validate as spec_validate  # noqa: E402
            spec = spec_load(spec_path)
            spec_validate(spec)
        except Exception as e:  # BlockSpecError, yaml errors, import errors
            errors.append(f"block-spec.yaml validation failed: {e}")

    # 2. functions.php contains lzb/init + lazyblocks()->add_block(
    fn = code_dir / "wp-theme" / "functions.php"
    if not fn.exists():
        errors.append("wp-theme/functions.php missing")
    else:
        text = fn.read_text(encoding="utf-8", errors="replace")
        if "lzb/init" not in text:
            errors.append("functions.php missing 'lzb/init' action hook")
        if "lazyblocks()->add_block(" not in text:
            errors.append(
                "functions.php missing 'lazyblocks()->add_block(' registration call"
            )

    # 3. blocks/ dir with at least one lazyblock-*/block.php
    blocks_dir = code_dir / "wp-theme" / "blocks"
    if not blocks_dir.is_dir():
        errors.append("wp-theme/blocks/ directory missing")
    else:
        any_block = False
        for child in blocks_dir.iterdir():
            if child.is_dir() and child.name.startswith("lazyblock-"):
                if (child / "block.php").exists():
                    any_block = True
                    break
        if not any_block:
            errors.append(
                "wp-theme/blocks/ has no lazyblock-*/block.php (run generate-lzb-templates)"
            )

    # 4. page-content.html exists
    page = code_dir / "page-content.html"
    if not page.exists():
        errors.append("page-content.html missing at 08_КОД/page-content.html")

    # Soft: section-card blocks should yield AUTO-GENERATED CSS marker
    if spec is not None:
        has_section_card = any(
            getattr(b, "type", None) == "section-card" for b in getattr(spec, "blocks", [])
        )
        if has_section_card:
            css = code_dir / "wp-theme" / "assets" / "css" / "main.css"
            if not css.exists():
                warnings.append(
                    "assets/css/main.css missing — section-card blocks need display:contents patches"
                )
            else:
                ctext = css.read_text(encoding="utf-8", errors="replace")
                if "AUTO-GENERATED" not in ctext:
                    warnings.append(
                        "assets/css/main.css lacks AUTO-GENERATED lzb-inner-blocks marker"
                    )

    for w in warnings:
        print(f"⚠ {w}", file=sys.stderr)
    for e in errors:
        print(f"❌ {e}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: stage_08_helper.py <project-root>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check(Path(sys.argv[1])))

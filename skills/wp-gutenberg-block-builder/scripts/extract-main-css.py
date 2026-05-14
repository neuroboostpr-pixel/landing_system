#!/usr/bin/env python3
"""Regenerate <project>/08_КОД/wp-theme/assets/css/main.css from DESIGN.md.

Uses the existing design_extractor.extract() — which scans DESIGN.md §3-§9
fenced ```css blocks — and writes ONLY main.css. style.css is left alone.

After writing main.css, also re-runs generate-css-patches.py to re-append
the `display: contents` rules for InnerBlocks wrappers — without these,
Lazy Blocks section+card grids collapse to one column because each
sub-block is wrapped in <div class="wp-block-lazyblock-<slug>">.

Used by /landing-style after frontend-builder edits DESIGN.md §5.

WARNING: any manual edits to main.css are overwritten on every run.
Edit DESIGN.md §3-§9 (single source of truth) instead.

Exit 0: main.css written + patches reapplied.
Exit 1: theme css dir missing (run /landing-build first), DESIGN.md missing,
        or css-patches step failed.
Exit 2: missing argv.

Usage: extract-main-css.py <project-dir>
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from design_extractor import DesignExtractError, extract  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: extract-main-css.py <project-dir>", file=sys.stderr)
        return 2
    project = Path(argv[1])
    md = project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    out_dir = project / "08_КОД" / "wp-theme" / "assets" / "css"
    out_path = out_dir / "main.css"
    if not out_dir.exists():
        print(f"theme css dir not found: {out_dir} — run /landing-build first", file=sys.stderr)
        return 1
    try:
        _style_css, main_css = extract(md)
    except DesignExtractError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    body = main_css.strip() if main_css.strip() else "/* main.css — DESIGN.md had no §3-§9 styles */"
    out_path.write_text(body + "\n", encoding="utf-8")

    # Re-apply display:contents patches if block-spec.yaml is present.
    # When called from /landing-style on a real project, block-spec.yaml
    # always exists (gate-08_build hard-check enforces it). In tests it
    # may be missing — that's fine, skip silently.
    if (project / "08_КОД" / "block-spec.yaml").exists():
        patches_script = Path(__file__).resolve().parent / "generate-css-patches.py"
        r = subprocess.run(
            [sys.executable, str(patches_script), "--project", str(project)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"css-patches step failed: {r.stderr}", file=sys.stderr)
            return 1

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

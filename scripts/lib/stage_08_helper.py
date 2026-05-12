#!/usr/bin/env python3
"""Stage-08 structural check (called from gate-check.sh as type=script).

Runs checks 4 (JSON valid), 5 (ACF group per H2), 6 (each group ≥1 field),
7 (block-<slug>.php exists), 8 (block.json per registered block), and 9
(block.json has recommended fields → warning).

Exit 0 = pass. Exit 1 = hard fail. Warnings printed to stderr but do not
affect exit code unless --strict-warnings is passed.

Usage: python stage_08_helper.py <project-root>
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402


def check(project: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # Bypass if legacy
    state = project / ".landing-state.yaml"
    if state.exists() and "legacy: true" in state.read_text(encoding="utf-8"):
        print("stage-08: legacy:true — skipping hard checks", file=sys.stderr)
        return 0

    md = project / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(md))
        ContentParser.validate(blocks)
    except (ContentParseError, FileNotFoundError) as e:
        errors.append(f"final-copy.md unparseable: {e}")
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        return 1

    expected_slugs = {b.slug for b in blocks}

    acf_path = project / "08_КОД" / "acf-fields.json"
    if not acf_path.exists():
        errors.append("acf-fields.json missing")
    else:
        try:
            acf_data = json.load(acf_path.open(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"acf-fields.json invalid JSON: {e}")
            acf_data = None

        if acf_data is not None:
            if not isinstance(acf_data, list):
                acf_data = [acf_data]
            acf_slugs = set()
            for g in acf_data:
                loc = (g.get("location") or [[{}]])[0][0] if g.get("location") else {}
                val = loc.get("value", "")
                if val.startswith("acf/lp-"):
                    slug = val.removeprefix("acf/lp-")
                    acf_slugs.add(slug)
                    if not g.get("fields"):
                        errors.append(f"ACF group '{slug}' has no fields (#6)")
            for slug in expected_slugs - acf_slugs:
                errors.append(f"ACF group missing for block '{slug}' (#5)")

    # Per-block file checks
    for slug in expected_slugs:
        part = project / "08_КОД" / "wp-theme" / "template-parts" / f"block-{slug}.php"
        if not part.exists():
            errors.append(f"template-parts/block-{slug}.php missing (#7)")
        bj = project / "08_КОД" / "gutenberg-blocks" / slug / "block.json"
        if not bj.exists():
            errors.append(f"gutenberg-blocks/{slug}/block.json missing (#8)")
        else:
            try:
                d = json.load(bj.open(encoding="utf-8"))
                missing = [k for k in ("title", "description", "category", "icon") if not d.get(k)]
                if missing:
                    warnings.append(f"block.json for '{slug}' missing recommended fields: {missing}")
            except json.JSONDecodeError as e:
                errors.append(f"block.json for '{slug}' invalid: {e}")

    # manual review warning
    if state.exists():
        st = state.read_text(encoding="utf-8")
        if "manual_field_review_needed:" in st:
            warnings.append(f"manual_field_review_needed flag set in state.yaml — verify generated fields")

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

#!/usr/bin/env python3
"""Lint composed.html against block-spec.yaml.

Exit codes:
  0 — no errors (warnings allowed)
  1 — at least one error
  2 — system error (spec missing, parse error, etc.)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))

from composed_inspector import inspect  # noqa: E402
from spec_inspector import inspect_spec  # noqa: E402
import lint_heuristics as lh  # noqa: E402


def _default_composed(project: Path):
    for cand in ("composed-brutalist.html", "composed.html"):
        p = project / "07b_COMPOSED" / cand
        if p.exists():
            return p
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="Project root (assumes 07b_COMPOSED/ and 08_КОД/)")
    ap.add_argument("--composed", help="Path to composed.html (overrides --project default)")
    ap.add_argument("--spec", help="Path to block-spec.yaml (overrides --project default)")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args(argv[1:])

    if args.spec:
        spec_path = Path(args.spec)
    elif args.project:
        spec_path = Path(args.project) / "08_КОД" / "block-spec.yaml"
    else:
        print("ERROR: must pass --project or --spec", file=sys.stderr)
        return 2
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}", file=sys.stderr)
        return 2

    if args.composed:
        composed_path = Path(args.composed)
    elif args.project:
        composed_path = _default_composed(Path(args.project))
    else:
        composed_path = None

    if composed_path is None or not composed_path.exists():
        print("WARNING: composed.html not found; skipping lint")
        return 0

    spec = inspect_spec(spec_path)
    probes = [b.probe_selector for b in spec.blocks if b.probe_selector]
    if not probes:
        print("WARNING: no probe_selector defined on any block; nothing to lint")
        return 0

    dom_blocks = {b.probe_selector: b for b in inspect(composed_path, probes)}

    issues = []
    for sb in spec.blocks:
        if not sb.probe_selector:
            continue
        dom_block = dom_blocks.get(sb.probe_selector)
        if dom_block is None or not dom_block.matches:
            issues.append(lh.LintIssue(
                severity="error", block_slug=sb.slug, heuristic="probe-match",
                message=f"{sb.slug} probe_selector {sb.probe_selector!r} not found in composed.html",
            ))
            continue

        if sb.probe_kind == "single" and len(dom_block.matches) != 1:
            issues.append(lh.LintIssue(
                severity="error", block_slug=sb.slug, heuristic="probe-match",
                message=f"{sb.slug} expected 1 instance, found {len(dom_block.matches)}",
            ))

        for idx, match in enumerate(dom_block.matches):
            issues.extend(lh.check_bullets(sb, match.soup))
            issues.extend(lh.check_color_swatches(sb, match.soup))
            for c in sb.controls + sb.card_controls:
                if c.type == "textarea":
                    issues.extend(lh.check_multi_paragraph(sb, match.soup, target_field=c.name))
            if sb.probe_kind == "card-collection":
                issues.extend(lh.check_slider_images(sb, match.soup, template_index=idx))
                issues.extend(lh.check_inline_svg_icon(sb, match.soup, template_index=idx))

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if args.json:
        import json as _json
        print(_json.dumps({
            "errors": [vars(i) for i in errors],
            "warnings": [vars(i) for i in warnings],
        }, ensure_ascii=False, indent=2))
    else:
        for i in errors:
            print(f"  ERROR [{i.heuristic}] {i.block_slug}: {i.message}")
            if i.suggested_fragment:
                print(f"    suggestion:\n      {i.suggested_fragment}")
        for i in warnings:
            print(f"  WARN  [{i.heuristic}] {i.block_slug}: {i.message}")
        print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

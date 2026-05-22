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
    ap.add_argument("--fix", action="store_true",
                    help="Auto-apply safe fixes to spec.yaml (only multi-paragraph; only inline-dict default format)")
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
            if sb.probe_kind == "card-collection" and sb.card_probe_selector:
                # Iterate per individual card. Card-level heuristics run on each
                # card's soup; section-level heuristics run on the section soup
                # AFTER detaching cards (so their inner <p>/<li>/etc. don't leak
                # into section counts).
                card_matches = match.soup.select(sb.card_probe_selector)

                # Card-level heuristics: bullets, swatches, multi-paragraph,
                # slider, svg — one pass per card with its template row.
                for card_idx, card_soup in enumerate(card_matches):
                    # Bullets/swatches typically belong to cards in our layouts.
                    issues.extend(lh.check_bullets(sb, card_soup))
                    issues.extend(lh.check_color_swatches(sb, card_soup))
                    for c in sb.card_controls:
                        if c.type == "textarea":
                            issues.extend(lh.check_multi_paragraph(
                                sb, card_soup, target_field=c.name
                            ))
                    issues.extend(lh.check_slider_images(sb, card_soup, template_index=card_idx))
                    issues.extend(lh.check_inline_svg_icon(sb, card_soup, template_index=card_idx))

                # Section-level: detach card subtrees from a soup copy, then
                # run section-control multi-paragraph against the remainder.
                # We use a clone via str(soup) → re-parse to avoid mutating.
                from bs4 import BeautifulSoup as _BS
                section_clone = _BS(str(match.soup), "html.parser")
                for card in section_clone.select(sb.card_probe_selector):
                    card.decompose()
                for c in sb.controls:
                    if c.type == "textarea":
                        issues.extend(lh.check_multi_paragraph(
                            sb, section_clone, target_field=c.name
                        ))
            else:
                # Legacy / single-block path: all heuristics run against the
                # whole match.soup. Same as the v1 behaviour.
                issues.extend(lh.check_bullets(sb, match.soup))
                issues.extend(lh.check_color_swatches(sb, match.soup))
                for c in sb.controls + sb.card_controls:
                    if c.type == "textarea":
                        issues.extend(lh.check_multi_paragraph(sb, match.soup, target_field=c.name))
                if sb.probe_kind == "card-collection":
                    # card-collection without card_probe_selector — best-effort
                    # using section-wide template index.
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

    # NOTE: --fix v1 supports only multi-paragraph extraction and only inline-dict
    # YAML defaults (`default: "..."`). Block-scalar defaults are not matched.
    if args.fix and errors:
        import shutil, time, re as _re
        ts = time.strftime("%Y%m%d-%H%M%S")
        backup = spec_path.with_suffix(spec_path.suffix + f".bak.{ts}")
        shutil.copy(spec_path, backup)
        print(f"Backup written: {backup}")

        spec_text = spec_path.read_text(encoding="utf-8")
        applied = 0

        for issue in errors:
            if issue.heuristic == "multi-paragraph":
                # Message format: "<slug>.<field>: composed has N paragraphs but spec default has only M"
                m = _re.match(r"([^.]+)\.(\w+):", issue.message)
                if not m:
                    continue
                slug, field = m.group(1), m.group(2)
                sb = next((b for b in spec.blocks if b.slug == slug), None)
                if not sb or not sb.probe_selector:
                    continue
                dom = dom_blocks.get(sb.probe_selector)
                if not dom or not dom.matches:
                    continue
                paragraphs = [p.get_text(" ", strip=True) for p in dom.matches[0].soup.find_all("p")]
                paragraphs = [p for p in paragraphs if p]
                if not paragraphs:
                    continue
                new_default = "\n\n".join(paragraphs)
                # Replace default in inline-dict spec format:
                #   { id: ..., name: feat_statement, ..., default: "..." }
                pattern = _re.compile(
                    rf"(\{{[^}}]*name:\s*{_re.escape(field)}[^}}]*default:\s*)\"[^\"]*\"",
                    _re.DOTALL,
                )
                quoted = new_default.replace('\\', '\\\\').replace('"', '\\"').replace("\n", "\\n")
                new_text, n = pattern.subn(
                    rf'\1"{quoted}"  # AUTO-LINT {ts}: filled from composed.html',
                    spec_text, count=1,
                )
                if n:
                    spec_text = new_text
                    applied += 1

        if applied:
            spec_path.write_text(spec_text, encoding="utf-8")
            print(f"Applied {applied} auto-fix(es). Re-run without --fix to verify.")
        else:
            print("No auto-fixable issues found.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

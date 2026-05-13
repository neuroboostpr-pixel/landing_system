#!/usr/bin/env python3
"""Render <project>/07a_WIREFRAME/wireframe.html from prototype.yaml + block-library."""
import argparse
import csv
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

CHECKED_TPL = (
    "#{rid}:checked ~ .variants-stage [data-variant=\"{rid}\"] {{ display: flex; }}"
)

UX_NOT_AVAILABLE_BANNER = (
    '<div style="margin:24px; padding:16px 24px; background:#fffbe6; border:1px solid #ffe58f; '
    'border-radius:8px; color:#7d4e00; font-size:14px;">'
    '<strong>⚠️ ui-ux-pro-max не найден</strong> — установи по адресу '
    '<code>~/.claude/skills/ui-ux-pro-max/</code> для получения рекомендаций по UX-паттернам. '
    'Инструкция: <a href="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill" target="_blank">'
    'github.com/nextlevelbuilder/ui-ux-pro-max-skill</a></div>'
)


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def load_ux_patterns(rules_dir: Path, niche: str) -> list[dict]:
    """Load top-5 landing patterns from landing.csv, filtered by niche keywords."""
    landing_csv = rules_dir / "landing.csv"
    if not landing_csv.exists():
        print(
            f"WARNING: ui-ux-pro-max landing.csv not found at {landing_csv}. "
            "Install ui-ux-pro-max at ~/.claude/skills/ui-ux-pro-max/ for pattern recommendations.",
            file=sys.stderr,
        )
        return []

    patterns: list[dict] = []
    niche_lower = niche.lower()
    niche_words = set(niche_lower.replace("-", " ").replace("_", " ").split())

    with landing_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    # Find niche-relevant patterns first
    matched: list[dict] = []
    unmatched: list[dict] = []
    for row in all_rows:
        keywords_str = row.get("Keywords", "").lower()
        keywords_set = set(k.strip() for k in keywords_str.replace(",", " ").split())
        if niche_words & keywords_set or any(
            w in keywords_str for w in niche_words
        ):
            matched.append(row)
        else:
            unmatched.append(row)

    selected = (matched + unmatched)[:5]
    return selected


def load_ux_rules(rules_dir: Path, block_types: list[str]) -> list[dict]:
    """Load critical + high severity UX rules from ux-guidelines.csv."""
    guidelines_csv = rules_dir / "ux-guidelines.csv"
    if not guidelines_csv.exists():
        print(
            f"WARNING: ui-ux-pro-max ux-guidelines.csv not found at {guidelines_csv}.",
            file=sys.stderr,
        )
        return []

    rules: list[dict] = []
    with guidelines_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            severity = row.get("Severity", "").strip().lower()
            if severity in ("critical", "high"):
                rules.append(row)
    return rules


def render_ux_patterns_html(patterns: list[dict]) -> str:
    """Render patterns list as HTML cards."""
    if not patterns:
        return ""
    parts: list[str] = []
    for p in patterns:
        name = html.escape(p.get("Pattern Name", "—"))
        section_order = html.escape(p.get("Section Order", "—"))
        cta = html.escape(p.get("Primary CTA Placement", "—"))
        conversion = html.escape(p.get("Conversion Optimization", "—"))
        parts.append(
            f'<div class="ux-pattern">'
            f'<div class="ux-pattern-title">{name}</div>'
            f'<div class="ux-pattern-detail"><strong>Section order:</strong> {section_order}</div>'
            f'<div class="ux-pattern-detail"><strong>CTA placement:</strong> {cta}</div>'
            f'<div class="ux-pattern-detail"><strong>Conversion:</strong> {conversion}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def render_ux_rules_html(rules: list[dict]) -> str:
    """Render rules list as HTML list items."""
    if not rules:
        return ""
    parts: list[str] = []
    for r in rules:
        severity = r.get("Severity", "").strip().lower()
        category = html.escape(r.get("Category", "—"))
        issue = html.escape(r.get("Issue", "—"))
        description = html.escape(r.get("Description", "—"))
        parts.append(
            f'<li class="ux-rule ux-rule-{severity}">'
            f'<strong>{category}:</strong> {issue} — {description}'
            f'</li>'
        )
    return "\n".join(parts)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--top", type=int, default=3)
    p.add_argument(
        "--ux-rules",
        default=str(Path.home() / ".claude" / "skills" / "ui-ux-pro-max" / "data"),
        help="Path to ui-ux-pro-max/data/ directory (default: ~/.claude/skills/ui-ux-pro-max/data/)",
    )
    args = p.parse_args()

    project_dir = Path(args.project)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        fail(f"no prototype.yaml at {proto_path}")
    proto = yaml.safe_load(proto_path.read_text())
    niche = proto["project"]["niche"]
    slug = proto["project"]["slug"]

    matcher_script = Path(__file__).parent / "match-candidates.py"
    inject_content_script = (
        Path(__file__).parent.parent.parent
        / "block-composition" / "scripts" / "inject-content.py"
    )
    if not inject_content_script.exists():
        fail(f"inject-content.py not found at {inject_content_script}")

    # Read prototype.md for top-of-page preview (fall back to YAML dump if missing)
    proto_md_path = project_dir / "07_ПРОТОТИП" / "prototype.md"
    if proto_md_path.exists():
        prototype_source_text = proto_md_path.read_text()
    else:
        prototype_source_text = (
            "(prototype.md not found — showing parsed YAML instead)\n\n"
            + yaml.dump(proto, sort_keys=False, allow_unicode=True)
        )

    # --- Load ui-ux-pro-max data ---
    rules_dir = Path(args.ux_rules).expanduser()
    patterns = load_ux_patterns(rules_dir, niche)
    block_types = [b["type"] for b in proto.get("blocks", [])]
    rules = load_ux_rules(rules_dir, block_types)

    ux_available = (rules_dir / "landing.csv").exists()
    if not ux_available:
        ux_patterns_html = UX_NOT_AVAILABLE_BANNER
        ux_rules_html = ""
    else:
        ux_patterns_html = render_ux_patterns_html(patterns)
        ux_rules_html = render_ux_rules_html(rules)

    print(
        f"INFO: ui-ux-pro-max — {len(patterns)} patterns, {len(rules)} rules loaded.",
        file=sys.stderr,
    )

    blocks_html_parts: list[str] = []
    checked_rules: list[str] = []
    candidates_log: dict = {"project_slug": slug, "blocks": []}

    for block in proto["blocks"]:
        position = block["position"]
        btype = block["type"]
        res = subprocess.run(
            [
                "python3", str(matcher_script),
                "--library", args.library,
                "--type", btype,
                "--niche", niche,
                "--top", str(args.top),
            ],
            capture_output=True, text=True, check=True,
        )
        candidate_ids = json.loads(res.stdout)
        if not candidate_ids:
            candidates_log["blocks"].append({
                "block_position": position,
                "block_type": btype,
                "candidates": [],
                "warning": f"no candidates for {btype} / {niche}",
            })
            blocks_html_parts.append(
                f'<section class="block-slot"><strong>Block {position} ({btype})</strong>: '
                f'no candidates found for niche {niche}.</section>'
            )
            continue

        candidates_log["blocks"].append({
            "block_position": position,
            "block_type": btype,
            "candidates": candidate_ids,
        })

        radios = []
        variants = []
        for i, cid in enumerate(candidate_ids):
            cat = _category_for(args.library, cid)
            block_dir = Path(args.library) / cat / cid

            # Inject content from prototype into each template before iframe embedding.
            # Uses inject-content.py from block-composition skill — same script as 07b Compose.
            with tempfile.TemporaryDirectory() as tmp:
                tmp_p = Path(tmp)
                injected_d = tmp_p / f"{cid}-desktop.html"
                injected_m = tmp_p / f"{cid}-mobile.html"
                for src_name, out_path in (
                    ("template.html", injected_d),
                    ("template-mobile.html", injected_m),
                ):
                    src_html = block_dir / "assets" / src_name
                    try:
                        subprocess.run(
                            [
                                "python3", str(inject_content_script),
                                "--template", str(src_html),
                                "--prototype", str(proto_path),
                                "--position", str(position),
                                "--output", str(out_path),
                            ],
                            capture_output=True, text=True, check=True,
                        )
                    except subprocess.CalledProcessError as e:
                        # Fall back to raw template if injection fails
                        print(
                            f"WARN: inject-content failed for {cid}/{src_name}: "
                            f"{e.stderr.strip()}",
                            file=sys.stderr,
                        )
                        out_path.write_text(src_html.read_text())
                tmpl_d = injected_d.read_text()
                tmpl_m = injected_m.read_text()

            rid = f"b{position}-v{i}"
            checked = "checked" if i == 0 else ""
            radios.append(
                f'<input type="radio" name="b{position}" id="{rid}" '
                f'value="{cid}" data-position="{position}" {checked}>'
                f'<label for="{rid}">{html.escape(cid)}</label>'
            )
            variants.append(
                f'<div class="variant" data-variant="{rid}">'
                f'<div class="device desktop"><div class="device-label">Desktop · {cid}</div>'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_d, quote=True)}"></iframe></div>'
                f'<div class="device mobile"><div class="device-label">Mobile · {cid}</div>'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_m, quote=True)}"></iframe></div>'
                f'</div>'
            )
            checked_rules.append(CHECKED_TPL.format(rid=rid))

        section = (
            f'<section class="block-slot" data-block-position="{position}">'
            f'<fieldset class="variant-picker">'
            f'<legend>Block {position} — {btype} — выбери композицию:</legend>'
            f'{"".join(radios)}'
            f'</fieldset>'
            f'<div class="variants-stage">{"".join(variants)}</div>'
            f'</section>'
        )
        blocks_html_parts.append(section)

    shell = Path(args.template).read_text()
    out = (
        shell.replace("{{project_slug}}", slug)
        .replace("{{niche}}", niche)
        .replace("{{prototype_source}}", html.escape(prototype_source_text))
        .replace("{{blocks_html}}", "\n".join(blocks_html_parts))
        .replace("{{checked_rules}}", "\n".join(checked_rules))
        .replace("{{ux_patterns_html}}", ux_patterns_html)
        .replace("{{ux_rules_html}}", ux_rules_html)
    )
    out_html = project_dir / "07a_WIREFRAME" / "wireframe.html"
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(out)

    (project_dir / "07a_WIREFRAME" / "candidates.yaml").write_text(
        yaml.dump(candidates_log, sort_keys=False, allow_unicode=True)
    )

    print(f"OK: rendered {out_html}")


def _category_for(library: str, block_id: str) -> str:
    cat = yaml.safe_load((Path(library) / "catalog.yaml").read_text())
    for b in cat.get("blocks", []):
        if b["id"] == block_id:
            return b["category"]
    raise SystemExit(f"ERROR: block {block_id} not in catalog")


if __name__ == "__main__":
    main()

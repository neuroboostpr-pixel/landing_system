#!/usr/bin/env python3
"""Render <project>/07a_WIREFRAME/wireframe.html from prototype.yaml + block-library."""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

import yaml

CHECKED_TPL = (
    "#{rid}:checked ~ .variants-stage [data-variant=\"{rid}\"] {{ display: flex; }}"
)


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--top", type=int, default=3)
    args = p.parse_args()

    project_dir = Path(args.project)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        fail(f"no prototype.yaml at {proto_path}")
    proto = yaml.safe_load(proto_path.read_text())
    niche = proto["project"]["niche"]
    slug = proto["project"]["slug"]

    matcher_script = Path(__file__).parent / "match-candidates.py"

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
            tmpl_d = (block_dir / "assets" / "template.html").read_text()
            tmpl_m = (block_dir / "assets" / "template-mobile.html").read_text()

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
        .replace("{{blocks_html}}", "\n".join(blocks_html_parts))
        .replace("{{checked_rules}}", "\n".join(checked_rules))
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

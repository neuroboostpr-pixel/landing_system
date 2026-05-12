#!/usr/bin/env python3
"""Compose final composed.html from selections.yaml + prototype.yaml + tokens.json."""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    args = p.parse_args()

    project = Path(args.project)
    selections = yaml.safe_load((project / "07a_WIREFRAME" / "selections.yaml").read_text())
    proto = yaml.safe_load((project / "07_ПРОТОТИП" / "prototype.yaml").read_text())
    tokens_path = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"

    library = Path(args.library)
    catalog = yaml.safe_load((library / "catalog.yaml").read_text())
    block_to_cat = {b["id"]: b["category"] for b in catalog["blocks"]}

    out_dir = project / "07b_COMPOSED"
    out_dir.mkdir(parents=True, exist_ok=True)

    scripts_dir = Path(__file__).parent
    inject_tokens = scripts_dir / "inject-tokens.py"
    inject_content = scripts_dir / "inject-content.py"

    desktop_parts: list[str] = []
    mobile_parts: list[str] = []
    desktop_styles: list[str] = []
    mobile_styles: list[str] = []
    log: list[str] = ["# Block injection log\n"]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        for sel in selections["selections"]:
            position = sel["block_position"]
            variant = sel["chosen_variant"]
            if variant not in block_to_cat:
                print(f"ERROR: variant {variant} not in catalog", file=sys.stderr)
                sys.exit(1)
            cat = block_to_cat[variant]
            block_dir = library / cat / variant

            for kind, suffix in (("desktop", "template.html"), ("mobile", "template-mobile.html")):
                src = block_dir / "assets" / suffix
                stage1 = tmp_p / f"{position}-{kind}-1.html"
                stage2 = tmp_p / f"{position}-{kind}-2.html"

                subprocess.run(
                    ["python3", str(inject_tokens), str(src), str(tokens_path), str(stage1)],
                    check=True,
                )
                subprocess.run(
                    ["python3", str(inject_content),
                     "--template", str(stage1),
                     "--prototype", str(project / "07_ПРОТОТИП" / "prototype.yaml"),
                     "--position", str(position),
                     "--output", str(stage2)],
                    check=True,
                )

                content = stage2.read_text()

                # Extract <style> blocks from <head> to preserve token-injected CSS
                style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", content, re.DOTALL)
                combined_style = "\n".join(style_blocks)

                body_start = content.find("<body")
                body_close = content.rfind("</body>")
                if body_start != -1 and body_close != -1:
                    inner = content[content.find(">", body_start) + 1: body_close]
                else:
                    inner = content

                if kind == "desktop":
                    desktop_styles.append(f"/* block {position}: {variant} */\n{combined_style}")
                    desktop_parts.append(f"<!-- block {position}: {variant} -->\n{inner}")
                else:
                    mobile_styles.append(f"/* block {position}: {variant} */\n{combined_style}")
                    mobile_parts.append(f"<!-- block {position}: {variant} -->\n{inner}")

            log.append(f"- block {position}: `{variant}` — desktop+mobile injected, tokens applied")

    shell = (
        "<!DOCTYPE html><html lang='ru'><head><meta charset='UTF-8'>"
        "<title>Composed — {slug}</title>"
        "<style>{styles}</style>"
        "</head><body>{body}</body></html>"
    )
    (out_dir / "composed.html").write_text(
        shell.format(
            slug=proto["project"]["slug"],
            styles="\n".join(desktop_styles),
            body="\n".join(desktop_parts),
        )
    )
    (out_dir / "composed-mobile.html").write_text(
        shell.format(
            slug=proto["project"]["slug"],
            styles="\n".join(mobile_styles),
            body="\n".join(mobile_parts),
        )
    )
    (out_dir / "block-injection-log.md").write_text("\n".join(log))

    print(f"OK: composed {len(selections['selections'])} blocks")


if __name__ == "__main__":
    main()

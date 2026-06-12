#!/usr/bin/env python3
"""Convert a structured prototype.md to prototype.yaml.

Expected MD format:
    # Project: <slug>
    # Niche: <services|b2c|local>

    ## Block N: <type>
    - headline: ...
    - subhead: ...
    - cta: ...
    - slot <type> <name>: <hint>
    - item: <title> | <text> | icon: <icon-name>

Usage: md-to-yaml.py <input.md> <output.yaml>
"""
import re
import sys
import yaml
from pathlib import Path

BLOCK_HEADER = re.compile(r"^##\s+Block\s+(\d+):\s+(\w[\w-]*)\s*$")
PROJECT_LINE = re.compile(r"^#\s+Project:\s*(\S+)\s*$")
NICHE_LINE = re.compile(r"^#\s+Niche:\s*(\w+)\s*$")
SLOT_LINE = re.compile(r"^-\s*slot\s+(\w+)\s+([\w-]+):\s*(.*)$")
KV_LINE = re.compile(r"^-\s*([\w-]+):\s*(.+)$")


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def main(in_path: str, out_path: str) -> None:
    lines = Path(in_path).read_text(encoding="utf-8").splitlines()

    project: dict = {}
    blocks: list = []
    current: dict | None = None

    for raw in lines:
        line = raw.rstrip()
        if not line:
            continue

        m = PROJECT_LINE.match(line)
        if m:
            project["slug"] = m.group(1)
            continue

        m = NICHE_LINE.match(line)
        if m:
            project["niche"] = m.group(1)
            continue

        m = BLOCK_HEADER.match(line)
        if m:
            if current is not None:
                blocks.append(current)
            current = {
                "position": int(m.group(1)),
                "type": m.group(2),
                "slots": [],
            }
            continue

        if current is None:
            continue

        m = SLOT_LINE.match(line)
        if m:
            current["slots"].append({
                "type": m.group(1),
                "name": m.group(2),
                "hint": m.group(3).strip(),
            })
            continue

        m = KV_LINE.match(line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if key == "item":
                parts = [p.strip() for p in val.split("|")]
                item = {"title": parts[0] if parts else ""}
                if len(parts) > 1:
                    item["text"] = parts[1]
                if len(parts) > 2 and parts[2].startswith("icon:"):
                    item["icon_slot"] = parts[2].split(":", 1)[1].strip()
                current.setdefault("items", []).append(item)
            elif key == "cta":
                current["cta"] = {"text": val, "action": ""}
            else:
                current[key] = val
            continue

    if current is not None:
        blocks.append(current)

    if "slug" not in project or "niche" not in project:
        fail("missing # Project: or # Niche: header")
    if not blocks:
        fail("no '## Block N: <type>' sections found")

    project["source_file"] = Path(in_path).name
    out = {"project": project, "blocks": blocks}
    Path(out_path).write_text(yaml.dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"OK: wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: md-to-yaml.py <input.md> <output.yaml>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])

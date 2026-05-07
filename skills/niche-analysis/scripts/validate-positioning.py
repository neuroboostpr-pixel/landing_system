#!/usr/bin/env python3
"""Validate 01a_АНАЛИЗ_НИШИ/positioning.md — mode-aware.

1. Reads `**Mode:** <mode>` header.
2. Loads template sections for that mode from config/positioning-modes.yaml.
3. Verifies all template sections are present (regex headers).

Exits 0 on valid, 1 on errors.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[3]
MODES_YAML = REPO_ROOT / "config" / "positioning-modes.yaml"

VALID_MODE_RE = re.compile(
    r"^(rational|emotional_aspiration|trust_authority|hybrid:[a-z_]+\+[a-z_]+|legacy_v1)$",
    re.IGNORECASE,
)


def load_modes():
    return yaml.safe_load(MODES_YAML.read_text(encoding="utf-8"))


def section_to_pattern(title):
    """Convert template_section title to a header regex.

    'Job statement' -> r'##\\s+(?:\\d+\\.\\s+)?Job\\s+statement'
    Allows numbered (## 1. Title) or unnumbered (## Title) headings.
    """
    escaped = re.escape(title).replace(r"\ ", r"\s+")
    return rf"^##\s+(?:\d+(?:\.\d+)?\.\s+)?{escaped}\s*$"


def validate(path):
    errors = []
    text = path.read_text(encoding="utf-8")

    mode_match = re.search(r"^\*\*Mode:\*\*\s*([a-z_+:]+)", text, re.MULTILINE | re.IGNORECASE)
    if not mode_match:
        return ["Missing **Mode:** header"]
    mode_raw = mode_match.group(1).strip().lower()
    if not VALID_MODE_RE.match(mode_raw):
        return [f"Invalid Mode value: '{mode_raw}'"]

    if mode_raw == "legacy_v1":
        return []
    if mode_raw.startswith("hybrid:"):
        primary = mode_raw.split(":", 1)[1].split("+")[0]
    else:
        primary = mode_raw

    modes = load_modes()
    template = modes.get("modes", {}).get(primary)
    if not template:
        return [f"Mode '{primary}' not found in positioning-modes.yaml"]

    sections = template.get("template_sections", [])
    for sec_title in sections:
        pattern = section_to_pattern(sec_title)
        if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            errors.append(f"Section '{sec_title}' missing for mode '{primary}'")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate-positioning.py <positioning.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: {path} not found", file=sys.stderr)
        return 1
    errors = validate(path)
    if errors:
        print("positioning.md validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK: {path} is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())

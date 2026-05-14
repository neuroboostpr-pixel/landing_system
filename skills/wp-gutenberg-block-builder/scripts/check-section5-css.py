#!/usr/bin/env python3
"""Verify every `### Block N — Name` heading in DESIGN.md §5 has at least one
fenced ```css block in its body.

Exit 0: every `### Block N` in §5 has ≥1 fenced ```css.
Exit 1: DESIGN.md missing, §5 missing, §5 has no `### Block N` headings,
        or at least one `### Block N` heading lacks a fenced ```css block.
Exit 2: missing argv.

Usage: check-section5-css.py <project-dir>
"""
import re
import sys
from pathlib import Path


# Keep _H2_RE in sync with scripts/lib/design_extractor.py — both must agree
# on what counts as a top-level §N. heading, otherwise the gate-check and the
# main.css extractor would disagree about what is inside §5.
_H2_RE = re.compile(r"^##\s+(\d+)(?:\.\d+)*\.?\s+.*$", re.MULTILINE)
# Case-sensitive on "Block" — matches DESIGN.md convention (`### Block N — Name`).
_H3_BLOCK_RE = re.compile(r"^###\s+(Block\s+\d+[^\n]*)", re.MULTILINE)
_CSS_FENCE_RE = re.compile(r"```css\n.*?\n```", re.DOTALL)


def _extract_section5(md: str) -> str | None:
    matches = list(_H2_RE.finditer(md))
    for i, m in enumerate(matches):
        if int(m.group(1)) == 5:
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
            return md[start:end]
    return None


def _split_blocks(section5: str) -> list[tuple[str, str]]:
    """Return [(heading, body), ...] for each `### Block N ...` in §5."""
    matches = list(_H3_BLOCK_RE.finditer(section5))
    out = []
    for i, m in enumerate(matches):
        head = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(section5)
        out.append((head, section5[body_start:body_end]))
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check-section5-css.py <project-dir>", file=sys.stderr)
        return 2
    project = Path(argv[1])
    md_path = project / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    if not md_path.exists():
        print(f"DESIGN.md not found: {md_path}", file=sys.stderr)
        return 1
    md = md_path.read_text(encoding="utf-8")
    section5 = _extract_section5(md)
    if section5 is None:
        print("DESIGN.md has no `## 5.` section", file=sys.stderr)
        return 1
    blocks = _split_blocks(section5)
    if not blocks:
        print("DESIGN.md §5 has no `### Block N` headings", file=sys.stderr)
        return 1
    missing = [head for head, body in blocks if not _CSS_FENCE_RE.search(body)]
    if missing:
        print(f"Blocks in §5 missing fenced ```css: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

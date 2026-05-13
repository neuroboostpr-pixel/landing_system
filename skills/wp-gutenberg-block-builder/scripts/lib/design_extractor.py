"""Extract CSS from <project>/05_ДИЗАЙН-СИСТЕМА/DESIGN.md.

DESIGN.md is the single source of truth for landing-system CSS. This module
parses its markdown, locates the canonical numbered sections, and returns two
strings ready for the WordPress theme:

  - ``style_css``: merged ``:root { ... }`` declarations from section 2 (Design
    tokens, all subsections). Any non-:root CSS in §2 fenced blocks (e.g.
    ``@media (prefers-reduced-motion) { :root { ... } }``) is appended verbatim
    after the merged ``:root`` block.
  - ``main_css``: concatenation of every fenced ``css`` block found inside
    sections 3 through 9 (grid, section primitives, per-block layouts, forms,
    motion, accessibility, component states).

Sections numbered >= 10 (asset checklist, open questions, sources) are skipped.
Anything outside numbered ``## N. Title`` headings is also skipped.

Public API: ``extract(md_path) -> tuple[str, str]`` and ``DesignExtractError``.
"""
from __future__ import annotations

import re
from pathlib import Path


class DesignExtractError(RuntimeError):
    """DESIGN.md is missing, unreadable, or structurally invalid."""


# Matches level-2 headings like "## 3. Grid & breakpoints" or "## 2. Design tokens".
# We deliberately ignore "### 2.1 Colors" subsections — they belong to whatever
# top-level section is currently active.
_H2_RE = re.compile(r"^##\s+(\d+)(?:\.\d+)*\.?\s+.*$", re.MULTILINE)
_CSS_FENCE_RE = re.compile(r"```css\n(.*?)\n```", re.DOTALL)
# Top-level :root { ... } with no nested braces in the body. The negative
# character class is what makes this "top-level" — nested @media wrappers
# contain their own braces and therefore won't match here.
# Only match top-level :root selectors — those that start at column 0 (i.e. not
# indented inside an @media wrapper). Body cannot contain nested braces, which
# is true for every :root block in DESIGN.md by convention (declarations only).
_ROOT_BLOCK_RE = re.compile(r"(?m)^:root\s*\{([^{}]*)\}")


def _split_sections(md: str) -> list[tuple[int, str]]:
    """Return ``[(top_level_number, body), ...]`` for each ``## N.`` section.

    Body is the raw markdown between this heading and the next ``## N.`` heading
    (exclusive). Content before the first heading is dropped.
    """
    matches = list(_H2_RE.finditer(md))
    sections: list[tuple[int, str]] = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        sections.append((num, md[start:end]))
    return sections


def _build_style_css(section2_blocks: list[str]) -> str:
    """Merge all top-level ``:root{...}`` from §2 fenced blocks into one.

    Non-:root content (e.g. an ``@media`` wrapper that contains its own :root)
    is appended verbatim after the merged block, preserving order across
    fenced blocks.
    """
    if not section2_blocks:
        return ""
    merged_body_parts: list[str] = []
    tail_parts: list[str] = []
    for block in section2_blocks:
        remainder = block
        # Pull out every top-level :root{...} occurrence and stash its body.
        positions: list[tuple[int, int, str]] = []
        for rm in _ROOT_BLOCK_RE.finditer(block):
            positions.append((rm.start(), rm.end(), rm.group(1).strip("\n")))
        if not positions:
            tail_parts.append(block.strip())
            continue
        # Accumulate bodies in source order.
        for _, _, body in positions:
            merged_body_parts.append(body.rstrip())
        # Reconstruct what's left after stripping the matched :root blocks.
        chunks = []
        cursor = 0
        for s, e, _ in positions:
            chunks.append(block[cursor:s])
            cursor = e
        chunks.append(block[cursor:])
        leftover = "".join(chunks).strip()
        if leftover:
            tail_parts.append(leftover)

    merged_body = "\n".join(p for p in merged_body_parts if p.strip())
    out = ":root {\n" + merged_body + "\n}"
    if tail_parts:
        out += "\n\n" + "\n\n".join(tail_parts)
    return out


def extract(md_path: Path | str) -> tuple[str, str]:
    """Return ``(style_css, main_css)`` extracted from DESIGN.md.

    Empty strings if the file has no css fenced blocks (caller decides whether
    to warn or fall back). Raises :class:`DesignExtractError` if the file is
    not found.
    """
    p = Path(md_path)
    if not p.exists():
        raise DesignExtractError(f"DESIGN.md not found: {p}")
    md = p.read_text(encoding="utf-8")

    sections = _split_sections(md)
    section2_css_blocks: list[str] = []
    main_css_blocks: list[str] = []
    for num, body in sections:
        if num == 2:
            section2_css_blocks.extend(_CSS_FENCE_RE.findall(body))
        elif 3 <= num <= 9:
            main_css_blocks.extend(_CSS_FENCE_RE.findall(body))
        # num >= 10 → skip; num == 1 → skip

    has_any_css = bool(section2_css_blocks) or bool(main_css_blocks)
    if not has_any_css:
        return "", ""

    style_css = _build_style_css(section2_css_blocks) if section2_css_blocks else ""
    main_css = "\n\n".join(b.strip("\n") for b in main_css_blocks) if main_css_blocks else ""
    return style_css, main_css

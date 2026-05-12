"""Parse 07_КОНТЕНТ/final-copy.md into a list of blocks.

Single source of truth for stage-08 generators. Each H2 (`## `) heading
becomes one Block. Field types are inferred by ordered regex heuristics
(see Field type detection table in spec).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ALIASES_FILE = REPO_ROOT / "scripts" / "lib" / "slug-aliases.yaml"

# kebab-case ASCII slug
_SLUG_RE = re.compile(r"[^a-z0-9]+")
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
# Cyrillic → Latin (simple table, ICAO/GOST hybrid for readable slugs)
_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


class ContentParseError(Exception):
    """Raised when content cannot be parsed into a valid block structure."""


@dataclass
class Field:
    name: str
    label: str
    type: str  # text | textarea | wysiwyg | url | image | repeater
    default: Optional[str] = None
    subfields: Optional[list["Field"]] = None
    defaults: Optional[list[dict]] = None


@dataclass
class Block:
    slug: str
    title: str
    fields: list[Field] = field(default_factory=list)
    source_line: int = 0


def _load_aliases() -> dict[str, str]:
    if not ALIASES_FILE.exists():
        return {}
    with ALIASES_FILE.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {k.lower().strip(): v for k, v in (data.get("aliases") or {}).items()}


def _strip_emoji(s: str) -> str:
    # Drop characters in Unicode category "So" (Symbol, other) — emoji and pictographs
    return "".join(c for c in s if unicodedata.category(c) != "So")


def _slugify(title: str, aliases: dict[str, str]) -> str:
    cleaned = _strip_emoji(title).lower().strip()
    if cleaned in aliases:
        return aliases[cleaned]
    transliterated = "".join(_TRANSLIT.get(c, c) for c in cleaned)
    slug = _SLUG_RE.sub("-", transliterated).strip("-")
    return slug or "block"


class ContentParser:
    @staticmethod
    def parse(md_path: str) -> list[Block]:
        text = Path(md_path).read_text(encoding="utf-8")
        aliases = _load_aliases()
        lines = text.splitlines()

        # Find H2 positions
        h2_positions: list[tuple[int, str]] = []
        for i, line in enumerate(lines):
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m:
                h2_positions.append((i, m.group(1)))

        blocks: list[Block] = []
        for idx, (line_no, title) in enumerate(h2_positions):
            slug = _slugify(title, aliases)
            # Body spans from this H2 + 1 to next H2 - 1 (or end of file)
            end = h2_positions[idx + 1][0] if idx + 1 < len(h2_positions) else len(lines)
            body = "\n".join(lines[line_no + 1:end]).strip()
            fields = _detect_fields(body, slug)
            blocks.append(Block(slug=slug, title=title, fields=fields, source_line=line_no + 1))

        return blocks

    @staticmethod
    def validate(blocks: list[Block]) -> None:
        if not blocks:
            raise ContentParseError("no H2 sections found in final-copy.md")
        seen: dict[str, int] = {}
        for b in blocks:
            if b.slug in seen:
                raise ContentParseError(
                    f"slug collision: '{b.slug}' appears at lines {seen[b.slug]} and {b.source_line} — "
                    f"rename one of the H2 headings or remove an alias"
                )
            seen[b.slug] = b.source_line
            if not b.fields:
                raise ContentParseError(
                    f"block '{b.slug}' (H2 at line {b.source_line}) has no parsable fields"
                )


_ITALIC_RE = re.compile(r"^\*([^*]+)\*\s*$")
_QUOTE_RE = re.compile(r"^>\s+(.+?)\s*$")


def _detect_fields(body: str, slug: str) -> list[Field]:
    fields: list[Field] = []
    used_field_names: set[str] = set()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]

    title_assigned = False

    def add(f: Field):
        if f.name in used_field_names:
            return
        used_field_names.add(f.name)
        fields.append(f)

    for idx, para in enumerate(paragraphs):
        first_line = para.splitlines()[0].strip()

        # Eyebrow: italic-only line OR blockquote, only at start
        if idx == 0 and (_ITALIC_RE.match(first_line) or _QUOTE_RE.match(first_line)):
            m = _ITALIC_RE.match(first_line) or _QUOTE_RE.match(first_line)
            add(Field(name="eyebrow", label="Eyebrow", type="text", default=m.group(1)))
            continue

        # Bullet list → repeater(text)
        if first_line.startswith("- ") or first_line.startswith("* "):
            items = []
            for line in para.splitlines():
                line = line.strip()
                if line.startswith(("- ", "* ")):
                    items.append(line[2:].strip())
            if items:
                add(Field(
                    name="bullets",
                    label="Bullets",
                    type="repeater",
                    subfields=[Field(name="text", label="Text", type="text")],
                    defaults=[{"text": it} for it in items],
                ))
            continue

        # Skip ### subheadings — handled in a later task
        if first_line.startswith("###"):
            continue

        # Title: first non-italic, non-list prose line (short enough to be a title)
        single_line_check = " ".join(para.split())
        if not title_assigned and len(single_line_check) <= 80:
            add(Field(name="title", label="Title", type="text", default=first_line))
            title_assigned = True
            # Remaining lines of this paragraph (if any) go to body/lede via next iteration
            remainder = "\n".join(para.splitlines()[1:]).strip()
            if remainder:
                paragraphs.insert(idx + 1, remainder)
            continue

        # Short paragraph → lede; long → body
        single_line = " ".join(para.split())
        if len(single_line) <= 80:
            add(Field(name="lede", label="Lede", type="text", default=single_line))
        else:
            add(Field(name="body", label="Body", type="textarea", default=para))

    return fields


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: content_parser.py <final-copy.md>", file=sys.stderr)
        sys.exit(2)
    blocks = ContentParser.parse(sys.argv[1])
    ContentParser.validate(blocks)
    for b in blocks:
        print(f"{b.slug}: {b.title} ({len(b.fields)} field(s))")

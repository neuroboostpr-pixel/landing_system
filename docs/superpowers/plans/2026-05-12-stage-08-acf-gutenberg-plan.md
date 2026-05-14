# Stage 08 — Verifiable WP Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `/landing-build` reliably produce ACF Blocks + Gutenberg artifacts (acf-fields.json, gutenberg-blocks/*/block.json, registration in functions.php), and make the stage-08 gate block deploys when these artifacts are missing.

**Architecture:** Three layers built on a single source of truth (`ContentParser`):
- **Layer A** — content parser (Python, pytest)
- **Layer B** — four generators (Python, bats-tested)
- **Layer C** — hard gate + legacy marker + backport (bash + Python helper, bats-tested)

Layers connect through `ContentParser` so all artifacts stay in sync with `final-copy.md`.

**Tech Stack:** Python 3 (`PyYAML`, `re`, `dataclasses`, `transliterate`), bash, bats, pytest, WP-CLI, ACF Free v6+.

**Test strategy:** pytest for the parser (`tests/phase-stage-08/test-content-parser.py`), bats for all shell pipeline + gate + backport. ~60 tests total. Manual E2E checklist after merge (deploy to staging, verify in WP admin).

**Verification rule:** at every step that runs tests/scripts, you MUST run the command and confirm the output before checking the box. Per superpowers:verification-before-completion — evidence before assertions.

---

## File Structure

### New files

```
landing_system/
├── scripts/
│   ├── lib/
│   │   ├── content_parser.py            ← Layer A
│   │   ├── slug-aliases.yaml            ← Layer A — slug normalisation table
│   │   ├── block-icons.yaml             ← Layer B — dashicon table
│   │   └── stage_08_helper.py           ← Layer C — JSON/structure checker for gate
│   ├── generate-wp-blocks.py            ← Layer B — orchestrator
│   ├── mark-legacy-projects.sh          ← Layer C — one-shot legacy marker
│   └── backport-acf-to-legacy.sh        ← Layer C — apply generators to existing project
│
├── skills/wp-gutenberg-block-builder/scripts/
│   ├── generate-block-json.py           ← Layer B — block.json per block
│   └── generate-block-registration.py   ← Layer B — register_block_type in functions.php
│
└── tests/phase-stage-08/
    ├── fixtures/
    │   ├── content/
    │   │   ├── minimal.md
    │   │   ├── all-field-types.md
    │   │   ├── repeater-blocks.md
    │   │   ├── slug-collision.md
    │   │   ├── empty.md
    │   │   └── empty-block.md
    │   ├── expected/
    │   │   ├── minimal.acf.json
    │   │   ├── minimal.functions-section.php
    │   │   ├── minimal.block-hero.json
    │   │   └── all-field-types.acf.json
    │   └── projects/
    │       ├── valid-project/             (full skeleton, gate passes)
    │       ├── missing-acf/               (no acf-fields.json — fail #3)
    │       ├── orphan-block/              (block.json with no PHP — fail #7)
    │       └── legacy-project/            (legacy: true in state.yaml)
    ├── test-content-parser.py
    ├── test-generate-acf.bats
    ├── test-generate-block-json.bats
    ├── test-generate-block-registration.bats
    ├── test-generate-wp-blocks.bats
    ├── test-gate-check-stage-08.bats
    ├── test-backport-legacy.bats
    └── test-mark-legacy-projects.bats
```

### Modified files

```
landing_system/
├── skills/wp-gutenberg-block-builder/
│   ├── SKILL.md                                  ← honest description
│   └── scripts/
│       ├── generate-acf.py                       ← rewrite using ContentParser
│       └── generate-theme.py                     ← extend (create block-<slug>.php from blocks)
├── skills/wp-cli-deployer/scripts/
│   └── deploy-wordpress.sh                       ← remove silent fail on wp acf import
├── config/stage-gates.yaml                       ← add 10 checks under 08_build
├── package.json                                  ← test:phase-stage-08 + generate-wp-blocks
├── docs/SETUP.md                                 ← manager-facing ACF/Gutenberg section
└── template/.landing-state.yaml                  ← document optional legacy: true field
```

---

## Key conventions locked for this plan

- **ACF key naming (deterministic):** `group_lp_<slug>` for groups, `field_lp_<slug>_<fieldname>` for fields, `field_lp_<slug>_<repeaterfield>_<subfield>` for repeater subfields. Slug is kebab-case from `Block.slug`. No UUIDs, no timestamps.
- **Block name:** `acf/lp-<slug>` (WordPress requires `acf/` namespace for ACF Blocks).
- **Block category:** `lp-blocks` (registered via `block_categories_all` filter).
- **AUTO-GENERATED markers in functions.php:** lines `// AUTO-GENERATED START: lp-block-registration — DO NOT EDIT MANUALLY` and `// AUTO-GENERATED END`. Anything between them is regenerated; anything outside is preserved.
- **Backup naming:** `<filename>.bak` for single-file backups, `.backport-backup-YYYYMMDD-HHMMSS/` for backport multi-file backups.
- **Block JSON path:** `<project>/08_КОД/gutenberg-blocks/<slug>/block.json`. Note the project root is `08_КОД` (Cyrillic).
- **Template part path:** `<project>/08_КОД/wp-theme/template-parts/block-<slug>.php`. Block.json's `renderTemplate` is relative path `template-parts/block-<slug>.php` (resolved from the theme root, ACF documentation confirms this).
- **Field type values:** `text | textarea | wysiwyg | url | image | repeater` — exact strings used in ACF JSON.

---

# Phase A — Content Parser (Layer A)

## Task A1: ContentParser skeleton + slug-aliases table

**Files:**
- Create: `scripts/lib/content_parser.py`
- Create: `scripts/lib/slug-aliases.yaml`
- Create: `tests/phase-stage-08/test-content-parser.py`
- Create: `tests/phase-stage-08/fixtures/content/minimal.md`

- [ ] **Step 1: Create the slug-aliases table**

`scripts/lib/slug-aliases.yaml`:

```yaml
# Heading text (lowercased, before transliteration) → canonical block slug.
# Lookup is case-insensitive, whitespace-stripped, emoji-stripped.
# Extend as new content patterns appear.
aliases:
  "тарифы": pricing
  "цены": pricing
  "стоимость": pricing
  "hero": hero
  "главный экран": hero
  "главная": hero
  "программа": program
  "модули": program
  "что входит": program
  "аудитория": audience
  "для кого": audience
  "кому подойдёт": audience
  "автор": author
  "об авторе": author
  "кейсы": cases
  "результаты": cases
  "отзывы": testimonials
  "вопросы": faq
  "faq": faq
  "частые вопросы": faq
  "контакты": contacts
  "футер": footer
  "подвал": footer
  "cta": cta
  "призыв": cta
  "записаться": cta
```

- [ ] **Step 2: Write the failing pytest skeleton**

`tests/phase-stage-08/test-content-parser.py`:

```python
"""Pytest suite for scripts/lib/content_parser.py."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, Block, Field, ContentParseError  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "content"


def test_minimal_parses_two_blocks():
    blocks = ContentParser.parse(str(FIXTURES / "minimal.md"))
    assert len(blocks) == 2
    assert blocks[0].slug == "hero"
    assert blocks[1].slug == "pricing"


def test_minimal_title_preserved():
    blocks = ContentParser.parse(str(FIXTURES / "minimal.md"))
    assert blocks[0].title == "Hero"
    assert blocks[1].title == "Тарифы"


def test_slug_from_alias():
    blocks = ContentParser.parse(str(FIXTURES / "minimal.md"))
    # "Тарифы" → alias → "pricing"
    assert blocks[1].slug == "pricing"
```

`tests/phase-stage-08/fixtures/content/minimal.md`:

```markdown
## Hero

Авторский курс Кирилла Безикова

Описание курса для людей которые хотят освоить нейросети.

## Тарифы

Базовый — 50 000 ₽
```

- [ ] **Step 3: Verify tests fail**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 3 tests FAIL — `ModuleNotFoundError: No module named 'content_parser'`.

- [ ] **Step 4: Implement minimal ContentParser**

`scripts/lib/content_parser.py`:

```python
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


def _detect_fields(body: str, slug: str) -> list[Field]:
    """Minimal field detection — extended in later tasks."""
    # Stub: return [title field with first non-empty line as default]
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return [Field(name="title", label="Title", type="text", default=line)]
    return []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: content_parser.py <final-copy.md>", file=sys.stderr)
        sys.exit(2)
    blocks = ContentParser.parse(sys.argv[1])
    ContentParser.validate(blocks)
    for b in blocks:
        print(f"{b.slug}: {b.title} ({len(b.fields)} field(s))")
```

- [ ] **Step 5: Run tests, verify they pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 3 tests pass.

- [ ] **Step 6: Wire into npm scripts**

Modify `package.json`. In `scripts` block (after `test:phase-preview-panel`):

```json
"test:phase-stage-08": "bats tests/phase-stage-08/*.bats && python -m pytest tests/phase-stage-08/test-content-parser.py -v",
"generate-wp-blocks": "python scripts/generate-wp-blocks.py"
```

(Note: bats glob will fail until first bats test exists; that's fine — task A1 only runs pytest.)

- [ ] **Step 7: Commit**

```bash
git add scripts/lib/slug-aliases.yaml scripts/lib/content_parser.py tests/phase-stage-08/test-content-parser.py tests/phase-stage-08/fixtures/content/minimal.md package.json
git commit -m "feat(content-parser): skeleton + slug-aliases + 3 pytest cases"
```

---

## Task A2: Field type detection — eyebrow, title, body, lede

**Files:**
- Modify: `scripts/lib/content_parser.py:_detect_fields`
- Modify: `tests/phase-stage-08/test-content-parser.py`
- Create: `tests/phase-stage-08/fixtures/content/all-field-types.md`

- [ ] **Step 1: Add failing tests**

Append to `tests/phase-stage-08/test-content-parser.py`:

```python
def test_eyebrow_from_italic_first_line():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    eyebrow = next((f for f in hero.fields if f.name == "eyebrow"), None)
    assert eyebrow is not None
    assert eyebrow.type == "text"
    assert "Авторская программа" in eyebrow.default


def test_title_is_first_prose_line():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    title = next((f for f in hero.fields if f.name == "title"), None)
    assert title is not None
    assert title.type == "text"
    assert title.default == "Авторский курс Кирилла Безикова"


def test_lede_short_paragraph():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    lede = next((f for f in hero.fields if f.name == "lede"), None)
    assert lede is not None
    assert lede.type == "text"
    assert len(lede.default) <= 80


def test_body_long_paragraph():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    audience = next(b for b in blocks if b.slug == "audience")
    body = next((f for f in audience.fields if f.name == "body"), None)
    assert body is not None
    assert body.type == "textarea"
    assert len(body.default) > 80
```

- [ ] **Step 2: Create fixture**

`tests/phase-stage-08/fixtures/content/all-field-types.md`:

```markdown
## Hero

*Авторская программа Кирилла Безикова*

Авторский курс Кирилла Безикова

Лучший курс по ИИ.

## Аудитория

Этот курс подойдёт для предпринимателей которые хотят автоматизировать рутинные задачи через нейросети и снизить операционные расходы.
```

- [ ] **Step 3: Run tests, verify they fail**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v -k "eyebrow or title or lede or body"`
Expected: 4 tests FAIL (current stub only returns one title field).

- [ ] **Step 4: Rewrite `_detect_fields`**

Replace the stub in `scripts/lib/content_parser.py`:

```python
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

        # Skip list paragraphs — handled in a later task
        if first_line.startswith("- ") or first_line.startswith("* "):
            continue

        # Skip ### subheadings — handled in a later task
        if first_line.startswith("###"):
            continue

        # Title: first non-italic, non-list prose line
        if not title_assigned:
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
```

- [ ] **Step 5: Run tests, verify all pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 7 tests pass (3 from A1 + 4 from A2).

- [ ] **Step 6: Commit**

```bash
git add scripts/lib/content_parser.py tests/phase-stage-08/test-content-parser.py tests/phase-stage-08/fixtures/content/all-field-types.md
git commit -m "feat(content-parser): detect eyebrow/title/lede/body fields"
```

---

## Task A3: Field type detection — bullets (repeater)

**Files:**
- Modify: `scripts/lib/content_parser.py:_detect_fields`
- Modify: `tests/phase-stage-08/test-content-parser.py`
- Modify: `tests/phase-stage-08/fixtures/content/all-field-types.md`

- [ ] **Step 1: Add failing tests**

Append to `tests/phase-stage-08/test-content-parser.py`:

```python
def test_bullets_become_repeater():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    bullets = next((f for f in hero.fields if f.name == "bullets"), None)
    assert bullets is not None
    assert bullets.type == "repeater"
    assert bullets.subfields is not None
    assert len(bullets.subfields) == 1
    assert bullets.subfields[0].name == "text"
    assert bullets.subfields[0].type == "text"


def test_bullets_default_rows():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    bullets = next(f for f in hero.fields if f.name == "bullets")
    assert bullets.defaults is not None
    assert len(bullets.defaults) >= 3
    assert all("text" in row for row in bullets.defaults)
```

- [ ] **Step 2: Extend fixture**

Append to `tests/phase-stage-08/fixtures/content/all-field-types.md` (at end of `## Hero` section, before `## Аудитория`):

```markdown
- Начните использовать нейросети на максимум
- Получайте сотни заявок и обрабатывайте их с помощью ИИ
- Освойте главный тренд ближайших лет
- Первые результаты уже через месяц

```

- [ ] **Step 3: Run tests, verify they fail**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v -k bullets`
Expected: 2 tests FAIL.

- [ ] **Step 4: Add bullet detection to `_detect_fields`**

In `scripts/lib/content_parser.py`, inside `_detect_fields`, replace the `# Skip list paragraphs — handled in a later task` block with:

```python
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
```

- [ ] **Step 5: Run tests, verify pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 9 tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/lib/content_parser.py tests/phase-stage-08/test-content-parser.py tests/phase-stage-08/fixtures/content/all-field-types.md
git commit -m "feat(content-parser): bullets → repeater(text) field"
```

---

## Task A4: Field type detection — CTA, image, ### repeater cards

**Files:**
- Modify: `scripts/lib/content_parser.py:_detect_fields`
- Modify: `tests/phase-stage-08/test-content-parser.py`
- Modify: `tests/phase-stage-08/fixtures/content/all-field-types.md`
- Create: `tests/phase-stage-08/fixtures/content/repeater-blocks.md`

- [ ] **Step 1: Add failing tests**

Append to `tests/phase-stage-08/test-content-parser.py`:

```python
def test_cta_label_and_url():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    cta_label = next((f for f in hero.fields if f.name == "cta-label"), None)
    cta_url = next((f for f in hero.fields if f.name == "cta-url"), None)
    assert cta_label is not None and cta_label.type == "text"
    assert cta_label.default == "ХОЧУ НА КУРС"
    assert cta_url is not None and cta_url.type == "url"
    assert cta_url.default == "#pricing"


def test_image_field():
    blocks = ContentParser.parse(str(FIXTURES / "all-field-types.md"))
    hero = next(b for b in blocks if b.slug == "hero")
    img = next((f for f in hero.fields if f.type == "image"), None)
    assert img is not None
    assert img.default is not None and img.default.endswith(".png")


def test_repeater_cards_from_h3_series():
    blocks = ContentParser.parse(str(FIXTURES / "repeater-blocks.md"))
    pricing = next(b for b in blocks if b.slug == "pricing")
    tiers = next((f for f in pricing.fields if f.type == "repeater" and f.name != "bullets"), None)
    assert tiers is not None
    assert tiers.subfields is not None
    sub_names = [sf.name for sf in tiers.subfields]
    assert "title" in sub_names
    assert "body" in sub_names
    assert tiers.defaults is not None and len(tiers.defaults) >= 2
```

- [ ] **Step 2: Extend hero fixture and create repeater fixture**

Append to `tests/phase-stage-08/fixtures/content/all-field-types.md`, after the bullets list:

```markdown
[ХОЧУ НА КУРС](#pricing)

![Кирилл Безиков](/assets/images/hero/hero-kirill.png)

```

Create `tests/phase-stage-08/fixtures/content/repeater-blocks.md`:

```markdown
## Тарифы

Выбери тариф

### Базовый

Доступ к видеоурокам.

### Стандарт

Доступ к видеоурокам и групповым звонкам.

### Премиум

Доступ ко всему + личные консультации.
```

- [ ] **Step 3: Run tests, verify they fail**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v -k "cta or image or repeater_cards"`
Expected: 3 tests FAIL.

- [ ] **Step 4: Extend `_detect_fields`**

Replace the `_detect_fields` body in `scripts/lib/content_parser.py` with full version:

```python
_ITALIC_RE = re.compile(r"^\*([^*]+)\*\s*$")
_QUOTE_RE = re.compile(r"^>\s+(.+?)\s*$")
_LINK_RE = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)\s*$")
_IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
_H3_RE = re.compile(r"^###\s+(.+?)\s*$")


def _detect_fields(body: str, slug: str) -> list[Field]:
    fields: list[Field] = []
    used_field_names: set[str] = set()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    title_assigned = False
    image_counter = 0

    def add(f: Field) -> None:
        if f.name not in used_field_names:
            used_field_names.add(f.name)
            fields.append(f)

    # First pass: detect H3 series (≥2 H3 in this body → repeater cards)
    h3_paragraphs = [p for p in paragraphs if p.splitlines()[0].startswith("###")]
    if len(h3_paragraphs) >= 2:
        cards = []
        for p in h3_paragraphs:
            lines = p.splitlines()
            h3_title = _H3_RE.match(lines[0]).group(1)
            card_body = "\n".join(lines[1:]).strip()
            cards.append({"title": h3_title, "body": card_body})
        add(Field(
            name="cards",
            label="Cards",
            type="repeater",
            subfields=[
                Field(name="title", label="Title", type="text"),
                Field(name="body", label="Body", type="textarea"),
            ],
            defaults=cards,
        ))

    for idx, para in enumerate(paragraphs):
        first_line = para.splitlines()[0].strip()

        # Skip H3 paragraphs (handled above)
        if first_line.startswith("###"):
            continue

        # Eyebrow: italic-only or blockquote at start
        if idx == 0 and (_ITALIC_RE.match(first_line) or _QUOTE_RE.match(first_line)):
            m = _ITALIC_RE.match(first_line) or _QUOTE_RE.match(first_line)
            add(Field(name="eyebrow", label="Eyebrow", type="text", default=m.group(1)))
            continue

        # Standalone image paragraph
        img_m = _IMG_RE.match(first_line) if len(para.splitlines()) == 1 else None
        if img_m:
            image_counter += 1
            fname = f"image-{image_counter}" if image_counter > 1 else "image"
            add(Field(name=fname, label=fname.replace("-", " ").capitalize(), type="image", default=img_m.group(2)))
            continue

        # Standalone CTA link [Label](url)
        link_m = _LINK_RE.match(first_line) if len(para.splitlines()) == 1 else None
        if link_m:
            add(Field(name="cta-label", label="CTA Label", type="text", default=link_m.group(1)))
            add(Field(name="cta-url", label="CTA URL", type="url", default=link_m.group(2)))
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

        # Title: first non-italic, non-list, non-link, non-image prose line
        if not title_assigned:
            add(Field(name="title", label="Title", type="text", default=first_line))
            title_assigned = True
            remainder = "\n".join(para.splitlines()[1:]).strip()
            if remainder:
                paragraphs.insert(idx + 1, remainder)
            continue

        # Short → lede, long → body
        single_line = " ".join(para.split())
        if len(single_line) <= 80:
            add(Field(name="lede", label="Lede", type="text", default=single_line))
        else:
            add(Field(name="body", label="Body", type="textarea", default=para))

    return fields
```

- [ ] **Step 5: Run tests, verify all pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 12 tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/lib/content_parser.py tests/phase-stage-08/test-content-parser.py tests/phase-stage-08/fixtures/content/
git commit -m "feat(content-parser): cta-link, image, H3-series → repeater(cards)"
```

---

## Task A5: Validation — collisions, empty blocks, zero H2

**Files:**
- Modify: `tests/phase-stage-08/test-content-parser.py`
- Create: `tests/phase-stage-08/fixtures/content/slug-collision.md`
- Create: `tests/phase-stage-08/fixtures/content/empty.md`
- Create: `tests/phase-stage-08/fixtures/content/empty-block.md`

The validate() function is already implemented in A1; this task adds fixtures and tests to lock the behaviour and tighten edge cases.

- [ ] **Step 1: Add failing tests**

Append to `tests/phase-stage-08/test-content-parser.py`:

```python
def test_validate_passes_on_minimal():
    blocks = ContentParser.parse(str(FIXTURES / "minimal.md"))
    ContentParser.validate(blocks)  # should not raise


def test_validate_rejects_zero_h2():
    blocks = ContentParser.parse(str(FIXTURES / "empty.md"))
    with pytest.raises(ContentParseError, match="no H2 sections"):
        ContentParser.validate(blocks)


def test_validate_rejects_slug_collision():
    blocks = ContentParser.parse(str(FIXTURES / "slug-collision.md"))
    with pytest.raises(ContentParseError, match="slug collision"):
        ContentParser.validate(blocks)


def test_validate_rejects_empty_block():
    blocks = ContentParser.parse(str(FIXTURES / "empty-block.md"))
    with pytest.raises(ContentParseError, match="no parsable fields"):
        ContentParser.validate(blocks)
```

- [ ] **Step 2: Create fixtures**

`tests/phase-stage-08/fixtures/content/empty.md`:

```markdown
Some preamble text but no H2 headings here.
```

`tests/phase-stage-08/fixtures/content/slug-collision.md`:

```markdown
## Тарифы

Описание тарифов.

## Цены

Цены курса.
```

(Both alias to `pricing` via `slug-aliases.yaml`.)

`tests/phase-stage-08/fixtures/content/empty-block.md`:

```markdown
## Hero

## Footer

Some content here.
```

(First block has no body → 0 fields.)

- [ ] **Step 3: Run tests, verify they pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 16 tests pass.

If `test_validate_rejects_empty_block` fails because Hero collected 0 paragraphs but the parser still attaches a default field — that's expected behaviour for now (no fields means empty block). If somehow Hero gets a stale field from previous iteration, debug by printing `blocks[0].fields`.

- [ ] **Step 4: Commit**

```bash
git add tests/phase-stage-08/test-content-parser.py tests/phase-stage-08/fixtures/content/
git commit -m "test(content-parser): validation edge cases (collision, empty, no-H2)"
```

---

## Task A6: Slug edge cases — emoji, English, transliteration

**Files:**
- Modify: `tests/phase-stage-08/test-content-parser.py`

- [ ] **Step 1: Add failing tests**

Append:

```python
def _parse_inline(md_text: str, tmp_path) -> list[Block]:
    p = tmp_path / "_inline.md"
    p.write_text(md_text, encoding="utf-8")
    return ContentParser.parse(str(p))


def test_slug_english_passthrough(tmp_path):
    blocks = _parse_inline("## Audience\n\nSome text\n", tmp_path)
    assert blocks[0].slug == "audience"


def test_slug_emoji_stripped(tmp_path):
    blocks = _parse_inline("## 🎯 Hero\n\nText\n", tmp_path)
    assert blocks[0].slug == "hero"


def test_slug_transliteration_no_alias(tmp_path):
    # "Особый блок" has no alias → transliterate to "osobyy-blok"
    blocks = _parse_inline("## Особый блок\n\nText\n", tmp_path)
    assert blocks[0].slug == "osobyy-blok"


def test_slug_aliases_for_pricing(tmp_path):
    blocks = _parse_inline("## Стоимость\n\nText\n", tmp_path)
    assert blocks[0].slug == "pricing"
```

- [ ] **Step 2: Run tests, verify they pass**

Run: `python -m pytest tests/phase-stage-08/test-content-parser.py -v`
Expected: 20 tests pass.

If any fail, the existing `_slugify()` already handles these cases via aliases + transliteration. Inspect the failing assertion and adjust the transliteration table or alias file if needed.

- [ ] **Step 3: Commit**

```bash
git add tests/phase-stage-08/test-content-parser.py
git commit -m "test(content-parser): slug edge cases (emoji, English, transliteration)"
```

---

# Phase B — Generators (Layer B)

## Task B1: `generate-acf.py` rewrite

**Files:**
- Modify: `skills/wp-gutenberg-block-builder/scripts/generate-acf.py` (full rewrite)
- Create: `tests/phase-stage-08/test-generate-acf.bats`
- Create: `tests/phase-stage-08/fixtures/expected/minimal.acf.json`

- [ ] **Step 1: Write failing bats**

`tests/phase-stage-08/test-generate-acf.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-acf.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "creates acf-fields.json from minimal.md" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/acf-fields.json" ]
}

@test "acf-fields.json is valid JSON" {
  python "$SCRIPT" --project "$WORK/project"
  python -c "import json; json.load(open('$WORK/project/08_КОД/acf-fields.json'))"
}

@test "contains one group per H2 block" {
  python "$SCRIPT" --project "$WORK/project"
  COUNT=$(python -c "import json; print(len(json.load(open('$WORK/project/08_КОД/acf-fields.json'))))")
  [ "$COUNT" = "2" ]
}

@test "group keys are deterministic" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"key": "group_lp_hero"' "$WORK/project/08_КОД/acf-fields.json"
  grep -q '"key": "group_lp_pricing"' "$WORK/project/08_КОД/acf-fields.json"
}

@test "location targets acf/lp-<slug> block" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"value": "acf/lp-hero"' "$WORK/project/08_КОД/acf-fields.json"
  grep -q '"value": "acf/lp-pricing"' "$WORK/project/08_КОД/acf-fields.json"
}

@test "rerun is idempotent (same output)" {
  python "$SCRIPT" --project "$WORK/project"
  cp "$WORK/project/08_КОД/acf-fields.json" "$WORK/first.json"
  python "$SCRIPT" --project "$WORK/project"
  diff "$WORK/first.json" "$WORK/project/08_КОД/acf-fields.json"
}

@test "backs up existing acf-fields.json" {
  python "$SCRIPT" --project "$WORK/project"
  echo "garbage" > "$WORK/project/08_КОД/acf-fields.json"
  python "$SCRIPT" --project "$WORK/project"
  [ -f "$WORK/project/08_КОД/acf-fields.json.bak" ]
  grep -q "garbage" "$WORK/project/08_КОД/acf-fields.json.bak"
}

@test "exits non-zero with parse error on bad content" {
  echo "no h2 here" > "$WORK/project/07_КОНТЕНТ/final-copy.md"
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -ne 0 ]
  [[ "$output" == *"no H2 sections"* ]]
}
```

- [ ] **Step 2: Run tests, verify they fail**

Run: `npx bats tests/phase-stage-08/test-generate-acf.bats`
Expected: 8 tests FAIL (script doesn't exist in new form yet).

- [ ] **Step 3: Rewrite `generate-acf.py`**

Replace contents of `skills/wp-gutenberg-block-builder/scripts/generate-acf.py` with:

```python
#!/usr/bin/env python3
"""Generate ACF Local JSON from 07_КОНТЕНТ/final-copy.md using ContentParser.

CLI: python generate-acf.py --project <path>
Output: <project>/08_КОД/acf-fields.json
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError, Field, Block  # noqa: E402


def _field_key(slug: str, fname: str, parent: str = "") -> str:
    if parent:
        return f"field_lp_{slug}_{parent}_{fname}"
    return f"field_lp_{slug}_{fname}"


def _field_to_acf(f: Field, slug: str, parent: str = "") -> dict:
    out = {
        "key": _field_key(slug, f.name, parent),
        "label": f.label,
        "name": f.name,
        "type": f.type,
    }
    if f.default is not None and f.type != "repeater":
        out["default_value"] = f.default
    if f.type == "repeater":
        out["sub_fields"] = [_field_to_acf(sf, slug, parent=f.name) for sf in (f.subfields or [])]
        if f.defaults:
            out["min"] = 0
    return out


def _block_to_group(b: Block) -> dict:
    return {
        "key": f"group_lp_{b.slug}",
        "title": b.title,
        "fields": [_field_to_acf(f, b.slug) for f in b.fields],
        "location": [[{"param": "block", "operator": "==", "value": f"acf/lp-{b.slug}"}]],
        "menu_order": 0,
        "position": "normal",
        "style": "default",
        "label_placement": "top",
        "instruction_placement": "label",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)

    try:
        blocks = ContentParser.parse(str(src))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    groups = [_block_to_group(b) for b in blocks]

    dest = Path(args.project) / "08_КОД" / "acf-fields.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        shutil.copy2(dest, dest.with_suffix(".json.bak"))

    with dest.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    print(f"wrote {dest} ({len(groups)} group(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, verify all pass**

Run: `npx bats tests/phase-stage-08/test-generate-acf.bats`
Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-acf.py tests/phase-stage-08/test-generate-acf.bats
git commit -m "feat(generate-acf): rewrite using ContentParser, 8 bats tests"
```

---

## Task B2: `generate-block-json.py` + block-icons table

**Files:**
- Create: `scripts/lib/block-icons.yaml`
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-block-json.py`
- Create: `tests/phase-stage-08/test-generate-block-json.bats`
- Create: `tests/phase-stage-08/fixtures/expected/minimal.block-hero.json`

- [ ] **Step 1: Create the icons table**

`scripts/lib/block-icons.yaml`:

```yaml
# Block slug → WordPress Dashicon name. Used by block.json generator.
# Fallback for unmapped slugs: "block-default".
icons:
  hero: cover-image
  pricing: tag
  program: portfolio
  audience: groups
  author: businessperson
  cases: awards
  testimonials: format-quote
  faq: format-aside
  footer: editor-alignleft
  cta: megaphone
  contacts: phone
```

- [ ] **Step 2: Write failing bats**

`tests/phase-stage-08/test-generate-block-json.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-block-json.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "creates block.json per block" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/pricing/block.json" ]
}

@test "block.json has apiVersion 3 and acf namespace name" {
  python "$SCRIPT" --project "$WORK/project"
  HERO="$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  python -c "
import json
d = json.load(open('$HERO'))
assert d['apiVersion'] == 3
assert d['name'] == 'acf/lp-hero'
assert d['category'] == 'lp-blocks'
assert d['acf']['renderTemplate'] == 'template-parts/block-hero.php'
"
}

@test "uses icon from block-icons.yaml" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"icon": "cover-image"' "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  grep -q '"icon": "tag"' "$WORK/project/08_КОД/gutenberg-blocks/pricing/block.json"
}

@test "uses fallback icon for unmapped slugs" {
  cat > "$WORK/project/07_КОНТЕНТ/final-copy.md" <<'MD'
## Особый блок

Какой-то текст.
MD
  python "$SCRIPT" --project "$WORK/project"
  grep -q '"icon": "block-default"' "$WORK/project/08_КОД/gutenberg-blocks/osobyy-blok/block.json"
}

@test "idempotent: rerun produces same file" {
  python "$SCRIPT" --project "$WORK/project"
  cp "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" "$WORK/first.json"
  python "$SCRIPT" --project "$WORK/project"
  diff "$WORK/first.json" "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
}
```

- [ ] **Step 3: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-generate-block-json.bats`
Expected: 5 tests FAIL.

- [ ] **Step 4: Implement script**

`skills/wp-gutenberg-block-builder/scripts/generate-block-json.py`:

```python
#!/usr/bin/env python3
"""Generate <project>/08_КОД/gutenberg-blocks/<slug>/block.json per block.

CLI: python generate-block-json.py --project <path>
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402


def _load_icons() -> dict:
    p = REPO_ROOT / "scripts" / "lib" / "block-icons.yaml"
    if not p.exists():
        return {}
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("icons") or {}


def _block_json(slug: str, title: str, icons: dict) -> dict:
    return {
        "apiVersion": 3,
        "name": f"acf/lp-{slug}",
        "title": title,
        "description": f"{title} block (auto-generated from 07_КОНТЕНТ/final-copy.md)",
        "category": "lp-blocks",
        "icon": icons.get(slug, "block-default"),
        "keywords": [slug, "lp"],
        "acf": {
            "mode": "preview",
            "renderTemplate": f"template-parts/block-{slug}.php",
        },
        "supports": {
            "align": False,
            "anchor": True,
            "html": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(src))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    icons = _load_icons()
    base = Path(args.project) / "08_КОД" / "gutenberg-blocks"

    for b in blocks:
        block_dir = base / b.slug
        block_dir.mkdir(parents=True, exist_ok=True)
        dest = block_dir / "block.json"
        with dest.open("w", encoding="utf-8", newline="\n") as f:
            json.dump(_block_json(b.slug, b.title, icons), f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"wrote {len(blocks)} block.json file(s) under {base}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-generate-block-json.bats`
Expected: 5 tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/lib/block-icons.yaml skills/wp-gutenberg-block-builder/scripts/generate-block-json.py tests/phase-stage-08/test-generate-block-json.bats
git commit -m "feat(generate-block-json): one block.json per block + 5 bats tests"
```

---

## Task B3: `generate-block-registration.py`

**Files:**
- Create: `skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py`
- Create: `tests/phase-stage-08/test-generate-block-registration.bats`
- Create: `tests/phase-stage-08/fixtures/expected/minimal.functions-section.php`

- [ ] **Step 1: Write failing bats**

`tests/phase-stage-08/test-generate-block-registration.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
  # Pre-existing functions.php with user code outside auto-generated zone
  cat > "$WORK/project/08_КОД/wp-theme/functions.php" <<'PHP'
<?php
function nu_setup() { add_theme_support('post-thumbnails'); }
add_action('after_setup_theme', 'nu_setup');
PHP
}

teardown() { rm -rf "$WORK"; }

@test "adds AUTO-GENERATED block in functions.php" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  grep -q "AUTO-GENERATED START: lp-block-registration" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "AUTO-GENERATED END" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "registers all blocks in the loop" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "'hero'" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "'pricing'" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "registers lp-blocks category" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "'lp-blocks'" "$WORK/project/08_КОД/wp-theme/functions.php"
  grep -q "block_categories_all" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "preserves user code outside markers" {
  python "$SCRIPT" --project "$WORK/project"
  grep -q "function nu_setup" "$WORK/project/08_КОД/wp-theme/functions.php"
}

@test "idempotent: rerun does not duplicate" {
  python "$SCRIPT" --project "$WORK/project"
  python "$SCRIPT" --project "$WORK/project"
  COUNT=$(grep -c "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php")
  [ "$COUNT" = "1" ]
}

@test "creates .bak before modifying" {
  python "$SCRIPT" --project "$WORK/project"
  [ -f "$WORK/project/08_КОД/wp-theme/functions.php.bak" ]
}

@test "fails if markers were manually removed and content changed" {
  python "$SCRIPT" --project "$WORK/project"
  # Strip out the auto-generated block but leave the file
  python -c "
import re
path = '$WORK/project/08_КОД/wp-theme/functions.php'
s = open(path).read()
s = re.sub(r'// AUTO-GENERATED START.*?// AUTO-GENERATED END\n', '', s, flags=re.DOTALL)
open(path, 'w').write(s)
"
  # Now rerun — adds markers back fine (no error, this is the recovery path)
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  grep -q "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php"
}
```

- [ ] **Step 2: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-generate-block-registration.bats`
Expected: 7 tests FAIL.

- [ ] **Step 3: Implement script**

`skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py`:

```python
#!/usr/bin/env python3
"""Inject (or update) AUTO-GENERATED block registration section in functions.php.

CLI: python generate-block-registration.py --project <path>
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402

MARKER_START = "// AUTO-GENERATED START: lp-block-registration — DO NOT EDIT MANUALLY"
MARKER_END = "// AUTO-GENERATED END"
SECTION_RE = re.compile(
    r"\n?// AUTO-GENERATED START: lp-block-registration.*?// AUTO-GENERATED END\n?",
    re.DOTALL,
)


def _render_section(slugs: list[str]) -> str:
    slug_php = ", ".join(f"'{s}'" for s in slugs)
    return f"""
{MARKER_START}
//                      Regenerated by generate-block-registration.py
if ( ! function_exists( 'lp_register_block_category' ) ) {{
    function lp_register_block_category( $categories ) {{
        return array_merge(
            $categories,
            [ [ 'slug' => 'lp-blocks', 'title' => 'Landing-page blocks', 'icon' => null ] ]
        );
    }}
    add_filter( 'block_categories_all', 'lp_register_block_category' );
}}

if ( ! function_exists( 'lp_register_acf_blocks' ) ) {{
    function lp_register_acf_blocks() {{
        $blocks = [ {slug_php} ];
        foreach ( $blocks as $slug ) {{
            $path = get_template_directory() . '/../../gutenberg-blocks/' . $slug;
            if ( file_exists( $path . '/block.json' ) ) {{
                register_block_type( $path );
            }}
        }}
    }}
    add_action( 'init', 'lp_register_acf_blocks' );
}}
{MARKER_END}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    args = ap.parse_args()

    src = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(src))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    fn_php = Path(args.project) / "08_КОД" / "wp-theme" / "functions.php"
    if not fn_php.exists():
        print(f"ERROR: {fn_php} not found", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(fn_php, fn_php.with_suffix(".php.bak"))
    src_text = fn_php.read_text(encoding="utf-8")

    section = _render_section([b.slug for b in blocks])

    if SECTION_RE.search(src_text):
        new_text = SECTION_RE.sub(section, src_text)
    else:
        # Append to end of file (after last `?>` if present, or just append)
        if src_text.rstrip().endswith("?>"):
            new_text = src_text.rstrip()[:-2].rstrip() + "\n" + section + "\n?>\n"
        else:
            new_text = src_text.rstrip() + "\n" + section

    fn_php.write_text(new_text, encoding="utf-8", newline="\n")
    print(f"wrote {fn_php} (registered {len(blocks)} block(s))")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-generate-block-registration.bats`
Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py tests/phase-stage-08/test-generate-block-registration.bats
git commit -m "feat(generate-block-registration): AUTO-GENERATED functions.php section + 7 bats tests"
```

---

## Task B4: `generate-theme.py` extension — create block-<slug>.php

**Files:**
- Modify: `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`
- Add tests: extend `tests/phase-stage-08/test-generate-acf.bats` or new test file

This is a small extension. We add a new mode to `generate-theme.py` that, given a project root, reads ContentParser blocks and creates missing `template-parts/block-<slug>.php` stubs. Existing files are NEVER overwritten.

- [ ] **Step 1: Write new test file**

`tests/phase-stage-08/test-generate-theme-blocks.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/skills/wp-gutenberg-block-builder/scripts/generate-theme.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme/template-parts"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
}

teardown() { rm -rf "$WORK"; }

@test "--blocks-only creates missing block-<slug>.php" {
  run python "$SCRIPT" --project "$WORK/project" --blocks-only
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php" ]
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-pricing.php" ]
}

@test "block-<slug>.php has nu_field() calls per ACF field" {
  python "$SCRIPT" --project "$WORK/project" --blocks-only
  grep -q "nu_field( 'title'" "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
}

@test "does NOT overwrite existing block-<slug>.php" {
  echo "<?php /* manual content, do not touch */" > "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
  python "$SCRIPT" --project "$WORK/project" --blocks-only
  grep -q "manual content, do not touch" "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
}
```

- [ ] **Step 2: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-generate-theme-blocks.bats`
Expected: 3 tests FAIL — `--blocks-only` flag not recognised.

- [ ] **Step 3: Read current `generate-theme.py` to find insertion point**

Run: `head -50 skills/wp-gutenberg-block-builder/scripts/generate-theme.py`

You'll see the script takes a `project-dir` positional argument and writes theme files. Add a `--blocks-only` flag that skips full-theme generation and only writes `template-parts/block-<slug>.php` files.

- [ ] **Step 4: Add blocks-only mode**

At the top of `skills/wp-gutenberg-block-builder/scripts/generate-theme.py`, after existing imports, add:

```python
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402


def _write_block_parts(project_dir: Path) -> int:
    """Write template-parts/block-<slug>.php for each block from final-copy.md.

    Never overwrites an existing file. Returns count of files written.
    """
    md = project_dir / "07_КОНТЕНТ" / "final-copy.md"
    blocks = ContentParser.parse(str(md))
    ContentParser.validate(blocks)
    parts_dir = project_dir / "08_КОД" / "wp-theme" / "template-parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for b in blocks:
        dest = parts_dir / f"block-{b.slug}.php"
        if dest.exists():
            continue
        lines = [
            "<?php",
            f"/**",
            f" * Block — {b.title}.",
            f" * Auto-scaffolded by generate-theme.py --blocks-only.",
            f" * Edit safely; will not be overwritten on regeneration.",
            f" */",
            "if ( ! defined( 'ABSPATH' ) ) { exit; }",
            "",
        ]
        for f in b.fields:
            default = (f.default or "").replace("'", "\\'") if f.default else ""
            if f.type == "repeater":
                lines.append(f"$nu_{f.name.replace('-', '_')} = nu_field_array( '{f.name}', array() );")
            else:
                lines.append(f"$nu_{f.name.replace('-', '_')} = nu_field( '{f.name}', '{default}' );")
        lines.append("?>")
        lines.append(f"<section id=\"{b.slug}\" class=\"lp-block lp-block--{b.slug}\">")
        for f in b.fields:
            if f.type in {"text", "textarea", "wysiwyg"}:
                lines.append(f"    <div class=\"lp-block__{f.name}\"><?php echo esc_html( $nu_{f.name.replace('-', '_')} ); ?></div>")
        lines.append("</section>")
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        written += 1
    return written
```

Locate where the script's `main()` (or `if __name__ == "__main__":`) lives. Add this at the very top of the entry-point handling (before existing argument parsing):

```python
def _maybe_blocks_only() -> bool:
    if "--blocks-only" in sys.argv:
        # Find --project or assume first positional
        try:
            i = sys.argv.index("--project")
            project = sys.argv[i + 1]
        except (ValueError, IndexError):
            print("ERROR: --blocks-only requires --project <path>", file=sys.stderr)
            sys.exit(2)
        n = _write_block_parts(Path(project))
        print(f"wrote {n} block template part(s)")
        sys.exit(0)
    return False


_maybe_blocks_only()
# ...existing script logic continues below (only reached if --blocks-only NOT in argv)...
```

- [ ] **Step 5: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-generate-theme-blocks.bats`
Expected: 3 tests pass.

- [ ] **Step 6: Commit**

```bash
git add skills/wp-gutenberg-block-builder/scripts/generate-theme.py tests/phase-stage-08/test-generate-theme-blocks.bats
git commit -m "feat(generate-theme): --blocks-only mode creates missing block-<slug>.php"
```

---

## Task B5: Orchestrator `generate-wp-blocks.py`

**Files:**
- Create: `scripts/generate-wp-blocks.py`
- Create: `tests/phase-stage-08/test-generate-wp-blocks.bats`

- [ ] **Step 1: Write failing bats**

`tests/phase-stage-08/test-generate-wp-blocks.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/generate-wp-blocks.py"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/project/07_КОНТЕНТ" "$WORK/project/08_КОД/wp-theme/template-parts"
  cp "$FIXTURES/content/minimal.md" "$WORK/project/07_КОНТЕНТ/final-copy.md"
  printf '<?php\n' > "$WORK/project/08_КОД/wp-theme/functions.php"
}

teardown() { rm -rf "$WORK"; }

@test "runs B1..B4 in order" {
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -eq 0 ]
  [ -f "$WORK/project/08_КОД/acf-fields.json" ]
  [ -f "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json" ]
  grep -q "AUTO-GENERATED START" "$WORK/project/08_КОД/wp-theme/functions.php"
  [ -f "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php" ]
}

@test "--dry-run does not write files" {
  run python "$SCRIPT" --project "$WORK/project" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"dry-run"* ]] || [[ "$output" == *"would"* ]]
  [ ! -f "$WORK/project/08_КОД/acf-fields.json" ]
}

@test "fails fast on content parse error" {
  echo "no h2" > "$WORK/project/07_КОНТЕНТ/final-copy.md"
  run python "$SCRIPT" --project "$WORK/project"
  [ "$status" -ne 0 ]
  [[ "$output" == *"no H2"* ]]
  [ ! -f "$WORK/project/08_КОД/acf-fields.json" ]
}
```

- [ ] **Step 2: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-generate-wp-blocks.bats`
Expected: 3 tests FAIL.

- [ ] **Step 3: Implement orchestrator**

`scripts/generate-wp-blocks.py`:

```python
#!/usr/bin/env python3
"""Orchestrate stage-08 generators: ACF → block.json → registration → block-*.php.

Usage:
    python scripts/generate-wp-blocks.py --project <path>
    python scripts/generate-wp-blocks.py --project <path> --dry-run
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402

STEPS = [
    ("ACF fields", "skills/wp-gutenberg-block-builder/scripts/generate-acf.py", []),
    ("block.json", "skills/wp-gutenberg-block-builder/scripts/generate-block-json.py", []),
    ("block registration", "skills/wp-gutenberg-block-builder/scripts/generate-block-registration.py", []),
    ("block template parts", "skills/wp-gutenberg-block-builder/scripts/generate-theme.py", ["--blocks-only"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Validate content first — fail fast before running any generator
    md = Path(args.project) / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(md))
        ContentParser.validate(blocks)
    except ContentParseError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ ContentParser: {len(blocks)} block(s) detected")

    if args.dry_run:
        print("(dry-run) would run the following generators:")
        for name, path, extra in STEPS:
            print(f"  - {name}: python {path} --project {args.project} {' '.join(extra)}")
        return

    for name, path, extra in STEPS:
        cmd = [sys.executable, str(REPO_ROOT / path), "--project", args.project, *extra]
        print(f"▶ {name}")
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"ERROR: {name} failed (exit {result.returncode})", file=sys.stderr)
            sys.exit(result.returncode)

    print(f"✓ stage-08 artifacts generated for {args.project}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-generate-wp-blocks.bats`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate-wp-blocks.py tests/phase-stage-08/test-generate-wp-blocks.bats
git commit -m "feat(generate-wp-blocks): orchestrator B1..B4 + dry-run + 3 bats tests"
```

---

# Phase C — Hard gate + legacy

## Task C1: stage_08_helper.py + 10 gate checks in config

**Files:**
- Create: `scripts/lib/stage_08_helper.py`
- Modify: `config/stage-gates.yaml` (under `08_build` → `hard_checks`)
- Create: `tests/phase-stage-08/test-gate-check-stage-08.bats`
- Create: `tests/phase-stage-08/fixtures/projects/valid-project/` (full skeleton)

- [ ] **Step 1: Build the valid-project fixture**

Create a fixture project that should pass all 10 checks. Use scripts B1-B4 to generate it.

```bash
# (Run this manually to seed the fixture — once)
FIX=tests/phase-stage-08/fixtures/projects/valid-project
mkdir -p "$FIX/07_КОНТЕНТ" "$FIX/08_КОД/wp-theme/template-parts"
cp tests/phase-stage-08/fixtures/content/minimal.md "$FIX/07_КОНТЕНТ/final-copy.md"
printf '<?php\nfunction nu_field($k,$d=""){return $d;}\nfunction nu_field_array($k,$d=array()){return $d;}\n' > "$FIX/08_КОД/wp-theme/functions.php"
cat > "$FIX/.landing-state.yaml" <<'YAML'
project: "valid-project"
stages:
  "08_build": {status: in_progress, timestamp: ""}
YAML
python scripts/generate-wp-blocks.py --project "$FIX"
```

After that, `git add tests/phase-stage-08/fixtures/projects/valid-project` — commit this seeded fixture so tests have a stable baseline.

- [ ] **Step 2: Write failing bats**

`tests/phase-stage-08/test-gate-check-stage-08.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  FIXTURES="$ROOT/tests/phase-stage-08/fixtures/projects"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  cp -r "$FIXTURES/valid-project" "$WORK/project"
}

teardown() { rm -rf "$WORK"; }

@test "happy path: valid-project passes gate" {
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -eq 0 ]
}

@test "#1 fails when wp-theme dir missing" {
  rm -rf "$WORK/project/08_КОД/wp-theme"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"wp-theme"* ]]
}

@test "#2 fails when no register_block_type in functions.php" {
  printf '<?php\n' > "$WORK/project/08_КОД/wp-theme/functions.php"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block registration"* ]]
}

@test "#3 fails when acf-fields.json missing" {
  rm "$WORK/project/08_КОД/acf-fields.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"acf-fields.json"* ]]
}

@test "#4 fails when acf-fields.json is invalid JSON" {
  echo "{ broken" > "$WORK/project/08_КОД/acf-fields.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
}

@test "#5 fails when ACF group missing for H2" {
  python -c "
import json
p = '$WORK/project/08_КОД/acf-fields.json'
d = json.load(open(p))
d.pop()
json.dump(d, open(p, 'w'))
"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"ACF group missing"* ]]
}

@test "#7 fails when block.php template part is missing" {
  rm "$WORK/project/08_КОД/wp-theme/template-parts/block-hero.php"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block-hero"* ]]
}

@test "#8 fails when block.json missing" {
  rm "$WORK/project/08_КОД/gutenberg-blocks/hero/block.json"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -ne 0 ]
  [[ "$output" == *"block.json"* ]]
}

@test "legacy: true bypasses all hard checks" {
  rm -rf "$WORK/project/08_КОД/wp-theme"  # would fail #1
  echo "legacy: true" >> "$WORK/project/.landing-state.yaml"
  run bash "$ROOT/scripts/gate-check.sh" --stage 08_build --project "$WORK/project" --auto
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 3: Implement stage_08_helper.py**

`scripts/lib/stage_08_helper.py`:

```python
#!/usr/bin/env python3
"""Stage-08 structural check (called from gate-check.sh as type=script).

Runs checks 4 (JSON valid), 5 (ACF group per H2), 6 (each group ≥1 field),
7 (block-<slug>.php exists), 8 (block.json per registered block), and 9
(block.json has recommended fields → warning).

Exit 0 = pass. Exit 1 = hard fail. Warnings printed to stderr but do not
affect exit code unless --strict-warnings is passed.

Usage: python stage_08_helper.py <project-root>
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))

from content_parser import ContentParser, ContentParseError  # noqa: E402


def check(project: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # Bypass if legacy
    state = project / ".landing-state.yaml"
    if state.exists() and "legacy: true" in state.read_text(encoding="utf-8"):
        print("stage-08: legacy:true — skipping hard checks", file=sys.stderr)
        return 0

    md = project / "07_КОНТЕНТ" / "final-copy.md"
    try:
        blocks = ContentParser.parse(str(md))
        ContentParser.validate(blocks)
    except (ContentParseError, FileNotFoundError) as e:
        errors.append(f"final-copy.md unparseable: {e}")
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        return 1

    expected_slugs = {b.slug for b in blocks}

    acf_path = project / "08_КОД" / "acf-fields.json"
    if not acf_path.exists():
        errors.append("acf-fields.json missing")
    else:
        try:
            acf_data = json.load(acf_path.open(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"acf-fields.json invalid JSON: {e}")
            acf_data = None

        if acf_data is not None:
            if not isinstance(acf_data, list):
                acf_data = [acf_data]
            acf_slugs = set()
            for g in acf_data:
                loc = (g.get("location") or [[{}]])[0][0] if g.get("location") else {}
                val = loc.get("value", "")
                if val.startswith("acf/lp-"):
                    slug = val.removeprefix("acf/lp-")
                    acf_slugs.add(slug)
                    if not g.get("fields"):
                        errors.append(f"ACF group '{slug}' has no fields (#6)")
            for slug in expected_slugs - acf_slugs:
                errors.append(f"ACF group missing for block '{slug}' (#5)")

    # Per-block file checks
    for slug in expected_slugs:
        part = project / "08_КОД" / "wp-theme" / "template-parts" / f"block-{slug}.php"
        if not part.exists():
            errors.append(f"template-parts/block-{slug}.php missing (#7)")
        bj = project / "08_КОД" / "gutenberg-blocks" / slug / "block.json"
        if not bj.exists():
            errors.append(f"gutenberg-blocks/{slug}/block.json missing (#8)")
        else:
            try:
                d = json.load(bj.open(encoding="utf-8"))
                missing = [k for k in ("title", "description", "category", "icon") if not d.get(k)]
                if missing:
                    warnings.append(f"block.json for '{slug}' missing recommended fields: {missing}")
            except json.JSONDecodeError as e:
                errors.append(f"block.json for '{slug}' invalid: {e}")

    # manual review warning
    if state.exists():
        st = state.read_text(encoding="utf-8")
        if "manual_field_review_needed:" in st:
            warnings.append(f"manual_field_review_needed flag set in state.yaml — verify generated fields")

    for w in warnings:
        print(f"⚠ {w}", file=sys.stderr)
    for e in errors:
        print(f"❌ {e}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: stage_08_helper.py <project-root>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check(Path(sys.argv[1])))
```

- [ ] **Step 4: Update `config/stage-gates.yaml` — `08_build` block**

Find the `"08_build":` block in `config/stage-gates.yaml` and replace its `hard_checks` list with:

```yaml
  "08_build":
    name: "WP Build"
    require_approved: ["07_content"]
    hard_checks:
      - id: design_md
        type: file_exists
        path: "{project}/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"
        required: true
      - id: final_copy
        type: file_exists
        path: "{project}/07_КОНТЕНТ/final-copy.md"
        required: true
      - id: wp_theme_dir
        type: file_exists
        path: "{project}/08_КОД/wp-theme"
        required: true
        fix_hint: "Run /landing-build to generate the wp-theme scaffold."
      - id: block_registration
        type: script
        script: "scripts/lib/check-block-registration.sh"
        args: ["{project}"]
        fix_hint: "No register_block_type found in functions.php. Run: python scripts/generate-wp-blocks.py --project {project}"
      - id: acf_and_blocks_structure
        type: script
        script: "scripts/lib/stage_08_helper.py"
        args: ["{project}"]
        fix_hint: "Run: python scripts/generate-wp-blocks.py --project {project}"
```

- [ ] **Step 5: Create the small helper for check #2**

`scripts/lib/check-block-registration.sh`:

```bash
#!/usr/bin/env bash
# Hard-check #2: at least one register_block_type call in functions.php.
# Bypassed by legacy:true in .landing-state.yaml.
set -u

PROJECT="${1:?project path required}"

if [ -f "$PROJECT/.landing-state.yaml" ] && grep -q "^[[:space:]]*legacy:[[:space:]]*true" "$PROJECT/.landing-state.yaml" 2>/dev/null; then
    exit 0
fi

FN="$PROJECT/08_КОД/wp-theme/functions.php"
if [ ! -f "$FN" ]; then
    echo "functions.php not found at $FN — no block registration possible" >&2
    exit 1
fi
if grep -qE "register_block_type" "$FN"; then
    exit 0
fi
echo "no register_block_type call found in functions.php" >&2
exit 1
```

- [ ] **Step 6: Run all gate-check tests**

Run: `npx bats tests/phase-stage-08/test-gate-check-stage-08.bats`
Expected: 9 tests pass.

If `gate-check.sh` requires `yq` and it's missing on the dev machine, tests will fail at step "yq not installed". Install once via `brew install yq` (macOS), `apt-get install yq` (Linux), or `choco install yq` (Windows). Skip the test setup with a `bats skip` if not available — but ideally install.

- [ ] **Step 7: Commit**

```bash
chmod +x scripts/lib/check-block-registration.sh
git add scripts/lib/stage_08_helper.py scripts/lib/check-block-registration.sh config/stage-gates.yaml tests/phase-stage-08/test-gate-check-stage-08.bats tests/phase-stage-08/fixtures/projects/valid-project/
git commit -m "feat(stage-08-gate): 10 hard-checks + legacy bypass + 9 bats tests"
```

---

## Task C2: `mark-legacy-projects.sh`

**Files:**
- Create: `scripts/mark-legacy-projects.sh`
- Create: `tests/phase-stage-08/test-mark-legacy-projects.bats`

- [ ] **Step 1: Write failing bats**

`tests/phase-stage-08/test-mark-legacy-projects.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/mark-legacy-projects.sh"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  mkdir -p "$WORK/Lendings/legacy-project" "$WORK/Lendings/valid-project"

  cat > "$WORK/Lendings/legacy-project/.landing-state.yaml" <<'YAML'
project: "legacy-project"
stages:
  "08_build": {status: in_progress, timestamp: ""}
YAML
  # No stage-08 artifacts → would fail gate
  mkdir -p "$WORK/Lendings/legacy-project/07_КОНТЕНТ"
  echo "## Hero\n\ntext" > "$WORK/Lendings/legacy-project/07_КОНТЕНТ/final-copy.md"

  # Copy known-good valid project
  cp -r "$ROOT/tests/phase-stage-08/fixtures/projects/valid-project/." "$WORK/Lendings/valid-project/"
}

teardown() { rm -rf "$WORK"; }

@test "marks legacy:true on project that fails gate" {
  run bash "$SCRIPT" "$WORK/Lendings"
  [ "$status" -eq 0 ]
  grep -q "^legacy: true" "$WORK/Lendings/legacy-project/.landing-state.yaml"
}

@test "does not mark project that passes gate" {
  bash "$SCRIPT" "$WORK/Lendings"
  ! grep -q "^legacy: true" "$WORK/Lendings/valid-project/.landing-state.yaml"
}

@test "idempotent: running twice does not duplicate" {
  bash "$SCRIPT" "$WORK/Lendings"
  bash "$SCRIPT" "$WORK/Lendings"
  COUNT=$(grep -c "^legacy: true" "$WORK/Lendings/legacy-project/.landing-state.yaml")
  [ "$COUNT" = "1" ]
}

@test "skips dirs without .landing-state.yaml" {
  mkdir -p "$WORK/Lendings/not-a-project"
  run bash "$SCRIPT" "$WORK/Lendings"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-mark-legacy-projects.bats`
Expected: 4 tests FAIL — script doesn't exist.

- [ ] **Step 3: Implement script**

`scripts/mark-legacy-projects.sh`:

```bash
#!/usr/bin/env bash
# Mark Lendings/* projects as legacy:true if they fail stage-08 gate.
# One-shot, idempotent. Run once after merging the systemic fix.
#
# Usage: mark-legacy-projects.sh [<lendings-root>]
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LENDINGS_ROOT="${1:-$(realpath "$REPO_ROOT/../Lendings")}"

if [ ! -d "$LENDINGS_ROOT" ]; then
    echo "❌ $LENDINGS_ROOT not found" >&2
    exit 1
fi

for project in "$LENDINGS_ROOT"/*/; do
    [ -f "$project.landing-state.yaml" ] || continue
    pname="$(basename "$project")"

    if grep -q "^legacy:" "$project.landing-state.yaml"; then
        echo "  $pname — already has legacy marker"
        continue
    fi

    if bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$project" --auto >/dev/null 2>&1; then
        echo "✓ $pname — passes stage-08, no marking needed"
    else
        echo "⚠ $pname — marking legacy:true"
        TS="$(date -u +%Y-%m-%d)"
        echo "legacy: true  # auto-marked $TS — pre-stage-08-hardening" >> "$project.landing-state.yaml"
    fi
done
```

- [ ] **Step 4: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-mark-legacy-projects.bats`
Expected: 4 tests pass.

If the test fails because gate-check.sh requires `07_content` to be approved first, the fixture may need that marker too. Inspect the failing assertion message and add `"07_content": {status: approved, timestamp: "2026-05-12T00:00:00Z"}` to the legacy-project's state.yaml.

- [ ] **Step 5: Commit**

```bash
chmod +x scripts/mark-legacy-projects.sh
git add scripts/mark-legacy-projects.sh tests/phase-stage-08/test-mark-legacy-projects.bats
git commit -m "feat(legacy): mark-legacy-projects.sh + 4 bats tests"
```

---

## Task C3: `backport-acf-to-legacy.sh`

**Files:**
- Create: `scripts/backport-acf-to-legacy.sh`
- Create: `tests/phase-stage-08/test-backport-legacy.bats`

- [ ] **Step 1: Write failing bats**

`tests/phase-stage-08/test-backport-legacy.bats`:

```bash
#!/usr/bin/env bats

setup() {
  ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"
  SCRIPT="$ROOT/scripts/backport-acf-to-legacy.sh"
  WORK="$(python -c "import tempfile; print(tempfile.mkdtemp().replace(chr(92),'/'))")"
  PROJECT="$WORK/legacy-project"
  mkdir -p "$PROJECT/07_КОНТЕНТ" "$PROJECT/08_КОД/wp-theme/template-parts"

  cp "$ROOT/tests/phase-stage-08/fixtures/content/minimal.md" "$PROJECT/07_КОНТЕНТ/final-copy.md"
  printf '<?php\nfunction nu_field($k,$d=""){return $d;}\nfunction nu_field_array($k,$d=array()){return $d;}\n' > "$PROJECT/08_КОД/wp-theme/functions.php"
  cat > "$PROJECT/.landing-state.yaml" <<'YAML'
project: "legacy-project"
stages:
  "07_content": {status: approved, timestamp: "2026-05-12T00:00:00Z"}
  "08_build": {status: in_progress, timestamp: ""}
legacy: true
YAML
}

teardown() { rm -rf "$WORK"; }

@test "creates artifacts when run without flags" {
  run bash "$SCRIPT" "$PROJECT"
  [ "$status" -eq 0 ]
  [ -f "$PROJECT/08_КОД/acf-fields.json" ]
  [ -f "$PROJECT/08_КОД/gutenberg-blocks/hero/block.json" ]
}

@test "creates backport-backup directory before modifying" {
  bash "$SCRIPT" "$PROJECT"
  ls -d "$PROJECT/.backport-backup-"* >/dev/null 2>&1
}

@test "--dry-run does not write files" {
  run bash "$SCRIPT" "$PROJECT" --dry-run
  [ "$status" -eq 0 ]
  [ ! -f "$PROJECT/08_КОД/acf-fields.json" ]
}

@test "without --force, refuses if acf-fields.json already exists" {
  bash "$SCRIPT" "$PROJECT"
  run bash "$SCRIPT" "$PROJECT"
  [ "$status" -ne 0 ]
  [[ "$output" == *"--force"* ]]
}

@test "with --force, regenerates over existing" {
  bash "$SCRIPT" "$PROJECT"
  run bash "$SCRIPT" "$PROJECT" --force
  [ "$status" -eq 0 ]
}

@test "removes legacy:true after successful run" {
  bash "$SCRIPT" "$PROJECT"
  ! grep -q "^legacy: true" "$PROJECT/.landing-state.yaml"
}
```

- [ ] **Step 2: Run, verify fail**

Run: `npx bats tests/phase-stage-08/test-backport-legacy.bats`
Expected: 6 tests FAIL.

- [ ] **Step 3: Implement script**

`scripts/backport-acf-to-legacy.sh`:

```bash
#!/usr/bin/env bash
# Backport stage-08 ACF/Gutenberg artifacts onto a legacy project.
# Usage: backport-acf-to-legacy.sh <project> [--dry-run] [--force]
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:?usage: backport-acf-to-legacy.sh <project> [--dry-run] [--force]}"
shift || true

DRY_RUN=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --force)   FORCE=1 ;;
    esac
done

[ -d "$PROJECT" ] || { echo "❌ project dir not found: $PROJECT" >&2; exit 1; }

# 1. Refuse without --force if acf-fields.json exists
ACF="$PROJECT/08_КОД/acf-fields.json"
if [ "$DRY_RUN" = "0" ] && [ "$FORCE" = "0" ] && [ -f "$ACF" ]; then
    echo "❌ $ACF already exists. Use --force to regenerate." >&2
    exit 1
fi

# 2. Validate content can be parsed (fail fast)
python "$REPO_ROOT/scripts/lib/content_parser.py" "$PROJECT/07_КОНТЕНТ/final-copy.md" >/dev/null || {
    echo "❌ content_parser failed — fix final-copy.md first" >&2
    exit 1
}

# 3. Dry-run mode
if [ "$DRY_RUN" = "1" ]; then
    python "$REPO_ROOT/scripts/generate-wp-blocks.py" --project "$PROJECT" --dry-run
    exit 0
fi

# 4. Backup
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="$PROJECT/.backport-backup-$TS"
mkdir -p "$BACKUP"
for f in "$PROJECT/08_КОД/wp-theme/functions.php" "$ACF"; do
    [ -f "$f" ] && cp "$f" "$BACKUP/" || true
done
echo "  backup → $BACKUP"

# 5. Run the orchestrator
python "$REPO_ROOT/scripts/generate-wp-blocks.py" --project "$PROJECT" || {
    echo "❌ generate-wp-blocks failed" >&2
    exit 1
}

# 6. Verify gate passes
bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$PROJECT" --auto || {
    echo "❌ Generated artifacts but gate still fails — investigate $BACKUP for rollback" >&2
    exit 1
}

# 7. Remove legacy marker
STATE="$PROJECT/.landing-state.yaml"
if [ -f "$STATE" ] && grep -q "^legacy: true" "$STATE"; then
    grep -v "^legacy: true" "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
fi

echo "✓ Backport complete for $(basename "$PROJECT"). Review generated files, then deploy."
```

- [ ] **Step 4: Run tests, verify pass**

Run: `npx bats tests/phase-stage-08/test-backport-legacy.bats`
Expected: 6 tests pass.

- [ ] **Step 5: Commit**

```bash
chmod +x scripts/backport-acf-to-legacy.sh
git add scripts/backport-acf-to-legacy.sh tests/phase-stage-08/test-backport-legacy.bats
git commit -m "feat(legacy): backport-acf-to-legacy.sh + 6 bats tests"
```

---

## Task C4: Fix `wp acf import` silent fail in deploy

**Files:**
- Modify: `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`

This is a small, surgical fix. No new bats — the change is in a script that runs against a live server and can't be unit-tested in isolation.

- [ ] **Step 1: Read current deploy script**

Run: `grep -n "wp acf import" skills/wp-cli-deployer/scripts/deploy-wordpress.sh`

Note the exact line. It currently looks like:

```bash
ssh "${BEGET_USER}@${BEGET_HOST}" \
    "echo '${ACF_CONTENT}' | wp acf import --json - --path=${BEGET_PATH} --allow-root" 2>/dev/null || true
```

- [ ] **Step 2: Replace the silent fail with loud fail + plugin check**

Replace those lines with:

```bash
if [ -f "$ACF_JSON" ]; then
    echo "▶ Проверяю что ACF активен на сервере"
    if ! ssh "${BEGET_USER}@${BEGET_HOST}" \
        "wp plugin is-active advanced-custom-fields --path=${BEGET_PATH} --allow-root" 2>/dev/null; then
        echo "❌ Плагин ACF не активен на сервере."
        echo "   Сначала установите и активируйте его:"
        echo "   ssh ${BEGET_USER}@${BEGET_HOST} \"wp plugin install advanced-custom-fields --activate --path=${BEGET_PATH} --allow-root\""
        exit 1
    fi
    echo "▶ Импорт ACF полей"
    ACF_CONTENT="$(cat "$ACF_JSON")"
    if ! ssh "${BEGET_USER}@${BEGET_HOST}" \
        "echo '${ACF_CONTENT}' | wp acf import --json - --path=${BEGET_PATH} --allow-root"; then
        echo "❌ wp acf import не прошёл. Проверьте формат $ACF_JSON и доступ ACF на сервере."
        exit 1
    fi
fi
```

- [ ] **Step 3: Manual verify**

Without a live server we can't run this, but check the script syntactically:

Run: `bash -n skills/wp-cli-deployer/scripts/deploy-wordpress.sh`
Expected: no output (no syntax errors).

- [ ] **Step 4: Commit**

```bash
git add skills/wp-cli-deployer/scripts/deploy-wordpress.sh
git commit -m "fix(deploy): wp acf import no longer silently fails; check plugin is active first"
```

---

## Task C5: Honest SKILL.md + documentation

**Files:**
- Modify: `skills/wp-gutenberg-block-builder/SKILL.md`
- Modify: `docs/SETUP.md` (or `template/CLAUDE.md` if SETUP.md doesn't exist)

- [ ] **Step 1: Rewrite SKILL.md to match reality**

Replace contents of `skills/wp-gutenberg-block-builder/SKILL.md`:

```markdown
---
name: wp-gutenberg-block-builder
description: Generate ACF Block Gutenberg blocks + ACF fields + theme template parts from 07_КОНТЕНТ/final-copy.md. Used by wp-builder agent during stage 08.
---

# wp-gutenberg-block-builder

Generates the four stage-08 WP artifacts from a single source of truth (`07_КОНТЕНТ/final-copy.md`):

1. `08_КОД/acf-fields.json` — ACF field groups, one per H2 block.
2. `08_КОД/gutenberg-blocks/<slug>/block.json` — block descriptor per block.
3. `08_КОД/wp-theme/functions.php` — `register_block_type()` for each block, inside `AUTO-GENERATED` markers.
4. `08_КОД/wp-theme/template-parts/block-<slug>.php` — scaffolded render template (only for missing files).

Use the orchestrator:

\```bash
python scripts/generate-wp-blocks.py --project <project-dir>
\```

It calls the four generators in order:
- `scripts/generate-acf.py`
- `scripts/generate-block-json.py`
- `scripts/generate-block-registration.py`
- `scripts/generate-theme.py --blocks-only`

All four are driven by `scripts/lib/content_parser.py` — a single source of truth that parses H2 headings into `Block` objects. Field types are inferred by ordered regex heuristics; see spec `docs/superpowers/specs/2026-05-12-stage-08-acf-gutenberg-design.md` for details.

## Honest scope

- Generates ACF Block-style Gutenberg blocks (`apiVersion: 3`, `acf/` namespace).
- Does NOT generate Native Gutenberg blocks (no React, no `edit.js`, no build step).
- Does NOT register form integrations (Fluent Forms, CRM webhooks) — that's `generate-integrations.py`.
- Does NOT generate analytics — `generate-analytics.py`.

## Stage-08 hard-gate

After generation, `bash scripts/gate-check.sh --stage 08_build --project <path>` enforces:

1. wp-theme/ exists.
2. `register_block_type` present in functions.php.
3. `acf-fields.json` exists, is valid JSON.
4. One ACF group per H2 block.
5. Each ACF group has ≥1 field.
6. Each block has `template-parts/block-<slug>.php`.
7. Each block has `gutenberg-blocks/<slug>/block.json`.
8. Warnings: block.json has title/description/category/icon; manual_field_review_needed empty.

Projects pre-dating this hardening can be marked `legacy: true` (auto via `scripts/mark-legacy-projects.sh`) to bypass the gate. Migrate them with `scripts/backport-acf-to-legacy.sh <project>`.
```

- [ ] **Step 2: Add SETUP.md ACF section**

Check if `docs/SETUP.md` exists: `ls docs/SETUP.md`

If yes, append:

```markdown
## ACF and Gutenberg blocks for managers

After deployment, the landing page exposes every text-editable element as an ACF field in the WordPress block sidebar. Managers can:

1. Open `/wp-admin`, navigate to the page.
2. Click any landing block in the editor canvas.
3. Use the right-hand sidebar form to edit headings, body text, button labels, prices, etc.
4. Repeater fields (e.g., pricing tiers, program modules) show as a list with **+ Add** and drag handles.
5. Click **Update** to publish.

No PHP edits required. To learn what fields each block has, see `08_КОД/acf-fields.json` in the project repo.

### When fields are missing

If the WordPress editor shows an empty block sidebar:

1. Verify ACF plugin is active: WP admin → Plugins → Advanced Custom Fields → Active.
2. Verify the ACF JSON was imported: WP admin → ACF → Field Groups → there should be groups named after each landing section (Hero, Pricing, etc.).
3. If groups are missing, re-import: from the project folder run `bash skills/wp-cli-deployer/scripts/deploy-wordpress.sh <project-dir>` — the deploy script now imports ACF fields and fails loudly if it can't.
```

If `docs/SETUP.md` doesn't exist, append the same section to `template/CLAUDE.md` under a new `## ACF and Gutenberg blocks for managers` heading.

- [ ] **Step 3: Commit**

```bash
git add skills/wp-gutenberg-block-builder/SKILL.md docs/SETUP.md template/CLAUDE.md
git commit -m "docs(stage-08): honest SKILL.md + manager-facing ACF guide"
```

---

# Final verification

- [ ] **Step F1: Full phase-stage-08 suite green**

Run: `npm run test:phase-stage-08`
Expected: ~60 tests pass (~30 pytest + ~30 bats).

- [ ] **Step F2: No regressions in other phases**

Run: `npm test` (runs all bats under tests/).
Expected: every existing bats suite (phase-1, phase-2, phase-niche, phase-preview-panel, phase-stage-08) green.

- [ ] **Step F3: Spec acceptance criteria walk-through**

Open `docs/superpowers/specs/2026-05-12-stage-08-acf-gutenberg-design.md`, "Acceptance Criteria" section, verify each of the 13 items:

1. `content_parser.py` exists + pytest passes (~25 cases) — Task A1-A6.
2. `generate-acf.py` produces valid ACF JSON — Task B1.
3. `generate-block-json.py` per block — Task B2.
4. `generate-block-registration.py` AUTO-GENERATED in functions.php — Task B3.
5. `generate-wp-blocks.py` orchestrator + dry-run — Task B5.
6. `gate-check` stage-08 has 8 hard + 2 warning checks — Task C1.
7. `mark-legacy-projects.sh` idempotent — Task C2.
8. `backport-acf-to-legacy.sh` with --dry-run/--force/autobackup — Task C3.
9. SKILL.md honest — Task C5.
10. `deploy-wordpress.sh` no silent fail on `wp acf import` — Task C4.
11. `/landing-deploy` blocked by gate if no legacy:true — implicit through Task C1 (config update).
12. `npm run test:phase-stage-08` green — Step F1.
13. SETUP.md documentation — Task C5.

If any item fails verification, file a follow-up task.

- [ ] **Step F4: Manual E2E (optional, recommended before merge)**

1. `bash scripts/landing-new.sh test-stage08` (or `/landing-new` from agent).
2. Walk stages 01-07 with minimal content (any text under 7 H2 headings in final-copy.md).
3. Run `npm run generate-wp-blocks -- --project Lendings/test-stage08`.
4. Run `bash scripts/gate-check.sh --stage 08_build --project Lendings/test-stage08 --auto` — should pass.
5. Deploy to staging via `/landing-deploy`.
6. Log into WP admin, edit a page, verify "Landing-page blocks" category in inserter with all your blocks.
7. Add a block, verify ACF form in sidebar shows fields with russian labels.

---

## Self-review summary

After writing this plan I checked it against the spec:

**Spec coverage:**
- All 13 acceptance criteria mapped to tasks (see Step F3).
- 8 hard + 2 warning checks covered: checks 1-3 via `config/stage-gates.yaml` `file_exists` type, check 4 via `stage_08_helper.py` JSON parsing, checks 5-7 via `stage_08_helper.py`, check 8 via `stage_08_helper.py`, check 9 → warning in stage_08_helper.py, check 10 → warning in stage_08_helper.py. The full 10-check coverage is achieved through 5 gate entries (3 `file_exists` + `check-block-registration.sh` + `stage_08_helper.py`).
- Legacy bypass implemented in both `check-block-registration.sh` and `stage_08_helper.py`.

**Placeholders scan:** No TBD, no "implement later", no "similar to Task N". Each step has the actual code/command/expected output. Acknowledged constraints (e.g., yq dependency, ACF plugin must exist on server) are documented inline.

**Type consistency check:**
- `ContentParser.parse(md_path: str) -> list[Block]` — used identically across B1, B2, B3, B4, stage_08_helper, backport.
- `Field` dataclass: `name`, `label`, `type`, `default`, `subfields`, `defaults` — consistent throughout.
- `Block` dataclass: `slug`, `title`, `fields`, `source_line` — consistent.
- ACF key naming: `group_lp_<slug>`, `field_lp_<slug>_<name>`, `field_lp_<slug>_<repeater>_<sub>` — consistent in B1.
- Block name pattern: `acf/lp-<slug>` — consistent in B2 (block.json), B1 (acf location), B3 (registration), spec.
- Block category: `lp-blocks` — consistent.
- Markers: `// AUTO-GENERATED START: lp-block-registration` and `// AUTO-GENERATED END` — same exact string in B3 script and tests.
- Backup naming: `.bak` suffix everywhere, `.backport-backup-YYYYMMDD-HHMMSS/` in C3.

Plan saved to `docs/superpowers/plans/2026-05-12-stage-08-acf-gutenberg-plan.md`.

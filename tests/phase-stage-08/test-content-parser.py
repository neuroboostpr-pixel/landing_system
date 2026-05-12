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

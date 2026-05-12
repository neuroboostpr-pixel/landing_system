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

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

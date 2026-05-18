# tests/wiki/test_utils.py
"""Тесты для wiki/utils.py."""
import pytest
from pathlib import Path
from scripts.wiki import utils


def test_slugify_basic():
    assert utils.slugify("Landing Orchestrator") == "landing-orchestrator"


def test_slugify_cyrillic():
    """Кириллица транслитерируется в латиницу для имён файлов."""
    assert utils.slugify("Финальная проверка") == "finalnaya-proverka"


def test_slugify_strip_special_chars():
    assert utils.slugify("Hero/Block: v2.0!") == "hero-block-v2-0"


def test_parse_frontmatter_present():
    """Парсит YAML frontmatter, возвращает (metadata, body)."""
    text = """---
type: agent
name: foo
---
Body text here.
"""
    meta, body = utils.parse_frontmatter(text)
    assert meta == {"type": "agent", "name": "foo"}
    assert body.strip() == "Body text here."


def test_parse_frontmatter_absent():
    """Если frontmatter нет — metadata пустой, body = весь текст."""
    text = "Just body, no frontmatter."
    meta, body = utils.parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_write_with_frontmatter(tmp_path):
    """Пишет файл с frontmatter и body."""
    path = tmp_path / "test.md"
    utils.write_with_frontmatter(
        path,
        metadata={"type": "agent", "name": "foo"},
        body="Body content.",
    )
    content = path.read_text()
    assert content.startswith("---\n")
    assert "type: agent" in content
    assert "Body content." in content


def test_atomic_write(tmp_path):
    """atomic_write не оставляет частичный файл при ошибке."""
    target = tmp_path / "out.md"
    utils.atomic_write(target, "hello")
    assert target.read_text() == "hello"
    # Перезапись
    utils.atomic_write(target, "world")
    assert target.read_text() == "world"

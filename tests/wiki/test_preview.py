"""Тесты генератора preview.html."""
from pathlib import Path

import pytest

from scripts.wiki import preview


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts" / "agents"
    concepts.mkdir(parents=True)
    (concepts / "foo.md").write_text(
        "---\ntype: agent\nname: foo\n---\n# Foo\n\nDoes things."
    )
    (concepts / "bar.md").write_text(
        "---\ntype: agent\nname: bar\n---\n# Bar\n\nOther."
    )
    return wiki


def test_render_produces_html(fake_wiki):
    html_path = preview.render(fake_wiki)
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "foo" in content
    assert "bar" in content


def test_render_groups_by_type(fake_wiki):
    html_path = preview.render(fake_wiki)
    content = html_path.read_text(encoding="utf-8")
    assert "agent" in content.lower()


def test_render_empty_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    html = preview.render(wiki)
    assert html.exists()

"""Tests for scripts.wiki.query — pure Python filter over index.yaml."""
import json
from pathlib import Path

import yaml
import pytest

from scripts.wiki import query


@pytest.fixture
def fake_index(tmp_path) -> Path:
    """Маленький index.yaml для тестов фильтрации."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    concepts_dir = wiki / "concepts" / "agents"
    concepts_dir.mkdir(parents=True)
    (concepts_dir / "block-composer.md").write_text(
        "---\nslug: block-composer\n---\nCard body for block-composer.\n",
        encoding="utf-8",
    )
    (concepts_dir / "frontend-builder.md").write_text(
        "---\nslug: frontend-builder\n---\nCard body for frontend-builder.\n",
        encoding="utf-8",
    )
    data = {
        "version": 1,
        "concepts": [
            {
                "slug": "block-composer", "type": "agent", "stage": "08",
                "name": "block-composer", "tags": ["wp", "gutenberg"],
                "triggers": ["landing-build"],
                "card": "concepts/agents/block-composer.md",
                "source": "agents/block-composer.md",
            },
            {
                "slug": "frontend-builder", "type": "agent", "stage": "08",
                "name": "frontend-builder", "tags": ["wp", "css"],
                "triggers": ["landing-build"],
                "card": "concepts/agents/frontend-builder.md",
                "source": "agents/frontend-builder.md",
            },
            {
                "slug": "seo-optimizer", "type": "agent", "stage": "12",
                "name": "seo-optimizer", "tags": ["seo"],
                "triggers": ["approve-deploy"],
                "card": "concepts/agents/seo-optimizer.md",
                "source": "agents/seo-optimizer.md",
            },
        ],
    }
    (wiki / "index.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    return wiki


def test_filter_by_stage(fake_index):
    result = query.filter_concepts(fake_index, stage="08")
    slugs = [c["slug"] for c in result]
    assert "block-composer" in slugs
    assert "frontend-builder" in slugs
    assert "seo-optimizer" not in slugs


def test_filter_by_type(fake_index):
    result = query.filter_concepts(fake_index, type_="agent")
    assert len(result) == 3


def test_filter_by_tag(fake_index):
    result = query.filter_concepts(fake_index, tag="gutenberg")
    assert len(result) == 1
    assert result[0]["slug"] == "block-composer"


def test_filter_by_trigger(fake_index):
    result = query.filter_concepts(fake_index, trigger="landing-build")
    assert {c["slug"] for c in result} == {"block-composer", "frontend-builder"}


def test_filter_by_slug_returns_single_match(fake_index):
    result = query.filter_concepts(fake_index, slug="block-composer")
    assert len(result) == 1
    assert result[0]["slug"] == "block-composer"


def test_filter_combined(fake_index):
    result = query.filter_concepts(fake_index, stage="08", tag="css")
    assert len(result) == 1
    assert result[0]["slug"] == "frontend-builder"


def test_filter_by_grep(fake_index):
    result = query.filter_concepts(fake_index, grep="seo")
    assert len(result) == 1
    assert result[0]["slug"] == "seo-optimizer"


def test_format_compact_includes_summary(fake_index):
    concepts = query.filter_concepts(fake_index, slug="block-composer")
    text = query.format_output(fake_index, concepts, fmt="compact")
    assert "block-composer" in text
    assert "wp" in text
    assert "concepts/agents/block-composer.md" in text


def test_format_slugs(fake_index):
    concepts = query.filter_concepts(fake_index, stage="08")
    text = query.format_output(fake_index, concepts, fmt="slugs")
    lines = [l for l in text.splitlines() if l.strip()]
    assert set(lines) == {"block-composer", "frontend-builder"}


def test_format_json_parses(fake_index):
    concepts = query.filter_concepts(fake_index, stage="08")
    text = query.format_output(fake_index, concepts, fmt="json")
    parsed = json.loads(text)
    assert len(parsed) == 2


def test_format_cards_reads_card_files(fake_index):
    concepts = query.filter_concepts(fake_index, slug="block-composer")
    text = query.format_output(fake_index, concepts, fmt="cards")
    assert "Card body for block-composer" in text


def test_filter_missing_slug_returns_empty(fake_index):
    result = query.filter_concepts(fake_index, slug="does-not-exist")
    assert result == []

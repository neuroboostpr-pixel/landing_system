"""Tests for new lint rules on index.yaml frontmatter references."""
import yaml
import pytest

from scripts.wiki import lint


def _make_index(tmp_path, concepts: list[dict]) -> dict:
    """Helper: write index.yaml and return parsed data."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    data = {
        "version": 1,
        "concepts": concepts,
    }
    (wiki / "index.yaml").write_text(
        yaml.safe_dump(data, allow_unicode=True), encoding="utf-8"
    )
    return data


def test_check_index_refs_detects_broken_related(tmp_path):
    data = _make_index(tmp_path, [
        {"slug": "a", "type": "agent", "name": "a", "card": "c", "source": "s",
         "related": ["does-not-exist"]},
    ])
    issues = lint.check_index_refs(data)
    assert any("does-not-exist" in i for i in issues["broken_refs"])


def test_check_index_refs_detects_duplicate_slug(tmp_path):
    data = _make_index(tmp_path, [
        {"slug": "dup", "type": "agent", "name": "a", "card": "c", "source": "s"},
        {"slug": "dup", "type": "skill", "name": "b", "card": "d", "source": "t"},
    ])
    issues = lint.check_index_refs(data)
    assert any("dup" in i for i in issues["dup_slugs"])


def test_check_index_refs_detects_missing_stage_for_stage_type(tmp_path):
    data = _make_index(tmp_path, [
        {"slug": "x", "type": "stage", "name": "x", "card": "c", "source": "s"},
    ])
    issues = lint.check_index_refs(data)
    assert any("stage field" in i for i in issues["missing_required"])


def test_check_index_refs_allows_valid_index(tmp_path):
    data = _make_index(tmp_path, [
        {"slug": "a", "type": "agent", "name": "a", "card": "c", "source": "s",
         "related": ["b"]},
        {"slug": "b", "type": "skill", "name": "b", "card": "d", "source": "t"},
    ])
    issues = lint.check_index_refs(data)
    assert all(not v for v in issues.values())


def test_check_index_refs_incomplete_concepts_skipped(tmp_path):
    """Incomplete entries (throttled, deferred) don't trigger missing-field errors."""
    data = _make_index(tmp_path, [
        {"slug": "x", "type": "stage", "name": "x", "card": "c", "source": "s",
         "incomplete": True},
    ])
    issues = lint.check_index_refs(data)
    assert not issues["missing_required"]


def test_check_index_refs_confidence_warns_not_errors(tmp_path):
    data = _make_index(tmp_path, [
        {"slug": "x", "type": "agent", "name": "x", "card": "c", "source": "s",
         "confidence": {"triggers": "low"}},
    ])
    issues = lint.check_index_refs(data)
    assert any("x" in i for i in issues["low_confidence"])
    assert not issues["broken_refs"]
    assert not issues["dup_slugs"]

"""Тесты парсеров project-artifacts."""
from pathlib import Path

import pytest

from scripts.wiki.parsers import (
    state_yaml,
    selections_yaml,
    tokens_json,
    composed_html,
)

FIXTURES = Path(__file__).parent / "fixtures" / "project"


def test_parse_state_yaml_returns_current_stage():
    result = state_yaml.parse(FIXTURES / ".landing-state.yaml")
    assert result["project"] == "test-project"
    assert result["current_stage"] == "07c_composed"  # последний in_progress
    assert "07a_prototype" in result["approved"]
    assert "07b_wireframe" in result["approved"]


def test_parse_state_yaml_all_locked():
    """Если ни одного in_progress — current_stage = первый locked."""
    # фикстура all-locked.yaml
    tmp = FIXTURES / "all-locked.yaml"
    tmp.write_text("""project: x
stages:
  "07a_prototype": {status: locked, timestamp: ""}
  "07b_wireframe": {status: locked, timestamp: ""}
""")
    try:
        result = state_yaml.parse(tmp)
        assert result["current_stage"] == "07a_prototype"
    finally:
        tmp.unlink()


def test_parse_selections_yaml():
    result = selections_yaml.parse(FIXTURES / "selections.yaml")
    assert result["blocks"]["hero"] == "hero-1"
    assert result["blocks"]["features"] == "features-3"


def test_parse_tokens_json():
    result = tokens_json.parse(FIXTURES / "tokens.json")
    assert result["colors"]["primary"] == "#1a1a1a"
    assert result["fonts"]["heading"] == "Playfair Display"


def test_parse_composed_html_extracts_blocks():
    result = composed_html.parse(FIXTURES / "composed.html")
    assert "blocks" in result
    block_names = [b["block_id"] for b in result["blocks"]]
    assert "hero-1" in block_names
    assert "features-3" in block_names


def test_parse_composed_html_extracts_photo_refs():
    result = composed_html.parse(FIXTURES / "composed.html")
    photos = result.get("photo_references", [])
    assert any("hero-bg.jpg" in p for p in photos)

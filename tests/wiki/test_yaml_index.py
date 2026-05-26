"""Tests for _build_yaml_index — deterministic YAML index builder."""
import yaml

from scripts.wiki import system_compiler


def test_build_yaml_index_basic_structure():
    concepts = [
        {
            "slug": "08-kod",
            "type": "stage",
            "stage": "08",
            "name": "Сборка",
            "tags": ["wp"],
            "triggers": ["approve-07b"],
            "card": "concepts/stages/08-kod.md",
            "source": "template/08_КОД/README.md",
        },
        {
            "slug": "block-composer",
            "type": "agent",
            "name": "block-composer",
            "tags": ["html"],
            "card": "concepts/agents/block-composer.md",
            "source": "agents/block-composer.md",
        },
    ]
    text = system_compiler._build_yaml_index(concepts)
    data = yaml.safe_load(text)
    assert data["version"] == 1
    assert data["counts"]["total"] == 2
    assert data["counts"]["by_type"] == {"stage": 1, "agent": 1}
    assert len(data["concepts"]) == 2
    assert data["concepts"][0]["slug"] == "08-kod"


def test_build_yaml_index_sorts_concepts_by_slug():
    concepts = [
        {"slug": "z-last", "type": "agent", "card": "a", "source": "b"},
        {"slug": "a-first", "type": "agent", "card": "a", "source": "b"},
    ]
    data = yaml.safe_load(system_compiler._build_yaml_index(concepts))
    assert [c["slug"] for c in data["concepts"]] == ["a-first", "z-last"]


def test_build_yaml_index_omits_none_fields():
    """Optional fields with None/empty values should not appear in YAML."""
    concepts = [
        {
            "slug": "x",
            "type": "agent",
            "name": "x",
            "card": "c",
            "source": "s",
            "tags": None,
            "triggers": None,
        }
    ]
    data = yaml.safe_load(system_compiler._build_yaml_index(concepts))
    c = data["concepts"][0]
    assert "tags" not in c
    assert "triggers" not in c


def test_build_yaml_index_preserves_confidence_and_incomplete():
    concepts = [
        {
            "slug": "x",
            "type": "stage",
            "stage": "08",
            "card": "c",
            "source": "s",
            "confidence": {"gates": "low"},
            "incomplete": True,
        }
    ]
    data = yaml.safe_load(system_compiler._build_yaml_index(concepts))
    c = data["concepts"][0]
    assert c["confidence"] == {"gates": "low"}
    assert c["incomplete"] is True


def test_build_yaml_index_has_schema_version_constant():
    assert system_compiler.INDEX_SCHEMA_VERSION == 1

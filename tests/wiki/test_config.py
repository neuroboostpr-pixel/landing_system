# tests/wiki/test_config.py
"""Тесты для wiki/config.py — определения путей и source-mode."""
import pytest
from pathlib import Path
from scripts.wiki import config


def test_core_sources_exist():
    assert hasattr(config, "CORE_SOURCES")
    assert isinstance(config.CORE_SOURCES, list)
    assert len(config.CORE_SOURCES) >= 5


def test_core_sources_include_5_categories_plus_catalog():
    paths = {s["path"] for s in config.CORE_SOURCES}
    assert "agents/*.md" in paths
    assert "skills/*/SKILL.md" in paths
    assert "commands/*.md" in paths
    assert "template/*/README.md" in paths
    assert "docs/standards/*.md" in paths
    assert "block-library/README.md" in paths


def test_reference_sources_exist_but_not_used_by_default():
    """REFERENCE_SOURCES определён для будущего, но не входит в CORE."""
    assert hasattr(config, "REFERENCE_SOURCES")
    core_paths = {s["path"] for s in config.CORE_SOURCES}
    ref_paths = {s["path"] for s in config.REFERENCE_SOURCES}
    assert core_paths.isdisjoint(ref_paths)


def test_system_sources_aliased_to_core_for_back_compat():
    """SYSTEM_SOURCES alias = CORE_SOURCES — старый код не ломается."""
    assert config.SYSTEM_SOURCES is config.CORE_SOURCES


def test_source_modes_defined():
    """Должны быть определены три режима: system, project-graph, conversations."""
    assert "system" in config.SOURCE_MODES
    assert "project-graph" in config.SOURCE_MODES
    assert "conversations" in config.SOURCE_MODES


def test_system_sources_list():
    """SYSTEM_SOURCES — список словарей с ключами path, concept_dir."""
    assert isinstance(config.SYSTEM_SOURCES, list)
    assert len(config.SYSTEM_SOURCES) >= 5  # agents, skills, commands, template, standards
    for entry in config.SYSTEM_SOURCES:
        assert "path" in entry
        assert "concept_dir" in entry


def test_system_sources_include_expected_paths():
    """Проверка что в системных источниках есть основные категории."""
    paths = [e["path"] for e in config.SYSTEM_SOURCES]
    assert any("agents" in p for p in paths)
    assert any("skills" in p for p in paths)
    assert any("commands" in p for p in paths)
    assert any("template" in p for p in paths)
    assert any("standards" in p for p in paths)


def test_project_sources_list():
    """PROJECT_SOURCES — список с путями относительно корня проекта."""
    assert isinstance(config.PROJECT_SOURCES, list)
    paths = [e["path"] for e in config.PROJECT_SOURCES]
    assert any(".landing-state.yaml" in p for p in paths)
    assert any("07_ПРОТОТИП" in p for p in paths)
    assert any("04_БРЕНД" in p for p in paths)


def test_repo_root_resolves_to_landing_system():
    """REPO_ROOT — корень landing-system, относительно которого считаются пути."""
    assert isinstance(config.REPO_ROOT, Path)
    assert config.REPO_ROOT.name == "landing-system"
    assert (config.REPO_ROOT / "agents").exists()


def test_wiki_dir_inside_repo():
    """WIKI_DIR — landing-system/wiki/."""
    assert config.WIKI_DIR == config.REPO_ROOT / "wiki"

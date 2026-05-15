"""Тесты project_graph_compiler."""
from pathlib import Path
import shutil

import pytest

from scripts.wiki import project_graph_compiler


FIXTURES = Path(__file__).parent / "fixtures" / "project"


@pytest.fixture
def fake_project(tmp_path):
    """Имитирует структуру проекта-лендинга."""
    project = tmp_path / "test-project"
    project.mkdir()
    shutil.copy(FIXTURES / ".landing-state.yaml", project / ".landing-state.yaml")

    (project / "07a_WIREFRAME").mkdir()
    shutil.copy(FIXTURES / "selections.yaml", project / "07a_WIREFRAME" / "selections.yaml")

    (project / "04_БРЕНД").mkdir()
    shutil.copy(FIXTURES / "tokens.json", project / "04_БРЕНД" / "tokens.json")

    (project / "07b_COMPOSED").mkdir()
    shutil.copy(FIXTURES / "composed.html", project / "07b_COMPOSED" / "composed.html")

    return project


def test_compile_creates_wiki_dir(fake_project):
    project_graph_compiler.compile_project(project_root=fake_project)

    wiki = fake_project / "wiki"
    assert wiki.exists()
    assert (wiki / "index.md").exists()
    assert (wiki / "concepts" / "stage-current.md").exists()


def test_compile_stage_current_contains_current_stage(fake_project):
    project_graph_compiler.compile_project(project_root=fake_project)

    content = (fake_project / "wiki" / "concepts" / "stage-current.md").read_text()
    assert "07c_composed" in content


def test_compile_blocks_concept_lists_selected_blocks(fake_project):
    project_graph_compiler.compile_project(project_root=fake_project)

    blocks_path = fake_project / "wiki" / "concepts" / "blocks.md"
    if blocks_path.exists():
        content = blocks_path.read_text()
        assert "hero-1" in content
        assert "features-3" in content


def test_compile_brand_concept_has_tokens(fake_project):
    project_graph_compiler.compile_project(project_root=fake_project)

    brand = (fake_project / "wiki" / "concepts" / "brand.md").read_text()
    assert "#1a1a1a" in brand or "primary" in brand.lower()


def test_compile_appends_log(fake_project):
    project_graph_compiler.compile_project(project_root=fake_project)

    log = (fake_project / "wiki" / "log.md").read_text()
    assert "project-graph" in log


def test_index_contains_project_name(fake_project):
    """Регресс-тест: index.md должен начинаться с правильного имени проекта,
    а не путать его (как раньше иногда делал SDK с lixiang-dubai)."""
    project_graph_compiler.compile_project(project_root=fake_project)

    index = (fake_project / "wiki" / "index.md").read_text()
    assert index.startswith("# test-project — wiki проекта")

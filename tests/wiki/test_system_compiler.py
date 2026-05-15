"""Тесты system_compiler с моком SDK."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts.wiki import system_compiler


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fake_repo(tmp_path):
    """Имитирует структуру landing-system минимально."""
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents" / "sample-agent.md").write_text(
        (FIXTURES / "agents" / "sample-agent.md").read_text()
    )
    return tmp_path


def test_compile_creates_wiki_dir(fake_repo, tmp_path, mocker):
    """compile_system создаёт wiki/concepts/agents/."""
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\nname: sample-agent\n---\nBody.",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="# Index\n- [[agent-sample-agent]]",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )

    concept = wiki / "concepts" / "agents" / "sample-agent.md"
    assert concept.exists()
    assert "type: agent" in concept.read_text()


def test_compile_creates_index(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nbody",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="# Landing-System Wiki\nIndex content",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    assert (wiki / "index.md").exists()
    assert "Landing-System Wiki" in (wiki / "index.md").read_text()


def test_compile_appends_log(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nb",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    log_text = (wiki / "log.md").read_text()
    assert "compile" in log_text.lower()
    assert "sample-agent" in log_text


def test_compile_skips_unchanged(fake_repo, tmp_path, mocker):
    """При повторном прогоне неизменённые файлы не зовут SDK."""
    wiki = tmp_path / "wiki"
    generate_mock = mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nbody",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    # Первый прогон — генерация
    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    first_call_count = generate_mock.call_count

    # Второй прогон без изменений — SDK не должен зваться для концептов
    # (зовётся только index — то есть на 1 больше, если файл не менялся; для агентов 0)
    generate_mock.reset_mock()
    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources
    )
    # _build_index замокан отдельно → sdk_client.generate не зовётся вообще
    assert generate_mock.call_count == 0


def test_dry_run_does_not_write(fake_repo, tmp_path, mocker):
    wiki = tmp_path / "wiki"
    mocker.patch(
        "scripts.wiki.system_compiler.sdk_client.generate",
        return_value="---\ntype: agent\n---\nb",
    )
    mocker.patch(
        "scripts.wiki.system_compiler._build_index",
        return_value="idx",
    )
    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    system_compiler.compile_system(
        repo_root=fake_repo, wiki_dir=wiki, sources=sources, dry_run=True
    )
    assert not (wiki / "concepts" / "agents" / "sample-agent.md").exists()
    assert not (wiki / "index.md").exists()

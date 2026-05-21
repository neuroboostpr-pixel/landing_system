"""Тесты system_compiler с моком SDK."""
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_cache_saved_once_per_compile_run(tmp_path: Path) -> None:
    """save_cache должен вызываться один раз за прогон, а не в цикле.

    Эта регрессия ловит то что описано в audit/01-scripts-wiki-python.md:
    раньше save_cache(...) звался ВНУТРИ цикла → O(N²) IO для 473 концептов.
    """
    repo_root = tmp_path / "repo"
    wiki_dir = tmp_path / "wiki"
    (repo_root / "agents").mkdir(parents=True)
    (repo_root / "agents" / "a.md").write_text("---\nname: a\n---\nA", encoding="utf-8")
    (repo_root / "agents" / "b.md").write_text("---\nname: b\n---\nB", encoding="utf-8")
    (repo_root / "agents" / "c.md").write_text("---\nname: c\n---\nC", encoding="utf-8")

    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    with patch("scripts.wiki.hash_cache.save_cache") as mock_save, \
         patch("scripts.wiki.system_compiler._compile_concept", return_value="---\nname: x\n---\nX"):
        system_compiler.compile_system(
            repo_root=repo_root,
            wiki_dir=wiki_dir,
            sources=sources,
            dry_run=False,
        )

    # Bootstrap pre-population + финальный save = максимум 2 вызова.
    # Если save_cache внутри цикла — будет ≥3 (по числу файлов).
    assert mock_save.call_count <= 2, (
        f"save_cache called {mock_save.call_count} times — should be ≤2 "
        "(once for bootstrap pre-pop, once at end). Per-file save = O(N²) IO."
    )


def test_failed_sdk_call_still_caches_source_hash(tmp_path: Path) -> None:
    """Если _compile_concept падает SDK-ошибкой — hash источника ВСЁ РАВНО
    должен попасть в кэш, чтобы на следующем коммите этот файл не звал SDK снова.

    Audit finding: system_compiler.py:179-183 — error logged but hash never
    cached → defeats hash-cache purpose for chronically-broken files.
    """
    from scripts.wiki import hash_cache, sdk_client

    repo_root = tmp_path / "repo"
    wiki_dir = tmp_path / "wiki"
    (repo_root / "agents").mkdir(parents=True)
    src = repo_root / "agents" / "broken.md"
    src.write_text("---\nname: broken\n---\nX", encoding="utf-8")

    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    with patch("scripts.wiki.system_compiler._compile_concept",
               side_effect=sdk_client.SDKError("simulated")):
        system_compiler.compile_system(
            repo_root=repo_root, wiki_dir=wiki_dir,
            sources=sources, dry_run=False,
        )

    cache = hash_cache.load_cache(wiki_dir / ".cache.json")
    assert "agents/broken.md" in cache, (
        "Source hash not cached after SDK error — file will re-call SDK "
        "on every subsequent commit (token leak)."
    )
    assert cache["agents/broken.md"] == hash_cache.compute_hash(src)

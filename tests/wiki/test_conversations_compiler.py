"""Тесты conversations_compiler."""
from pathlib import Path

import pytest

from scripts.wiki import conversations_compiler


@pytest.fixture
def fake_memory(tmp_path):
    daily = tmp_path / "daily"
    daily.mkdir()
    (daily / "2026-05-15.md").write_text(
        "- **[решение]** Цены берём у конкурентов\n"
        "- **[урок]** verify-composed падает без processed/"
    )
    (daily / "2026-05-14.md").write_text(
        "- **[грабли]** Bootstrap падал без pythonpath\n"
    )
    return tmp_path


def test_compile_creates_compiled_dir(fake_memory, mocker):
    mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value=(
            "---\ntype: conversation-concept\nname: prices-from-competitors\n---\n"
            "# Цены\n\nРешили брать у конкурентов.\n"
        ),
    )
    conversations_compiler.compile_conversations(memory_root=fake_memory)
    assert (fake_memory / "compiled" / "concepts").exists()


def test_compile_writes_concept_files(fake_memory, mocker):
    sdk_output = (
        "---\ntype: conversation-concept\nname: prices\n---\n# Цены\n\nA\n"
        "---END---\n"
        "---\ntype: conversation-concept\nname: bootstrap-fix\n---\n# Bootstrap\n\nB\n"
    )
    mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value=sdk_output,
    )
    conversations_compiler.compile_conversations(memory_root=fake_memory)
    concepts = list((fake_memory / "compiled" / "concepts").glob("*.md"))
    assert len(concepts) == 2
    names = {c.stem for c in concepts}
    assert "prices" in names
    assert "bootstrap-fix" in names


def test_compile_handles_empty_dailies(tmp_path, mocker):
    """Если daily/ пустая — ничего не пишем."""
    (tmp_path / "daily").mkdir()
    gen = mocker.patch(
        "scripts.wiki.conversations_compiler.sdk_client.generate",
        return_value="x",
    )
    conversations_compiler.compile_conversations(memory_root=tmp_path)
    gen.assert_not_called()

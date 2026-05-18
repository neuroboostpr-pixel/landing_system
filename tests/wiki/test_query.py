"""Тесты query (с моком SDK)."""
from pathlib import Path

import pytest

from scripts.wiki import query


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts"
    concepts.mkdir(parents=True)
    (wiki / "index.md").write_text("# Index\n- [[landing-orchestrator]]")
    (concepts / "landing-orchestrator.md").write_text(
        "---\ntype: agent\n---\n# Orchestrator\n\nГлавный дирижёр pipeline."
    )
    return wiki


def test_query_returns_answer(fake_wiki, mocker):
    mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="Это главный агент.\n\nИсточники: [[landing-orchestrator]]",
    )
    result = query.ask(wiki_dirs=[fake_wiki], question="Что такое landing-orchestrator?")
    assert "главный" in result.lower()


def test_query_returns_no_match(fake_wiki, mocker):
    mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="не нашёл, попробуй задать вопрос конкретнее",
    )
    result = query.ask(wiki_dirs=[fake_wiki], question="Что-то совсем не из wiki?")
    assert "не нашёл" in result.lower()


def test_query_combines_multiple_wikis(fake_wiki, mocker):
    """ask() принимает список wiki_dirs и складывает их индексы."""
    other = fake_wiki.parent / "other_wiki"
    other.mkdir()
    (other / "index.md").write_text("# Other\n- [[different-concept]]")
    gen = mocker.patch(
        "scripts.wiki.query.sdk_client.generate",
        return_value="answer",
    )
    query.ask(wiki_dirs=[fake_wiki, other], question="?")
    user_msg = gen.call_args.kwargs["user"]
    assert "different-concept" in user_msg

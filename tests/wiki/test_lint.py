"""Тесты lint — 6 структурных проверок (LLM-проверка тестируется отдельно)."""
from pathlib import Path

import pytest

from scripts.wiki import lint


@pytest.fixture
def fake_wiki(tmp_path):
    wiki = tmp_path / "wiki"
    concepts = wiki / "concepts"
    concepts.mkdir(parents=True)
    return wiki


def test_no_issues_in_empty_wiki(fake_wiki):
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert result["broken_links"] == []
    assert result["orphans"] == []


def test_detects_broken_link(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text(
        "---\ntype: x\n---\n# A\nСсылка на [[non-existent]]"
    )
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("non-existent" in issue for issue in result["broken_links"])


def test_detects_orphan(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text("---\ntype: x\n---\n# A")
    (fake_wiki / "concepts" / "b.md").write_text("---\ntype: x\n---\n# B\n[[a]]")
    # 'a' ссылается из b, не сирота. 'b' — ни на кого нет ссылок → сирота.
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("b" in o for o in result["orphans"])
    assert not any(o == "a" or o.endswith("/a") for o in result["orphans"])


def test_detects_empty_concept(fake_wiki):
    (fake_wiki / "concepts" / "tiny.md").write_text("---\ntype: x\n---\n# Tiny\n\nshort")
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("tiny" in s for s in result["empty"])


def test_detects_missing_backlink(fake_wiki):
    (fake_wiki / "concepts" / "a.md").write_text(
        "---\ntype: x\n---\n# A\n[[b]]"
    )
    (fake_wiki / "concepts" / "b.md").write_text(
        "---\ntype: x\n---\n# B\nНет ссылки на a"
    )
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert any("a" in pair and "b" in pair for pair in result["missing_backlinks"])


def test_exit_code_zero_on_clean(fake_wiki):
    """Если нет issues — exit 0."""
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert lint.compute_exit_code(result) == 0


def test_exit_code_nonzero_on_issues(fake_wiki):
    """Critical issues (broken_refs, dup_slugs) cause exit 1; warn-only (empty, orphans) do not."""
    # Warn-only: a tiny concept only produces 'empty' — exit code should be 0.
    (fake_wiki / "concepts" / "tiny.md").write_text("---\ntype: x\n---\n# T")
    result = lint.run_checks(fake_wiki, llm_check=False)
    assert lint.compute_exit_code(result) == 0  # empty is warn-only

    # Critical: inject a broken_ref issue → exit 1.
    result_critical = dict(result)
    result_critical["broken_refs"] = ["some-slug.related → missing-target"]
    assert lint.compute_exit_code(result_critical) != 0

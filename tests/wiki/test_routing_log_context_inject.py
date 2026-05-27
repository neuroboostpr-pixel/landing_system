"""Tests for log_context_inject() in scripts/wiki/routing_log.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def log_path(tmp_path):
    return tmp_path / "logs" / "wiki-usage.jsonl"


@pytest.fixture(autouse=True)
def patch_log_path(log_path, monkeypatch):
    """Перенаправляем LOG_PATH в tmp."""
    import scripts.wiki.routing_log as rl
    monkeypatch.setattr(rl, "LOG_PATH", log_path)


def test_log_context_inject_writes_jsonl(log_path):
    from scripts.wiki.routing_log import log_context_inject

    log_context_inject(
        session_id="sess-123",
        source_category="session_start",
        source_label="project_wiki",
        est_tokens=314,
        can_be_wiki=False,
        path="lixiang-dubai3/wiki/index.md",
        model="claude-sonnet-4-6",
    )

    lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "context_inject"
    assert record["source_category"] == "session_start"
    assert record["source_label"] == "project_wiki"
    assert record["est_tokens"] == 314
    assert record["can_be_wiki"] is False
    assert record["path"] == "lixiang-dubai3/wiki/index.md"
    assert record["model"] == "claude-sonnet-4-6"
    assert record["session_id"] == "sess-123"
    assert "ts" in record


def test_log_context_inject_can_be_wiki_true(log_path):
    from scripts.wiki.routing_log import log_context_inject

    log_context_inject(
        session_id="s1",
        source_category="direct_read",
        source_label="agents/niche-analyst.md",
        est_tokens=800,
        can_be_wiki=True,
    )

    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["can_be_wiki"] is True
    assert record["source_category"] == "direct_read"


def test_log_context_inject_optional_fields_default(log_path):
    from scripts.wiki.routing_log import log_context_inject

    log_context_inject(
        session_id="s1",
        source_category="bash_stdout",
        source_label="gate-check.sh",
        est_tokens=500,
    )

    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["path"] == ""
    assert record["model"] == ""
    assert record["can_be_wiki"] is False

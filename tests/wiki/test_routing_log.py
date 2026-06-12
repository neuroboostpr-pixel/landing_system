"""Tests for scripts/wiki/routing_log.py."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
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


def test_log_query_writes_jsonl(log_path):
    from scripts.wiki.routing_log import log_query
    log_query("sess1", {"stage": "08", "type": "agent"}, ["wp-builder"], 4200)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "wiki_query"
    assert record["session_id"] == "sess1"
    assert record["hits"] == ["wp-builder"]
    assert record["hits_count"] == 1
    assert record["est_tokens_saved"] == 4200
    assert "ts" in record


def test_log_direct_read_writes_jsonl(log_path):
    from scripts.wiki.routing_log import log_direct_read
    log_direct_read("sess1", "agents/wp-builder.md", 3200, had_prior_query=True)
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["type"] == "direct_read"
    assert record["path"] == "agents/wp-builder.md"
    assert record["est_tokens"] == 3200
    assert record["had_prior_query"] is True


def test_read_events_filters_by_days(log_path, monkeypatch):
    from scripts.wiki import routing_log as rl
    log_path.parent.mkdir(parents=True, exist_ok=True)
    old_ts = (datetime.now() - timedelta(days=10)).isoformat(timespec="seconds")
    recent_ts = datetime.now().isoformat(timespec="seconds")
    with log_path.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"ts": old_ts, "type": "wiki_query", "session_id": "old"}) + "\n")
        f.write(json.dumps({"ts": recent_ts, "type": "wiki_query", "session_id": "new"}) + "\n")
    events = rl.read_events(since_days=7)
    assert len(events) == 1
    assert events[0]["session_id"] == "new"


def test_oserror_does_not_raise(log_path, monkeypatch):
    import scripts.wiki.routing_log as rl
    def broken_open(*a, **kw):
        raise OSError("disk full")
    monkeypatch.setattr(rl, "_open_log", broken_open)
    # Не должно бросать исключение
    rl.log_query("s", {}, [], 0)


def test_estimate_tokens_file(tmp_path):
    from scripts.wiki.routing_log import estimate_tokens_file
    f = tmp_path / "test.md"
    f.write_bytes(b"x" * 400)
    assert estimate_tokens_file(f) == 114  # int(400 / 3.5) = 114 for ASCII text

    missing = tmp_path / "missing.md"
    assert estimate_tokens_file(missing) == 0

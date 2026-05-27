"""Tests for stage/agent/skill launch tracking with via_wiki correlation."""
from __future__ import annotations

import json
from pathlib import Path
import pytest

from scripts.wiki import routing_log


@pytest.fixture(autouse=True)
def tmp_log(tmp_path, monkeypatch):
    log_file = tmp_path / "wiki-usage.jsonl"
    monkeypatch.setattr(routing_log, "LOG_PATH", log_file)
    return log_file


def _write_query(tmp_log: Path, session_id: str, stage: str) -> None:
    record = {
        "ts": "2026-05-27T10:00:00",
        "type": "wiki_query",
        "session_id": session_id,
        "filters": {"stage": stage, "type": "agent"},
        "hits": [],
        "hits_count": 0,
        "est_tokens_saved": 0,
    }
    with tmp_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def test_was_wiki_queried_true(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    assert routing_log.was_wiki_queried("sess1", "04") is True


def test_was_wiki_queried_false_no_query(tmp_log):
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_false_wrong_stage(tmp_log):
    _write_query(tmp_log, "sess1", "03")
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_false_wrong_session(tmp_log):
    _write_query(tmp_log, "sess2", "04")
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_stage_prefix_match(tmp_log):
    # "04_brand" stage query should match was_wiki_queried("sess1", "04")
    _write_query(tmp_log, "sess1", "04_brand")
    assert routing_log.was_wiki_queried("sess1", "04") is True


def test_log_stage_start_via_wiki_true(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    routing_log.log_stage_start("sess1", "04_brand", "lixiang-dubai3")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    stage_events = [e for e in events if e["type"] == "stage_start"]
    assert len(stage_events) == 1
    assert stage_events[0]["via_wiki"] is True
    assert stage_events[0]["stage"] == "04_brand"
    assert stage_events[0]["project"] == "lixiang-dubai3"


def test_log_stage_start_via_wiki_false(tmp_log):
    routing_log.log_stage_start("sess1", "04_brand", "lixiang-dubai3")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    stage_events = [e for e in events if e["type"] == "stage_start"]
    assert stage_events[0]["via_wiki"] is False


def test_log_agent_call_writes_record(tmp_log):
    _write_query(tmp_log, "sess1", "04")
    routing_log.log_agent_call("sess1", "brand-architect", "04")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    agent_events = [e for e in events if e["type"] == "agent_call"]
    assert len(agent_events) == 1
    assert agent_events[0]["agent"] == "brand-architect"
    assert agent_events[0]["via_wiki"] is True


def test_log_skill_call_writes_record(tmp_log):
    routing_log.log_skill_call("sess1", "landing-brand", "04")
    events = [json.loads(l) for l in tmp_log.read_text().splitlines() if l.strip()]
    skill_events = [e for e in events if e["type"] == "skill_call"]
    assert len(skill_events) == 1
    assert skill_events[0]["skill"] == "landing-brand"
    assert skill_events[0]["via_wiki"] is False


def test_was_wiki_queried_missing_filters_field(tmp_log):
    """wiki_query без поля filters не крашит и не даёт false-positive."""
    record = {
        "ts": "2026-05-27T10:00:00",
        "type": "wiki_query",
        "session_id": "sess1",
        "hits": [],
    }
    with tmp_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    assert routing_log.was_wiki_queried("sess1", "04") is False


def test_was_wiki_queried_invalid_json_in_log(tmp_log):
    """Битые строки в логе пропускаются."""
    with tmp_log.open("a", encoding="utf-8") as f:
        f.write("not-json\n")
    _write_query(tmp_log, "sess1", "04")
    assert routing_log.was_wiki_queried("sess1", "04") is True


def test_was_wiki_queried_empty_stage_returns_false(tmp_log):
    """Пустой stage аргумент всегда возвращает False."""
    _write_query(tmp_log, "sess1", "")
    assert routing_log.was_wiki_queried("sess1", "") is False


import subprocess
import sys


def test_cli_log_agent_call(tmp_path):
    """CLI вызов пишет agent_call в лог."""
    log_file = tmp_path / "wiki-usage.jsonl"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.wiki.log",
         "--type", "agent_call",
         "--agent", "test-agent",
         "--stage", "04",
         "--session-id", "test-sess"],
        capture_output=True, text=True,
        cwd="d:/AI_TEAMS/landing_system",
        env={**__import__("os").environ, "WIKI_LOG_PATH": str(log_file)},
    )
    assert result.returncode == 0


def test_cli_log_stage_start(tmp_path):
    """CLI вызов stage_start возвращает 0."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.wiki.log",
         "--type", "stage_start",
         "--stage", "04_brand",
         "--project", "test-project",
         "--session-id", "test-sess"],
        capture_output=True, text=True,
        cwd="d:/AI_TEAMS/landing_system",
    )
    assert result.returncode == 0


def test_cli_missing_required_arg():
    """CLI без --type возвращает ненулевой код."""
    result = subprocess.run(
        [sys.executable, "-m", "scripts.wiki.log", "--agent", "x"],
        capture_output=True, text=True,
        cwd="d:/AI_TEAMS/landing_system",
    )
    assert result.returncode != 0

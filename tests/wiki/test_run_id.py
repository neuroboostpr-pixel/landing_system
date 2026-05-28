from __future__ import annotations
import pytest
from pathlib import Path


@pytest.fixture
def run_id_path(tmp_path, monkeypatch):
    p = tmp_path / ".wiki-run-id"
    import scripts.wiki.run_id as rid
    monkeypatch.setattr(rid, "RUN_ID_PATH", p)
    return p


def test_get_returns_none_if_no_file(run_id_path):
    from scripts.wiki.run_id import get
    assert get() is None


def test_get_or_create_creates_file(run_id_path):
    from scripts.wiki.run_id import get_or_create
    result = get_or_create()
    assert run_id_path.exists()
    assert result.startswith("landing-")


def test_get_or_create_returns_same_id_on_second_call(run_id_path):
    from scripts.wiki.run_id import get_or_create
    first = get_or_create()
    second = get_or_create()
    assert first == second


def test_get_reads_existing_file(run_id_path):
    from scripts.wiki.run_id import get
    run_id_path.write_text("landing-20260528-1721", encoding="utf-8")
    assert get() == "landing-20260528-1721"


def test_reset_generates_new_id(run_id_path):
    from scripts.wiki.run_id import get_or_create, reset
    from unittest.mock import patch
    from datetime import datetime, timedelta

    first = get_or_create()

    # Mock _generate to simulate time passing
    with patch('scripts.wiki.run_id._generate') as mock_gen:
        future_time = (datetime.now() + timedelta(minutes=1)).strftime("%Y%m%d-%H%M")
        mock_gen.return_value = f"landing-{future_time}"
        second = reset()

    assert second != first
    assert run_id_path.read_text(encoding="utf-8") == second


def test_run_id_format(run_id_path):
    from scripts.wiki.run_id import get_or_create
    result = get_or_create()
    import re
    assert re.match(r"landing-\d{8}-\d{4}", result), f"Bad format: {result}"


def test_log_py_uses_run_id_when_no_session_id(tmp_path, monkeypatch):
    """log.py берёт session_id из .wiki-run-id если --session-id не передан."""
    import scripts.wiki.run_id as rid
    import scripts.wiki.routing_log as rl

    run_id_file = tmp_path / ".wiki-run-id"
    run_id_file.write_text("landing-20260528-1721", encoding="utf-8")
    monkeypatch.setattr(rid, "RUN_ID_PATH", run_id_file)

    log_path = tmp_path / "logs" / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log_path)
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

    import scripts.wiki.log as log_mod
    log_mod.main(["log.py", "--type", "agent_call", "--agent", "brand-architect", "--stage", "04"])

    import json
    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["session_id"] == "landing-20260528-1721"


def test_log_py_creates_run_id_when_no_file(tmp_path, monkeypatch):
    """log.py auto-creates run_id if .wiki-run-id doesn't exist."""
    import scripts.wiki.run_id as rid
    import scripts.wiki.routing_log as rl

    run_id_file = tmp_path / ".wiki-run-id"
    monkeypatch.setattr(rid, "RUN_ID_PATH", run_id_file)

    log_path = tmp_path / "logs" / "wiki-usage.jsonl"
    monkeypatch.setattr(rl, "LOG_PATH", log_path)
    monkeypatch.delenv("CLAUDE_SESSION_ID", raising=False)

    import scripts.wiki.log as log_mod
    log_mod.main(["log.py", "--type", "agent_call", "--agent", "brand-architect", "--stage", "04"])

    import json
    record = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert record["session_id"].startswith("landing-")
    assert run_id_file.exists()

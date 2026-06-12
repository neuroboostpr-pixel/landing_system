"""Tests for scripts/wiki/preflight.py."""
from __future__ import annotations

import pytest


def test_check_disk_space_ok():
    from scripts.wiki.preflight import check_disk_space
    result = check_disk_space(min_mb=1)
    assert result.ok is True
    assert result.name == "disk_space"


def test_check_logs_dir_writable_missing_dir(tmp_path, monkeypatch):
    from scripts.wiki import preflight, routing_log
    missing = tmp_path / "nonexistent_logs"
    monkeypatch.setattr(routing_log, "LOG_PATH", missing / "wiki-usage.jsonl")
    result = preflight.check_logs_dir_writable()
    # Папка не существует но может быть создана — должно быть ok
    assert result.ok is True


def test_check_index_yaml_missing(tmp_path, monkeypatch):
    from scripts.wiki import preflight, config
    monkeypatch.setattr(config, "WIKI_DIR", tmp_path / "wiki")
    result = preflight.check_index_yaml_exists()
    assert result.ok is False
    assert "index.yaml" in result.message
    assert "compile" in result.fix_hint


def test_run_preflight_returns_all_results():
    from scripts.wiki.preflight import run_preflight, CheckResult
    results = run_preflight()
    assert isinstance(results, list)
    assert all(isinstance(r, CheckResult) for r in results)
    assert len(results) == 4  # disk_space, logs_writable, index_exists, index_parseable
    # run_preflight никогда не бросает исключений

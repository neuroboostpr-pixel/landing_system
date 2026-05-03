"""Tests for tools.env."""
import os
from pathlib import Path
import pytest
from tools.env import load_env, get_required, get_optional


def test_load_env_reads_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n# comment\n")
    monkeypatch.delenv("FOO", raising=False)
    load_env(str(env_file))
    assert os.environ["FOO"] == "bar"
    assert os.environ["BAZ"] == "qux"


def test_load_env_skips_comments_and_empty(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# header\n\nFOO=bar\n")
    load_env(str(env_file))
    assert os.environ["FOO"] == "bar"


def test_get_required_raises_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_KEY", raising=False)
    with pytest.raises(KeyError) as exc:
        get_required("MISSING_KEY")
    assert "MISSING_KEY" in str(exc.value)


def test_get_required_returns_value(monkeypatch):
    monkeypatch.setenv("PRESENT_KEY", "value")
    assert get_required("PRESENT_KEY") == "value"


def test_get_optional_returns_default(monkeypatch):
    monkeypatch.delenv("OPT_KEY", raising=False)
    assert get_optional("OPT_KEY", "default") == "default"

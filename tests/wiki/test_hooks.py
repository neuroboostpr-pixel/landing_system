"""Smoke-тесты хуков — что они принимают пустой stdin и не падают."""
import json
import subprocess
import sys
from pathlib import Path


HOOKS = Path(__file__).resolve().parents[2] / "scripts" / "wiki" / "hooks"


def test_session_start_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="{}",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


def test_session_start_invalid_json():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input="not json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0  # не падает на мусоре


def test_session_end_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_end.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_pre_compact_empty_stdin():
    result = subprocess.run(
        [sys.executable, str(HOOKS / "pre_compact.py")],
        input="{}",
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0


def test_session_start_injects_landing_system_index(tmp_path, monkeypatch):
    """Когда cwd = landing-system/, в выводе должен быть system_wiki_index."""
    # Имитация: указываем cwd как landing-system
    repo = Path(__file__).resolve().parents[2]
    payload = {"cwd": str(repo)}
    result = subprocess.run(
        [sys.executable, str(HOOKS / "session_start.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Если wiki/index.md есть — должен быть упомянут
    if (repo / "wiki" / "index.md").exists():
        assert "system_wiki_index" in result.stdout

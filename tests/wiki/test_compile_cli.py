# tests/wiki/test_compile_cli.py
"""Тесты для CLI compile.py."""
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def run_compile(*args):
    """Запускает compile.py как подпроцесс."""
    return subprocess.run(
        [sys.executable, "-m", "scripts.wiki.compile", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_help_shows_source_mode():
    """`--help` показывает флаг --source-mode со всеми тремя режимами."""
    result = run_compile("--help")
    assert result.returncode == 0
    assert "--source-mode" in result.stdout
    assert "system" in result.stdout
    assert "project-graph" in result.stdout
    assert "conversations" in result.stdout


def test_requires_source_mode():
    """Без --source-mode CLI падает с понятной ошибкой."""
    result = run_compile()
    assert result.returncode != 0
    assert "source-mode" in (result.stderr + result.stdout).lower()


def test_invalid_source_mode():
    """Невалидный --source-mode → exit с ошибкой."""
    result = run_compile("--source-mode=invalid")
    assert result.returncode != 0


def test_system_mode_not_yet_implemented():
    """system mode принимается, но в PR-F.1 говорит что не реализован."""
    result = run_compile("--source-mode=system", "--dry-run")
    # В PR-F.1 — печатает stub, exit 0
    assert result.returncode == 0
    assert "not implemented" in (result.stdout + result.stderr).lower() or \
           "PR-F.2" in (result.stdout + result.stderr)


def test_project_graph_requires_project():
    """project-graph без --project → ошибка."""
    result = run_compile("--source-mode=project-graph")
    assert result.returncode != 0
    assert "project" in (result.stdout + result.stderr).lower()

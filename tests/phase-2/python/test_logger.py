"""Tests for tools.logger."""
import sys
from io import StringIO
from tools.logger import info, warn, error, success


def test_info_writes_to_stderr_with_prefix(capsys):
    info("hello")
    captured = capsys.readouterr()
    assert "hello" in captured.err
    assert "ℹ" in captured.err or "[info]" in captured.err


def test_warn_writes_to_stderr(capsys):
    warn("danger")
    captured = capsys.readouterr()
    assert "danger" in captured.err
    assert "⚠" in captured.err or "[warn]" in captured.err


def test_error_writes_to_stderr(capsys):
    error("broken")
    captured = capsys.readouterr()
    assert "broken" in captured.err
    assert "❌" in captured.err or "[error]" in captured.err


def test_success_writes_to_stderr(capsys):
    success("done")
    captured = capsys.readouterr()
    assert "done" in captured.err
    assert "✅" in captured.err or "[ok]" in captured.err

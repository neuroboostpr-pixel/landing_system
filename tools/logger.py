"""Stderr-only structured logging for CLI scripts.

stdout is reserved for machine output (paths, JSON, etc).
stderr carries human-facing progress.
"""
import sys


def _write(prefix: str, msg: str) -> None:
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def info(msg: str) -> None:
    _write("ℹ", msg)


def warn(msg: str) -> None:
    _write("⚠", msg)


def error(msg: str) -> None:
    _write("❌", msg)


def success(msg: str) -> None:
    _write("✅", msg)

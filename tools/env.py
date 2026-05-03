"""Lightweight .env loader.

Avoids the python-dotenv dep — landing-system .env files are simple
KEY=VALUE pairs with optional comments. We don't need full POSIX shell
semantics.
"""
import os
from pathlib import Path
from typing import Optional


def load_env(path: str) -> None:
    """Load KEY=VALUE pairs from a file into os.environ.

    Lines starting with '#' or empty lines are skipped.
    Quotes around values are stripped.
    Existing env vars are NOT overwritten (.env is fallback, not override).
    """
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_required(key: str) -> str:
    """Return env var or raise KeyError with a friendly message."""
    if key not in os.environ or not os.environ[key]:
        raise KeyError(
            f"Required env var '{key}' not set. "
            f"Add it to .env.local or project .env. "
            f"See spec section 19 for how to obtain it."
        )
    return os.environ[key]


def get_optional(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return env var or default."""
    return os.environ.get(key, default)

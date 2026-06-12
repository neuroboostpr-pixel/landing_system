"""Shared pytest fixtures + sys.path setup."""
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def good_html():
    return (FIXTURES / "good-site.html").read_text(encoding="utf-8")


@pytest.fixture
def bad_html():
    return (FIXTURES / "bad-site.html").read_text(encoding="utf-8")

"""Tests for composed_inspector.py — DOM probe matching."""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

spec = importlib.util.spec_from_file_location("composed_inspector", LIB / "composed_inspector.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
inspect = mod.inspect

FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def test_minimal_probe_matches_one_nav():
    blocks = inspect(FIX / "minimal-composed.html", probes=[".nav"])
    assert len(blocks) == 1
    assert blocks[0].probe_selector == ".nav"
    assert len(blocks[0].matches) == 1


def test_minimal_probe_no_match_returns_zero_matches():
    blocks = inspect(FIX / "minimal-composed.html", probes=[".nonexistent"])
    assert len(blocks) == 1
    assert len(blocks[0].matches) == 0

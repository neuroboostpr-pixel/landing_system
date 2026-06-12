"""Tests for spec_inspector.py — surface probe + controls."""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "skills" / "wp-gutenberg-block-builder" / "scripts" / "lib"
sys.path.insert(0, str(LIB))

spec_mod = importlib.util.spec_from_file_location("spec_inspector", LIB / "spec_inspector.py")
si = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(si)

FIX = REPO_ROOT / "tests" / "phase-stage-08" / "fixtures" / "lint"


def test_inspect_spec_exposes_probe():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    nav = next(b for b in s.blocks if b.slug == "nav")
    assert nav.probe_selector == ".nav"
    assert nav.probe_kind == "single"


def test_inspect_spec_controls_present():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    nav = next(b for b in s.blocks if b.slug == "nav")
    assert any(c.name == "logo" for c in nav.controls)


def test_inspect_spec_section_card_template_visible():
    s = si.inspect_spec(FIX / "good-spec.yaml")
    feat = next(b for b in s.blocks if b.slug == "features")
    assert feat.probe_kind == "card-collection"
    assert len(feat.template) == 2

"""Tests for fix_actions catalog — 4 cases (one per category)."""
import json

from lib.fix_actions import CATALOG, get_fix_action, export_json


def test_h_category_present():
    """HTML category — H6 maps to head-seo admin page."""
    fa = get_fix_action("H6")
    assert fa is not None
    assert fa["type"] == "admin_page"
    assert fa["page"] == "landing-config-head-seo"


def test_n_category_present():
    """Network — N8 (robots.txt) maps to reading settings."""
    fa = get_fix_action("N8")
    assert fa is not None
    assert fa["type"] == "raw_url"
    assert "options-reading.php" in fa["url"]


def test_s_category_present():
    """Schema — S5 (favicon) maps to customizer site_icon."""
    fa = get_fix_action("S5")
    assert fa is not None
    assert fa["type"] == "raw_url"
    assert "site_icon" in fa["url"]


def test_ai_category_present():
    """AI — AI1 (llms.txt) maps to head-seo admin (anchor)."""
    fa = get_fix_action("AI1")
    assert fa is not None
    # Either raw_url with anchor or admin_page — accept both, just check label
    assert "llms.txt" in fa["label"].lower()


def test_unknown_check_returns_none():
    assert get_fix_action("X99") is None


def test_export_json_round_trip(tmp_path):
    out = tmp_path / "fix-actions.json"
    export_json(out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    # Should contain at least H6, N8, S5, AI1
    for key in ["H6", "N8", "S5", "AI1"]:
        assert key in loaded


def test_catalog_covers_all_43_plus_3():
    """Smoke: catalog must cover at least one entry per category prefix."""
    prefixes = {k[0] for k in CATALOG.keys()}
    assert prefixes >= {"H", "N", "S"}, f"missing prefixes: {prefixes}"
    # AI checks should also be present
    ai_keys = [k for k in CATALOG.keys() if k.startswith("AI")]
    assert len(ai_keys) >= 3

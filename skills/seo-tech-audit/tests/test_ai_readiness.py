"""Tests for ai_readiness runner (AI1/AI2/AI3)."""
from pathlib import Path
from unittest.mock import patch, MagicMock

from runners.ai_readiness import (
    check_llms_txt,
    check_schema_org_types,
    check_no_js_render,
    run_all,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_response(status=200, text=""):
    r = MagicMock()
    r.status_code = status
    r.text = text
    return r


def test_ai1_llms_txt_valid():
    good = (FIXTURES / "good-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, good)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["id"] == "AI1"
    assert r["passed"] is True


def test_ai1_llms_txt_missing():
    resp = _make_response(404, "")
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["passed"] is False


def test_ai1_llms_txt_invalid_format():
    bad = (FIXTURES / "bad-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, bad)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        r = check_llms_txt("https://x/")
    assert r["passed"] is False


def test_ai2_schema_org_organization():
    good = (FIXTURES / "good-schema.html").read_text(encoding="utf-8")
    r = check_schema_org_types(good, "https://x/")
    assert r["id"] == "AI2"
    assert r["passed"] is True


def test_ai2_schema_org_missing_org_type():
    html = '<html><head><script type="application/ld+json">{"@type":"Article"}</script></head><body>x</body></html>'
    r = check_schema_org_types(html, "https://x/")
    assert r["passed"] is False


def test_ai3_no_js_sufficient_content():
    good = (FIXTURES / "good-body.html").read_text(encoding="utf-8")
    r = check_no_js_render(good, "https://x/")
    assert r["id"] == "AI3"
    assert r["passed"] is True


def test_ai3_no_js_blank_spa():
    blank = (FIXTURES / "no-js-empty.html").read_text(encoding="utf-8")
    r = check_no_js_render(blank, "https://x/")
    assert r["passed"] is False


def test_run_all_returns_three_results():
    good_schema = (FIXTURES / "good-schema.html").read_text(encoding="utf-8")
    good_llms = (FIXTURES / "good-llms.txt").read_text(encoding="utf-8")
    resp = _make_response(200, good_llms)
    with patch("runners.ai_readiness.fetch", return_value=resp):
        results = run_all("https://x/", good_schema)
    ids = sorted(r["id"] for r in results)
    assert ids == ["AI1", "AI2", "AI3"]

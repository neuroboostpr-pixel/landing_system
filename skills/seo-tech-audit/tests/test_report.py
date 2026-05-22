"""Tests for report.py — Markdown + JSON serialization."""
from lib.report import build_site_report, build_aggregate_report, render_markdown


SAMPLE_RESULTS = [
    {"id": "H1", "passed": True, "evidence": "status=200"},
    {"id": "H4", "passed": False, "evidence": "title=\"\""},
    {"id": "N8", "passed": True, "evidence": "size=512B"},
]

THRESHOLDS = {
    "H1": {"hard": True, "desc": "HTTP 200"},
    "H4": {"hard": True, "desc": "<title> present"},
    "N8": {"hard": True, "desc": "robots.txt"},
}


def test_site_report_structure():
    rep = build_site_report("https://x/", SAMPLE_RESULTS, THRESHOLDS)
    assert rep["host"] == "https://x/"
    assert rep["hard_total"] == 3
    assert rep["hard_passed"] == 2  # H1 + N8 pass; H4 fails
    assert rep["all_total"] == 3
    assert rep["passed"] is False  # 1 hard fail


def test_aggregate_report_combines_sites():
    a = build_site_report("https://a/", SAMPLE_RESULTS, THRESHOLDS)
    b = build_site_report("https://b/", [
        {"id": "H1", "passed": True, "evidence": ""},
        {"id": "H4", "passed": True, "evidence": ""},
        {"id": "N8", "passed": True, "evidence": ""},
    ], THRESHOLDS)
    agg = build_aggregate_report([a, b])
    assert agg["total_sites"] == 2
    assert agg["sites_passed"] == 1
    assert agg["overall_passed"] is False


def test_markdown_contains_summary_table():
    rep = build_site_report("https://x/", SAMPLE_RESULTS, THRESHOLDS)
    md = render_markdown([rep])
    assert "# Audit Report" in md
    assert "https://x/" in md
    assert "H4" in md  # failed check shown
    assert "❌" in md or "FAIL" in md


def test_markdown_multisite_aggregate():
    a = build_site_report("https://a/", SAMPLE_RESULTS, THRESHOLDS)
    b = build_site_report("https://b/", SAMPLE_RESULTS, THRESHOLDS)
    md = render_markdown([a, b])
    assert "https://a/" in md
    assert "https://b/" in md

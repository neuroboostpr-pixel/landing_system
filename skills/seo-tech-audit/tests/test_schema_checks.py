"""Tests for schema_checks runner — Open Graph, Twitter Card, JSON-LD, favicon."""
from runners.schema_checks import check_schema


def _by(results, check_id):
    return next(r for r in results if r["id"] == check_id)


def test_s1_og_all_five_present(good_html):
    results = check_schema(good_html, "https://x/")
    assert _by(results, "S1")["passed"] is True


def test_s1_og_missing_image_fails():
    html = """<html><head>
    <meta property="og:title" content="x">
    <meta property="og:description" content="x">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://x/">
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    s1 = _by(results, "S1")
    assert s1["passed"] is False
    assert "og:image" in s1["evidence"]


def test_s3_twitter_card_absent_is_soft_fail():
    html = "<html><head><title>x</title></head><body></body></html>"
    results = check_schema(html, "https://x/")
    assert _by(results, "S3")["passed"] is False


def test_s4_json_ld_present():
    html = """<html><head>
    <script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"X"}</script>
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    assert _by(results, "S4")["passed"] is True


def test_s4_json_ld_invalid_fails():
    html = """<html><head>
    <script type="application/ld+json">{invalid json</script>
    </head><body></body></html>"""
    results = check_schema(html, "https://x/")
    assert _by(results, "S4")["passed"] is False


def test_s5_favicon_present(good_html):
    results = check_schema(good_html, "https://x/")
    assert _by(results, "S5")["passed"] is True


def test_s5_favicon_missing_fails():
    html = "<html><head><title>x</title></head><body></body></html>"
    results = check_schema(html, "https://x/")
    assert _by(results, "S5")["passed"] is False


def test_returns_5_results(good_html):
    results = check_schema(good_html, "https://x/")
    ids = sorted(r["id"] for r in results)
    assert ids == ["S1", "S2", "S3", "S4", "S5"]

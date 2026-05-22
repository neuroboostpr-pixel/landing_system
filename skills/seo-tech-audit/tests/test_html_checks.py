"""Tests for html_checks runner. Each check has pass+fail case."""
from runners.html_checks import check_html


def _result_by_id(results, check_id):
    return next(r for r in results if r["id"] == check_id)


def test_h1_returns_status_field(good_html):
    results = check_html(good_html, "https://good.example.com/")
    h1 = _result_by_id(results, "H1")
    assert "passed" in h1
    assert "evidence" in h1


def test_h4_title_present_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H4")["passed"] is True


def test_h4_title_present_bad():
    html = "<!doctype html><html><head></head><body></body></html>"
    results = check_html(html, "https://x/")
    assert _result_by_id(results, "H4")["passed"] is False


def test_h5_title_length_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H5")["passed"] is True


def test_h5_title_length_bad(bad_html):
    results = check_html(bad_html, "https://x/")
    assert _result_by_id(results, "H5")["passed"] is False


def test_h8_exactly_one_h1_good(good_html):
    results = check_html(good_html, "https://good.example.com/")
    assert _result_by_id(results, "H8")["passed"] is True


def test_h8_exactly_one_h1_bad_two_h1(bad_html):
    results = check_html(bad_html, "https://x/")
    assert _result_by_id(results, "H8")["passed"] is False


def test_h10_lang_present(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H10")["passed"] is True
    assert _result_by_id(bad, "H10")["passed"] is False


def test_h12_canonical_present(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H12")["passed"] is True
    assert _result_by_id(bad, "H12")["passed"] is False


def test_h14_noindex_detected(bad_html):
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(bad, "H14")["passed"] is False


def test_h15_alt_ratio(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H15")["passed"] is True
    assert _result_by_id(bad, "H15")["passed"] is False


def test_h22_noopener_required(good_html, bad_html):
    good = check_html(good_html, "https://x/")
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(good, "H22")["passed"] is True
    assert _result_by_id(bad, "H22")["passed"] is False


def test_h23_click_here_anchor(bad_html):
    bad = check_html(bad_html, "https://x/")
    assert _result_by_id(bad, "H23")["passed"] is False


def test_returns_25_results(good_html):
    results = check_html(good_html, "https://x/")
    ids = sorted(r["id"] for r in results)
    expected = sorted(f"H{i}" for i in range(1, 26))
    assert ids == expected

"""Tests for network_checks runner — mocked HTTP responses."""
from unittest.mock import MagicMock, patch

from runners.network_checks import (
    check_robots_txt,
    check_sitemap_xml,
    check_404_status,
    check_www_redirect,
    check_security_headers,
)


def _make_response(status=200, text="", headers=None, url=""):
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.headers = headers or {}
    r.url = url
    r.history = []
    return r


def test_robots_txt_present_and_valid():
    resp = _make_response(200, "User-agent: *\nDisallow:\nSitemap: https://x/sitemap.xml")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_robots_txt("https://x/")
    assert res["id"] == "N8"
    assert res["passed"] is True


def test_robots_txt_missing():
    resp = _make_response(404, "")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_robots_txt("https://x/")
    assert res["passed"] is False


def test_sitemap_xml_valid_and_in_robots():
    robots_text = "User-agent: *\nSitemap: https://x/sitemap.xml"
    sitemap_resp = _make_response(200,
        '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>https://x/</loc></url></urlset>')
    with patch("runners.network_checks.fetch", return_value=sitemap_resp):
        res = check_sitemap_xml("https://x/", robots_text=robots_text)
    assert res["id"] == "N9"
    assert res["passed"] is True


def test_sitemap_xml_missing_from_robots():
    robots_text = "User-agent: *\nDisallow:"
    sitemap_resp = _make_response(200, '<?xml version="1.0"?><urlset/>')
    with patch("runners.network_checks.fetch", return_value=sitemap_resp):
        res = check_sitemap_xml("https://x/", robots_text=robots_text)
    assert res["passed"] is False
    assert "robots" in res["evidence"].lower()


def test_404_returns_404():
    resp = _make_response(404, "Not found")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_404_status("https://x/")
    assert res["passed"] is True


def test_404_returns_200_is_bad():
    resp = _make_response(200, "Soft 404")
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_404_status("https://x/")
    assert res["passed"] is False


def test_www_redirect_to_canonical():
    final = _make_response(200, "", url="https://x.com/")
    history_redir = MagicMock(status_code=301, url="https://www.x.com/")
    final.history = [history_redir]
    with patch("runners.network_checks.fetch", return_value=final):
        res = check_www_redirect("https://x.com/")
    assert res["passed"] is True


def test_security_headers_3_of_4():
    resp = _make_response(200, "", headers={
        "Strict-Transport-Security": "max-age=31536000",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
    })
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_security_headers("https://x/")
    assert res["passed"] is True
    assert "3" in res["evidence"]


def test_security_headers_only_1_fails():
    resp = _make_response(200, "", headers={"X-Frame-Options": "DENY"})
    with patch("runners.network_checks.fetch", return_value=resp):
        res = check_security_headers("https://x/")
    assert res["passed"] is False

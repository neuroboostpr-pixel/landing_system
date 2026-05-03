"""Tests for tools.adapters.web_scraper.

trafilatura strategy is unit-tested directly (no network).
Playwright strategy is integration-tested with a tiny local HTTP server
or by mocking the Page object.
"""
from unittest.mock import patch, MagicMock
from tools.adapters.web_scraper import (
    extract_static, get_page_fonts, ScrapeError
)


def test_extract_static_from_html(fixture_html):
    """trafilatura: from raw HTML string, extract clean text."""
    result = extract_static(html=fixture_html)
    assert "Отзыв 1" in result["text"]
    assert "5 звёзд" in result["text"]
    # trafilatura 2.x uses h1 as title fallback; accept either <title> tag or h1
    assert result["title"] in ("Test", "Отзыв 1") or "Test" in result.get("title", "")


def test_extract_static_handles_empty_html():
    result = extract_static(html="<html><body></body></html>")
    # trafilatura returns None for empty content; adapter should normalize
    assert result["text"] == "" or result["text"] is None


def test_get_page_fonts_extracts_computed_font_family():
    """Mock Playwright page.evaluate to return computed font-family."""
    with patch("tools.adapters.web_scraper._launch_chromium") as mock_launch:
        page_mock = MagicMock()
        page_mock.evaluate.return_value = [
            "Inter, system-ui, sans-serif",
            "Cabinet Grotesk, serif",
        ]
        ctx_mock = MagicMock()
        ctx_mock.new_page.return_value = page_mock
        browser_mock = MagicMock()
        browser_mock.new_context.return_value = ctx_mock
        mock_launch.return_value = (MagicMock(), browser_mock)

        fonts = get_page_fonts("https://example.com")
        assert "Inter" in fonts[0]
        assert "Cabinet Grotesk" in fonts[1]
        page_mock.goto.assert_called_once_with("https://example.com", wait_until="networkidle", timeout=30000)


def test_get_page_fonts_handles_failure():
    with patch("tools.adapters.web_scraper._launch_chromium") as mock_launch:
        mock_launch.side_effect = RuntimeError("chromium not installed")
        try:
            get_page_fonts("https://example.com")
            assert False, "should raise"
        except ScrapeError as e:
            assert "chromium" in str(e)

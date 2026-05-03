"""Tests for tools.adapters.web_scraper.

trafilatura strategy is unit-tested directly (no network).
Playwright strategy is integration-tested with a tiny local HTTP server
or by mocking the Page object.
"""
import pytest
from unittest.mock import patch, MagicMock
from tools.adapters.web_scraper import (
    extract_static, get_page_fonts, ScrapeError
)


def test_extract_static_from_html(fixture_html):
    """trafilatura: from raw HTML string, extract clean text."""
    result = extract_static(html=fixture_html)
    assert "Отзыв 1" in result["text"]
    assert "5 звёзд" in result["text"]
    assert result["title"] == "Test"  # tightened — <title> tag is now reliable


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
        mock_launch.side_effect = ScrapeError("chromium launch failed: test")
        with pytest.raises(ScrapeError) as exc_info:
            get_page_fonts("https://example.com")
        assert "chromium launch failed" in str(exc_info.value)


def test_extract_static_prefers_title_tag_over_h1():
    """trafilatura 2.x falls back to <h1> when <title> is missing — but if
    <title> exists, we must return it (not the h1)."""
    html = """<!DOCTYPE html><html>
    <head><title>Real Page Title</title></head>
    <body><article><h1>Отзыв 1</h1><p>5 звёзд!</p></article></body></html>"""
    result = extract_static(html=html)
    assert result["title"] == "Real Page Title"


def test_extract_static_falls_back_when_no_title_tag():
    """When <title> is absent, trafilatura's h1 fallback is acceptable."""
    html = """<!DOCTYPE html><html>
    <head></head>
    <body><article><h1>Some Heading</h1><p>Content</p></article></body></html>"""
    result = extract_static(html=html)
    # Either trafilatura's metadata extracts something, or it's empty — both ok
    # The point is no crash; title is whatever trafilatura returned (may be h1 or empty)
    assert "title" in result

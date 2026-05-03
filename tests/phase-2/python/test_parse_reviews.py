"""Tests for parse-reviews.py.

Uses importlib to import the script as a module, then mocks
tools.adapters.web_scraper at the module level.
"""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

PARSE_SCRIPT = (Path(__file__).resolve().parent.parent.parent.parent
                / ".skills" / "client-assets-collection" / "scripts" / "parse-reviews.py")


def _load():
    spec = importlib.util.spec_from_file_location("parse_reviews_mod", PARSE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["parse_reviews_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_detect_source_yandex_maps():
    mod = _load()
    assert mod.detect_source("https://yandex.ru/maps/-/test") == "yandex-maps"
    assert mod.detect_source("https://2gis.ru/moscow/firm/123") == "2gis"
    assert mod.detect_source("https://otzovik.com/review_1.html") == "otzovik"
    assert mod.detect_source("https://example.com") == "other"


def test_parse_returns_reviews_list_dynamic(tmp_path):
    """For Я.Карты, parser uses extract_dynamic (Playwright)."""
    mod = _load()
    fake_extract = {
        "text": "Отзыв 1\n5 звёзд. Отлично!\n\nОтзыв 2\n4 звезды. Хорошо.",
        "title": "Yandex Maps — Test",
        "raw_html": "",
    }
    out = tmp_path / "yandex-maps"

    with patch.object(mod, "extract_dynamic", return_value=fake_extract) as m:
        result = mod.parse_reviews("https://yandex.ru/maps/test", str(out))
        m.assert_called_once()

    assert "reviews" in result
    assert len(result["reviews"]) >= 1
    json_files = list(out.glob("*.json"))
    assert len(json_files) == 1


def test_parse_uses_static_for_blog_sites(tmp_path):
    """For Otzovik/iRecommend/blog-like sources, parser uses extract_static."""
    mod = _load()
    fake_extract = {
        "text": "Long article body with reviews scattered.",
        "title": "Otzovik review page",
        "raw_html": "",
    }
    out = tmp_path / "otzovik"

    with patch.object(mod, "extract_static", return_value=fake_extract) as m:
        mod.parse_reviews("https://otzovik.com/review_1.html", str(out))
        m.assert_called_once()


def test_parse_warns_on_zero_reviews(tmp_path):
    """parse_reviews must call warn() (not success()) when 0 reviews extracted."""
    mod = _load()
    fake_extract = {"text": "", "title": "empty", "raw_html": ""}
    out = tmp_path / "empty"

    with patch.object(mod, "extract_static", return_value=fake_extract):
        with patch.object(mod, "warn") as mock_warn, \
             patch.object(mod, "success") as mock_success:
            result = mod.parse_reviews("https://otzovik.com/empty.html", str(out))
            assert mock_warn.called, "warn() should be called when 0 reviews"
            mock_success.assert_not_called()
            assert result["review_count"] == 0


def test_split_reviews_falls_back_to_single_newline_for_unstructured_blob():
    mod = _load()
    # Each line is 120+ chars so 5 lines joined by single \n exceed the 500-char threshold
    line = "This is a review with plenty of content so the total blob exceeds five hundred characters easily."
    text = "\n".join([f"{line} Review #{i}." for i in range(5)])
    assert len(text) > 500, "test data must exceed 500 chars to trigger fallback"
    result = mod.split_reviews(text)
    assert len(result) == 5


def test_needs_dynamic_ignores_query_string_yandex():
    """needs_dynamic must not match 'yandex.ru/maps' appearing only in a query param."""
    mod = _load()
    assert mod.needs_dynamic("https://yandex.ru/maps/some-org") is True
    assert mod.needs_dynamic("https://example.com/?ref=yandex.ru/maps") is False

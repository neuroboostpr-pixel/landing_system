"""Tests for lucide-fetcher.py — download Lucide SVG, render as brand-colored PNG."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import importlib.util


SCRIPT = REPO / "skills" / "visual-generation" / "scripts" / "lucide-fetcher.py"


def _load():
    spec = importlib.util.spec_from_file_location("lucide_fetcher", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SAMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" x2="21" y1="6" y2="6"/>
  <line x1="3" x2="21" y1="12" y2="12"/>
  <line x1="3" x2="21" y1="18" y2="18"/>
</svg>"""


def test_lucide_url_for_name():
    mod = _load()
    url = mod.lucide_url("menu")
    assert "lucide-icons/lucide" in url
    assert url.endswith("/menu.svg")


def test_cache_path_for_name(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    p = mod.cache_path("menu")
    assert str(p).endswith("menu.svg")


def test_fetch_returns_cached_when_exists(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    cached = tmp_path / "menu.svg"
    cached.write_text(SAMPLE_SVG)
    result = mod.fetch_svg("menu")
    assert result == cached
    assert result.read_text() == SAMPLE_SVG


def test_fetch_downloads_when_not_cached(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_SVG
    with patch.object(mod, "_http_get", return_value=mock_resp):
        result = mod.fetch_svg("menu")
    assert result.read_text() == SAMPLE_SVG


def test_render_to_png_with_brand_color(tmp_path):
    mod = _load()
    svg_path = tmp_path / "menu.svg"
    svg_path.write_text(SAMPLE_SVG)
    png_path = tmp_path / "menu.png"
    mod.render_to_png(svg_path, png_path, brand_color="#1e3a8a", size=1024)
    assert png_path.exists()
    assert png_path.stat().st_size > 100


def test_fetch_and_render_full_flow(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path / "cache"))
    cached = tmp_path / "cache" / "menu.svg"
    cached.parent.mkdir(parents=True)
    cached.write_text(SAMPLE_SVG)

    out_png = tmp_path / "out.png"
    result = mod.fetch_and_render("menu", out_png, brand_color="#c47a3a", size=512)
    assert result == out_png
    assert out_png.exists()

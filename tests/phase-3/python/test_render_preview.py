"""Tests for design-tokens-generation/scripts/render-preview.py"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "build-tokens.py"
RENDER_SCRIPT = ROOT / "skills" / "design-tokens-generation" / "scripts" / "render-preview.py"


def _load(script):
    spec = importlib.util.spec_from_file_location(script.stem, script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_creates_design_preview_html(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    result = _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    assert result == 0
    assert (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").exists()


def test_preview_has_doctype(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html


def test_preview_has_color_swatches(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "#ff5733" in html


def test_preview_has_font_specimens(brand_kit_project):
    _load(BUILD_SCRIPT).main(["prog", str(brand_kit_project)])
    _load(RENDER_SCRIPT).main(["prog", str(brand_kit_project)])
    html = (brand_kit_project / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").read_text(encoding="utf-8")
    assert "Cabinet Grotesk" in html
    assert "Inter" in html


def test_render_graceful_with_missing_tokens_json(tmp_path):
    """render-preview.py must succeed even when tokens.json is absent."""
    (tmp_path / "05_ДИЗАЙН-СИСТЕМА").mkdir(parents=True)
    result = _load(RENDER_SCRIPT).main(["prog", str(tmp_path)])
    assert result == 0
    assert (tmp_path / "05_ДИЗАЙН-СИСТЕМА" / "design-preview.html").exists()

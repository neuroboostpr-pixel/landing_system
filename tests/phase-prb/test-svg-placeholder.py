"""Tests for SVG placeholder generator (ports open-design placeholder.ts pattern, Apache-2.0)."""
from pathlib import Path

from skills.photo_curation.scripts.svg_placeholder import (
    make_placeholder_svg,
    write_placeholder,
)


def test_make_placeholder_returns_svg_string():
    svg = make_placeholder_svg(
        slot_id="hero-bg",
        width=1920, height=1080,
        hint="Фото объекта услуги",
        brand_primary="#1e3a8a",
    )
    assert svg.startswith("<svg")
    assert "</svg>" in svg
    assert "hero-bg" in svg
    assert "Фото объекта услуги" in svg
    assert "#1e3a8a" in svg


def test_make_placeholder_includes_dimensions():
    svg = make_placeholder_svg(slot_id="x", width=400, height=300, hint="h", brand_primary="#000")
    assert 'width="400"' in svg
    assert 'height="300"' in svg


def test_write_placeholder_saves_under_png_filename(tmp_path):
    # Port of open-design trick: svg content saved with .png extension.
    out = tmp_path / "slot.png"
    write_placeholder(
        out_path=out,
        slot_id="testimonial-1",
        width=500, height=500,
        hint="Аватар клиента",
        brand_primary="#c47a3a",
    )
    assert out.exists()
    content = out.read_bytes()
    assert content.startswith(b"<svg") or content.startswith(b"<?xml")

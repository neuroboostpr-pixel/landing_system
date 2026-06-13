"""Pytest suite for skills/wp-cli-deployer/scripts/fix-page-content-images.py.

Covers the transform() contract documented in docs/asset-pipeline.md:
  - photo placeholders → attachment IDs (any subfolder, any supported ext)
  - string asset paths → attachment IDs (any subfolder, any supported ext)
  - image-object attrs → URL-encoded JSON
  - raw SVG/HTML in textarea attrs → URL-encoded string
  - idempotency: re-running on transformed output must be a no-op
"""
import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "wp-cli-deployer" / "scripts" / "fix-page-content-images.py"

spec = importlib.util.spec_from_file_location("fix_page_content_images", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
transform = mod.transform


PHOTO_MAP = {
    "hero.jpg": "10",
    "model-l9.png": "11",
    "favicon.ico": "12",
    "logo.svg": "13",
    "decoration.webp": "14",
    "Team_Photo.jpg": "15",
}


def test_placeholder_filename_with_underscores():
    """Имя файла с подчёркиваниями (Team_Photo.jpg) — раньше regex [^_]+ не
    матчил, плейсхолдер оставался в page-content (BLOCKER §4.2 «битые картинки»)."""
    html = '"section_image": __IMAGE_ATTACHMENT_ID__assets/photos/Team_Photo.jpg__'
    out, stats = transform(html, PHOTO_MAP)
    assert "15" in out and "__IMAGE_ATTACHMENT_ID__" not in out
    assert stats["placeholders"] == 1


def test_placeholder_basename_only():
    """Плейсхолдер без assets/<sub>/ префикса — матчится по basename."""
    html = '"hero_bg": __IMAGE_ATTACHMENT_ID__hero.jpg__'
    out, stats = transform(html, PHOTO_MAP)
    assert "10" in out and "__IMAGE_ATTACHMENT_ID__" not in out
    assert stats["placeholders"] == 1


def test_placeholder_in_photos_subfolder():
    html = '"hero_bg": __IMAGE_ATTACHMENT_ID__assets/photos/hero.jpg__'
    out, stats = transform(html, PHOTO_MAP)
    assert "10" in out
    assert stats["placeholders"] == 1


def test_placeholder_in_icons_subfolder():
    html = '"favicon": __IMAGE_ATTACHMENT_ID__assets/icons/favicon.ico__'
    out, stats = transform(html, PHOTO_MAP)
    assert "12" in out
    assert stats["placeholders"] == 1


def test_string_path_png():
    html = '{"id":"assets/photos/model-l9.png"}'
    out, stats = transform(html, PHOTO_MAP)
    assert '"11"' in out
    assert stats["string_paths"] == 1


def test_string_path_webp():
    html = '{"bg":"assets/decorations/decoration.webp"}'
    out, stats = transform(html, PHOTO_MAP)
    assert '"14"' in out
    assert stats["string_paths"] == 1


def test_string_path_image_key_url_encoded_object():
    """photoN keys are image attrs — must produce URL-encoded {id,url} JSON,
    not a bare ID string (Lazy Blocks image control needs the object form)."""
    html = '"photo1": "assets/photos/hero.jpg"'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["string_paths"] == 1
    # Decoded value must equal {"id": 10, "url": ""}
    encoded = out.split('"photo1": "')[1].rstrip('"')
    decoded = json.loads(urllib.parse.unquote(encoded))
    assert decoded == {"id": 10, "url": ""}


def test_string_path_hero_bg_url_encoded_object():
    """hero_bg is in IMAGE_ATTR_KEYS — string path must also become URL-encoded JSON."""
    html = '"hero_bg": "assets/photos/hero.jpg"'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["string_paths"] == 1
    encoded = out.split('"hero_bg": "')[1].rstrip('"')
    decoded = json.loads(urllib.parse.unquote(encoded))
    assert decoded == {"id": 10, "url": ""}


def test_image_object_url_encoded():
    html = '"hero_bg": {"id": 10, "url": ""}'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["image_objects"] == 1
    # Encoded contains %7B (encoded `{`)
    assert "%7B" in out
    # Decode and compare structure
    encoded = out.split('"hero_bg": "')[1].rstrip('"')
    decoded = json.loads(urllib.parse.unquote(encoded))
    assert decoded == {"id": 10, "url": ""}


def test_favicon_treated_as_image_object():
    html = '"favicon": {"id": 12, "url": ""}'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["image_objects"] == 1
    assert "%7B" in out


def test_logo_treated_as_image_object():
    html = '"logo": {"id": 13, "url": "https://example.com/logo.svg"}'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["image_objects"] == 1


def test_svg_textarea_url_encoded():
    svg = '<svg viewBox="0 0 24 24"><path d="M1 2"/></svg>'
    html = f'"icon_svg":"{svg}"'
    out, stats = transform(html, PHOTO_MAP)
    assert stats["svg_attrs"] == 1
    # Decoded value matches original
    encoded = out.split('"icon_svg":"')[1].rstrip('"')
    assert urllib.parse.unquote(encoded) == svg
    # No raw `<` remains in the attr value
    assert "<svg" not in out


def test_svg_already_encoded_is_left_alone():
    svg = '<svg viewBox="0 0 24 24"><path d="M1 2"/></svg>'
    encoded = urllib.parse.quote(svg)
    html = f'"icon_svg":"{encoded}"'
    out, stats = transform(html, PHOTO_MAP)
    # Skipped (no raw `<`), counter stays 0
    assert stats["svg_attrs"] == 0
    assert out == html


def test_multiple_svg_attrs():
    html = (
        '"icon_svg":"<svg>a</svg>"'
        ',"svg":"<svg>b</svg>"'
        ',"background_svg":"<svg>c</svg>"'
    )
    out, stats = transform(html, PHOTO_MAP)
    assert stats["svg_attrs"] == 3


def test_idempotent_full_run():
    """Running transform twice on the same input must yield same output."""
    html = (
        '"hero_bg": {"id": 10, "url": ""},'
        '"icon_svg":"<svg viewBox=\\"0 0 24 24\\"><path d=\\"M1\\"/></svg>",'
        '"thumbnail":"assets/photos/hero.jpg"'
    )
    once, _ = transform(html, PHOTO_MAP)
    twice, stats2 = transform(once, PHOTO_MAP)
    assert once == twice
    # Second run: every counter is 0
    assert stats2["placeholders"] == 0
    assert stats2["string_paths"] == 0
    assert stats2["image_objects"] == 0
    assert stats2["svg_attrs"] == 0


def test_unknown_filename_maps_to_zero():
    html = '"hero_bg": __IMAGE_ATTACHMENT_ID__assets/photos/nope.jpg__'
    out, stats = transform(html, PHOTO_MAP)
    assert "0" in out
    assert stats["placeholders"] == 1

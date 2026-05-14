"""Tests for inject-content.py icon + infographic substitution."""
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# Same import pattern as PR-B test-inject-photos.py
try:
    from skills.block_composition.scripts.inject_content import inject_block
except ImportError:
    pytest.skip("inject_block not importable yet", allow_module_level=True)


def test_inject_icon_from_visuals_dir(tmp_path):
    block_html = '<section><div data-slot="feature-1-icon" data-slot-type="icon"></div></section>'
    block_meta = {
        "id": "ru-features-01",
        "slots": [{"type": "icon", "name": "feature-1-icon", "hint": "shield"}]
    }
    visuals_dir = tmp_path / "07d_VISUALS"
    icons_dir = visuals_dir / "icons"
    icons_dir.mkdir(parents=True)
    (icons_dir / "feature-1-icon.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 100)

    result = inject_block(block_html, block_meta, {}, visuals_dir=visuals_dir)

    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert "feature-1-icon.png" in img.get("src", "")


def test_inject_infographic_from_visuals_dir(tmp_path):
    block_html = '<section><div data-slot="kpi-1" data-slot-type="infographic"></div></section>'
    block_meta = {
        "id": "ru-stats-01",
        "slots": [{"type": "infographic", "name": "kpi-1", "chart_type": "number"}]
    }
    visuals_dir = tmp_path / "07d_VISUALS"
    info_dir = visuals_dir / "infographics"
    info_dir.mkdir(parents=True)
    (info_dir / "kpi-1.png").write_bytes(b"\x89PNG\r\n" + b"\x00" * 100)

    result = inject_block(block_html, block_meta, {}, visuals_dir=visuals_dir)

    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None
    assert "infographics/kpi-1.png" in img.get("src", "") or "kpi-1.png" in img.get("src", "")


def test_inject_falls_back_to_placeholder_when_visuals_missing(tmp_path):
    block_html = '<section><div data-slot="feature-1-icon" data-slot-type="icon"></div></section>'
    block_meta = {
        "id": "ru-features-01",
        "slots": [{"type": "icon", "name": "feature-1-icon"}]
    }
    result = inject_block(block_html, block_meta, {}, visuals_dir=None)

    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None


def test_inject_pra_compat_no_visuals_no_photo_selections(tmp_path):
    """Regression: PR-A behavior preserved when both PR-B and PR-C inputs absent."""
    block_html = '<section><div data-slot="hero-bg" data-slot-type="photo"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "hint": "object"}]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=None, visuals_dir=None)
    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None

"""Tests for inject-content.py photo substitution (PR-B integration)."""
from pathlib import Path
import sys

import pytest
from bs4 import BeautifulSoup


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

# Module loaded via conftest.py namespace registration
from skills.block_composition.scripts.inject_content import inject_block  # noqa: E402


def test_inject_uses_processed_photo_when_selections_exists():
    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "hint": "Фото объекта"}]
    }
    content = {}
    selections = {
        "slots": [
            {"slot_id": "hero-bg", "strategy": "bring-your-own",
             "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"}}
        ]
    }
    result = inject_block(block_html, block_meta, content, photo_selections=selections)
    soup = BeautifulSoup(result, "html.parser")
    img = soup.find("img")
    assert img is not None, "Expected <img> element when selections provided"
    assert "processed/hero-bg/desktop.jpg" in img.get("src", "")


def test_inject_falls_back_to_placeholder_when_no_selections():
    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "hint": "Фото"}]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=None)
    soup = BeautifulSoup(result, "html.parser")
    placeholder = soup.find(class_="slot-placeholder")
    assert placeholder is not None, "Expected .slot-placeholder div when no selections"
    assert "photo slot" in placeholder.text


def test_inject_uses_picture_element_for_mobile_variant():
    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9", "mobile_ratio": "9:16"}]
    }
    selections = {
        "slots": [
            {"slot_id": "hero-bg", "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"}}
        ]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=selections)
    soup = BeautifulSoup(result, "html.parser")
    picture = soup.find("picture")
    assert picture is not None, "Expected <picture> element when mobile_ratio defined"
    sources = picture.find_all("source")
    assert any("mobile" in s.get("srcset", "") for s in sources), \
        "Expected a <source> with mobile srcset"


def test_inject_no_mobile_ratio_uses_plain_img():
    block_html = '<section><div data-slot="hero-bg"></div></section>'
    block_meta = {
        "id": "ru-hero-01",
        "slots": [{"type": "photo", "name": "hero-bg", "ratio": "16:9"}]  # no mobile_ratio
    }
    selections = {
        "slots": [
            {"slot_id": "hero-bg", "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg", "mobile": None}}
        ]
    }
    result = inject_block(block_html, block_meta, {}, photo_selections=selections)
    soup = BeautifulSoup(result, "html.parser")
    assert soup.find("picture") is None, "No <picture> expected without mobile_ratio"
    img = soup.find("img")
    assert img is not None, "Expected plain <img> when no mobile_ratio"

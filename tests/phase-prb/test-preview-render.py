"""Tests for photo-preview.html generator."""
from pathlib import Path

from skills.photo_curation.scripts.preview_render import render_preview


def test_preview_shows_all_slots_with_processed_paths(tmp_path):
    selections = {
        "strategy_default": "bring-your-own",
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "processed": {"desktop": "processed/hero-bg/desktop.jpg",
                           "mobile": "processed/hero-bg/mobile.jpg"},
             "ai_approved_by_user": False},
            {"slot_id": "testimonial-1", "block_id": "ru-test-01", "ratio": "1:1",
             "strategy": "generate", "chosen_photo_id": None,
             "processed": {"desktop": "processed/testimonial-1/ai-generated.jpg",
                           "mobile": None},
             "ai_approved_by_user": True},
            {"slot_id": "process-3", "block_id": "ru-proc-01", "ratio": "4:3",
             "strategy": "placeholder", "chosen_photo_id": None,
             "processed": {"desktop": "processed/process-3/placeholder.png",
                           "mobile": None},
             "ai_approved_by_user": False},
        ]
    }
    out = tmp_path / "photo-preview.html"
    render_preview(selections, out)
    html = out.read_text()
    # All 3 slots rendered
    assert "hero-bg" in html
    assert "testimonial-1" in html
    assert "process-3" in html
    # AI badge for the generate slot
    assert "AI" in html
    # Strategy labels present
    assert "client" in html or "Клиент" in html or "Фото клиента" in html


def test_preview_with_empty_slots(tmp_path):
    out = tmp_path / "photo-preview.html"
    render_preview({"slots": []}, out)
    html = out.read_text()
    assert "<html" in html
    assert "</html>" in html


def test_preview_escapes_html(tmp_path):
    selections = {"slots": [
        {"slot_id": "<x>", "block_id": "y", "ratio": "1:1",
         "strategy": "placeholder",
         "processed": {"desktop": "x.png", "mobile": None}}
    ]}
    out = tmp_path / "photo-preview.html"
    render_preview(selections, out)
    html = out.read_text()
    assert "<x>" not in html
    assert "&lt;x&gt;" in html

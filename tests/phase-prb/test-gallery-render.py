"""Tests for photo-board.html generator."""
from pathlib import Path

from skills.photo_curation.scripts.gallery_render import render_board


def test_render_board_produces_html_with_photos_and_slots(tmp_path):
    catalog = {
        "photos": [
            {"id": "photo_001", "thumb_path": "intake/photo_001.thumb.jpg",
             "caption": "Test photo", "tags": ["portrait"]},
            {"id": "photo_002", "thumb_path": "intake/photo_002.thumb.jpg",
             "caption": "Other", "tags": ["object"]},
        ]
    }
    selections_draft = {
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "candidates": [{"photo_id": "photo_002", "score": 0.9, "reason": "wide"}],
             "ai_fallback_needed": False, "required_user_approval": False},
            {"slot_id": "testimonial-1-avatar", "block_id": "ru-test-01", "ratio": "1:1",
             "candidates": [],
             "ai_fallback_needed": True, "required_user_approval": True,
             "ai_prompt": "Portrait of client"},
        ]
    }
    out = tmp_path / "photo-board.html"
    render_board(catalog, selections_draft, out)
    html = out.read_text()
    # Photos rendered
    assert "photo_001" in html
    assert "photo_002" in html
    # Slots rendered
    assert "hero-bg" in html
    assert "testimonial-1-avatar" in html
    # AI approval checkbox for identity-safe slot
    assert "ai_approved_by_user" in html or "toggleAiApproval" in html
    assert "Согласен" in html
    # Drag-drop data attributes
    assert "data-photo-id" in html
    assert "data-slot-id" in html


def test_render_board_includes_confirm_button(tmp_path):
    catalog = {"photos": []}
    selections_draft = {"slots": []}
    out = tmp_path / "photo-board.html"
    render_board(catalog, selections_draft, out)
    html = out.read_text()
    assert "Подтвердить" in html or "Confirm" in html
    assert "selections.yaml" in html  # JS exports as this filename


def test_render_board_escapes_html_in_captions(tmp_path):
    catalog = {"photos": [
        {"id": "x", "thumb_path": "x.jpg", "caption": "<script>alert(1)</script>", "tags": []}
    ]}
    out = tmp_path / "photo-board.html"
    render_board(catalog, {"slots": []}, out)
    html = out.read_text()
    # Script tag must be escaped, not raw
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html

#!/usr/bin/env python3
"""Render photo-board.html (split-view drag-drop UI for matching photos to slots)."""
import json
from html import escape
from pathlib import Path
from typing import Mapping

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = SCRIPT_DIR / "gallery-template.html"


def _photo_card(photo: dict) -> str:
    tags = ", ".join(photo.get("tags", []))
    return f"""<div class="photo" data-photo-id="{escape(photo['id'])}" draggable="true">
  <img src="{escape(photo.get('thumb_path', ''))}" alt="{escape(photo.get('caption', ''))}">
  <div class="caption">{escape(photo.get('caption', ''))}</div>
  <div class="tags">{escape(tags)}</div>
</div>"""


def _slot_card(slot: dict, photos_by_id: Mapping[str, dict]) -> str:
    slot_id = slot["slot_id"]
    chosen = slot.get("chosen_photo_id")
    candidates = slot.get("candidates", [])
    if not chosen and candidates:
        chosen = candidates[0]["photo_id"]
    classes = "slot"
    if chosen:
        classes += " has-photo"
    elif slot.get("ai_fallback_needed"):
        classes += " fallback"

    photo_html = '<div class="slot-photo empty">Перетащи фотку сюда</div>'
    if chosen and chosen in photos_by_id:
        p = photos_by_id[chosen]
        photo_html = f'<div class="slot-photo"><img src="{escape(p["thumb_path"])}"><span>{escape(p.get("caption", ""))}</span></div>'

    ai_banner = ""
    if slot.get("required_user_approval"):
        ai_banner = f"""<div class="ai-banner">
  &#9888; Этот слот требует AI-сгенерированного лица человека.
  <label><input type="checkbox" onchange="toggleAiApproval('{escape(slot_id)}', this.checked)"> Согласен на использование AI</label>
</div>"""

    return f"""<div class="{classes}" data-slot-id="{escape(slot_id)}">
  <div class="slot-header">
    <span>{escape(slot_id)}</span>
    <span>{escape(slot.get('ratio', ''))}</span>
  </div>
  <div class="slot-meta">{escape(slot.get('block_id', ''))}</div>
  {photo_html}
  {ai_banner}
</div>"""


def render_board(catalog: dict, selections_draft: dict, out_path: Path) -> None:
    """Render photo-board.html from catalog + draft selections."""
    template = TEMPLATE_PATH.read_text()
    photos = catalog.get("photos", []) or []
    slots = selections_draft.get("slots", []) or []
    photos_by_id = {p["id"]: p for p in photos}

    photos_html = "\n".join(_photo_card(p) for p in photos)
    slots_html = "\n".join(_slot_card(s, photos_by_id) for s in slots)
    initial_state = json.dumps({"slots": slots}, ensure_ascii=False)

    rendered = (template
        .replace("{{PHOTO_COUNT}}", str(len(photos)))
        .replace("{{SLOT_COUNT}}", str(len(slots)))
        .replace("{{PHOTOS_HTML}}", photos_html)
        .replace("{{SLOTS_HTML}}", slots_html)
        .replace("{{INITIAL_STATE_JSON}}", initial_state)
    )
    Path(out_path).write_text(rendered, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--draft", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    catalog = yaml.safe_load(Path(args.catalog).read_text())
    draft = yaml.safe_load(Path(args.draft).read_text())
    render_board(catalog, draft, Path(args.out))


if __name__ == "__main__":
    main()

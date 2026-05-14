#!/usr/bin/env python3
"""Render photo-preview.html — 'photos in their slot positions' for final approval."""
from html import escape
from pathlib import Path

import yaml


PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Photo Preview — фото в местах</title>
<style>
body { font-family: ui-sans-serif, system-ui; margin: 0; padding: 24px; background: #f5f5f4; }
h1 { font-size: 20px; }
.slot { background: white; border-radius: 8px; padding: 16px; margin-bottom: 16px; border: 1px solid #e5e5e4; }
.slot.ai { border-color: #c47a3a; }
.slot.placeholder { border-color: #aaa; background: #fafafa; }
.slot-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.badge.client { background: #ddf; color: #1e3a8a; }
.badge.ai { background: #c47a3a; color: white; }
.badge.placeholder { background: #888; color: white; }
.images { display: grid; grid-template-columns: 1fr 200px; gap: 16px; align-items: start; }
.images img { max-width: 100%; border-radius: 4px; border: 1px solid #e5e5e4; }
.controls { text-align: center; padding: 24px; }
button { padding: 12px 24px; background: #1e3a8a; color: white; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
</style>
</head><body>
<h1>📸 Фото в макетных местах</h1>
<p>Проверь как выглядят фотки в финальной композиции. Если всё ок — переходи в композицию страницы.</p>
{{SLOTS_HTML}}
<div class="controls">
  <button onclick="alert('Approve flow handled by photo-curator agent — return to chat.')">✓ Утвердить и собрать composed.html</button>
</div>
</body></html>"""


STRATEGY_LABELS = {
    "bring-your-own": ("client", "Фото клиента"),
    "generate": ("ai", "AI-генерация"),
    "placeholder": ("placeholder", "Плейсхолдер"),
}


def _slot_block(slot: dict) -> str:
    strategy = slot.get("strategy", "placeholder")
    badge_class, badge_text = STRATEGY_LABELS.get(strategy, ("placeholder", "—"))
    processed = slot.get("processed") or {}
    desktop = processed.get("desktop") or ""
    mobile = processed.get("mobile")

    images_html = f'<img src="{escape(desktop)}" alt="desktop">'
    if mobile:
        images_html += f'<img src="{escape(mobile)}" alt="mobile" style="max-width:200px">'

    slot_class = "slot"
    if strategy == "generate":
        slot_class += " ai"
    elif strategy == "placeholder":
        slot_class += " placeholder"

    return f"""<div class="{slot_class}">
  <div class="slot-header">
    <span>{escape(slot['slot_id'])} <small style="font-weight:400;color:#888">({escape(slot.get('block_id',''))})</small></span>
    <span class="badge {badge_class}">{escape(badge_text)}</span>
  </div>
  <div class="images">{images_html}</div>
</div>"""


def render_preview(selections: dict, out_path: Path) -> None:
    slots = selections.get("slots", []) or []
    slots_html = "\n".join(_slot_block(s) for s in slots)
    out = PREVIEW_TEMPLATE.replace("{{SLOTS_HTML}}", slots_html)
    Path(out_path).write_text(out, encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selections", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sel = yaml.safe_load(Path(args.selections).read_text())
    render_preview(sel, Path(args.out))


if __name__ == "__main__":
    main()

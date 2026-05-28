"""Generate side-by-side mockup preview (variant A + B) from visual-concept + prototype.

CLI:
  python generate-mockup.py --concept path/visual-concept.yaml \
    --prototype path/prototype.yaml --output path/mockup-preview.html
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml


def build_variant_b(palette: dict) -> dict:
    """Build alternative palette interpretation (lighter if dark, darker if light)."""
    bg = palette.get("bg", "#FFFFFF")
    h = bg.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    accent = palette.get("accent", "#C9A84C")

    if brightness < 100:
        new_bg = "#1C1C1E"
        new_surface = "#2C2C2E"
        new_text = "#FFFFFF"
        variant_desc = "чуть светлее, мягче"
    else:
        new_bg = "#F0EDE8"
        new_surface = "#E8E4DE"
        new_text = "#111111"
        variant_desc = "тёплые нейтралы, уютнее"

    return {
        "bg": new_bg,
        "accent": accent,
        "text": new_text,
        "surface": new_surface,
        "_variant_desc": variant_desc,
    }


def _extract_hero(blocks: list) -> dict:
    for b in blocks:
        if b.get("type") == "hero":
            return b.get("content", {})
    return blocks[0].get("content", {}) if blocks else {}


def _extract_second_block(blocks: list) -> dict:
    for b in sorted(blocks, key=lambda x: x.get("position", 99)):
        if b.get("type") != "hero":
            return b
    return {}


def _render_hero_block(content: dict, palette: dict) -> str:
    headline = content.get("headline", "Заголовок лендинга")
    subheadline = content.get("subheadline", "")
    cta = content.get("cta_primary", "Узнать больше")
    badges = content.get("badges", [])

    bg = palette["bg"]
    accent = palette["accent"]
    text = palette["text"]

    badges_html = "".join(
        f'<span style="border:1px solid {accent};color:{accent};padding:4px 12px;border-radius:4px;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;">{b}</span>'
        for b in (badges if isinstance(badges, list) else [])
    )

    return f"""
<div style="background:{bg};padding:80px 40px;text-align:center;min-height:400px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;">
  <div style="width:60px;height:2px;background:{accent};"></div>
  <h1 style="color:{text};font-size:clamp(2rem,5vw,3.5rem);font-weight:700;line-height:1.1;max-width:700px;margin:0;">{headline}</h1>
  {f'<p style="color:{text};opacity:.7;font-size:1.1rem;max-width:500px;margin:0;">{subheadline}</p>' if subheadline else ''}
  <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">
    <a style="background:{accent};color:{bg};padding:14px 32px;border-radius:4px;font-weight:700;font-size:14px;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;">{cta}</a>
  </div>
  {f'<div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:center;">{badges_html}</div>' if badges_html else ''}
</div>"""


def _render_second_block(block: dict, palette: dict) -> str:
    if not block:
        return ""
    content = block.get("content", {})
    btype = block.get("type", "")
    headline = content.get("headline", "")
    body = content.get("body", content.get("body_1", ""))

    bg = palette.get("surface", palette["bg"])
    text = palette["text"]
    accent = palette["accent"]

    return f"""
<div style="background:{bg};padding:60px 40px;text-align:center;">
  {f'<div style="width:40px;height:2px;background:{accent};margin:0 auto 16px;"></div>' if headline else ''}
  {f'<h2 style="color:{text};font-size:1.8rem;font-weight:700;margin:0 0 16px;">{headline}</h2>' if headline else ''}
  {f'<p style="color:{text};opacity:.7;max-width:600px;margin:0 auto;line-height:1.7;">{body}</p>' if body else ''}
  {f'<p style="color:{text};opacity:.4;font-size:.85rem;margin:16px 0 0;font-style:italic;">[{btype} block]</p>' if not body else ''}
</div>"""


def generate_mockup(concept_path: str, prototype_path: str, output_path: str) -> int:
    concept_file = Path(concept_path)
    if not concept_file.exists():
        print(f"ERROR: concept not found: {concept_path}", file=sys.stderr)
        return 1

    proto_file = Path(prototype_path)
    if not proto_file.exists():
        print(f"ERROR: prototype not found: {prototype_path}", file=sys.stderr)
        return 1

    concept = yaml.safe_load(concept_file.read_text(encoding="utf-8")) or {}
    proto = yaml.safe_load(proto_file.read_text(encoding="utf-8")) or {}

    palette_a = concept.get("palette", {"bg": "#FFFFFF", "accent": "#000000", "text": "#000000"})
    palette_b = build_variant_b(palette_a)
    concept_name = concept.get("name", "Концепт")
    blocks = proto.get("blocks", [])

    hero_content = _extract_hero(blocks)
    second_block = _extract_second_block(blocks)

    variant_b_desc = palette_b.pop("_variant_desc", "альтернативный")

    hero_a = _render_hero_block(hero_content, palette_a)
    second_a = _render_second_block(second_block, palette_a)
    hero_b = _render_hero_block(hero_content, palette_b)
    second_b = _render_second_block(second_block, palette_b)

    mood_tags = " · ".join(concept.get("mood", []))

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup Preview — {concept_name}</title>
  <link href="https://fonts.bunny.net/css?family=inter:400,500,700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: #EFEFEF; padding: 2rem; }}
    .header {{ text-align: center; margin-bottom: 2rem; }}
    .header h1 {{ font-size: 1.4rem; color: #333; margin-bottom: .5rem; }}
    .header p {{ color: #666; font-size: .9rem; }}
    .variants {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }}
    @media (max-width: 900px) {{ .variants {{ grid-template-columns: 1fr; }} }}
    .variant {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,.1); }}
    .variant-label {{ padding: 16px 20px; background: #F8F8F8; border-bottom: 1px solid #E0E0E0; }}
    .variant-label strong {{ font-size: 1rem; color: #111; }}
    .variant-label span {{ font-size: .8rem; color: #888; margin-left: 8px; }}
    .variant-content {{ overflow: hidden; }}
    .palette-strip {{ display: flex; padding: 8px 16px; gap: 8px; background: #F8F8F8; flex-wrap: wrap; }}
    .palette-swatch {{ display: flex; align-items: center; gap: 6px; font-size: .75rem; color: #555; }}
    .palette-swatch-dot {{ width: 16px; height: 16px; border-radius: 50%; border: 1px solid rgba(0,0,0,.1); flex-shrink: 0; }}
    .actions {{ padding: 16px 20px; background: #F8F8F8; border-top: 1px solid #E0E0E0; display: flex; gap: 12px; justify-content: center; }}
    .btn-choose {{ padding: 10px 24px; border-radius: 6px; font-size: .9rem; font-weight: 600; cursor: pointer; border: 2px solid #333; background: #333; color: #fff; }}
    .btn-choose:hover {{ background: #111; }}
    .footer {{ text-align: center; margin-top: 2rem; font-size: .75rem; color: #aaa; }}
    .feedback-note {{ text-align: center; margin-top: 1rem; font-size: .85rem; color: #666; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Mockup Preview — {concept_name}</h1>
    <p>Настроение: {mood_tags} · Два варианта реализации — выбери или опиши правки</p>
  </div>

  <div class="variants">
    <div class="variant">
      <div class="variant-label">
        <strong>Вариант A</strong>
        <span>— буквальная реализация концепта</span>
      </div>
      <div class="palette-strip">
        {''.join(f'<div class="palette-swatch"><div class="palette-swatch-dot" style="background:{v}"></div><span>{k}: {v}</span></div>' for k, v in palette_a.items())}
      </div>
      <div class="variant-content">{hero_a}{second_a}</div>
      <div class="actions">
        <button class="btn-choose" onclick="alert('Выбран Вариант A. Напиши в чат: «Вариант A» или опиши правки.')">Выбрать A</button>
      </div>
    </div>

    <div class="variant">
      <div class="variant-label">
        <strong>Вариант B</strong>
        <span>— {variant_b_desc}</span>
      </div>
      <div class="palette-strip">
        {''.join(f'<div class="palette-swatch"><div class="palette-swatch-dot" style="background:{v}"></div><span>{k}: {v}</span></div>' for k, v in palette_b.items())}
      </div>
      <div class="variant-content">{hero_b}{second_b}</div>
      <div class="actions">
        <button class="btn-choose" onclick="alert('Выбран Вариант B. Напиши в чат: «Вариант B» или опиши правки.')">Выбрать B</button>
      </div>
    </div>
  </div>

  <p class="feedback-note">Напиши в чат: «Вариант A», «Вариант B», или опиши правки — например «Вариант A, но акцент холоднее»</p>
  <p class="footer">Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')} · landing-system mockup</p>
</body>
</html>"""

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"OK: wrote {output_path}")
    return 0


def main(argv: list | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--concept", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--output", required=True)
    ns = p.parse_args(args)
    return generate_mockup(ns.concept, ns.prototype, ns.output)


if __name__ == "__main__":
    sys.exit(main())

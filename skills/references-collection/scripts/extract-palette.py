"""Extract color palette and typography from text description or image analysis.

CLI:
  python extract-palette.py --text "описание стиля" --source "OFFtrail" --output refs-palette.html
  python extract-palette.py --refs-yaml index.yaml --output refs-palette.html
"""
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

import yaml

HEX_RE = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b')

KNOWN_FONTS = [
    "Inter", "Roboto", "Open Sans", "Montserrat", "Lato", "Poppins",
    "Archivo Black", "Archivo", "Manrope", "Raleway", "Nunito",
    "Playfair Display", "Merriweather", "Source Sans", "DM Sans",
    "Space Grotesk", "Plus Jakarta Sans", "Outfit", "Unbounded",
]

COLOR_ROLES = {
    "фон": "background", "background": "background", "bg": "background",
    "акцент": "accent", "accent": "accent", "cta": "accent",
    "текст": "text", "text": "text",
    "footer": "footer", "футер": "footer",
    "surface": "surface", "карточк": "surface",
}

COLOR_NAMES = {
    "#2B72B8": "насыщенный синий, энергичный",
    "#1A56DB": "ярко-синий, технологичный",
    "#0A0A0A": "почти чёрный, глубокий",
    "#161616": "тёмно-серый, минималистичный",
    "#FFFFFF": "белый, чистый",
    "#F5F5F5": "светло-серый, мягкий",
    "#C9A84C": "матовое золото, премиум",
    "#E8407A": "ярко-розовый, игривый",
}


def _guess_color_name(hex_color: str) -> str:
    h = hex_color.upper()
    if h in COLOR_NAMES:
        return COLOR_NAMES[h]
    r = int(h[1:3], 16)
    g = int(h[3:5], 16)
    b = int(h[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness < 50:
        return "тёмный, глубокий"
    if brightness > 200:
        return "светлый, чистый"
    if r > g and r > b:
        return "тёплый, акцентный"
    if b > r and b > g:
        return "холодный, технологичный"
    if g > r and g > b:
        return "натуральный, органичный"
    return "нейтральный"


def _guess_role_from_context(hex_color: str, context: str) -> str:
    context_lower = context.lower()
    for keyword, role in COLOR_ROLES.items():
        if keyword in context_lower:
            return role
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness < 60:
        return "background"
    if brightness > 200:
        return "text"
    return "accent"


def parse_text_description(text: str) -> dict:
    """Extract colors and fonts from a text description."""
    colors = []
    seen_hex = set()

    for m in HEX_RE.finditer(text):
        hex_val = "#" + m.group(1).upper()
        if len(hex_val) == 4:
            hex_val = "#" + "".join(c*2 for c in hex_val[1:])
        if hex_val in seen_hex:
            continue
        seen_hex.add(hex_val)
        start = max(0, m.start() - 30)
        context = text[start:m.start()]
        role = _guess_role_from_context(hex_val, context)
        colors.append({
            "hex": hex_val,
            "role": role,
            "label": _guess_color_name(hex_val),
        })

    fonts = []
    for font in KNOWN_FONTS:
        if font.lower() in text.lower():
            fonts.append(font)

    return {"colors": colors, "fonts": fonts}


def render_palette_html(palettes: list, output_path: str) -> None:
    """Render HTML preview of extracted palettes."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    cards_html = ""
    for p in palettes:
        source = p.get("source", "Референс")
        mood = p.get("mood", "")
        fonts = p.get("fonts", [])
        colors = p.get("colors", [])

        swatches = ""
        for c in colors:
            role_label = {
                "background": "Фон", "accent": "Акцент", "text": "Текст",
                "footer": "Footer", "surface": "Surface",
            }.get(c.get("role", ""), c.get("role", ""))
            r = int(c["hex"][1:3], 16)
            g = int(c["hex"][3:5], 16)
            b = int(c["hex"][5:7], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            text_color = "#000000" if brightness > 128 else "#FFFFFF"
            swatches += f"""
            <div class="swatch" style="background:{c['hex']};color:{text_color}">
              <div class="swatch-role">{role_label}</div>
              <div class="swatch-hex">{c['hex']}</div>
              <div class="swatch-label">{c.get('label','')}</div>
            </div>"""

        fonts_html = "".join(f'<span class="font-tag">{f}</span>' for f in fonts) or "<span class='font-tag muted'>не определено</span>"

        cards_html += f"""
        <div class="ref-card">
          <h2 class="ref-title">{source}</h2>
          {f'<div class="ref-mood">Настроение: {mood}</div>' if mood else ''}
          <div class="swatches-row">{swatches}</div>
          <div class="fonts-row"><strong>Типографика:</strong> {fonts_html}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Палитры референсов</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #F8F8F8; color: #111; margin: 0; padding: 2rem; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 2rem; color: #333; }}
    .ref-card {{ background: #fff; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
    .ref-title {{ font-size: 1.2rem; margin: 0 0 .5rem; }}
    .ref-mood {{ font-size: .85rem; color: #666; margin-bottom: 1rem; }}
    .swatches-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 1rem; }}
    .swatch {{ border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
    .swatch-role {{ font-size: .7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: .7; }}
    .swatch-hex {{ font-size: 1rem; font-weight: 700; font-family: monospace; margin: 4px 0; }}
    .swatch-label {{ font-size: .75rem; opacity: .8; }}
    .fonts-row {{ font-size: .9rem; color: #444; }}
    .font-tag {{ display: inline-block; background: #F0F0F0; border-radius: 4px; padding: 2px 10px; margin: 2px; font-size: .85rem; }}
    .font-tag.muted {{ color: #999; }}
    .generated {{ font-size: .75rem; color: #aaa; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>Извлечённые палитры референсов</h1>
  {cards_html if cards_html else '<p style="color:#999">Нет данных о палитрах</p>'}
  <p class="generated">Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</body>
</html>"""

    out.write_text(html, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--text", help="Текстовое описание стиля")
    p.add_argument("--source", default="Референс", help="Название источника")
    p.add_argument("--refs-yaml", help="Путь к index.yaml для batch-обработки")
    p.add_argument("--output", required=True, help="Путь для refs-palette.html")
    ns = p.parse_args(args)

    palettes = []

    if ns.text:
        extracted = parse_text_description(ns.text)
        extracted["source"] = ns.source
        palettes.append(extracted)

    if ns.refs_yaml:
        idx_path = Path(ns.refs_yaml)
        if idx_path.exists():
            data = yaml.safe_load(idx_path.read_text(encoding="utf-8")) or {}
            for ref in data.get("references", []):
                if ref.get("status") == "approved" and ref.get("notes"):
                    extracted = parse_text_description(ref["notes"])
                    extracted["source"] = ref.get("title", ref.get("value", "Референс"))
                    extracted["mood"] = ref.get("mood", "")
                    palettes.append(extracted)

    render_palette_html(palettes, ns.output)
    print(f"OK: wrote {ns.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

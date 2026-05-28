#!/usr/bin/env python3
# skills/photo-styling/scripts/generate-photo-prompts.py
# Fallback for when HUGGINGFACE_TOKEN is not set.
# Generates ChatGPT/Shedevrum-ready prompts for manual photo processing.
# Usage: python generate-photo-prompts.py <photos_dir> <brand_kit_md> <output_md>
import re
import sys
from pathlib import Path

HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")

DEFAULT_PALETTE = ["#1A1A1A", "#FFFFFF", "#C9A84C"]
DEFAULT_TONE = "professional, clean, premium"

PHOTO_TEMPLATES = {
    "portrait": (
        "Remove the background, keep only the person. "
        "Place on a clean {bg_color} background. "
        "Style: {tone}. "
        "Do NOT alter face, age, body proportions or skin tone. "
        "Output: PNG with transparent background, 800×1000 px."
    ),
    "team": (
        "Remove background from this group photo. "
        "Place on {bg_color} studio background. "
        "Style: {tone}, editorial. "
        "Do NOT alter faces or proportions. "
        "Output: PNG transparent BG, 1200×800 px."
    ),
    "product": (
        "Place this product on a clean {bg_color} surface with soft shadow. "
        "Accent color: {accent_color}. "
        "Style: {tone}, product photography. "
        "Output: JPG, 1200×1200 px."
    ),
    "process": (
        "Enhance lighting and colour grade this photo. "
        "Dominant palette: {palette}. Style: {tone}. "
        "Keep composition as-is. Output: JPG, 1600×900 px."
    ),
    "default": (
        "Process this photo for landing page use. "
        "Colour palette: {palette}. Tone: {tone}. "
        "Remove distracting background elements if needed. "
        "Output: JPG, 1200×800 px."
    ),
}


def _guess_template(filename: str) -> str:
    name = Path(filename).stem.lower()
    for key in ("portrait", "team", "product", "process"):
        if key in name:
            return key
    return "default"


def _parse_brand_kit(brand_kit_path: str) -> dict:
    path = Path(brand_kit_path)
    if not path.is_file():
        return {"palette": DEFAULT_PALETTE, "tone": DEFAULT_TONE}

    text = path.read_text(encoding="utf-8", errors="replace")
    colors = HEX_RE.findall(text)
    palette = ["#" + c for c in colors[:5]] if colors else DEFAULT_PALETTE

    tone = DEFAULT_TONE
    tone_match = re.search(r"##\s*Tone\s*\n(.+)", text)
    if tone_match:
        tone = tone_match.group(1).strip()

    return {"palette": palette, "tone": tone}


def generate_prompts(photos: list, brand_kit_path: str, output_path: str) -> int:
    """Generate photo-prompts.md. Returns 0 on success, 1 on error."""
    brand = _parse_brand_kit(brand_kit_path)
    palette = brand["palette"]
    tone = brand["tone"]
    bg_color = palette[0] if palette else "#1A1A1A"
    accent_color = palette[2] if len(palette) > 2 else palette[-1]
    palette_str = ", ".join(palette[:4])

    lines = [
        "# Photo Prompts (ChatGPT / Шедеврум)",
        "",
        "> Сгенерировано автоматически — HUGGINGFACE_TOKEN не задан.",
        "> Скопируй каждый промпт в ChatGPT или Шедеврум вместе с фото.",
        "",
    ]

    if not photos:
        lines += ["_Список фотографий пуст._", ""]
    else:
        for photo in photos:
            tmpl_key = _guess_template(photo)
            prompt = PHOTO_TEMPLATES[tmpl_key].format(
                bg_color=bg_color,
                accent_color=accent_color,
                tone=tone,
                palette=palette_str,
            )
            lines += [
                f"## {photo}",
                "",
                f"**Промпт:**",
                "",
                f"> {prompt}",
                "",
            ]

    try:
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
        return 0
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: generate-photo-prompts.py <photos_dir> <brand_kit_md> <output_md>", file=sys.stderr)
        return 1

    photos_dir = Path(sys.argv[1])
    brand_kit = sys.argv[2]
    output = sys.argv[3]

    photos = sorted(
        p.name for p in photos_dir.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
    ) if photos_dir.is_dir() else []

    return generate_prompts(photos, brand_kit, output)


if __name__ == "__main__":
    sys.exit(main())

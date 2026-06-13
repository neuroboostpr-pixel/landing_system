#!/usr/bin/env python3
# skills/client-assets-collection/scripts/analyze-photo-style.py
# Analyze client photos (palette, contrast, orientation) via Pillow.
# Generates 02_МАТЕРИАЛЫ_КЛИЕНТА/style-report.md with a consistency verdict.
# Usage: python analyze-photo-style.py <photos_dir> <output_report>
import sys
from pathlib import Path

from PIL import Image, ImageStat

PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Thresholds
MIN_PHOTOS_FOR_CONSISTENT = 2   # need at least 2 photos to judge consistency
HUE_SPREAD_THRESHOLD = 80       # avg hue spread (0-255); >80 → inconsistent palette
CONTRAST_LOW = 30               # RMS contrast below this → "flat" lighting


def _dominant_color(img: Image.Image) -> str:
    """Return hex of the single most frequent colour (quantised to 8 colours)."""
    small = img.resize((50, 50)).convert("RGB")
    quantised = small.quantize(colors=8, method=Image.Quantize.MEDIANCUT).convert("RGB")
    pixels = list(quantised.getdata())
    freq: dict = {}
    for px in pixels:
        freq[px] = freq.get(px, 0) + 1
    dominant = max(freq, key=lambda k: freq[k])
    return "#{:02X}{:02X}{:02X}".format(*dominant)


def _rms_contrast(img: Image.Image) -> float:
    """Root-mean-square contrast of the luminance channel."""
    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    return stat.rms[0]


def analyze_photo(path: str) -> dict:
    """Return dict with orientation, dominant_color, contrast for one photo."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    orientation = "landscape" if w >= h else "portrait"
    return {
        "filename": Path(path).name,
        "orientation": orientation,
        "dominant_color": _dominant_color(img),
        "contrast": round(_rms_contrast(img), 1),
        "width": w,
        "height": h,
    }


def _verdict(analyses: list) -> str:
    if len(analyses) < MIN_PHOTOS_FOR_CONSISTENT:
        return "не хватает"

    orientations = {a["orientation"] for a in analyses}
    contrasts = [a["contrast"] for a in analyses]
    low_contrast_count = sum(1 for c in contrasts if c < CONTRAST_LOW)

    if low_contrast_count > len(analyses) // 2:
        return "нужна обработка"
    if len(orientations) > 1:
        return "нужна обработка"
    return "однородный"


def generate_report(photos: list, output_path: str) -> int:
    """Analyse photos and write style-report.md. Returns 0 on success."""
    analyses = []
    errors = []
    for path in photos:
        try:
            analyses.append(analyze_photo(path))
        except Exception as exc:  # noqa: BLE001 — surface file-level errors softly
            errors.append(f"{Path(path).name}: {exc}")

    verdict = _verdict(analyses)

    lines = [
        "# Photo Style Report",
        "",
        f"**Вердикт:** {verdict}",
        "",
        "| Файл | Ориентация | Доминирующий цвет | Контраст |",
        "|------|-----------|-------------------|----------|",
    ]
    for a in analyses:
        swatch = f"![{a['dominant_color']}](https://via.placeholder.com/20/{a['dominant_color'].lstrip('#')})"
        lines.append(
            f"| {a['filename']} | {a['orientation']} | {swatch} {a['dominant_color']} | {a['contrast']} |"
        )

    if errors:
        lines += ["", "## Ошибки при анализе", ""]
        lines += [f"- {e}" for e in errors]

    lines += [
        "",
        "## Рекомендации",
        "",
    ]
    if verdict == "однородный":
        lines.append("✅ Фотографии однородны — можно передавать в photo-stylist без правок.")
    elif verdict == "нужна обработка":
        lines.append(
            "⚠️ Обнаружены различия в ориентации или низкий контраст. "
            "Рекомендуется: выровнять освещение, привести к единой ориентации перед обработкой."
        )
    else:
        lines.append(
            "❌ Фотографий мало. Запросите у клиента дополнительные материалы "
            "(минимум 3–5 для полного анализа)."
        )

    try:
        Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: analyze-photo-style.py <photos_dir> <output_report>", file=sys.stderr)
        return 1

    photos_dir = Path(sys.argv[1])
    output = sys.argv[2]

    photos = sorted(
        str(p) for p in photos_dir.iterdir()
        if p.is_file() and p.suffix.lower() in PHOTO_EXTS
    ) if photos_dir.is_dir() else []

    if not photos:
        print(f"No photos found in {photos_dir}", file=sys.stderr)

    return generate_report(photos, output)


if __name__ == "__main__":
    sys.exit(main())

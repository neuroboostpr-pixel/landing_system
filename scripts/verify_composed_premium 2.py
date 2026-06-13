#!/usr/bin/env python3
"""Premium-проверка composed.html — v2 (B2, спека reference-driven flow §3.2).

ОБЯЗАТЕЛЬНО (fail):
  - CSS-токены в :root
  - clamp() для типографики
  - движение (IntersectionObserver / @keyframes / transition)
  - hover-эффекты
  - prefers-reduced-motion
  - production-голова: og:title + og:image, favicon, theme-color, шрифты
  - ЗАПРЕТ: эмодзи в заголовках <h1>–<h3>

РЕКОМЕНДАЦИИ (warn, не fail): glassmorphism, parallax, slider, lightbox,
gradient text, count-up, clip-path — добавляются под потребность места
(docs/standards/design-elements-rules.md), а не «обязательным набором».

Exit: 0 PASS · 1 FAIL · 2 файл не найден.
Usage: verify_composed_premium.py <composed.html>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED: list[tuple[str, str]] = [
    (r":root\s*\{", "CSS-токены в :root"),
    (r"clamp\(", "clamp() для адаптивной типографики"),
    (r"IntersectionObserver|@keyframes|transition\s*:", "движение (IO/@keyframes/transition)"),
    (r":hover\s*\{|:hover\s*,", "hover-эффекты"),
    (r"@media\s*\(\s*prefers-reduced-motion", "prefers-reduced-motion"),
    (r"property=[\"']og:title", "OG: og:title"),
    (r"property=[\"']og:image", "OG: og:image"),
    (r"rel=[\"'](icon|shortcut icon|apple-touch-icon)", "favicon link"),
    (r"name=[\"']theme-color", "meta theme-color"),
    (r"fonts\.|@font-face|font-family", "подключение шрифтов"),
]

RECOMMENDED: list[tuple[str, str]] = [
    (r"backdrop-filter\s*:", "glassmorphism (backdrop-filter)"),
    (r"(scrollY|[^\w]y)\s*\*\s*0\.\d", "parallax"),
    (r"slider-track|swiper|slick", "слайдер"),
    (r"lightbox", "lightbox"),
    (r"text-fill-color\s*:\s*transparent", "gradient text"),
    (r"requestAnimationFrame|count-up", "count-up"),
    (r"clip-path\s*:|mask-image\s*:", "нестандартные формы"),
    (r"translateY\(-\d", "hover lift"),
]

# эмодзи-диапазоны (основные блоки)
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF\U0001F900-\U0001F9FF✅❌❗❤]"
)
_HEADING = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.DOTALL | re.IGNORECASE)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_composed_premium.py <composed.html>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: файл не найден: {path}", file=sys.stderr)
        return 2
    html = path.read_text(encoding="utf-8", errors="replace")

    print("═" * 55)
    print(f"Premium verify v2 — {path}")
    print("═" * 55)

    failed: list[str] = []
    for pattern, desc in REQUIRED:
        ok = re.search(pattern, html) is not None
        print(f"  {'✓' if ok else '✗'}  {desc}")
        if not ok:
            failed.append(desc)

    # запрет: эмодзи в заголовках
    emoji_headings = [
        m.group(0)[:60] for m in _HEADING.finditer(html) if _EMOJI.search(m.group(1))
    ]
    if emoji_headings:
        print("  ✗  ЗАПРЕТ: эмодзи в заголовках <h1>–<h3>:")
        for h in emoji_headings[:5]:
            print(f"       {h}")
        failed.append("эмодзи в заголовках")
    else:
        print("  ✓  нет эмодзи в заголовках")

    print("  — рекомендации (не блокируют):")
    for pattern, desc in RECOMMENDED:
        ok = re.search(pattern, html) is not None
        print(f"  {'·' if ok else '○'}  {desc}{'' if ok else ' (нет — ок, если месту не нужно)'}")

    print("─" * 55)
    if failed:
        print(f"FAIL: {len(failed)} обязательных пунктов не выполнено:")
        for f in failed:
            print(f"  - {f}")
        print("Стандарты: docs/standards/premium-07b-checklist.md, "
              "docs/standards/design-elements-rules.md")
        return 1
    print("PASS: все обязательные premium-пункты выполнены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

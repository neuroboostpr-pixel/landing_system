#!/usr/bin/env python3
"""Гейт КОЛЛАЖ/ГЛУБИНА (строгий, измеримый) для 07c/07f — reference-driven §3.

Слабый предшественник проверял НАЛИЧИЕ паттерна (есть один blob → галочка),
поэтому плоская вёрстка «карточки в ряд» проходила. Этот гейт измеряет
КОМПОЗИЦИЮ количественно: сколько слоёв, есть ли наезды за рамку, парящий
декор, крупная типографика, вырезанное фото на форме, глубина-свечение.

Критерии (каждый — порог, а не «есть/нет»):
  1. Слои:        >= MIN_ABS элементов position:absolute (реальная многослойность)
  2. Наезды:      >= MIN_OVERLAP «выходов за рамку» (negative margin / translate(-…)/ inset:-)
  3. Парящий декор: >= MIN_DECOR абсолютных декор-элементов (ромбы/блобы/росчерки)
  4. Крупная типографика: hero clamp с верхом >= 4rem (огромный заголовок)
  5. Вырезанное фото на форме: img поверх блоба/absolute (не прямоугольник в колонке)
  6. Глубина-свечение: >= MIN_GLOW radial-gradient / крупных мягких теней

PASS: выполнено >= CRITERIA_MIN критериев. Иначе FAIL со списком чего не хватает.

Exit 0 — OK; 1 — плоско; 2 — файл не найден.
Usage: verify_collage_depth.py <composed.html>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MIN_ABS = 6          # элементов position:absolute
MIN_OVERLAP = 2      # наездов за рамку
MIN_DECOR = 2        # парящих декор-элементов
MIN_GLOW = 2         # свечений/глубоких теней
CRITERIA_MIN = 5     # из 6 критериев


def main(path: Path) -> int:
    if not path.is_file():
        print(f"ERROR: файл не найден: {path}", file=sys.stderr)
        return 2
    html = path.read_text(encoding="utf-8", errors="replace")

    results: list[tuple[bool, str]] = []

    # 1. Слои
    n_abs = len(re.findall(r"position\s*:\s*absolute", html))
    results.append((n_abs >= MIN_ABS,
                    f"слои position:absolute: {n_abs} (нужно ≥{MIN_ABS})"))

    # 2. Наезды за рамку: negative margin / translate с минусом / inset с минусом
    overlaps = (
        len(re.findall(r"margin[\w-]*\s*:\s*[^;]*-\d", html))
        + len(re.findall(r"translate[XY]?\([^)]*-\d", html))
        + len(re.findall(r"inset\s*:\s*[^;]*-\d", html))
        + len(re.findall(r"(top|bottom|left|right)\s*:\s*-\d", html))
    )
    results.append((overlaps >= MIN_OVERLAP,
                    f"наезды за рамку (neg margin/translate/inset): {overlaps} (нужно ≥{MIN_OVERLAP})"))

    # 3. Парящий декор: классы decor/shape/diamond/ромб/blob с absolute, или svg-декор
    decor = len(re.findall(r'class="[^"]*\b(decor|shape|diamond|blob|romb|float|spark|glow-orb)\b', html, re.I))
    results.append((decor >= MIN_DECOR,
                    f"парящий декор-элементы: {decor} (нужно ≥{MIN_DECOR})"))

    # 4. Крупная типографика: clamp с верхней границей >= 4rem где-нибудь в hero h1
    big = re.findall(r"clamp\([^)]*?(\d(?:\.\d)?)rem\s*\)", html)
    big_max = max([float(x) for x in big], default=0)
    results.append((big_max >= 4.0,
                    f"крупная типографика: max clamp top {big_max}rem (нужно ≥4rem)"))

    # 5. Вырезанное фото на форме: img рядом с blob/absolute-подложкой
    has_blob = re.search(r'class="[^"]*\bblob\b|border-radius\s*:\s*\d+%\s+\d+%', html)
    has_overlap_img = re.search(r'class="[^"]*\b(cutout|hero-photo|on-shape)\b', html)
    results.append((bool(has_blob and has_overlap_img),
                    "вырезанное фото на форме-подложке (blob + cutout/hero-photo)"))

    # 6. Глубина-свечение
    glow = (len(re.findall(r"radial-gradient", html))
            + len(re.findall(r"box-shadow\s*:[^;]*\b(4[0-9]|[5-9][0-9]|\d{3})px", html)))
    results.append((glow >= MIN_GLOW,
                    f"свечение/глубокие тени: {glow} (нужно ≥{MIN_GLOW})"))

    print("═" * 55)
    print(f"Collage depth (строгий) — {path}")
    print("═" * 55)
    passed = 0
    for ok, desc in results:
        print(f"  {'✓' if ok else '✗'}  {desc}")
        if ok:
            passed += 1

    print("─" * 55)
    if passed < CRITERIA_MIN:
        print(f"FAIL: выполнено {passed}/{len(results)} критериев коллажа "
              f"(нужно ≥{CRITERIA_MIN}). Вёрстка плоская — это «карточки в ряд», "
              f"а не композиция со слоями. См. reference-driven §3 + collage-plan.md.")
        return 1
    print(f"PASS: коллаж — {passed}/{len(results)} критериев (порог {CRITERIA_MIN}).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify_collage_depth.py <composed.html>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))

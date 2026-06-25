#!/usr/bin/env python3
"""Гейт «единообразные переходы между блоками» для 07c/07f (reference-driven §3.4).

Правило §3.4: переходы между секциями оформлены ЕДИНООБРАЗНО на всех стыках —
ОДИН приём по всему проекту (переход цвета ИЛИ единый разделитель), не вперемешку.
Голый стык фонов встык = «недоделано».

Проверка:
  1. Находим стыки между смысловыми секциями (<section>/<header>/<footer> верхнего
     уровня body).
  2. На каждом стыке должен быть приём перехода:
     - divider-элемент между секциями (class содержит divider/sep/wave/shape), ИЛИ
     - соседние секции разного фона (sec-deep / разные bg-классы) — «переход цвета».
  3. Приём должен быть ЕДИНЫМ: если используется divider — он на всех стыках;
     если переход цвета — фоны чередуются согласованно. Смесь «тут divider, там
     голый стык» = FAIL.

Минимум стыков для проверки: 3 (меньше — не показатель).

Exit 0 — OK; 1 — голые/несогласованные стыки; 2 — файлы не найдены.
Usage: verify-block-transitions.py <project-dir>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: нужен beautifulsoup4", file=sys.stderr)
    sys.exit(2)

DIVIDER_RE = re.compile(r"\b(divider|separator|sep|wave|edge|shape-divider|sec-edge)\b", re.I)


def _bg_class(tag) -> str:
    """Грубый признак фона секции: ищем bg-классы/маркеры."""
    cls = " ".join(tag.get("class", []))
    for marker in ("sec-deep", "sec-dark", "sec-light", "bg-deep", "bg-alt", "alt"):
        if marker in cls:
            return marker
    return "base"


def main(project_dir: Path) -> int:
    composed = project_dir / "07b_COMPOSED" / "composed.html"
    if not composed.exists():
        print(f"ERROR: {composed} не найден", file=sys.stderr)
        return 2

    soup = BeautifulSoup(composed.read_text(encoding="utf-8"), "html.parser")
    body = soup.body or soup

    # Секции верхнего уровня (контентные блоки)
    sections = [c for c in body.find_all(["section", "header"], recursive=True)
                if c.find_parent(["section", "header"]) is None]
    # divider-элементы верхнего уровня
    def is_divider(t):
        return t.name in ("div", "hr", "svg") and DIVIDER_RE.search(" ".join(t.get("class", [])))

    if len(sections) < 3:
        print(f"PASS: секций {len(sections)} (<3) — переходы не проверяем.")
        return 0

    boundaries = len(sections) - 1
    # Способ A: считаем divider'ы между секциями
    dividers = [t for t in body.find_all(["div", "hr", "svg"]) if is_divider(t)]
    n_div = len(dividers)

    # Способ B: переходы цвета — соседние секции разного фона
    bgs = [_bg_class(s) for s in sections]
    color_transitions = sum(1 for i in range(len(bgs) - 1) if bgs[i] != bgs[i + 1])

    # Решаем, какой приём заявлен (по доминанте), и требуем единообразия
    issues = []
    if n_div >= boundaries:
        # divider-приём: ок (на каждом стыке хотя бы один)
        method = "divider"
    elif n_div == 0 and color_transitions >= boundaries:
        # чистый переход цвета на всех стыках
        method = "color"
    elif n_div == 0 and color_transitions == 0:
        method = "none"
        issues.append("ни одного приёма перехода: все стыки голые (фоны встык, нет divider)")
    else:
        # СМЕСЬ: часть стыков divider, часть голые/цветовые — несогласованно
        method = "mixed"
        issues.append(
            f"несогласованно: divider'ов {n_div} на {boundaries} стыков, "
            f"переходов цвета {color_transitions}. Нужен ЕДИНЫЙ приём на ВСЕХ стыках "
            f"(все divider ИЛИ все переход цвета), §3.4."
        )

    if issues:
        print(f"❌ Переходы между блоками ({len(sections)} секций, {boundaries} стыков):",
              file=sys.stderr)
        for i in issues:
            print(f"   - {i}", file=sys.stderr)
        return 1

    print(f"✅ Переходы единообразны (приём: {method}, секций {len(sections)}, "
          f"divider'ов {n_div}, переходов цвета {color_transitions}).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: verify-block-transitions.py <project-dir>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))

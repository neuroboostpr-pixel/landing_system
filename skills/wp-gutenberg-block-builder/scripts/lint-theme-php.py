#!/usr/bin/env python3
"""C2 — линтер собранной wp-темы против болячек сборки (спека §4.2).

Проверки:
  1. block.php: нет <script> (скрипты — только в файлы темы; в блоке они
     попадают в превью редактора и ломают его).
  2. block.php: каждая объявленная function обёрнута в function_exists
     (повторное объявление при нескольких инстансах блока роняет редактор).
  3. functions.php: НЕТ add_theme_support('wp-block-styles') — дефолтные
     стили WP перебивают наши кнопки.
  4. CSS темы: есть правило ширины верхних обёрток блоков (max-width: none
     для .wp-block*) и baseline img-geometry (height: auto / object-fit) —
     наша CSS-геометрия приоритетнее размеров, которые навешивает WP.

Usage: lint-theme-php.py <theme_dir>
Exit: 0 PASS · 1 FAIL · 2 нет папки.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def lint_theme(theme: Path) -> list[str]:
    problems: list[str] = []

    # 1+2: block.php
    for block_php in sorted(theme.glob("blocks/*/block.php")):
        text = block_php.read_text(encoding="utf-8", errors="replace")
        rel = block_php.relative_to(theme)
        if re.search(r"<script\b", text, re.IGNORECASE):
            problems.append(
                f"{rel}: <script> внутри block.php — скрипты только в файлы темы "
                f"(assets/js/), иначе ломается превью редактора")
        for m in re.finditer(r"\bfunction\s+([a-zA-Z_]\w*)\s*\(", text):
            fname = m.group(1)
            if f"function_exists('{fname}')" not in text and \
               f'function_exists("{fname}")' not in text:
                problems.append(
                    f"{rel}: function {fname}() не обёрнута в function_exists — "
                    f"повторное объявление уронит редактор")

    # 3: functions.php
    functions_php = theme / "functions.php"
    if functions_php.exists():
        text = functions_php.read_text(encoding="utf-8", errors="replace")
        if re.search(r"add_theme_support\(\s*['\"]wp-block-styles['\"]", text):
            problems.append(
                "functions.php: add_theme_support('wp-block-styles') подключает "
                "дефолтные стили WP, которые перебивают кнопки — убрать")

    # 4: CSS
    css_texts = []
    for css in sorted(theme.glob("assets/css/*.css")) + sorted(theme.glob("*.css")):
        css_texts.append(css.read_text(encoding="utf-8", errors="replace"))
    css_all = "\n".join(css_texts)
    if css_all.strip():
        if not re.search(r"\.wp-block[^{]*\{[^}]*max-width\s*:\s*none", css_all, re.DOTALL):
            problems.append(
                "CSS темы: нет правила ширины для верхних обёрток блоков "
                "(.wp-block… { max-width: none; }) — сетка будет зажата («масштаб поехал»)")
        if not re.search(r"img[^{]*\{[^}]*(height\s*:\s*auto|object-fit)", css_all, re.DOTALL):
            problems.append(
                "CSS темы: нет baseline img-geometry (height: auto / object-fit) — "
                "размеры от WP перебьют CSS-геометрию форм")
    else:
        problems.append("CSS темы не найден (assets/css/*.css)")

    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: lint-theme-php.py <theme_dir>", file=sys.stderr)
        return 2
    theme = Path(sys.argv[1])
    if not theme.is_dir():
        print(f"ERROR: нет папки {theme}", file=sys.stderr)
        return 2
    problems = lint_theme(theme)
    if problems:
        print(f"FAIL: {len(problems)} болячек сборки (спека reference-driven §4.2):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("PASS: болячек сборки не найдено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

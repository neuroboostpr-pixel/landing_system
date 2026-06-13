#!/usr/bin/env python3
"""C3 — проверка токенизации цветов (спека reference-driven flow §4.3).

Прямые цвета (#hex / rgb() / rgba() / hsl() / hsla()) допустимы ТОЛЬКО:
  - внутри определения токенов `:root { ... }`;
  - в whitelist бренд-цветов (мессенджеры, точка «онлайн»);
  - в `<meta name="theme-color">` (там переменные не работают);
  - на строке с маркером `/* token-exempt */`.

Любой другой прямой цвет «протекает» при переключении палитры → ошибка сборки.

Usage: verify_tokens.py <file.html|file.css> [...]
Exit: 0 PASS · 1 FAIL · 2 нет файлов.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# бренд-цвета, которые легально хардкодить (спека §4.3)
WHITELIST = {
    "#25d366",  # WhatsApp
    "#0088cc", "#2aabee", "#229ed9",  # Telegram
    "#4bb34b", "#31a24c", "#00c853",  # зелёная точка «онлайн»
    "#fff", "#ffffff", "#000", "#000000",  # базовые в og/manifest-контексте не считаем? НЕТ:
}
# ВАЖНО: белый/чёрный НЕ исключение в CSS — убираем их из whitelist:
WHITELIST -= {"#fff", "#ffffff", "#000", "#000000"}

COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)"
)
EXEMPT_MARKER = "token-exempt"


def _root_spans(text: str) -> list[tuple[int, int]]:
    """Диапазоны содержимого блоков :root { ... } (по простому скобочному счёту)."""
    spans = []
    for m in re.finditer(r":root\s*\{", text):
        depth = 1
        i = m.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        spans.append((m.end(), i))
    return spans


def _theme_color_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end())
            for m in re.finditer(r"<meta[^>]*theme-color[^>]*>", text, re.IGNORECASE)]


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    ok_spans = _root_spans(text) + _theme_color_spans(text)
    violations = []
    for m in COLOR_RE.finditer(text):
        pos = m.start()
        if any(a <= pos < b for a, b in ok_spans):
            continue
        value = m.group(0)
        if value.lower() in WHITELIST:
            continue
        # var(--x, #fallback) — fallback внутри var() допускаем? НЕТ — тоже течёт.
        line_start = text.rfind("\n", 0, pos) + 1
        line_end = text.find("\n", pos)
        line = text[line_start:line_end if line_end != -1 else len(text)]
        if EXEMPT_MARKER in line:
            continue
        lineno = text.count("\n", 0, pos) + 1
        violations.append(f"{path}:{lineno}: прямой цвет {value} вне :root — {line.strip()[:80]}")
    return violations


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: verify_tokens.py <file.html|file.css> [...]", file=sys.stderr)
        return 2
    all_violations: list[str] = []
    for a in argv:
        p = Path(a)
        if p.is_dir():
            files = sorted(list(p.rglob("*.css")) + list(p.rglob("*.html")))
        else:
            files = [p]
        for f in files:
            if not f.is_file():
                print(f"ERROR: нет файла {f}", file=sys.stderr)
                return 2
            all_violations += check_file(f)
    if all_violations:
        print(f"FAIL: {len(all_violations)} прямых цветов вне токенов "
              f"(сломают переключатель палитры):")
        for v in all_violations[:60]:
            print(f"  {v}")
        if len(all_violations) > 60:
            print(f"  … ещё {len(all_violations) - 60}")
        print("Правило: все цвета через var(--…) из :root; исключения — "
              "бренд-цвета мессенджеров или /* token-exempt */ (спека §4.3).")
        return 1
    print("PASS: прямых цветов вне :root не найдено.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

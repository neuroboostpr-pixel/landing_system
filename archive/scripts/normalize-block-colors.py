#!/usr/bin/env python3
"""B36 — привести цвета в шаблонах блоков к токен-переменным var(--lp-*).

Проблема: 40 ru-* блоков держат БРЕНДОВЫЕ хардкод-цвета (#0066ff, #ed6f5c…) —
прямо в CSS или как дефолты переменных --color-* в :root. Они «протекают» в
финальный лендинг, потому что inject-tokens их не заменяет.

Эта нормализация:
  1. Переименовывает префикс --color-* → --lp-* (канон, 93/151 блока уже на нём).
  2. Нейтрализует дефолты в :root: значение каждой цветовой --lp-* переменной →
     lo-fi нейтраль по РОЛИ (имя переменной = роль).
  3. Прямые хардкод-цвета в свойствах (background/color/border) → var(--lp-*)
     по эвристике яркости + контексту свойства.

После этого inject-tokens.py подставит реальные цвета дизайн-системы проекта,
а без него блок рендерится нейтральным (не брендовым).

Использование:
  python scripts/normalize-block-colors.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB = REPO_ROOT / "block-library"
SKIP_DIRS = {"_patterns", "_shapes", "_styles", "references"}

# --color-* / --font-* / прочие старые имена → канонические --lp-* по роли.
# ВАЖНО: длинные ключи раньше коротких (font-display до font), иначе подстрока
# съест хвост. Переименование применяется по \b-границе.
VAR_RENAME = {
    "color-bg-alt": "lp-bg-alt",
    "color-bg": "lp-bg",
    "color-surface": "lp-bg-alt",
    "color-bone": "lp-bg-alt",
    "color-fg": "lp-text",
    "color-text": "lp-text",
    "color-muted": "lp-text-muted",
    "color-accent": "lp-accent",
    "color-primary": "lp-accent",
    "color-deco": "lp-accent",
    "color-stripe": "lp-accent",
    "color-border": "lp-border",
    # шрифты — те же канонические --lp-font-* (B36 их пропустил).
    "font-display": "lp-font-display",
    "font-body": "lp-font-body",
}

# нейтральные lo-fi дефолты по роли (то, что окажется в :root).
NEUTRAL_DEFAULT = {
    "lp-bg": "#f5f5f5",
    "lp-bg-alt": "#e8e8e8",
    "lp-text": "#1a1a1a",
    "lp-text-muted": "#999",
    "lp-accent": "#333",
    "lp-border": "#e0e0e0",
}

# нейтральные хексы, которые сами по себе менять не обязательно
NEUTRAL_HEX = {
    "#fff", "#ffffff", "#f5f5f5", "#e8e8e8", "#e0e0e0", "#d0d0d0", "#333",
    "#333333", "#999", "#999999", "#666", "#666666", "#555", "#555555",
    "#111", "#1a1a1a", "#fafafa", "#ccc", "#cccccc", "#888", "#777", "#aaa",
    "#222", "#444", "#000", "#000000", "#eee", "#f0f0f0", "#d9d9d9", "#bbb",
}

_HEX_RE = re.compile(r"#[0-9a-fA-F]{3,6}\b")


def _expand_hex(h: str) -> str:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return h


def luminance(hex_color: str) -> float:
    """Относительная яркость 0..1 (перцептивная)."""
    h = _expand_hex(hex_color)
    if len(h) != 6:
        return 0.5
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.1152 * b


def _saturation(hex_color: str) -> float:
    h = _expand_hex(hex_color)
    if len(h) != 6:
        return 0.0
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == 0:
        return 0.0
    return (mx - mn) / mx


def role_for_color(hex_color: str, prop: str) -> str:
    """Роль цвета по яркости/насыщенности + CSS-свойству."""
    lum = luminance(hex_color)
    sat = _saturation(hex_color)
    prop = (prop or "").lower()
    # насыщенный (брендовый) → accent
    if sat >= 0.35 and 0.1 < lum < 0.92:
        return "accent"
    # по свойству
    if "border" in prop:
        return "border"
    if prop.startswith("background") or prop == "background-color":
        return "bg" if lum > 0.6 else "text"
    if prop == "color" or prop.endswith("-color") and "border" not in prop:
        return "text" if lum < 0.5 else "muted"
    # запасной — по яркости
    if lum > 0.75:
        return "bg"
    if lum < 0.3:
        return "text"
    return "muted"


_ROLE_TO_VAR = {
    "bg": "lp-bg",
    "bg-alt": "lp-bg-alt",
    "text": "lp-text",
    "muted": "lp-text-muted",
    "accent": "lp-accent",
    "border": "lp-border",
}


def normalize_colors(css: str) -> str:
    out = css

    # 1. Переименовать префиксы переменных (и в var(), и в определениях).
    for old, new in VAR_RENAME.items():
        out = re.sub(rf"--{re.escape(old)}\b", f"--{new}", out)

    # 2. Нейтрализовать дефолты переменных в определениях `--lp-x: <value>;`.
    def _neutralize(m):
        var = m.group(1)
        if var in NEUTRAL_DEFAULT:
            return f"--{var}: {NEUTRAL_DEFAULT[var]};"
        return m.group(0)
    out = re.sub(r"--(lp-[a-z-]+)\s*:\s*[^;]+;", _neutralize, out)

    # 3. Прямые хардкод-цвета в свойствах (не в var-определениях) → var(--lp-*).
    #    Идём по `prop: ...#hex...;`, заменяя ненейтральные хексы.
    def _prop_repl(m):
        prop, value = m.group(1), m.group(2)
        # пропускаем определения переменных (уже обработаны)
        if prop.startswith("--"):
            return m.group(0)

        def _hex_repl(hm):
            hx = hm.group(0)
            if hx.lower() in NEUTRAL_HEX:
                return hx
            role = role_for_color(hx, prop)
            var = _ROLE_TO_VAR.get(role, "lp-accent")
            return f"var(--{var})"
        new_value = _HEX_RE.sub(_hex_repl, value)
        return f"{prop}:{new_value}{m.group(3)}"

    # терминатор — ; или закрывающая } (последнее свойство без ;)
    out = re.sub(
        r"([a-zA-Z-]+)\s*:\s*([^;{}]*#[0-9a-fA-F]{3,6}[^;{}]*?)\s*([;}])",
        _prop_repl, out,
    )
    return out


def _has_brand_color(css: str) -> bool:
    for hx in _HEX_RE.findall(css):
        if hx.lower() not in NEUTRAL_HEX:
            return True
    return False


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    changed: list[str] = []
    for catdir in sorted(LIB.iterdir()):
        if not catdir.is_dir() or catdir.name.startswith((".", "_")) or catdir.name in SKIP_DIRS:
            continue
        for bd in sorted(catdir.iterdir()):
            for tpl in (bd / "assets" / "template.html", bd / "assets" / "template-mobile.html"):
                if not tpl.exists():
                    continue
                original = tpl.read_text(encoding="utf-8")
                out = normalize_colors(original)
                if out != original:
                    changed.append(f"{catdir.name}/{bd.name}/{tpl.name}")
                    if not args.dry_run:
                        tpl.write_text(out, encoding="utf-8")

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Изменено файлов: {len(changed)}")
    for c in changed[:20]:
        print(f"  {c}")
    if len(changed) > 20:
        print(f"  … ещё {len(changed) - 20}")


if __name__ == "__main__":
    main()

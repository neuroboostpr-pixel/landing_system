#!/usr/bin/env python3
"""verify-block-php-uses-attributes.py — флоу-гарантия (2026-06-22).

Болячка: при ручной перезаписи block.php под composed-дизайн текстовые поля
(heading/subheading/cta_text/...) зашивались ХАРДКОДОМ вместо $attributes —
правки в wp-admin не отображались на сайте.

Проверка: для каждого блока из block-spec.yaml каждый control с типом text/
textarea (редактируемое поле) ДОЛЖЕН читаться в block.php как
$attributes['<name>'] (или передаваться в переменную из $attributes).
Иначе — FAIL: «поле X не читается из $attributes (хардкод?)».

Usage: verify-block-php-uses-attributes.py --project <dir>
Exit: 0 PASS · 1 FAIL · 2 нет файлов.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import yaml

TEXT_TYPES = {"text", "textarea", "rich-text", "number"}
# поля, которые легитимно рендерятся статикой (не текст-контент)
SKIP_NAMES = {"icon", "icon_svg", "image", "svg"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    a = ap.parse_args()
    proj = Path(a.project)
    spec_path = proj / "08_КОД" / "block-spec.yaml"
    blocks_dir = proj / "08_КОД" / "wp-theme" / "blocks"
    if not spec_path.exists() or not blocks_dir.is_dir():
        print(f"нет файлов: {spec_path} / {blocks_dir}", file=sys.stderr)
        return 2
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    blocks = spec.get("blocks") or []
    fails = []
    for b in blocks:
        slug = b.get("slug")
        if not slug:
            continue
        php = blocks_dir / f"lazyblock-{slug}" / "block.php"
        if not php.exists():
            continue
        txt = php.read_text(encoding="utf-8")
        controls = (b.get("controls") or []) + (b.get("card_controls") or [])
        for c in controls:
            name = c.get("name") or c.get("slug")
            ctype = (c.get("type") or "text").lower()
            if not name or ctype not in TEXT_TYPES:
                continue
            if any(s in name.lower() for s in SKIP_NAMES):
                continue
            # пройдено, если есть $attributes['name'] или $attributes["name"]
            pat = r"\$attributes\[\s*['\"]" + re.escape(name) + r"['\"]\s*\]"
            if not re.search(pat, txt):
                fails.append(f"[{slug}] поле '{name}' ({ctype}) не читается из $attributes — хардкод? (правки в wp-admin не отобразятся)")
    if fails:
        print(f"FAIL: {len(fails)} полей зашиты хардкодом вместо $attributes:")
        for f in fails:
            print(f"  ❌ {f}")
        print("Каждое редактируемое поле из block-spec обязано рендериться через $attributes['name'].")
        return 1
    print(f"PASS: все редактируемые поля блоков читаются из $attributes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

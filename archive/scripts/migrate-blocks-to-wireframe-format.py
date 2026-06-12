#!/usr/bin/env python3
"""Конвертирует новые блоки (index.html + styles.css в корне) под старый
формат wireframe-rendering (assets/template.html + assets/template-mobile.html).

Не удаляет index.html/styles.css — создаёт parallel assets/ структуру.
"""
import re
import shutil
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "block-library"


def migrate_block(block_dir: Path) -> bool:
    """Returns True if migrated."""
    new_index = block_dir / "index.html"
    new_css = block_dir / "styles.css"
    old_template = block_dir / "assets" / "template.html"

    if not new_index.exists() or not new_css.exists():
        return False  # not a new-format block
    if old_template.exists():
        return False  # already migrated

    assets = block_dir / "assets"
    assets.mkdir(exist_ok=True)

    # Combine HTML + CSS into self-contained template.html
    html = new_index.read_text(encoding="utf-8")
    css = new_css.read_text(encoding="utf-8")

    # Scoped template — works as standalone fragment with inline <style>
    template = f"""<style>{css}</style>
{html}"""
    old_template.write_text(template, encoding="utf-8")

    # Mobile вариант — тот же HTML с дополнительным viewport CSS
    mobile_template = f"""<style>{css}
/* Forced mobile viewport for preview */
@media (min-width: 0) {{
  body, .lp-hero-cinematic-split, [class^="lp-"] {{ font-size: 14px; }}
}}
</style>
{html}"""
    (assets / "template-mobile.html").write_text(mobile_template, encoding="utf-8")

    return True


def main():
    migrated = 0
    skipped = 0
    for cat_dir in LIB.iterdir():
        if not cat_dir.is_dir() or cat_dir.name.startswith("_") or cat_dir.name.startswith("."):
            continue
        for block_dir in cat_dir.iterdir():
            if not block_dir.is_dir():
                continue
            if migrate_block(block_dir):
                migrated += 1
                print(f"  ✓ {block_dir.relative_to(LIB)}")
            else:
                skipped += 1
    print(f"\n✅ Migrated: {migrated}, skipped: {skipped} (old format or no source)")


if __name__ == "__main__":
    main()

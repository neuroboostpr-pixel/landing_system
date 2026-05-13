#!/usr/bin/env python3
"""Derive 01a_АНАЛИЗ_НИШИ/landing-structure.md from 07_ПРОТОТИП/prototype.yaml.

Bridge for prototype-first flow (PR-D): wp-builder reads landing-structure.md to
know which template-parts/*.php to generate. In prototype-first flow we skip
01a niche analysis, so we synthesize this file from the prototype block list.
"""
import argparse
import sys
from pathlib import Path

import yaml


# Block type → template-part PHP file name
BLOCK_TYPE_TO_PHP = {
    "hero": "section-hero.php",
    "features": "section-features.php",
    "social-proof": "section-proof.php",
    "testimonials": "section-proof.php",
    "trust": "section-proof.php",
    "process": "section-process.php",
    "pricing": "section-pricing.php",
    "faq": "section-faq.php",
    "cta": "section-form.php",
    "quiz": "section-quiz.php",
    "gallery": "section-gallery.php",
}

# Block type → human-readable label for the blocks table
BLOCK_TYPE_LABEL = {
    "hero": "Hero",
    "features": "Features",
    "social-proof": "Social Proof",
    "testimonials": "Social Proof",
    "trust": "Trust",
    "process": "Process",
    "pricing": "Pricing",
    "faq": "FAQ",
    "cta": "CTA",
    "quiz": "Quiz",
    "gallery": "Gallery",
}


def derive(project_dir: Path) -> str:
    """Build markdown content."""
    project_dir = Path(project_dir)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        sys.exit(f"ERROR: {proto_path} not found")

    prototype = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
    blocks = prototype.get("blocks", []) or []

    # Deduplicate: preserve insertion order, one PHP file per type
    php_files: list[str] = []
    seen_types: set[str] = set()
    block_rows: list[tuple[str, str]] = []  # (label, php)

    for b in blocks:
        block_type = (b.get("type") or "").lower()
        php = BLOCK_TYPE_TO_PHP.get(block_type)
        label = BLOCK_TYPE_LABEL.get(block_type, block_type.title())
        if php and php not in php_files:
            php_files.append(php)
            seen_types.add(block_type)
            block_rows.append((label, php))

    lines = [
        "# Landing Structure (auto-derived from prototype.yaml)",
        "",
        "> Тип бренда: 1",
        "> Режим: prototype_first",
        "",
        "Этот файл сгенерирован автоматически из `07_ПРОТОТИП/prototype.yaml`",
        "скриптом `scripts/derive-landing-structure.py`. Используется `wp-builder` как",
        "источник списка `template-parts/*.php` для генерации WordPress темы.",
        "",
        "## Блоки лендинга (в порядке отображения)",
        "",
        "| # | Блок | Обязательный? | Цель | Содержание (откуда) |",
        "|---|---|---|---|---|",
    ]

    if block_rows:
        for i, (label, _php) in enumerate(block_rows, 1):
            lines.append(f"| {i} | {label} | yes | — | prototype.yaml |")
    else:
        lines.append("| — | (нет блоков) | — | — | — |")

    lines += [
        "",
        "## Обоснование выбора структуры",
        "",
        "Структура определена пользователем через prototype.yaml (prototype-first flow).",
        "Нишевый анализ (этап 01a) не запускался — используется готовый прототип.",
        "",
        "## Контракт с wp-builder",
        "",
        "Список template-parts которые должны быть сгенерированы:",
        "",
    ]

    for php in php_files:
        lines.append(f"- `template-parts/{php}`")
    if not php_files:
        lines.append("- (нет блоков — пустой прототип)")

    lines.append("")
    lines.append(f"Источник: {len(blocks)} блоков в prototype.yaml.")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Derive landing-structure.md from prototype.yaml (PR-D bridge)."
    )
    ap.add_argument("--project", required=True, help="Project directory")
    args = ap.parse_args()

    project = Path(args.project)
    out_dir = project / "01a_АНАЛИЗ_НИШИ"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "landing-structure.md"

    content = derive(project)
    out_path.write_text(content, encoding="utf-8")
    print(f"OK: wrote {out_path}")


if __name__ == "__main__":
    main()

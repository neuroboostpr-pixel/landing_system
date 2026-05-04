#!/usr/bin/env python3
"""Generate ACF fields JSON from 07_КОНТЕНТ/final-copy.md.

CLI: python3 generate-acf.py <project-dir>
Stdout: path to created acf-fields.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.logger import error, success, warn

SECTION_ALIASES = {
    "hero": "hero", "герой": "hero", "главный": "hero",
    "about": "about", "о нас": "about", "о компании": "about",
    "services": "services", "услуги": "services", "сервисы": "services",
    "what you get": "services",
    "proof": "proof", "отзывы": "proof", "результаты": "proof",
    "testimonials": "proof", "кейсы": "proof",
    "form": "form", "форма": "form", "заявка": "form", "форма заявки": "form",
    "faq": "faq", "вопросы": "faq", "частые вопросы": "faq",
    "вопрос-ответ": "faq",
}

SECTION_FIELDS = {
    "hero": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {"label": "Подзаголовок", "name": "subheading", "type": "textarea"},
        {"label": "Текст кнопки", "name": "cta_text", "type": "text"},
        {"label": "Фоновое изображение", "name": "bg_image", "type": "image"},
    ],
    "about": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {"label": "Текст", "name": "body", "type": "wysiwyg"},
        {"label": "Фото", "name": "photo", "type": "image"},
    ],
    "services": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Услуги", "name": "items", "type": "repeater",
            "sub_fields": [
                {"label": "Название", "name": "title", "type": "text"},
                {"label": "Описание", "name": "description", "type": "textarea"},
                {"label": "Иконка", "name": "icon", "type": "text"},
            ],
        },
    ],
    "proof": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Отзывы", "name": "testimonials", "type": "repeater",
            "sub_fields": [
                {"label": "Имя", "name": "name", "type": "text"},
                {"label": "Текст отзыва", "name": "text", "type": "textarea"},
                {"label": "Фото", "name": "photo", "type": "image"},
            ],
        },
    ],
    "form": [
        {"label": "Заголовок формы", "name": "heading", "type": "text"},
        {"label": "Подзаголовок", "name": "subheading", "type": "text"},
        {"label": "ID формы Fluent Forms", "name": "form_id", "type": "number"},
    ],
    "faq": [
        {"label": "Заголовок", "name": "heading", "type": "text"},
        {
            "label": "Вопросы и ответы", "name": "items", "type": "repeater",
            "sub_fields": [
                {"label": "Вопрос", "name": "question", "type": "text"},
                {"label": "Ответ", "name": "answer", "type": "textarea"},
            ],
        },
    ],
}

DEFAULT_FIELDS = [
    {"label": "Заголовок", "name": "heading", "type": "text"},
    {"label": "Текст", "name": "body", "type": "wysiwyg"},
]


def _normalize_section(name: str) -> str:
    return SECTION_ALIASES.get(name.lower().strip(), name.lower().strip())


def _parse_sections(copy_path: Path) -> list:
    text = copy_path.read_text(encoding="utf-8")
    return re.findall(r"^##\s+(.+)$", text, re.MULTILINE)


def _build_acf_group(raw_section: str) -> dict:
    normalized = _normalize_section(raw_section)
    group_key = f"group_lp_{normalized[:20].replace(' ', '_')}"
    fields_template = SECTION_FIELDS.get(normalized, DEFAULT_FIELDS)

    def _make_field(f: dict, prefix: str) -> dict:
        field = {
            "key": f"field_{prefix}_{f['name']}",
            "label": f["label"],
            "name": f["name"],
            "type": f["type"],
        }
        if f["type"] == "repeater" and "sub_fields" in f:
            field["sub_fields"] = [_make_field(sf, prefix + "_sub") for sf in f["sub_fields"]]
        return field

    prefix = normalized[:8].replace(" ", "_")
    return {
        "key": group_key,
        "title": f"LP — {raw_section.title()}",
        "fields": [_make_field(f, prefix) for f in fields_template],
        "location": [[{
            "param": "page_template",
            "operator": "==",
            "value": "front-page.php",
        }]],
    }


def main(argv: list) -> int:
    cwd = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    copy_path = cwd / "07_КОНТЕНТ" / "final-copy.md"
    if not copy_path.exists():
        error(f"final-copy.md not found: {copy_path} — run /landing-content first")
        return 1

    sections = _parse_sections(copy_path)
    if not sections:
        warn("No ## sections in final-copy.md — using default section set")
        sections = ["hero", "about", "services", "proof", "form", "faq"]

    groups = [_build_acf_group(s) for s in sections]
    output = {"version": "5.12.0", "groups": groups}

    out_path = cwd / "08_КОД" / "acf-fields.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    success(f"ACF fields: {out_path} ({len(groups)} groups)")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

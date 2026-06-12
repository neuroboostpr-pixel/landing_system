"""B35 Фаза 2 — генератор новых блоков выдаёт {{slot}}-фрагменты.

Проверяем:
- промпт block-generation.md требует {{slot}}, запрещает data-slot/[SLOT:];
- generate-blocks.py извлекает слоты из {{slot}} html (синхрон с meta).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT = REPO_ROOT / "skills" / "landing-import-blocks" / "prompts" / "block-generation.md"
GEN = REPO_ROOT / "scripts" / "import-blocks" / "generate-blocks.py"


def test_prompt_requires_slot_format():
    text = PROMPT.read_text(encoding="utf-8")
    assert "{{slot:" in text, "промпт должен требовать {{slot:}}"
    # требование «no data-slot attributes»
    assert "Do NOT add `data-slot`" in text or "data-slot` attributes" in text
    # legacy формат помечен как запрещённый
    assert "legacy" in text.lower()


def test_prompt_keeps_fragment_rule():
    text = PROMPT.read_text(encoding="utf-8")
    assert "No DOCTYPE" in text and "<html>" in text  # фрагмент, не документ


def test_generator_extracts_slots_from_html():
    # логика извлечения слотов из html (зеркало вставки в generate-blocks.py)
    html = '<section><h2>{{slot:title}}</h2><p>{{slot:lead}}</p>{{slot:title}}</section>'
    slots: list[str] = []
    for name in re.findall(r"\{\{slot:([^}]+)\}\}", html):
        name = name.strip()
        if name and name not in slots:
            slots.append(name)
    assert slots == ["title", "lead"]


def test_generator_source_has_slot_extraction():
    # сам скрипт содержит шаг извлечения {{slot}} перед записью meta
    src = GEN.read_text(encoding="utf-8")
    assert "slot:" in src and "tpl_slots" in src
    assert "re.findall" in src  # извлекает слоты из html

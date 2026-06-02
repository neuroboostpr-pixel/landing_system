"""B35 Фаза 0 — каждый template.html соответствует стандарту формата.

Стандарт: docs/standards/block-template-format.md
- фрагмент (нет <!DOCTYPE html>/<html>),
- плейсхолдеры только {{slot:name}} (нет data-slot, нет [Рус-подсказок]),
- имена слотов ⊆ meta.yaml::slots[].name (кроме item-схемы).

Эти тесты сначала КРАСНЫЕ для 48 ru-* блоков — фиксируют объём миграции,
который чинит scripts/normalize-block-templates.py (Фаза 1).
"""
import re
from pathlib import Path

import yaml
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "block-library"
SKIP_DIRS = {"_patterns", "_shapes", "_styles", "references"}

SLOT_RE = re.compile(r"\{\{slot:([^}]+)\}\}")
# псевдо-плейсхолдер: [текст с кириллицей] ИЛИ [N…]/[SLOT…] с заглавной —
# запрещён. Чистые числовые сноски [1],[2] не считаются плейсхолдером.
BRACKET_RE = re.compile(r"\[[^\]]*(?:[А-Яа-яЁё]|[A-Z][a-z]|N[^\]]|SLOT)[^\]]*\]")
# B36: цвета — только через var(--lp-*); хардкод-хексы должны быть нейтральными.
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,6}\b")
NEUTRAL_HEX = {
    "#fff", "#ffffff", "#f5f5f5", "#e8e8e8", "#e0e0e0", "#d0d0d0", "#333",
    "#333333", "#999", "#999999", "#666", "#666666", "#555", "#555555",
    "#111", "#1a1a1a", "#fafafa", "#ccc", "#cccccc", "#888", "#777", "#aaa",
    "#222", "#444", "#000", "#000000", "#eee", "#f0f0f0", "#d9d9d9", "#bbb",
}
# item-схема: эти префиксы резолвятся из items[] и не обязаны быть в meta.slots
ITEM_PREFIX_RE = re.compile(
    r"^(item|feature|step|stage|faq|tier|plan|card|metric|stat|fact|"
    r"benefit|advantage|service|testimonial|review|logo|model|tab|"
    r"point|reason)[-_]\d+", re.I
)


def _iter_templates():
    for catdir in sorted(LIB.iterdir()):
        if not catdir.is_dir() or catdir.name.startswith((".", "_")) or catdir.name in SKIP_DIRS:
            continue
        for bd in sorted(catdir.iterdir()):
            tpl = bd / "assets" / "template.html"
            if tpl.exists():
                yield catdir.name, bd.name, tpl


_TEMPLATES = list(_iter_templates())
_IDS = [f"{c}/{b}" for c, b, _ in _TEMPLATES]

# B35 Фаза 0: тесты КРАСНЫЕ by design (фиксируют объём миграции). Снять xfail
# в Фазе 1 после прогона scripts/normalize-block-templates.py.
_PENDING_NORMALIZE = pytest.mark.xfail(
    reason="B35 Фаза 1: нормализация шаблонов ещё не прогнана", strict=False
)


def test_templates_exist():
    assert _TEMPLATES, "не найдено ни одного template.html"


@pytest.mark.parametrize("cat,bid,tpl", _TEMPLATES, ids=_IDS)
def test_is_fragment_not_document(cat, bid, tpl):
    text = tpl.read_text(encoding="utf-8")
    low = text.lower()
    assert "<!doctype" not in low, f"{bid}: template — полный документ (есть <!DOCTYPE>)"
    assert "<html" not in low, f"{bid}: template содержит <html> (должен быть фрагмент)"


@pytest.mark.parametrize("cat,bid,tpl", _TEMPLATES, ids=_IDS)
def test_only_slot_placeholders(cat, bid, tpl):
    text = tpl.read_text(encoding="utf-8")
    # именно атрибут data-slot= (не data-slot-type= и подобные)
    assert not re.search(r"data-slot\s*=", text), \
        f"{bid}: используется legacy data-slot= (нужен {{{{slot:}}}})"
    m = BRACKET_RE.search(text)
    assert not m, f"{bid}: русский плейсхолдер в скобках '{m.group(0) if m else ''}' (нужен {{{{slot:}}}})"


@pytest.mark.parametrize("cat,bid,tpl", _TEMPLATES, ids=_IDS)
def test_no_brand_hardcoded_colors(cat, bid, tpl):
    # B36: брендовые цвета должны идти через var(--lp-*); хардкод-хексы только
    # из нейтральной lo-fi палитры.
    text = tpl.read_text(encoding="utf-8")
    brand = sorted({h for h in HEX_RE.findall(text) if h.lower() not in NEUTRAL_HEX})
    assert not brand, f"{bid}: брендовые хардкод-цвета {brand} — нужен var(--lp-*)"


@pytest.mark.parametrize("cat,bid,tpl", _TEMPLATES, ids=_IDS)
def test_slots_subset_of_meta(cat, bid, tpl):
    text = tpl.read_text(encoding="utf-8")
    slots_in_tpl = {m.strip() for m in SLOT_RE.findall(text)}
    if not slots_in_tpl:
        return  # нет {{slot}} — нечего проверять
    meta_path = tpl.parent.parent / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    meta_slots = {s["name"] for s in (meta.get("slots") or []) if isinstance(s, dict) and "name" in s}
    for s in slots_in_tpl:
        if ITEM_PREFIX_RE.match(s):
            continue  # item-схема резолвится из items[], meta не обязана
        assert s in meta_slots, \
            f"{bid}: слот '{s}' в template отсутствует в meta.yaml::slots"

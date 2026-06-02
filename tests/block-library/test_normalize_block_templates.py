"""B35 Фаза 1 — normalize-block-templates.py приводит шаблон к стандарту."""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "normalize-block-templates.py"


def _load():
    spec = importlib.util.spec_from_file_location("normalize_block_templates", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_data_slot_to_slot_placeholder():
    m = _load()
    html = '<section><h2 data-slot="headline">[HEADLINE: привет]</h2></section>'
    out, slots = m.normalize_html(html)
    assert "data-slot" not in out
    assert "{{slot:headline}}" in out
    assert "[HEADLINE" not in out
    assert "headline" in slots


def test_full_document_to_fragment():
    m = _load()
    html = (
        '<!DOCTYPE html><html lang="ru"><head><style>.x{color:red}</style></head>'
        '<body><section class="x" data-slot="title">[Заголовок]</section></body></html>'
    )
    out, slots = m.normalize_html(html)
    assert "<!doctype" not in out.lower()
    assert "<html" not in out.lower()
    assert "<head" not in out.lower()
    assert "<body" not in out.lower()
    # стиль сохранён
    assert ".x{color:red}" in out
    # section сохранён, плейсхолдер сконвертирован
    assert "{{slot:title}}" in out


def test_nested_data_slot_only_leaf_converted():
    # элемент с дочерними тегами не должен терять структуру —
    # текст заменяется в листовом элементе
    m = _load()
    html = '<section data-slot="wrap"><span data-slot="title">[T]</span></section>'
    out, slots = m.normalize_html(html)
    # внутренний leaf конвертирован
    assert "{{slot:title}}" in out
    # внешний data-slot с дочерними тегами — НЕ затирает детей текстом
    assert "<span" in out
    assert "title" in slots


def test_data_slot_bracket_with_inline_tag_converted():
    # реальный кейс: <h2 data-slot="x">[HEADLINE: <span>преимущества</span>]</h2>
    # содержимое целиком — плейсхолдер в скобках, хоть и с inline-тегом внутри.
    m = _load()
    html = '<h2 data-slot="headline">[HEADLINE: <span>привет</span>]</h2>'
    out, slots = m.normalize_html(html)
    assert "{{slot:headline}}" in out
    assert "[HEADLINE" not in out
    assert "<span" not in out  # inline-обёртка плейсхолдера ушла
    assert "headline" in slots


def test_bracket_without_data_slot_still_converted():
    # [рус] в элементе без data-slot, но он явно плейсхолдер → конвертим по классу
    m = _load()
    html = '<p class="lead">[Описание выгоды]</p>'
    out, slots = m.normalize_html(html)
    assert "[Описание" not in out
    assert "{{slot:" in out


def test_bracket_partial_with_decoration_sibling():
    # <span class="ticker-unit">[Текст] <span class="star">✳</span></span>
    # [...] — только часть, рядом декоративный span; конвертим только bracket.
    m = _load()
    html = '<span class="ticker-unit">[Текст бегущей строки] <span class="star">✳</span></span>'
    out, slots = m.normalize_html(html)
    assert "[Текст" not in out
    assert "{{slot:" in out
    assert "✳" in out  # декор сохранён
    assert 'class="star"' in out


def test_existing_slot_placeholders_preserved():
    m = _load()
    html = '<section><h2>{{slot:heading}}</h2></section>'
    out, slots = m.normalize_html(html)
    assert "{{slot:heading}}" in out
    assert "heading" in slots


def test_collect_slots_dedup():
    m = _load()
    html = '<div>{{slot:a}}{{slot:b}}{{slot:a}}</div>'
    _, slots = m.normalize_html(html)
    assert slots == ["a", "b"] or set(slots) == {"a", "b"}


def test_sync_meta_slots():
    m = _load()
    meta = {"id": "x", "slots": [{"name": "content", "type": "text"}]}
    m.sync_meta_slots(meta, ["title", "subhead"])
    names = {s["name"] for s in meta["slots"]}
    assert names == {"title", "subhead"}, names
    assert all(s.get("type") == "text" for s in meta["slots"])

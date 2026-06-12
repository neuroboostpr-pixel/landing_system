"""_flatten_sections_to_blocks не теряет данные sub-блоков прототипа.

Регрессия: старый flatten мержил sub-блоки с `if k not in merged` и терял всё
кроме первого — кнопки/бейджи/повторяющиеся карточки оставались пустыми.
"""
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RW = REPO_ROOT / "skills" / "wireframe-rendering" / "scripts" / "render-wireframe.py"
IC = REPO_ROOT / "skills" / "block-composition" / "scripts" / "inject-content.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _proto():
    return {"sections": [
        {"id": "hero", "blocks": [
            {"type": "heading", "text": "ЗАГОЛОВОК"},
            {"type": "paragraph", "text": "Подзаголовок секции."},
            {"type": "info_badge", "label": "Старт", "value": "27 июня"},
            {"type": "cta_button", "text": "Хочу на курс"},
            {"type": "cta_button", "text": "Подробнее"},
        ]},
        {"id": "tariffs", "blocks": [
            {"type": "tariff_card", "name": "БАЗОВЫЙ", "price": "9900"},
            {"type": "tariff_card", "name": "ПРО", "price": "19900"},
            {"type": "tariff_card", "name": "ВИП", "price": "39900"},
        ]},
    ]}


def test_hero_keeps_cta_and_badges():
    rw = _load(RW, "render_wireframe")
    ic = _load(IC, "inject_content")
    blocks = {b["id"]: b for b in rw._flatten_sections_to_blocks(_proto())}
    hero = blocks["hero"]
    assert ic.resolve_slot(hero, "title") == "ЗАГОЛОВОК"
    assert ic.resolve_slot(hero, "subhead") == "Подзаголовок секции."
    # кнопки больше не теряются
    assert ic.resolve_slot(hero, "primary-cta-label") == "Хочу на курс"
    assert ic.resolve_slot(hero, "secondary-cta-label") == "Подробнее"
    # бейдж собран из label+value
    assert "Старт" in ic.resolve_slot(hero, "badge-1")
    assert "27 июня" in ic.resolve_slot(hero, "badge-1")


def test_repeated_cards_become_items():
    rw = _load(RW, "render_wireframe")
    ic = _load(IC, "inject_content")
    blocks = {b["id"]: b for b in rw._flatten_sections_to_blocks(_proto())}
    tar = blocks["tariffs"]
    assert len(tar["items"]) == 3
    # повторяющиеся слоты резолвятся по индексу
    assert ic.resolve_slot(tar, "tier-1-name") == "БАЗОВЫЙ"
    assert ic.resolve_slot(tar, "tier-2-name") == "ПРО"
    assert ic.resolve_slot(tar, "tier-3-name") == "ВИП"
    assert ic.resolve_slot(tar, "tier-1-price") == "9900"


def test_legacy_blocks_format_passthrough():
    rw = _load(RW, "render_wireframe")
    proto = {"blocks": [{"type": "hero", "headline": "X"}]}
    out = rw._flatten_sections_to_blocks(proto)
    assert out[0]["headline"] == "X"
    assert out[0]["position"] == 1

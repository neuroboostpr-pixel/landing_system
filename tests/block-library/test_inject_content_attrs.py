"""Регрессия: {{slot}} внутри HTML-атрибутов не должен ломать разметку.

Баг: substitute_text_placeholders заменял незаполненный {{slot}} на
<span>[name]</span> ВЕЗДЕ, включая значения атрибутов (href, aria-label),
что ломало HTML (атрибуты вываливались как текст).
"""
import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IC = REPO_ROOT / "skills" / "block-composition" / "scripts" / "inject-content.py"


def _load():
    spec = importlib.util.spec_from_file_location("inject_content", IC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_slot_in_attribute_stays_plain_text():
    m = _load()
    html = '<a href="{{slot:nav-link-1-url}}" aria-label="{{slot:nav-aria-label}}">{{slot:nav-link-1-label}}</a>'
    out = m.substitute_text_placeholders(html, {"items": ["Главная"]})
    # никакого <span> внутри атрибутов
    assert not re.search(r'(?:href|aria-label)="[^"]*<span', out)
    # url-слот → '#'
    assert 'href="#"' in out
    # текст ссылки заполнен из items
    assert ">Главная<" in out
    # никаких сырых {{slot}}
    assert "{{slot:" not in out


def test_unfilled_text_slot_becomes_visible_placeholder():
    m = _load()
    html = "<h2>{{slot:headline}}</h2>"
    out = m.substitute_text_placeholders(html, {})
    # в тексте — видимая серая заглушка, не пусто
    assert "[headline]" in out
    assert "<span" in out


def test_filled_attr_url_uses_value():
    m = _load()
    html = '<a href="{{slot:cta-url}}">x</a>'
    out = m.substitute_text_placeholders(html, {"cta": {"href": "https://e.com"}})
    assert 'href="https://e.com"' in out


def test_image_slot_becomes_placeholder_img():
    m = _load()
    out = m.substitute_text_placeholders(
        "<div>{{slot:art-image}}</div><span>{{slot:badge-1-icon}}</span><h2>{{slot:headline}}</h2>",
        {},
    )
    # image/icon слоты → <img> с data-URI; текстовый слот — нет
    assert out.count("<img") == 2
    assert "data:image" in out
    assert 'alt="art-image"' in out
    assert "[headline]" in out  # текст не картинка


def test_image_slot_in_src_attr_gets_datauri():
    # <img src="{{slot:hero-image}}"> без значения → data-URI, не пустой src
    m = _load()
    html = '<picture><source srcset="{{slot:hero-image-mobile}}"><img src="{{slot:hero-image}}" alt="{{slot:hero-image-alt}}"></picture>'
    out = m.substitute_text_placeholders(html, {})
    assert 'src=""' not in out
    assert "data:image" in out
    # alt — текст, остаётся пустым (не картинка)
    assert 'alt=""' in out


def test_src_attr_always_gets_image_even_with_nonimage_name():
    # слот в src/srcset → картинка-плейсхолдер даже если имя не «image»
    # (напр. pricing-portrait) — иначе пустой src даёт битую картинку.
    m = _load()
    html = '<picture><source srcset="{{slot:pricing-portrait-mobile}}"><img src="{{slot:pricing-portrait}}"></picture>'
    out = m.substitute_text_placeholders(html, {})
    assert 'src=""' not in out
    assert 'srcset=""' not in out
    assert out.count("data:image") == 2


def test_image_slot_detection():
    m = _load()
    assert m._is_image_slot("brand-logo")
    assert m._is_image_slot("case-1-photo")
    assert m._is_image_slot("hero-visual-image")
    # -mobile это вариант картинки (srcset), а не текст → True
    assert m._is_image_slot("case-image-1-mobile")
    assert m._is_image_slot("hero-image-mobile")
    # alt/url/caption — это текст/ссылки, не визуал
    assert not m._is_image_slot("brand-logo-alt")
    assert not m._is_image_slot("hero-image-caption")
    assert not m._is_image_slot("nav-link-1-url")
    assert not m._is_image_slot("headline")


def test_header_block_renders_valid_html(tmp_path):
    # сквозной: header-блок со слотами-в-атрибутах → валидный <header>
    m = _load()
    tpl = (
        '<header aria-label="{{slot:header-aria-label}}" class="lp-h">'
        '<a href="{{slot:brand-link}}">{{slot:brand-name}}</a>'
        '<a href="{{slot:nav-link-1-url}}">{{slot:nav-label-1}}</a>'
        "</header>"
    )
    block = {"text": "IQIDO", "items": ["Home", "About"]}
    out = m.inject_block(tpl, block, {})
    assert "{{slot:" not in out
    assert not re.search(r'(?:href|aria-label)="[^"]*<span', out)
    assert "IQIDO" in out
    assert ">Home<" in out

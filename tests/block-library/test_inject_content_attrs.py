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

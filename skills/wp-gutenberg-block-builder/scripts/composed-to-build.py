#!/usr/bin/env python3
"""C1 — конвертер composed.html → файлы для сборки WordPress-темы.

Спека reference-driven flow §4.1: «всё, что нужно для сборки сайта, выводится
ИЗ composed.html, а не пишется заново руками». Конвертер порождает:

  08_КОД/block-spec.yaml                       — секции → блоки (single /
                                                 section-card с repeater-картами)
  08_КОД/fonts-deps.yaml                       — шрифты и внешние зависимости
  08_КОД/assets-manifest.yaml                  — фото/картинки макета
  05_ДИЗАЙН-СИСТЕМА/tokens.from-composed.json  — CSS-токены из :root

Сгенерированный spec — каркас 1:1 по макету (тексты дословно). Манагер может
дополнить controls, но структура и дефолты выводятся из макета автоматически.
Существующий block-spec.yaml бэкапится в .bak.

Usage:
  composed-to-build.py --project <dir> [--composed <path>]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

HEADINGS = ("h1", "h2", "h3", "h4")


# ── helpers ──────────────────────────────────────────────────────────────

def _slugify(value: str, fallback: str) -> str:
    value = re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")
    return value or fallback


def _text(el) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()


def _normalize_img(src: str) -> str:
    """Локальную картинку → `assets/photos/<basename>` (контракт asset-pipeline /
    deploy-фиксера, спека §4.2 «картинки битые / плейсхолдеры не заменились»).
    Внешние URL (http/https/data:) — как есть."""
    if not src or src.startswith(("http://", "https://", "data:", "//")):
        return src
    base = src.rsplit("/", 1)[-1]
    return f"assets/photos/{base}" if base else src


def _srcset_urls(srcset: str) -> list[str]:
    urls: list[str] = []
    for item in str(srcset or "").split(","):
        url = item.strip().split(" ", 1)[0]
        if url:
            urls.append(url)
    return urls


def _picture_sources(img) -> list[str]:
    picture = img.find_parent("picture")
    if picture is None:
        return []
    out: list[str] = []
    for source in picture.find_all("source"):
        if source.get("srcset"):
            out.extend(_srcset_urls(source["srcset"]))
        elif source.get("src"):
            out.append(source["src"])
    return out


def _first_picture_source(img) -> str:
    sources = _picture_sources(img)
    return _normalize_img(sources[0]) if sources else ""


def _extract_root_tokens(html: str) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for m in re.finditer(r":root\s*\{(.*?)\}", html, re.DOTALL):
        for var, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
            tokens[var.strip()] = val.strip()
    return tokens


def _extract_fonts(soup: BeautifulSoup, html: str) -> dict:
    stylesheets = [
        link.get("href") for link in soup.find_all("link", rel=lambda v: v and "stylesheet" in v)
        if link.get("href")
    ]
    font_sheets = [h for h in stylesheets if "font" in h.lower()]
    families = sorted(set(re.findall(r"font-family\s*:\s*['\"]?([^'\";,}]+)", html)))
    scripts = [s.get("src") for s in soup.find_all("script", src=True)]
    return {
        "stylesheets": font_sheets or stylesheets,
        "font_families": families,
        "external_scripts": scripts,
    }


def _extract_images(soup: BeautifulSoup, html: str) -> list[str]:
    imgs = []
    for img in soup.find_all("img"):
        imgs.extend(_normalize_img(src) for src in _picture_sources(img))
        if img.get("src"):
            imgs.append(_normalize_img(img.get("src")))
    css_urls = re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", html)
    css_imgs = [_normalize_img(u) for u in css_urls
                if not u.startswith("data:") and "font" not in u]
    seen, out = set(), []
    for u in imgs + css_imgs:
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _card_signature(el) -> tuple:
    """Структурная сигнатура потенциальной карточки (группировка без классов)."""
    return (el.name, bool(el.find(HEADINGS)), bool(el.find("p")), bool(el.find("img")))


def _find_card_grid(section):
    """Найти повторяющиеся карточки в секции.

    Сначала по одинаковому непустому классу (тогда у карт есть CSS-селектор),
    иначе — по одинаковой структурной сигнатуре. Голые `<div>`-карточки без
    класса раньше терялись и секция схлопывалась в один блок (спека §4.2
    «карточки не рендерятся / внутренние блоки-карточки теряются»)."""
    for container in section.find_all(True):
        children = [c for c in container.find_all(True, recursive=False)]
        if len(children) < 2:
            continue
        # 1) по классу — карта получает реальный селектор
        classes = Counter(tuple(c.get("class") or []) for c in children)
        (cls, count), = [classes.most_common(1)[0]]
        if count >= 2 and cls:
            cards = [c for c in children if tuple(c.get("class") or []) == cls]
            return container, cards
        # 2) по структуре — карта = есть заголовок или абзац
        sigs = Counter(_card_signature(c) for c in children)
        (sig, scount), = [sigs.most_common(1)[0]]
        if scount >= 2 and (sig[1] or sig[2]):
            cards = [c for c in children if _card_signature(c) == sig]
            return container, cards
    return None, None


def _card_fields(card) -> dict[str, str]:
    """Поля карточки: заголовок/тексты/ссылка."""
    fields: dict[str, str] = {}
    h = card.find(HEADINGS)
    if h:
        fields["name"] = _text(h)
    paragraphs = [_text(p) for p in card.find_all("p") if _text(p)]
    if paragraphs:
        fields["text"] = "\n\n".join(paragraphs)
    a = card.find("a")
    if a:
        fields["cta_text"] = _text(a)
        if a.get("href"):
            fields["cta_url"] = a["href"]
    img = card.find("img")
    if img and img.get("src"):
        fields["image"] = _normalize_img(img["src"])
        mobile = _first_picture_source(img)
        if mobile:
            fields["image_mobile"] = mobile
    return fields


def _section_controls(section, exclude_card_container=None) -> list[dict]:
    """Контролы single-блока / шапки секции (вне карточной сетки)."""
    controls: list[dict] = []

    def outside_cards(el) -> bool:
        return exclude_card_container is None or exclude_card_container not in el.parents

    h = next((el for el in section.find_all(HEADINGS) if outside_cards(el)), None)
    if h is not None:
        controls.append({"id": "c_heading", "name": "heading", "type": "text",
                         "label": "Заголовок", "default": _text(h)})
    paragraphs = [_text(p) for p in section.find_all("p")
                  if outside_cards(p) and _text(p)]
    if paragraphs:
        controls.append({"id": "c_subheading", "name": "subheading", "type": "textarea",
                         "label": "Подзаголовок", "default": "\n\n".join(paragraphs)})
    a = next((el for el in section.find_all("a") if outside_cards(el) and _text(el)), None)
    if a is not None:
        controls.append({"id": "c_cta_text", "name": "cta_text", "type": "text",
                         "label": "Текст кнопки", "default": _text(a)})
        if a.get("href"):
            controls.append({"id": "c_cta_url", "name": "cta_url", "type": "url",
                             "label": "Ссылка кнопки", "default": a["href"]})
    img = next((el for el in section.find_all("img") if outside_cards(el)), None)
    if img is not None and img.get("src"):
        controls.append({"id": "c_image", "name": "image", "type": "image",
                         "label": "Изображение", "default": _normalize_img(img["src"])})
        mobile = _first_picture_source(img)
        if mobile:
            controls.append({"id": "c_image_mobile", "name": "image_mobile", "type": "image",
                             "label": "Изображение mobile", "default": mobile})
    return controls


def _build_blocks(soup: BeautifulSoup) -> list[dict]:
    blocks: list[dict] = []
    sections = soup.find_all(["section", "header", "footer"], recursive=True)
    # только верхнеуровневые (не вложенные друг в друга)
    sections = [s for s in sections
                if not any(p.name in ("section", "header", "footer") for p in s.parents)]
    for i, section in enumerate(sections, start=1):
        sid = section.get("id")
        cls = (section.get("class") or [None])[0]
        slug = _slugify(sid or (cls or ""), f"block-{i}")
        probe = f"#{sid}" if sid else (f".{cls}" if cls else section.name)
        title_el = section.find(HEADINGS)
        title = _text(title_el)[:60] if title_el else slug

        container, cards = _find_card_grid(section)
        block: dict = {
            "slug": slug,
            "title": title,
            "icon": "block-default",
            "category": "lp-blocks",
            "probe_selector": probe,
            "probe_kind": "single",
        }
        if cards:
            block["type"] = "section-card"
            block["probe_kind"] = "card-collection"
            # section_grid_class обязателен (block_spec.validate). Если у контейнера
            # карточек нет класса — синтезируем `<slug>-grid`: generate-lzb-templates
            # навесит его на грид-обёртку, generate-css-patches пропишет под него
            # сеточные правила (внутренне согласовано, не зависит от классов макета).
            grid_cls = (container.get("class") or [""])[0]
            block["section_grid_class"] = grid_cls or f"{slug}-grid"
            block["controls"] = _section_controls(section, exclude_card_container=container)
            first_fields = _card_fields(cards[0])
            card_controls = []
            type_map = {"name": "text", "text": "textarea",
                        "cta_text": "text", "cta_url": "url", "image": "image",
                        "image_mobile": "image"}
            label_map = {"name": "Заголовок карточки", "text": "Текст карточки",
                         "cta_text": "Кнопка", "cta_url": "Ссылка", "image": "Картинка",
                         "image_mobile": "Картинка mobile"}
            for fname, fval in first_fields.items():
                card_controls.append({
                    "id": f"c_card_{fname}", "name": fname,
                    "type": type_map.get(fname, "text"),
                    "label": label_map.get(fname, fname),
                    "default": fval,
                })
            card_cls = (cards[0].get("class") or [None])[0]
            block["card"] = {
                "slug": f"{slug}-card",
                "title": f"{title} — карточка",
                "controls": card_controls,
                "template": [_card_fields(c) for c in cards],
            }
            if card_cls:
                block["card_probe_selector"] = f".{card_cls}"
        else:
            block["type"] = "single"
            block["controls"] = _section_controls(section)
        blocks.append(block)
    return blocks


# ── main ─────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--composed", default="")
    args = ap.parse_args()

    project = Path(args.project)
    composed = Path(args.composed) if args.composed else (
        project / "07b_COMPOSED" / "composed.html")
    if not composed.exists():
        print(f"ERROR: нет {composed}", file=sys.stderr)
        return 2

    html = composed.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(html, "lxml")

    # 1) токены
    tokens = _extract_root_tokens(html)
    tokens_path = project / "05_ДИЗАЙН-СИСТЕМА" / "tokens.from-composed.json"
    tokens_path.parent.mkdir(parents=True, exist_ok=True)
    tokens_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2),
                           encoding="utf-8")

    # 2) блоки
    page_title = _text(soup.title) if soup.title else "Home"
    spec = {
        "version": 1,
        "generated_from": "07b_COMPOSED/composed.html",
        "generator": "composed-to-build.py",
        "page": {"title": page_title, "slug": "home"},
        "blocks": _build_blocks(soup),
    }
    out_dir = project / "08_КОД"
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_path = out_dir / "block-spec.yaml"
    if spec_path.exists():
        spec_path.replace(spec_path.with_suffix(".yaml.bak"))
    spec_path.write_text(
        yaml.dump(spec, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8")

    # 3) шрифты/зависимости
    fonts = _extract_fonts(soup, html)
    (out_dir / "fonts-deps.yaml").write_text(
        yaml.dump(fonts, allow_unicode=True, sort_keys=False), encoding="utf-8")

    # 4) ассеты
    assets = {"images": _extract_images(soup, html)}
    (out_dir / "assets-manifest.yaml").write_text(
        yaml.dump(assets, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print(f"OK: {len(spec['blocks'])} блоков → {spec_path}")
    print(f"    токены: {len(tokens)} → {tokens_path}")
    print(f"    шрифты: {len(fonts['stylesheets'])} стилей; "
          f"картинок: {len(assets['images'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

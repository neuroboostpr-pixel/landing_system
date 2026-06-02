#!/usr/bin/env python3
"""B35 Фаза 1 — привести шаблоны блоков к стандарту block-template-format.md.

Что делает для каждого block-library/<f>/<id>/assets/template.html
(и template-mobile.html):
  1. data-slot="X" с листовым текстом → {{slot:X}} (атрибут удаляется).
     Элемент с дочерними ТЕГАМИ не затирается (только убираем data-slot).
  2. Полный <!DOCTYPE html> документ → фрагмент: <style> из <head> + содержимое
     <body>, без <html>/<head>/<body>.
  3. Синхронизировать meta.yaml::slots с набором {{slot}} из шаблона.

Использование:
  python scripts/normalize-block-templates.py [--dry-run]

Идемпотентно: повторный прогон уже-нормализованного блока ничего не меняет.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml
from bs4 import BeautifulSoup, NavigableString

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB = REPO_ROOT / "block-library"
SKIP_DIRS = {"_patterns", "_shapes", "_styles", "references"}
SLOT_RE = re.compile(r"\{\{slot:([^}]+)\}\}")


def _has_child_tags(el) -> bool:
    from bs4 import Tag
    return any(isinstance(c, Tag) for c in el.children)


# плейсхолдер-с-кириллицей (для частичной замены в тексте)
_BRACKET_RE = re.compile(r"\[[^\]]*[А-Яа-яЁё][^\]]*\]")
# плейсхолдер «весь элемент»: непустые скобки с буквой/цифрой (вкл. [N+], [SLOT: x])
_WHOLE_BRACKET_RE = re.compile(r"^\[[^\]]*[A-Za-zА-Яа-яЁё0-9][^\]]*\]$")


def _slug_from_el(el, used: set[str], counter: list[int]) -> str:
    """Вывести имя слота для элемента без data-slot из class/тега."""
    classes = el.get("class") or []
    for c in classes:
        # берём осмысленный хвост BEM-класса: lp-x__title → title
        tail = re.split(r"__|--", c)[-1]
        tail = re.sub(r"[^a-z0-9-]", "", tail.lower())
        if tail and tail not in ("lp", "") and tail not in used:
            return tail
    base = el.name or "slot"
    counter[0] += 1
    return f"{base}-{counter[0]}"


def normalize_html(html: str) -> tuple[str, list[str]]:
    """Вернуть (нормализованный_html, упорядоченный_список_слотов)."""
    is_doc = "<html" in html.lower() or "<!doctype" in html.lower()
    soup = BeautifulSoup(html, "html.parser")
    used_names: set[str] = set()
    counter = [0]

    # 1. data-slot → {{slot}}. Если содержимое — плейсхолдер в [скобках]
    #    (даже с inline-тегами), заменяем всё содержимое на {{slot:name}}.
    for el in soup.select("[data-slot]"):
        name = el.get("data-slot", "").strip()
        del el["data-slot"]
        if not name:
            continue
        used_names.add(name)
        inner = el.decode_contents()
        if not _has_child_tags(el) or _BRACKET_RE.search(inner):
            el.clear()
            el.append(NavigableString(f"{{{{slot:{name}}}}}"))

    # 2. Остаточные [рус-плейсхолдеры] без data-slot — выводим имя из class/тега.
    #    (а) элемент целиком обёрнут в [...] → заменяем всё содержимое;
    #    (б) [...] — лишь часть (рядом декор) → заменяем только bracket-текст.
    from bs4 import Tag
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        inner = el.decode_contents().strip()
        if "{{slot:" in inner:
            continue
        if _WHOLE_BRACKET_RE.match(inner):
            # (а) весь элемент — плейсхолдер (вкл. [N+], [SLOT: x])
            name = _slug_from_el(el, used_names, counter)
            used_names.add(name)
            el.clear()
            el.append(NavigableString(f"{{{{slot:{name}}}}}"))
            continue
        # (б) bracket-фрагмент внутри текстового узла элемента
        for txt in [c for c in el.children if isinstance(c, NavigableString)]:
            if _BRACKET_RE.search(str(txt)):
                name = _slug_from_el(el, used_names, counter)
                used_names.add(name)
                replaced = _BRACKET_RE.sub(f"{{{{slot:{name}}}}}", str(txt), count=1)
                txt.replace_with(NavigableString(replaced))
                break

    if is_doc:
        # 2. собрать фрагмент: все <style> + содержимое body
        parts: list[str] = []
        for style in soup.find_all("style"):
            parts.append(str(style))
        body = soup.body
        if body is not None:
            for child in body.contents:
                parts.append(str(child))
        else:
            # нет body — берём всё кроме html/head
            root = soup.find("html") or soup
            for child in root.contents:
                parts.append(str(child))
        out = "".join(parts)
    else:
        out = str(soup)

    # нормализуем лишние пустые строки в начале/конце
    out = out.strip() + "\n"

    # 3. собрать слоты в порядке появления (dedup)
    seen: list[str] = []
    for name in SLOT_RE.findall(out):
        name = name.strip()
        if name not in seen:
            seen.append(name)
    return out, seen


# item-схема: эти слоты резолвятся из items[] и не обязаны быть в meta.slots
_ITEM_PREFIX_RE = re.compile(
    r"^(item|feature|step|stage|faq|tier|plan|card|metric|stat|fact|"
    r"benefit|advantage|service|testimonial|review|logo|model|tab|"
    r"point|reason)[-_]\d+", re.I
)


def sync_meta_slots(meta: dict, slots: list[str]) -> None:
    """Переписать meta['slots'] под фактические {{slot}} шаблона.

    Сохраняет существующие атрибуты слота (type/required/max_chars), если имя
    совпало; новые получают type: text. item-схема включается как есть.
    """
    old_by_name = {
        s["name"]: s for s in (meta.get("slots") or [])
        if isinstance(s, dict) and "name" in s
    }
    new_slots: list[dict] = []
    for name in slots:
        if name in old_by_name:
            new_slots.append(old_by_name[name])
        else:
            new_slots.append({"name": name, "type": "text"})
    meta["slots"] = new_slots


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    changed: list[str] = []
    for catdir in sorted(LIB.iterdir()):
        if not catdir.is_dir() or catdir.name.startswith((".", "_")) or catdir.name in SKIP_DIRS:
            continue
        for bd in sorted(catdir.iterdir()):
            if not bd.is_dir():
                continue
            meta_path = bd / "meta.yaml"
            templates = [
                t for t in (bd / "assets" / "template.html",
                            bd / "assets" / "template-mobile.html")
                if t.exists()
            ]
            if not templates:
                continue

            all_slots: list[str] = []
            tpl_dirty = False
            for tpl in templates:
                original = tpl.read_text(encoding="utf-8")
                out, slots = normalize_html(original)
                for s in slots:
                    if s not in all_slots:
                        all_slots.append(s)
                if out != original:
                    tpl_dirty = True
                    if not args.dry_run:
                        tpl.write_text(out, encoding="utf-8")

            # синхронизировать meta (по слотам desktop+mobile)
            meta_dirty = False
            if meta_path.exists() and all_slots:
                meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
                before = [s for s in (meta.get("slots") or [])]
                sync_meta_slots(meta, all_slots)
                if meta["slots"] != before:
                    meta_dirty = True
                    if not args.dry_run:
                        meta_path.write_text(
                            yaml.dump(meta, default_flow_style=False,
                                      sort_keys=False, allow_unicode=True),
                            encoding="utf-8",
                        )

            if tpl_dirty or meta_dirty:
                flags = []
                if tpl_dirty:
                    flags.append("tpl")
                if meta_dirty:
                    flags.append("meta")
                changed.append(f"{catdir.name}/{bd.name} [{'+'.join(flags)}]")

    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Изменено блоков: {len(changed)}")
    for c in changed[:20]:
        print(f"  {c}")
    if len(changed) > 20:
        print(f"  … ещё {len(changed) - 20}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Re-render composed.html — подстановка фото/иконок/инфографики (07d/07e/07f).

Reference-driven flow: composed.html рисует агент; этот скрипт НЕ собирает
макет (машинная склейка из block-library в архиве), а только заменяет
визуальные placeholders в ГОТОВОМ макете:

  1. Фото (PR-B): элементы с data-slot="<name>" — если в
     07c_PHOTOS/selections.yaml у слота есть processed.desktop → <img>/<picture>.
  2. Иконки/инфографика (PR-C): текстовые маркеры [SLOT: <name>] и пустые
     элементы data-slot="<name>" — если есть 07d_VISUALS/icons/<name>.png
     или 07d_VISUALS/infographics/<name>.png → <img class="lp-icon"/lp-chart">.

Исходный composed.html бэкапится в composed.html.bak при первом изменении.

Usage:
  rerender-composed.py --project <dir> [--composed <path>]
Exit: 0 ок (даже если заменять нечего) · 2 нет composed.html.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from bs4 import BeautifulSoup


def _photo_map(project: Path) -> dict[str, dict]:
    sel_path = project / "07c_PHOTOS" / "selections.yaml"
    if not sel_path.exists():
        return {}
    data = yaml.safe_load(sel_path.read_text(encoding="utf-8")) or {}
    out = {}
    for item in data.get("selections", []) or []:
        slot = item.get("slot") or item.get("slot_name")
        if slot and item.get("processed", {}).get("desktop"):
            out[slot] = item["processed"]
    return out


def _visual_path(project: Path, name: str) -> Path | None:
    for sub in ("icons", "infographics"):
        for ext in (".png", ".svg", ".webp"):
            p = project / "07d_VISUALS" / sub / f"{name}{ext}"
            if p.exists():
                return p
    return None


def _img_tag(soup: BeautifulSoup, src: str, name: str, cls: str):
    img = soup.new_tag("img", src=src, alt=name)
    img["class"] = cls
    img["loading"] = "lazy"
    return img


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

    html = composed.read_text(encoding="utf-8")
    original = html
    replaced: list[str] = []

    # 2a. Текстовые маркеры [SLOT: name] → <img> (иконки/инфографика)
    def _slot_marker(m: re.Match) -> str:
        name = m.group(1).strip()
        vp = _visual_path(project, name)
        if vp is None:
            return m.group(0)
        rel = vp.relative_to(project) if vp.is_relative_to(project) else vp
        cls = "lp-chart" if "infographic" in str(vp) else "lp-icon"
        replaced.append(name)
        return f'<img class="{cls}" src="{rel}" alt="{name}" loading="lazy">'

    html = re.sub(r"\[SLOT:\s*([\w-]+)\s*\]", _slot_marker, html)

    # DOM-замены
    soup = BeautifulSoup(html, "html.parser")
    photos = _photo_map(project)
    for el in soup.find_all(attrs={"data-slot": True}):
        name = el["data-slot"]
        # 1. фото
        if name in photos:
            proc = photos[name]
            img = _img_tag(soup, proc["desktop"], name, "lp-photo")
            if proc.get("mobile"):
                picture = soup.new_tag("picture")
                source = soup.new_tag("source", media="(max-width: 768px)",
                                      srcset=proc["mobile"])
                picture.append(source)
                picture.append(img)
                el.clear()
                el.append(picture)
            else:
                el.clear()
                el.append(img)
            replaced.append(name)
            continue
        # 2b. визуал в пустой data-slot
        if not el.get_text(strip=True) and not el.find("img"):
            vp = _visual_path(project, name)
            if vp is not None:
                rel = vp.relative_to(project) if vp.is_relative_to(project) else vp
                cls = "lp-chart" if "infographic" in str(vp) else "lp-icon"
                el.append(_img_tag(soup, str(rel), name, cls))
                replaced.append(name)

    new_html = str(soup)
    if replaced and new_html != original:
        bak = composed.with_suffix(".html.bak")
        if not bak.exists():
            bak.write_text(original, encoding="utf-8")
        composed.write_text(new_html, encoding="utf-8")
        print(f"OK: заменено {len(replaced)} слотов: {', '.join(sorted(set(replaced))[:10])}")
    else:
        print("OK: заменять нечего (нет готовых фото/визуалов для placeholders)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

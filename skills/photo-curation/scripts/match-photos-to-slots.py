#!/usr/bin/env python3
"""match-photos-to-slots.py — PR-K жадное сопоставление фото → photo-слотам.

Алгоритм:
  1. Загружает `.classifications.json` (из classify-photos.py).
  2. Сканирует слоты используемых блоков:
        a) парсит composed.html → собирает все `data-block="<id>"`;
        b) для каждого блока читает `block-library/<cat>/<id>/meta.yaml`
           и достаёт `slots: type=photo`.
        Если composed.html нет — fallback на все блоки library.
  3. Сопоставляет жадно:
        — приоритет редким типам (hero обычно 1 на проект, потом portrait,
          потом team/car/product/interior, в конце lifestyle/background);
        — внутри типа берём фото с максимально близким ratio к slot.ratio.
  4. Для не закрытых слотов пишет `__NEEDS_GENERATION__`.
  5. Output: пишет `selections.yaml` рядом (по умолчанию
     `<project>/07c_PHOTOS/selections.suggested.yaml` чтобы не перетереть
     утверждённую пользователем версию).

Slot type → photo type приоритет:
  hero-bg / hero-*       → hero (fallback: background, lifestyle)
  team-*                 → team (fallback: portrait, lifestyle)
  portrait-* / expert-*  → portrait (fallback: team)
  car-* / vehicle-*      → car/vehicle
  product-*              → product
  interior-*             → interior (fallback: background, lifestyle)
  bg-* / background-*    → background (fallback: interior, lifestyle)
  *                      → lifestyle (универсальный fallback)

Usage:
    python3 match-photos-to-slots.py <project_dir>
"""
import json
import re
import sys
from pathlib import Path

import yaml

LIBRARY_DEFAULT = Path(__file__).resolve().parents[3] / "block-library"

# Приоритет типов: редкие сверху, универсальные снизу.
TYPE_PRIORITY = [
    "hero", "portrait", "team", "car", "vehicle",
    "product", "interior", "background", "lifestyle",
]

# slot_name pattern → preferred photo types (порядок = приоритет)
SLOT_TYPE_MAP = [
    (re.compile(r"^hero[-_]?(bg|background|image|main)?"), ["hero", "background", "lifestyle"]),
    (re.compile(r"^team\b"),                              ["team", "portrait", "lifestyle"]),
    (re.compile(r"^(portrait|expert|founder|author)"),    ["portrait", "team"]),
    (re.compile(r"^(car|auto)"),                          ["car", "vehicle", "product"]),
    (re.compile(r"^vehicle"),                             ["vehicle", "car", "product"]),
    (re.compile(r"^product"),                             ["product", "lifestyle"]),
    (re.compile(r"^(interior|office|room)"),              ["interior", "background", "lifestyle"]),
    (re.compile(r"^(bg|background|texture)"),             ["background", "interior", "lifestyle"]),
    (re.compile(r"^(gallery|portfolio|case)"),            ["lifestyle", "product", "interior"]),
]


def preferred_types_for_slot(slot_name: str) -> list:
    name = slot_name.lower()
    for pat, types in SLOT_TYPE_MAP:
        if pat.match(name):
            return types
    return ["lifestyle", "portrait", "background"]


def ratio_distance(a: str, b: str) -> float:
    """Расстояние между двумя строковыми ratio. 0 = идентичны, 1 = очень далеко."""
    def to_val(r):
        if not r or r == "?":
            return None
        try:
            w, h = r.split(":")
            return float(w) / float(h)
        except (ValueError, ZeroDivisionError):
            return None
    va, vb = to_val(a), to_val(b)
    if va is None or vb is None:
        return 0.5  # неизвестно — средний штраф
    if vb == 0:
        return 1.0
    return abs(va - vb) / vb


def scan_composed_blocks(composed: Path) -> list:
    """Парсит composed.html, возвращает [(block_id, category)]."""
    if not composed.exists():
        return []
    text = composed.read_text(encoding="utf-8")
    blocks = []
    for m in re.finditer(r'data-block=["\']([\w-]+)["\']', text):
        bid = m.group(1)
        cat = bid.split("-")[1] if "-" in bid else "?"
        blocks.append((bid, cat))
    return blocks


def load_block_meta(library: Path, category: str, block_id: str) -> dict:
    meta_path = library / category / block_id / "meta.yaml"
    if not meta_path.exists():
        # пробуем без жёсткой категории — сканим все
        for cat_dir in library.iterdir():
            if not cat_dir.is_dir():
                continue
            cand = cat_dir / block_id / "meta.yaml"
            if cand.exists():
                meta_path = cand
                break
        else:
            return {}
    return yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}


def collect_photo_slots(blocks: list, library: Path) -> list:
    """Возвращает [{block_id, slot_name, ratio, mobile_ratio, required}]."""
    out = []
    for bid, cat in blocks:
        meta = load_block_meta(library, cat, bid)
        for slot in meta.get("slots") or []:
            if slot.get("type") != "photo":
                continue
            out.append({
                "block_id": bid,
                "slot_name": slot.get("name", "unnamed"),
                "ratio": slot.get("ratio", "?"),
                "mobile_ratio": slot.get("mobile_ratio", ""),
                "required": slot.get("required", False),
            })
    return out


def greedy_match(slots: list, classifications: dict) -> dict:
    """Жадно сопоставляет slot → photo_filename.

    Возвращает {block_id: {slot_name: photo_filename | '__NEEDS_GENERATION__'}}.
    """
    # фото с типами
    available = {fname: meta for fname, meta in classifications.items()}

    # отсортируем слоты по приоритету: required + rarity типа
    def slot_priority(s):
        prefs = preferred_types_for_slot(s["slot_name"])
        # rare type first → берём минимальный индекс в TYPE_PRIORITY
        rarity = min(
            (TYPE_PRIORITY.index(t) for t in prefs if t in TYPE_PRIORITY),
            default=len(TYPE_PRIORITY),
        )
        return (0 if s["required"] else 1, rarity)

    slots_sorted = sorted(slots, key=slot_priority)
    used = set()
    result = {}

    for slot in slots_sorted:
        prefs = preferred_types_for_slot(slot["slot_name"])
        slot_ratio = slot["ratio"]
        best_photo = None
        best_score = (10, 1e9)  # (type_pref_index, ratio_distance) — меньше = лучше

        for fname, meta in available.items():
            if fname in used:
                continue
            ptype = meta.get("type", "lifestyle")
            if ptype not in prefs:
                continue
            pref_idx = prefs.index(ptype)
            rd = ratio_distance(slot_ratio, meta.get("ratio", "?"))
            score = (pref_idx, rd)
            if score < best_score:
                best_score = score
                best_photo = fname

        chosen = best_photo if best_photo else "__NEEDS_GENERATION__"
        if best_photo:
            used.add(best_photo)
        result.setdefault(slot["block_id"], {})[slot["slot_name"]] = chosen

    return result


def main(project_dir: Path, library: Path = None) -> int:
    library = library or LIBRARY_DEFAULT
    inbox = project_dir / "07c_PHOTOS" / "inbox"
    classifications_path = inbox / ".classifications.json"
    if not classifications_path.exists():
        print(f"ERROR: {classifications_path} не найден — запусти classify-photos.py сначала",
              file=sys.stderr)
        return 2

    classifications = json.loads(classifications_path.read_text(encoding="utf-8"))
    if not classifications:
        print("WARN: классификаций нет — нечего сопоставлять", file=sys.stderr)

    composed = project_dir / "07b_COMPOSED" / "composed.html"
    blocks = scan_composed_blocks(composed)
    if not blocks:
        print(f"WARN: composed.html не дал блоков, сканируем всю library", file=sys.stderr)
        # fallback: возьмём все блоки library
        for cat_dir in library.iterdir():
            if not cat_dir.is_dir() or cat_dir.name.startswith("_"):
                continue
            for block_dir in cat_dir.iterdir():
                if (block_dir / "meta.yaml").exists():
                    blocks.append((block_dir.name, cat_dir.name))

    slots = collect_photo_slots(blocks, library)
    if not slots:
        print("INFO: photo-слотов в блоках не найдено", file=sys.stderr)

    mapping = greedy_match(slots, classifications)

    # форматим в selections.yaml-совместимую структуру
    out_blocks = []
    for bid, slot_map in mapping.items():
        out_blocks.append({"block_id": bid, "slots": slot_map})

    out = {
        "version": 1,
        "source": "match-photos-to-slots.py",
        "blocks": out_blocks,
    }
    needs_gen = [
        (bid, slot)
        for bid, slot_map in mapping.items()
        for slot, fname in slot_map.items()
        if fname == "__NEEDS_GENERATION__"
    ]
    out["needs_generation"] = [
        {"block_id": bid, "slot": slot} for bid, slot in needs_gen
    ]

    out_path = project_dir / "07c_PHOTOS" / "selections.suggested.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        yaml.safe_dump(out, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"OK: {len(slots)} slots → {out_path}", file=sys.stderr)
    if needs_gen:
        print(f"   {len(needs_gen)} слотов требуют генерации", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: match-photos-to-slots.py <project_dir> [<library_dir>]", file=sys.stderr)
        sys.exit(2)
    proj = Path(sys.argv[1])
    lib = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    sys.exit(main(proj, lib))

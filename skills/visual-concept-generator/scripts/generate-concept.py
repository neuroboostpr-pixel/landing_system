"""Generate 2-3 visual concept proposals from brief + prototype + reference palettes.

CLI:
  python generate-concept.py --brief path/brief.md --prototype path/prototype.yaml \
    [--palette-json '[{"hex":"#2B72B8","role":"background"}]'] \
    --output path/visual-concept.yaml --index 0
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

CONCEPT_TEMPLATES = [
    {
        "name": "Доверие через статус",
        "emotional_goal": "Снять барьер недоверия к бренду через язык luxury",
        "fit_keywords": ["премиум", "premium", "luxury", "статус", "exclusive", "дорог"],
        "palette": {
            "bg": "#0A0A0A",
            "accent": "#C9A84C",
            "text": "#FFFFFF",
            "surface": "#161616",
        },
        "typography_direction": "Inter 700, строгий гротеск, uppercase заголовки",
        "mood": ["cinematic", "luxury", "editorial"],
        "color_rationale": "Тёмный фон + золото = язык Rolls-Royce / Bentley. Снимает вопрос о премиальности.",
    },
    {
        "name": "Современность и технологии",
        "emotional_goal": "Позиционировать бренд как tech-инновацию, а не просто авто",
        "fit_keywords": ["ev", "electric", "tech", "технолог", "инновац", "будущ"],
        "palette": {
            "bg": "#FFFFFF",
            "accent": "#1A56DB",
            "text": "#111111",
            "surface": "#F5F7FA",
        },
        "typography_direction": "Inter 700, clean, без засечек, modern",
        "mood": ["technical", "minimal", "corporate"],
        "color_rationale": "Белый фон + синий акцент = язык Tesla / BMW i. Технологичность и доверие.",
    },
    {
        "name": "Тепло и семья",
        "emotional_goal": "Показать что автомобиль создан для семьи и реальной жизни",
        "fit_keywords": ["семь", "family", "комфорт", "comfort", "жизн", "life", "простор"],
        "palette": {
            "bg": "#FAFAFA",
            "accent": "#B87333",
            "text": "#1A1A1A",
            "surface": "#F0EDE8",
        },
        "typography_direction": "Inter 500/700, тёплый, читаемый",
        "mood": ["editorial", "warm", "minimal"],
        "color_rationale": "Тёплые нейтралы + медь = близко к эстетике UAE luxury interior. Семейное тепло.",
    },
]


def _extract_brief_text(brief_path: str) -> str:
    p = Path(brief_path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8").lower()


def _extract_prototype_types(prototype_path: str) -> list:
    p = Path(prototype_path)
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return [b.get("type", "") for b in data.get("blocks", [])]


def generate_concepts(
    brief_path: str,
    prototype_path: str,
    palette_context: list,
) -> list:
    """Return 2-3 concept proposals ranked by fit to brief + prototype."""
    brief_text = _extract_brief_text(brief_path)

    scored = []
    for tmpl in CONCEPT_TEMPLATES:
        score = sum(1 for kw in tmpl["fit_keywords"] if kw in brief_text)
        scored.append((score, tmpl))

    scored.sort(key=lambda x: -x[0])
    concepts = [c for _, c in scored[:3]]

    if palette_context:
        ref_concept = _build_ref_concept(palette_context)
        if ref_concept["palette"]["bg"] != concepts[0]["palette"]["bg"]:
            concepts.insert(1, ref_concept)
            concepts = concepts[:3]

    return concepts


def _build_ref_concept(palette_context: list) -> dict:
    """Build a concept based on extracted reference palette."""
    bg = next((c["hex"] for c in palette_context if c.get("role") == "background"), "#FFFFFF")
    accent = next((c["hex"] for c in palette_context if c.get("role") == "accent"), "#C9A84C")
    text_col = "#FFFFFF" if _is_dark(bg) else "#111111"
    surface = _darken(bg, 10) if _is_dark(bg) else _lighten(bg, 5)
    return {
        "name": "По референсу",
        "emotional_goal": "Реализовать визуальный стиль, близкий к предоставленному референсу",
        "fit_keywords": [],
        "palette": {"bg": bg, "accent": accent, "text": text_col, "surface": surface},
        "typography_direction": "Определяется референсом",
        "mood": ["editorial"],
        "color_rationale": f"Палитра извлечена из референса: фон {bg}, акцент {accent}.",
    }


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 < 128


def _darken(hex_color: str, pct: int) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = 1 - pct / 100
    return "#{:02X}{:02X}{:02X}".format(int(r * factor), int(g * factor), int(b * factor))


def _lighten(hex_color: str, pct: int) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    factor = pct / 100
    return "#{:02X}{:02X}{:02X}".format(
        int(r + (255 - r) * factor),
        int(g + (255 - g) * factor),
        int(b + (255 - b) * factor),
    )


def save_concept(concept: dict, output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump(concept, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main(argv: list | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--brief", required=True)
    p.add_argument("--prototype", required=True)
    p.add_argument("--palette-json", default="[]")
    p.add_argument("--output", required=True)
    p.add_argument("--index", type=int, default=0, help="Which concept to save (0-based)")
    ns = p.parse_args(args)

    palette_context = json.loads(ns.palette_json)
    concepts = generate_concepts(ns.brief, ns.prototype, palette_context)

    if ns.index >= len(concepts):
        print(f"ERROR: index {ns.index} out of range (have {len(concepts)} concepts)", file=sys.stderr)
        return 1

    chosen = concepts[ns.index]
    chosen["approved_by_manager"] = True
    save_concept(chosen, ns.output)
    print(f"OK: saved concept '{chosen['name']}' to {ns.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

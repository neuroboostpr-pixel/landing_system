#!/usr/bin/env python3
"""Render <project>/07a_WIREFRAME/wireframe.html from prototype.yaml + block-library."""
from __future__ import annotations

import argparse
import csv
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

CHECKED_TPL = (
    "#{rid}:checked ~ .lp-preview-stage [data-variant=\"{rid}\"] {{ display: block; }}"
)
CHECKED_TAB_TPL = (
    "#{rid}:checked ~ .lp-variant-tabs label[for=\"{rid}\"] {{ "
    "background: #111; color: #fff; border-color: #111; }}"
    "#{rid}:checked ~ .lp-variant-tabs label[for=\"{rid}\"] .lp-tab-title {{ color: #fff; }}"
    "#{rid}:checked ~ .lp-variant-tabs label[for=\"{rid}\"] .lp-tab-id {{ color: #bbb; }}"
)
CHECKED_MOOD_TAB_TPL = (
    "#{rid}:checked ~ .lp-mood-tabs label[for=\"{rid}\"] {{ background: #111; color: #fff; border-color: #111; }}"
)
HIDDEN_RADIO_CSS = "input[name^=\"b\"][type=\"radio\"].lp-variant-radio { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }"
MOOD_RADIOS_CSS = "input[name^=\"mood-\"][type=\"radio\"].lp-mood-radio { position: absolute; left: -9999px; opacity: 0; pointer-events: none; }"

MOODS = ["brutalist", "editorial-warm", "swiss-modernist", "retro-windows", "coral-soft", "monochrome-precision"]

# B36-bridge: блоки используют var(--lp-*); mood palette.css определяют --color-*.
# Этот :root (а) даёт нейтральные lo-fi дефолты, чтобы блок был виден без mood,
# (б) маппит --lp-* ← --color-* — если palette/mood определит --color-*, блок
# подхватит цвет. Префикс блоков (--lp-*) и palette (--color-*) так состыкованы.
WIREFRAME_BRIDGE_CSS = (
    ":root{"
    "--lp-bg:var(--color-bg,#f5f5f5);"
    "--lp-bg-alt:var(--color-bg-alt,#e8e8e8);"
    "--lp-text:var(--color-fg,#1a1a1a);"
    "--lp-text-muted:var(--color-fg-muted,#777);"
    "--lp-accent:var(--color-accent,#333);"
    "--lp-primary:var(--color-accent,#333);"
    "--lp-border:var(--color-border,#e0e0e0);"
    "--lp-radius:8px;--lp-radius-lg:14px;"
    "--lp-spacing-xs:6px;--lp-spacing-sm:12px;--lp-spacing-md:20px;"
    "--lp-spacing-lg:36px;--lp-spacing-xl:64px;"
    "--lp-font-display:system-ui,-apple-system,sans-serif;"
    "--lp-font-body:system-ui,-apple-system,sans-serif;"
    "}"
    # --- Preview-only safety overrides (диск-блоки НЕ трогаем) ---
    # Заголовки некоторых блоков имеют max-width в em + overflow:hidden,
    # рассчитанные на короткие тексты → длинный реальный заголовок обрезается.
    # В превью разрешаем перенос и снимаем обрезку, чтобы текст был виден весь.
    '[class*="__title"],[class*="__headline"],[class*="__heading"]{'
    "max-width:none!important;overflow:visible!important;"
    "white-space:normal!important;overflow-wrap:anywhere;word-break:break-word;"
    "font-size:clamp(1.5rem,4vw,3.25rem)!important;}"
    # Медиа-контейнеры с min-height:40rem+ распирают блок по вертикали в превью.
    # Ограничиваем разумной высотой, картинка-плейсхолдер ложится аккуратно.
    '[class*="__media"],[class*="__visual"],[class*="__image"],[class*="__art"],'
    '[class*="__photo"],[class*="__portrait"],[class*="__picture"]{'
    "min-height:0!important;max-height:26rem!important;}"
    'img,picture{max-height:26rem;}'
)


def _wrap_srcdoc(block_html: str, mood_css: str = "", tokens_css: str = "") -> str:
    """Префиксует/обрамляет HTML блока для srcdoc.

    Порядок каскада (последнее переопределяет):
      1. WIREFRAME_BRIDGE_CSS — нейтральные lp-дефолты + preview-overrides — ДО
         блока (блок может переопределить дефолты под себя),
      2. сам блок (его <style> с собственным :root --lp-*),
      3. mood_css + tokens_css — ПОСЛЕ блока, поэтому переопределяют блочный
         :root: дизайн-система проекта (tokens.json) и mood выигрывают, и блок
         выглядит как на готовом лендинге, а не в своих дефолтных цветах.
    """
    head = f"<style>{WIREFRAME_BRIDGE_CSS}</style>"
    tail = ""
    if mood_css or tokens_css:
        tail = f"<style>{mood_css}{tokens_css}</style>"
    return head + block_html + tail


def _load_project_tokens(project_dir: Path) -> dict:
    """Загрузить tokens.json дизайн-системы проекта (этап 05). {} если нет."""
    import json as _json
    for rel in ("05_ДИЗАЙН-СИСТЕМА/tokens.json", "04_БРЕНД/tokens.json"):
        p = project_dir / rel
        if p.exists():
            try:
                return _json.loads(p.read_text(encoding="utf-8")) or {}
            except Exception:
                return {}
    return {}


def _flatten_token_strings(node, out: dict, prefix: str = "") -> None:
    """Собрать все строковые листья токенов в плоскую карту key→value."""
    if isinstance(node, dict):
        for k, v in node.items():
            key = f"{prefix}-{k}" if prefix else str(k)
            _flatten_token_strings(v, out, key)
    elif isinstance(node, str):
        out[prefix.lower()] = node


def _pick(flat: dict, *needles: str) -> str:
    """Первое значение-цвет, чей ключ содержит ВСЕ слова одного из needles."""
    import re as _re
    hexre = _re.compile(r"^#[0-9a-fA-F]{3,8}$|^rgb")
    for needle in needles:
        words = needle.split()
        for k, v in flat.items():
            if all(w in k for w in words) and hexre.match(str(v).strip()):
                return v.strip()
    return ""


def _design_tokens_root_css(tokens: dict | None) -> str:
    """Построить :root{--lp-*} из tokens.json проекта (любая структура).

    Возвращает '' если токенов нет. Маппинг по семантике ключей.
    """
    if not tokens:
        return ""
    flat: dict = {}
    _flatten_token_strings(tokens.get("colors") or tokens.get("color") or {}, flat)
    fonts: dict = {}
    _flatten_token_strings(
        tokens.get("typography") or tokens.get("fonts") or {}, fonts
    )

    accent = _pick(flat, "primary orange", "accent", "primary", "brand")
    bg = _pick(flat, "bg primary", "neutral white", "bg", "background", "white", "light")
    bg_alt = _pick(flat, "bg alt", "bg secondary", "surface", "light gray", "bg-alt")
    text = _pick(flat, "text primary", "text gray", "fg", "secondary black", "text", "ink")
    muted = _pick(flat, "text muted", "text secondary", "medium gray", "placeholder", "muted")
    border = _pick(flat, "border gray", "border", "border-gray")
    font = ""
    for k, v in fonts.items():
        if "primary" in k or "body" in k or "base" in k or "sans" in k:
            font = v
            break
    if not font and fonts:
        font = next(iter(fonts.values()))

    rules: list[str] = []
    if accent:
        rules.append(f"--lp-accent:{accent};--lp-primary:{accent};")
    if bg:
        rules.append(f"--lp-bg:{bg};")
    if bg_alt:
        rules.append(f"--lp-bg-alt:{bg_alt};")
    if text:
        rules.append(f"--lp-text:{text};")
    if muted:
        rules.append(f"--lp-text-muted:{muted};")
    if border:
        rules.append(f"--lp-border:{border};")
    if font:
        safe = font.replace("{", "").replace("}", "")
        rules.append(f"--lp-font-display:{safe};--lp-font-body:{safe};")
    if not rules:
        return ""
    return ":root{" + "".join(rules) + "}"

# Маппинг технического типа блока -> понятное русское название и цель
BLOCK_TYPE_RU: dict[str, str] = {
    "nav": "Навигация (шапка сайта)",
    "header": "Шапка сайта",
    "hero": "Первый экран сайта",
    "features": "Преимущества / возможности",
    "features-2": "Преимущества (вторая секция)",
    "trust": "Доверие (логотипы / факты)",
    "social-proof": "Социальное доказательство (отзывы / клиенты)",
    "gallery": "Галерея (фотографии / модели)",
    "models-gallery": "Каталог моделей (карусель)",
    "process": "Процесс работы / этапы",
    "pricing": "Цены / тарифы",
    "cta": "Призыв к действию (форма заявки)",
    "cta-form": "Форма заявки",
    "form": "Форма",
    "test-drive-form": "Форма записи на тест-драйв",
    "faq": "Часто задаваемые вопросы (FAQ)",
    "team": "Команда",
    "contacts": "Контакты",
    "footer": "Подвал сайта",
    "quiz": "Квиз / опрос",
}

BLOCK_PURPOSE_RU: dict[str, str] = {
    "hero": "Первое впечатление + главный CTA",
    "features": "Объяснить ценность продукта/услуги",
    "features-2": "Дополнительные преимущества / технические детали",
    "social-proof": "Снять возражения через примеры/отзывы",
    "trust": "Показать что вам можно доверять",
    "gallery": "Дать визуальное представление о продукте",
    "models-gallery": "Показать ассортимент / каталог",
    "process": "Объяснить как происходит сделка",
    "pricing": "Показать цены / варианты тарифов",
    "cta": "Преобразовать интерес в заявку",
    "cta-form": "Собрать контакт через короткую форму",
    "form": "Собрать контакт",
    "test-drive-form": "Записать на тест-драйв",
    "faq": "Снять оставшиеся возражения",
    "team": "Показать кто за компанией стоит",
    "contacts": "Способы связи и адрес",
    "footer": "Технические ссылки и соцсети",
    "nav": "Навигация по разделам сайта",
    "header": "Логотип + меню + быстрый CTA",
    "quiz": "Квалификация и сбор контакта через игру",
}

# Маппинг section.id → catalog block type (для sections-based prototype.yaml)
# Маппинг prototype section.id → B34 category (11 категорий taxonomy.yaml).
# Старых псевдо-категорий (conversion/gallery) больше нет — cta это forms,
# team/gallery относятся к content/features по роли.
SECTION_TO_CATALOG_TYPE: dict[str, str] = {
    "header": "header",
    "hero": "hero",
    "tagline": "features",
    "why_ai_visual": "features",
    "why_neurokreator": "features",
    "for_whom": "features",
    "curriculum": "content",       # «как это работает» → content/process
    "ai_tools": "features",
    "tariffs": "pricing",
    "footer": "footer",
    # Fallback для других типов:
    "features": "features",
    "process": "content",          # process — это variant content
    "pricing": "pricing",
    "faq": "faq",
    "marquee": "marquee",
    "social-proof": "social-proof",
    "trust": "trust",
    "about": "content",
    "gallery": "features",          # галерея-секция → ближайшее по роли
    "team": "content",              # team → content/about (B34 решение 4)
    "contacts": "footer",
    "cta": "forms",                 # CTA-форма заявки → forms
    "forms": "forms",
    "quiz": "quiz",                 # спец-обработка quiz-role в matcher
}

# Опц. маппинг section.id → B34 variant (передаётся как --variant в matcher).
SECTION_TO_VARIANT: dict[str, str] = {
    "curriculum": "process",
    "process": "process",
    "about": "about",
    "team": "about",
}


UX_NOT_AVAILABLE_BANNER = (
    '<div style="margin:24px; padding:16px 24px; background:#fffbe6; border:1px solid #ffe58f; '
    'border-radius:8px; color:#7d4e00; font-size:14px;">'
    '<strong>⚠️ ui-ux-pro-max не найден</strong> — установи по адресу '
    '<code>~/.claude/skills/ui-ux-pro-max/</code> для получения рекомендаций по UX-паттернам. '
    'Инструкция: <a href="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill" target="_blank">'
    'github.com/nextlevelbuilder/ui-ux-pro-max-skill</a></div>'
)


def fail(m: str) -> None:
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def _load_mood_css(library_dir: Path, mood_name: str) -> str:
    """Load CSS from mood's palette.css file. Returns empty string if not found."""
    palette_path = library_dir / "_styles" / mood_name / "palette.css"
    if not palette_path.exists():
        return ""
    return palette_path.read_text(encoding="utf-8")


def _flatten_sections_to_blocks(proto: dict) -> list[dict]:
    """Flatten prototype into canonical blocks list compatible with wireframe logic.

    Supports:
    - Legacy format: proto["blocks"] — return as-is (backward compat)
    - Sections format: proto["sections"][].blocks[] — each section = one wireframe position
    """
    # Legacy: top-level blocks[]
    if "blocks" in proto and isinstance(proto.get("blocks"), list) and proto["blocks"]:
        # Ensure each has a position
        for i, b in enumerate(proto["blocks"]):
            if "position" not in b:
                b["position"] = i + 1
        return proto["blocks"]

    # Sections: flatten
    sections = proto.get("sections", [])
    result = []
    position = 1
    for section in sections:
        section_id = section.get("id", "")
        btype = SECTION_TO_CATALOG_TYPE.get(section_id, "features")
        bvariant = section.get("variant") or SECTION_TO_VARIANT.get(section_id, "")

        merged = _merge_section_blocks(section)
        merged.update({"id": section_id, "type": btype, "position": position})
        if bvariant:
            merged["variant"] = bvariant

        # Copy section-level fields (не перетирая собранные)
        for k in ("name", "layout", "width", "height", "bg_color"):
            if k in section and k not in merged:
                merged[k] = section[k]

        result.append(merged)
        position += 1

    return result


# sub-block.type → семантическое поле блока для resolve_slot/SLOT_MAPPING.
_SUBTYPE_TO_FIELD = {
    "heading": "title", "title": "title", "headline": "title",
    "paragraph": "subhead", "subtitle": "subhead", "lead": "subhead",
    "text": "subhead",
    "button": "cta", "cta_button": "cta", "cta": "cta",
}
# типы sub-блоков, которые НЕ идут в items[] (это единичные смысловые поля).
_SINGULAR_SUBTYPES = set(_SUBTYPE_TO_FIELD) | {
    "logo", "menu", "info_badge", "scrolling_list",
}


def _merge_section_blocks(section: dict) -> dict:
    """Собрать данные sub-блоков секции БЕЗ потери при коллизии.

    - Повторяющиеся sub-блоки (module/feature/card/tariff/step/…) → items[]
      (для слотов feature-N-*, card-N-*, tier-N-*, badge-N).
    - heading/paragraph/button → семантические поля title/subhead/cta.
    - Прочие первые-встреченные поля сохраняются как есть (обратная совмест.).
    """
    merged: dict = {}
    items: list = []
    badges: list = []
    secondary_cta_seen = False

    for sub in section.get("blocks", []):
        if not isinstance(sub, dict):
            continue
        stype = (sub.get("type") or "").lower()

        # повторяющиеся карточки → items[]
        if stype not in _SINGULAR_SUBTYPES:
            items.append(dict(sub))
            continue

        # info_badge → копим в badges[] (для badge-1/2/3)
        if stype == "info_badge":
            label = sub.get("label") or sub.get("text") or ""
            value = sub.get("value") or ""
            badges.append((f"{label} {value}".strip() or label or value))
            continue

        # кнопки → cta (первая = primary, вторая = secondary)
        if stype in ("button", "cta_button", "cta"):
            txt = sub.get("text") or sub.get("label") or ""
            if "cta" not in merged:
                merged["cta"] = {"text": txt, "href": sub.get("href", "#")}
            elif not secondary_cta_seen:
                merged["cta_secondary"] = txt
                secondary_cta_seen = True
            continue

        # heading/paragraph → семантическое поле, не перетирая занятое
        field = _SUBTYPE_TO_FIELD.get(stype)
        if field and field not in merged:
            merged[field] = sub.get("text") or sub.get("highlight") or ""
            # сохраняем доп. поля sub-блока (highlight, label, value)
            for k, v in sub.items():
                if k not in ("type", "text") and k not in merged:
                    merged[k] = v
            continue

        # прочее — первое встреченное поле выигрывает (как раньше)
        for k, v in sub.items():
            if k not in merged:
                merged[k] = v

    if items:
        merged["items"] = items
    if badges:
        merged.setdefault("badges", badges)
        for i, b in enumerate(badges, 1):
            merged.setdefault(f"badge-{i}", b)
    return merged


def load_ux_patterns(rules_dir: Path, niche: str) -> list[dict]:
    """Load top-5 landing patterns from landing.csv, filtered by niche keywords."""
    landing_csv = rules_dir / "landing.csv"
    if not landing_csv.exists():
        print(
            f"WARNING: ui-ux-pro-max landing.csv not found at {landing_csv}. "
            "Install ui-ux-pro-max at ~/.claude/skills/ui-ux-pro-max/ for pattern recommendations.",
            file=sys.stderr,
        )
        return []

    patterns: list[dict] = []
    niche_lower = niche.lower()
    niche_words = set(niche_lower.replace("-", " ").replace("_", " ").split())

    with landing_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    # Find niche-relevant patterns first
    matched: list[dict] = []
    unmatched: list[dict] = []
    for row in all_rows:
        keywords_str = row.get("Keywords", "").lower()
        keywords_set = set(k.strip() for k in keywords_str.replace(",", " ").split())
        if niche_words & keywords_set or any(
            w in keywords_str for w in niche_words
        ):
            matched.append(row)
        else:
            unmatched.append(row)

    selected = (matched + unmatched)[:5]
    return selected


def load_ux_rules(rules_dir: Path, block_types: list[str]) -> list[dict]:
    """Load critical + high severity UX rules from ux-guidelines.csv AND web-interface.csv (merged, deduped by Issue)."""
    rules: list[dict] = []
    seen_issues: set[str] = set()

    for csv_name in ("ux-guidelines.csv", "web-interface.csv"):
        csv_path = rules_dir / csv_name
        if not csv_path.exists():
            print(
                f"WARNING: ui-ux-pro-max {csv_name} not found at {csv_path}.",
                file=sys.stderr,
            )
            continue
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                severity = (row.get("Severity") or "").strip().lower()
                if severity in ("critical", "high"):
                    issue_key = (row.get("Issue") or "").strip()
                    if issue_key not in seen_issues:
                        seen_issues.add(issue_key)
                        rules.append(row)

    return rules


def load_colors(rules_dir: Path, niche: str) -> list[dict]:
    """Load top 3 palette rows from colors.csv filtered by niche keywords."""
    colors_csv = rules_dir / "colors.csv"
    if not colors_csv.exists():
        return []
    niche_lower = niche.lower().replace("-", " ").replace("_", " ")
    niche_words = set(niche_lower.split())
    with colors_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    matched: list[dict] = []
    unmatched: list[dict] = []
    for row in rows:
        product_type = row.get("Product Type", "").lower()
        if any(w in product_type for w in niche_words):
            matched.append(row)
        else:
            unmatched.append(row)
    return (matched + unmatched)[:3]


def load_typography(rules_dir: Path, niche: str) -> list[dict]:
    """Load top 3 font pairs from typography.csv filtered by niche."""
    typo_csv = rules_dir / "typography.csv"
    if not typo_csv.exists():
        return []
    niche_lower = niche.lower().replace("-", " ").replace("_", " ")
    niche_words = set(niche_lower.split())
    with typo_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    matched: list[dict] = []
    unmatched: list[dict] = []
    for row in rows:
        keywords = row.get("Mood/Style Keywords", "").lower()
        best_for = row.get("Best For", "").lower()
        combined = keywords + " " + best_for
        if any(w in combined for w in niche_words):
            matched.append(row)
        else:
            unmatched.append(row)
    return (matched + unmatched)[:3]


def load_styles(rules_dir: Path) -> list[dict]:
    """Load all styles from styles.csv for per-block style hint lookup."""
    styles_csv = rules_dir / "styles.csv"
    if not styles_csv.exists():
        return []
    with styles_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def render_palettes_html(palettes: list[dict]) -> str:
    """Render top color palettes as swatch cards."""
    if not palettes:
        return "<p style='color:#999;font-size:13px;'>colors.csv не найден</p>"
    parts: list[str] = []
    for p in palettes:
        product = html.escape(p.get("Product Type", "—"))
        primary = html.escape(p.get("Primary (Hex)", "#ccc"))
        secondary = html.escape(p.get("Secondary (Hex)", "#eee"))
        cta = html.escape(p.get("CTA (Hex)", "#666"))
        bg = html.escape(p.get("Background (Hex)", "#fff"))
        text_c = html.escape(p.get("Text (Hex)", "#000"))
        swatches = "".join(
            f'<div style="width:32px;height:32px;border-radius:6px;background:{c};border:1px solid rgba(0,0,0,.1);title={c}"></div>'
            for c in [bg, primary, secondary, cta, text_c]
        )
        parts.append(
            f'<div class="palette-card">'
            f'<div class="palette-name">{product}</div>'
            f'<div class="palette-swatches">{swatches}</div>'
            f'<div class="palette-hex">Accent: {primary} | CTA: {cta}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def render_typography_html(pairs: list[dict]) -> str:
    """Render typography pairs as sample cards."""
    if not pairs:
        return "<p style='color:#999;font-size:13px;'>typography.csv не найден</p>"
    parts: list[str] = []
    for p in pairs:
        name = html.escape(p.get("Font Pairing Name", "—"))
        heading = html.escape(p.get("Heading Font", "—"))
        body = html.escape(p.get("Body Font", "—"))
        mood = html.escape(p.get("Mood/Style Keywords", "—")[:60])
        parts.append(
            f'<div class="typo-card">'
            f'<div class="typo-name">{name}</div>'
            f'<div class="typo-heading" style="font-size:18px;font-weight:700;">{heading}</div>'
            f'<div class="typo-body" style="font-size:13px;color:#666;">{body}</div>'
            f'<div class="typo-mood" style="font-size:11px;color:#999;">{mood}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def get_style_hint_for_block(block_meta: dict, all_styles: list[dict]) -> str:
    """Return a style recommendation string for a block based on recommended_styles_ru."""
    rsr = block_meta.get("recommended_styles_ru", [])
    if not rsr:
        return ""
    hints: list[str] = []
    for style_name in rsr[:2]:
        for s in all_styles:
            if style_name.lower() in s.get("Style Category", "").lower():
                keywords = s.get("AI Prompt Keywords", "")[:80]
                hints.append(f"<strong>{html.escape(style_name)}</strong>: {html.escape(keywords)}")
                break
        else:
            hints.append(f"<strong>{html.escape(style_name)}</strong>")
    return " | ".join(hints)


def render_ux_patterns_html(patterns: list[dict]) -> str:
    """Render patterns list as HTML cards."""
    if not patterns:
        return ""
    parts: list[str] = []
    for p in patterns:
        name = html.escape(p.get("Pattern Name", "—"))
        section_order = html.escape(p.get("Section Order", "—"))
        cta = html.escape(p.get("Primary CTA Placement", "—"))
        conversion = html.escape(p.get("Conversion Optimization", "—"))
        parts.append(
            f'<div class="ux-pattern">'
            f'<div class="ux-pattern-title">{name}</div>'
            f'<div class="ux-pattern-detail"><strong>Section order:</strong> {section_order}</div>'
            f'<div class="ux-pattern-detail"><strong>CTA placement:</strong> {cta}</div>'
            f'<div class="ux-pattern-detail"><strong>Conversion:</strong> {conversion}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def hint_for_block(btype: str, ux_patterns: list[dict]) -> str:
    """Find a UX pattern hint for a block type from landing.csv."""
    for p in ux_patterns:
        kw = p.get("Keywords", "").lower()
        if btype.replace("-", " ") in kw or btype in kw:
            name = p.get("Pattern Name", "")
            conversion = p.get("Conversion Optimization", "")[:120]
            return f"💡 UX-паттерн: {name} — {conversion}"
    return ""


def render_ux_rules_html(rules: list[dict]) -> str:
    """Render rules list as HTML list items."""
    if not rules:
        return ""
    parts: list[str] = []
    for r in rules:
        severity = r.get("Severity", "").strip().lower()
        category = html.escape(r.get("Category", "—"))
        issue = html.escape(r.get("Issue", "—"))
        description = html.escape(r.get("Description", "—"))
        parts.append(
            f'<li class="ux-rule ux-rule-{severity}">'
            f'<strong>{category}:</strong> {issue} — {description}'
            f'</li>'
        )
    return "\n".join(parts)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True)
    p.add_argument("--library", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--top", type=int, default=8,
                   help="Max candidates shown per block (default: 8, was 5)")
    p.add_argument(
        "--ux-rules",
        default=str(Path.home() / ".claude" / "skills" / "ui-ux-pro-max" / "data"),
        help="Path to ui-ux-pro-max/data/ directory (default: ~/.claude/skills/ui-ux-pro-max/data/)",
    )
    args = p.parse_args()

    project_dir = Path(args.project)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        fail(f"no prototype.yaml at {proto_path}")
    proto = yaml.safe_load(proto_path.read_text(encoding="utf-8"))
    # Дизайн-система проекта (этап 05) → :root для каждого блока в превью.
    # Реальные цвета/шрифты клиента; пусто (нейтральный fallback) до этапа 05.
    _tokens_css = _design_tokens_root_css(_load_project_tokens(project_dir))
    niche = (proto.get("project") or {}).get("niche") or proto.get("niche") or "generic"
    slug = (
        (proto.get("project") or {}).get("slug")
        or proto.get("slug")
        or proto.get("name", "project")
    )

    # Flatten sections-based proto into canonical blocks list
    proto_blocks = _flatten_sections_to_blocks(proto)

    matcher_script = Path(__file__).parent / "match-candidates.py"
    inject_content_script = (
        Path(__file__).parent.parent.parent
        / "block-composition" / "scripts" / "inject-content.py"
    )
    if not inject_content_script.exists():
        fail(f"inject-content.py not found at {inject_content_script}")

    # Read prototype.md for top-of-page preview (fall back to YAML dump if missing)
    proto_md_path = project_dir / "07_ПРОТОТИП" / "prototype.md"
    if proto_md_path.exists():
        prototype_source_text = proto_md_path.read_text(encoding="utf-8")
    else:
        prototype_source_text = (
            "(prototype.md not found — showing parsed YAML instead)\n\n"
            + yaml.dump(proto, sort_keys=False, allow_unicode=True)
        )

    # --- Load ui-ux-pro-max data ---
    rules_dir = Path(args.ux_rules).expanduser()
    patterns = load_ux_patterns(rules_dir, niche)
    block_types = [b["type"] for b in proto_blocks]
    rules = load_ux_rules(rules_dir, block_types)
    palettes = load_colors(rules_dir, niche)
    typo_pairs = load_typography(rules_dir, niche)
    all_styles = load_styles(rules_dir)

    ux_available = (rules_dir / "landing.csv").exists()
    if not ux_available:
        ux_patterns_html = UX_NOT_AVAILABLE_BANNER
        ux_rules_html = ""
        palettes_html = ""
        typography_html = ""
    else:
        ux_patterns_html = render_ux_patterns_html(patterns)
        ux_rules_html = render_ux_rules_html(rules)
        palettes_html = render_palettes_html(palettes)
        typography_html = render_typography_html(typo_pairs)

    print(
        f"INFO: ui-ux-pro-max — {len(patterns)} patterns, {len(rules)} rules, "
        f"{len(palettes)} palettes, {len(typo_pairs)} typo pairs, "
        f"{len(all_styles)} styles loaded.",
        file=sys.stderr,
    )

    blocks_html_parts: list[str] = []
    checked_rules: list[str] = []
    checked_tab_rules: list[str] = []
    candidates_log: dict = {"project_slug": slug, "blocks": []}

    # Check if enrichment-log.md exists alongside prototype.yaml
    enrichment_log_path = project_dir / "07_ПРОТОТИП" / "enrichment-log.md"
    enrichment_log_content = ""
    if enrichment_log_path.exists():
        try:
            enrichment_log_content = enrichment_log_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            enrichment_log_content = enrichment_log_path.read_text(encoding="cp1251")

    total_blocks = len(proto_blocks)

    # Count blocks per B34 category from catalog.yaml (NOT by folder name —
    # after B34 a block's category can differ from its physical folder, which
    # caused "shown 11 of 10": footer counted folders, matcher counted category).
    library_dir = Path(args.library)
    category_counts: dict[str, int] = {}
    _catalog_path = library_dir / "catalog.yaml"
    if _catalog_path.exists():
        _cat = yaml.safe_load(_catalog_path.read_text(encoding="utf-8")) or {}
        for b in _cat.get("blocks", []):
            c = b.get("category")
            if c:
                category_counts[c] = category_counts.get(c, 0) + 1
    for block in proto_blocks:
        position = block["position"]
        btype = block["type"]
        bvariant = block.get("variant", "")
        quiz_role = block.get("quiz_role", "")
        matcher_cmd = [
            sys.executable, str(matcher_script),
            "--library", args.library,
            "--type", btype,
            "--niche", niche,
            "--top", "999",  # Show ALL candidates (no limiting)
        ]
        if bvariant:
            matcher_cmd += ["--variant", bvariant]
        if quiz_role:
            matcher_cmd += ["--quiz-role", quiz_role]
        try:
            res = subprocess.run(
                matcher_cmd,
                capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
            )
            candidate_ids = json.loads(res.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"WARN: matcher failed for {btype}: {e}", file=sys.stderr)
            candidate_ids = []

        if not candidate_ids:
            candidates_log["blocks"].append({
                "block_position": position,
                "block_type": btype,
                "candidates": [],
                "warning": f"no candidates for {btype} / {niche}",
            })
            type_ru = BLOCK_TYPE_RU.get(btype, btype)
            purpose_ru = BLOCK_PURPOSE_RU.get(btype, "")
            blocks_html_parts.append(
                f'<section class="lp-block-wrapper" data-block-position="{position}">'
                f'<header class="lp-block-header">'
                f'<div class="lp-block-counter">БЛОК {position} / {total_blocks}</div>'
                f'<h2>{html.escape(type_ru)} <span class="lp-block-type-slug">({html.escape(btype)})</span></h2>'
                f'<p class="lp-block-sub"><strong>Цель блока:</strong> {html.escape(purpose_ru) or "—"}</p>'
                f'<p class="lp-block-sub" style="color:#c4424c;"><strong>⚠️ Нет подходящих кандидатов</strong> в block-library для ниши <code>{html.escape(niche)}</code>.</p>'
                f'</header>'
                f'<div class="lp-block-empty">Нужен новый блок? '
                f'<code>python3 skills/block-library-management/scripts/scaffold-block.py --id &lt;new-id&gt; --category {html.escape(btype)}</code>'
                f'</div></section>'
            )
            continue

        candidates_log["blocks"].append({
            "block_position": position,
            "block_type": btype,
            "candidates": candidate_ids,
        })

        radios = []
        variant_cards = []
        tab_labels = []
        for i, cid in enumerate(candidate_ids):
            block_dir = _block_dir_for(args.library, cid)

            # Inject content from prototype into each template before iframe embedding.
            # Uses inject-content.py from block-composition skill — same script as 07b Compose.
            with tempfile.TemporaryDirectory() as tmp:
                tmp_p = Path(tmp)
                injected_d = tmp_p / f"{cid}-desktop.html"
                injected_m = tmp_p / f"{cid}-mobile.html"
                for src_name, out_path in (
                    ("template.html", injected_d),
                    ("template-mobile.html", injected_m),
                ):
                    src_html = block_dir / "assets" / src_name
                    try:
                        subprocess.run(
                            [
                                sys.executable, str(inject_content_script),
                                "--template", str(src_html),
                                "--prototype", str(proto_path),
                                "--position", str(position),
                                "--output", str(out_path),
                            ],
                            capture_output=True, text=True, check=True, encoding="utf-8", errors="replace",
                        )
                    except subprocess.CalledProcessError as e:
                        # Fall back to raw template if injection fails
                        print(
                            f"WARN: inject-content failed for {cid}/{src_name}: "
                            f"{e.stderr.strip()}",
                            file=sys.stderr,
                        )
                        if src_html.exists():
                            out_path.write_text(src_html.read_text(encoding="utf-8"))
                        else:
                            # Block template doesn't exist, skip this block
                            out_path.write_text(f"<p>Block {cid}/{src_name} not found</p>")

                # Ensure both files exist before reading
                if not injected_d.exists():
                    injected_d.write_text(f"<p>Desktop template for {cid} not found</p>")
                if not injected_m.exists():
                    injected_m.write_text(f"<p>Mobile template for {cid} not found</p>")

                tmpl_d = injected_d.read_text(encoding="utf-8")
                tmpl_m = injected_m.read_text(encoding="utf-8")

            rid = f"b{position}-v{i}"
            checked = "checked" if i == 0 else ""
            # Load Russian display name and layout summary from meta.yaml
            meta_path = block_dir / "meta.yaml"
            meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            # B36-bridge + дизайн-система: блоки на var(--lp-*); подмешиваем
            # :root-дефолты (+ mood palette, если у блока выбран style_mood), чтобы
            # переменные разрешались и стили накладывались в превью.
            _mood = meta.get("style_mood") or ""
            _mood_css = _load_mood_css(Path(args.library), _mood) if _mood else ""
            tmpl_d = _wrap_srcdoc(tmpl_d, _mood_css, _tokens_css)
            tmpl_m = _wrap_srcdoc(tmpl_m, _mood_css, _tokens_css)
            # display_name_ru — короткое человеко-понятное имя; layout_summary_ru — что в макете
            display_name_full = meta.get("display_name_ru") or cid
            # Trim until first dot/newline for a short headline; keep full as tooltip
            short_name = display_name_full.split(".")[0].split("\n")[0].strip()
            if len(short_name) > 90:
                short_name = short_name[:87].rstrip() + "…"
            short_name_html = html.escape(short_name)
            layout_summary = html.escape(meta.get("layout_summary_ru", "") or display_name_full)
            niches_meta = meta.get("use_cases") or meta.get("niches_suitable") or []
            niches_str = ", ".join(niches_meta[:4]) if isinstance(niches_meta, list) else ""
            mood_str = meta.get("style_mood") or ""
            meta_tags_parts: list[str] = []
            if niches_str:
                meta_tags_parts.append(html.escape(niches_str))
            if mood_str:
                meta_tags_parts.append(html.escape(mood_str))
            meta_tags = " · ".join(meta_tags_parts)
            radios.append(
                f'<input type="radio" class="lp-variant-radio" name="b{position}" id="{rid}" '
                f'value="{html.escape(cid, quote=True)}" data-position="{position}" {checked}>'
            )
            # Desktop iframe рендерится при ФИКСИРОВАННОЙ ширине 1280px (где
            # блочные vw/min-height работают как на реальном лендинге), затем
            # масштабируется CSS transform:scale внутри .iframe-scaler — блок
            # выглядит как на странице, только уменьшенный (не искажён).
            variant_cards.append(
                f'<div class="lp-preview-card" data-variant="{rid}">'
                f'<div class="device desktop"><div class="device-label">Desktop · {html.escape(cid)}</div>'
                f'<div class="iframe-scaler desktop-scaler">'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_d, quote=True)}"></iframe></div></div>'
                f'<div class="device mobile"><div class="device-label">Mobile · {html.escape(cid)}</div>'
                f'<div class="iframe-scaler mobile-scaler">'
                f'<iframe sandbox srcdoc="{html.escape(tmpl_m, quote=True)}"></iframe></div></div>'
                f'</div>'
            )
            tab_labels.append(
                f'<label for="{rid}" title="{layout_summary}">'
                f'<span class="lp-tab-title">Вариант {i+1} — {short_name_html}</span>'
                f'<span class="lp-tab-id" style="display:block;font-size:11px;color:#888;margin-top:2px;">'
                f'{html.escape(cid)}{(" · " + meta_tags) if meta_tags else ""}'
                f'</span>'
                f'</label>'
            )
            checked_rules.append(CHECKED_TPL.format(rid=rid))
            checked_tab_rules.append(CHECKED_TAB_TPL.format(rid=rid))

        # Block-level hint
        hint = hint_for_block(btype, patterns)
        last_meta: dict = {}
        if candidate_ids:
            last_block_dir = _block_dir_for(args.library, candidate_ids[0])
            last_meta_path = last_block_dir / "meta.yaml"
            if last_meta_path.exists():
                last_meta = yaml.safe_load(last_meta_path.read_text(encoding="utf-8")) or {}
        style_hint = get_style_hint_for_block(last_meta, all_styles)
        hint_parts = []
        if hint:
            hint_parts.append(html.escape(hint))
        if style_hint:
            hint_parts.append(f"🎨 Стиль: {style_hint}")
        hint_html = (
            f'<div class="lp-block-hint">{"<br>".join(hint_parts)}</div>' if hint_parts else ''
        )

        # Pull a short description of THIS block from prototype for the header
        proto_block = block
        # "Что здесь" — конкретный текст первой смысловой строки прототипа
        what_here_text = ""
        for k in ("headline", "title", "subhead", "subtitle", "primary_cta", "cta_primary", "cta"):
            v = proto_block.get(k)
            if v and isinstance(v, str) and v.strip():
                what_here_text = v.strip()[:200]
                break

        # "Контент" — список slot-полей которые есть в прото-блоке
        SLOT_KEYS_RU = {
            "headline": "заголовок",
            "title": "заголовок",
            "subhead": "подзаголовок",
            "subtitle": "подзаголовок",
            "cta_primary": "главная кнопка",
            "primary_cta": "главная кнопка",
            "cta_secondary": "вторая кнопка",
            "cta": "кнопка",
            "photo_slot": "фото",
            "image": "изображение",
            "items": "список пунктов",
            "features": "список преимуществ",
            "logos": "логотипы",
            "form": "форма",
            "questions": "вопросы",
            "badges": "бейджи",
            "stats": "цифры",
            "testimonials": "отзывы",
            "models": "модели",
            "faq": "вопросы-ответы",
            "cards": "карточки",
            "metrics": "метрики",
        }
        content_slots: list[str] = []
        for k in proto_block.keys():
            if k in ("id", "type", "position", "quiz_role", "notes"):
                continue
            ru = SLOT_KEYS_RU.get(k)
            if ru and ru not in content_slots:
                content_slots.append(ru)
        content_slots_str = ", ".join(content_slots) if content_slots else "—"

        type_ru = BLOCK_TYPE_RU.get(btype, btype)
        purpose_ru = BLOCK_PURPOSE_RU.get(btype, "—")

        # Composite header — 4 строки: счётчик, тип, что здесь, цель, контент
        what_here_html = (
            f'<p class="lp-block-sub"><strong>Что здесь:</strong> {html.escape(what_here_text)}</p>'
            if what_here_text else ""
        )

        # Footer: "shown N of M available <category> blocks" + links
        first_cat = _category_for(args.library, candidate_ids[0]) if candidate_ids else btype
        cat_total = category_counts.get(first_cat, len(candidate_ids))
        shown_n = len(candidate_ids)
        # Link from <project>/07a_WIREFRAME/wireframe.html to landing-system block-library:
        # use file:// absolute path so the link works regardless of cwd.
        cat_dir_abs = (Path(args.library) / first_cat).resolve()
        cat_dir_url = f"file://{cat_dir_abs}"
        footer_html = (
            f'<footer class="lp-block-footer">'
            f'<p>Показано {shown_n} из <strong>{cat_total}</strong> доступных '
            f'<code>{html.escape(first_cat)}</code> блоков. Все блоки →&nbsp;'
            f'<a href="{html.escape(cat_dir_url, quote=True)}" target="_blank">'
            f'открыть папку библиотеки</a>.</p>'
            f'</footer>'
        )

        # Reorder buttons (Feature 2: Block Reordering)
        disabled_up = "disabled" if position == 1 else ""
        disabled_down = "disabled" if position == total_blocks else ""
        reorder_buttons = (
            f'<div class="lp-reorder-buttons">'
            f'<button type="button" onclick="reorderBlock(this, -1)" {disabled_up}>'
            f'↑ вверх</button>'
            f'<button type="button" onclick="reorderBlock(this, +1)" {disabled_down}>'
            f'↓ вниз</button>'
            f'</div>'
        )

        section = (
            f'<section class="lp-block-wrapper" data-block-position="{position}">'
            f'{reorder_buttons}'
            f'<header class="lp-block-header">'
            f'<div class="lp-block-counter" style="font-size:11px;letter-spacing:1px;color:#888;text-transform:uppercase;font-weight:600;">'
            f'БЛОК {position} / {total_blocks}</div>'
            f'<h2 style="margin:4px 0 8px;">{html.escape(type_ru)} '
            f'<span class="lp-block-type-slug" style="font-size:13px;color:#aaa;font-weight:400;">({html.escape(btype)})</span></h2>'
            f'{what_here_html}'
            f'<p class="lp-block-sub"><strong>Цель блока:</strong> {html.escape(purpose_ru)}</p>'
            f'<p class="lp-block-sub" style="color:#666;font-size:13px;"><strong>Контент:</strong> {html.escape(content_slots_str)}</p>'
            f'</header>'
            f'{hint_html}'
            f'{"".join(radios)}'
            f'<div class="lp-preview-stage">{"".join(variant_cards)}</div>'
            f'<nav class="lp-variant-tabs">{"".join(tab_labels)}</nav>'
            f'{footer_html}'
            f'</section>'
        )
        blocks_html_parts.append(section)

    # Build enrichment panel HTML if log exists
    if enrichment_log_content:
        enrichment_panel_html = (
            '<details class="enrichment-panel" open>'
            '<summary>Квиз-фаннел расширен по best-practices (Marquiz / Tilda / Skillbox)</summary>'
            f'<pre>{html.escape(enrichment_log_content)}</pre>'
            '</details>'
        )
    else:
        enrichment_panel_html = ""

    shell = Path(args.template).read_text(encoding="utf-8")
    out = (
        shell.replace("{{project_slug}}", slug)
        .replace("{{niche}}", niche)
        .replace("{{prototype_source}}", html.escape(prototype_source_text))
        .replace("{{blocks_html}}", "\n".join(blocks_html_parts))
        .replace("{{checked_rules}}", HIDDEN_RADIO_CSS + "\n" + "\n".join(checked_rules))
        .replace("{{checked_tab_rules}}", "\n".join(checked_tab_rules))
        # mood-табы — неактивная фича; зануляем плейсхолдер, иначе он остаётся
        # сырым текстом в CSS и ломает стиль (at-rule expected на этой строке).
        .replace("{{checked_mood_tab_rules}}", "")
        .replace("{{ux_patterns_html}}", ux_patterns_html)
        .replace("{{ux_rules_html}}", ux_rules_html)
        .replace("{{palettes_html}}", palettes_html)
        .replace("{{typography_html}}", typography_html)
        .replace("{{enrichment_panel_html}}", enrichment_panel_html)
    )
    out_html = project_dir / "07a_WIREFRAME" / "wireframe.html"
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(out, encoding="utf-8")

    (project_dir / "07a_WIREFRAME" / "candidates.yaml").write_text(
        yaml.dump(candidates_log, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    print(f"OK: rendered {out_html}")


def _category_for(library: str, block_id: str) -> str:
    cat = yaml.safe_load((Path(library) / "catalog.yaml").read_text(encoding="utf-8"))
    for b in cat.get("blocks", []):
        if b["id"] == block_id:
            return b["category"]
    raise SystemExit(f"ERROR: block {block_id} not in catalog")


def _block_dir_for(library: str, block_id: str) -> Path:
    """Физический путь к папке блока на диске.

    B34: семантическая `category` (footer) может отличаться от папки на диске
    (contacts/). Для путей берём `folder`/`path` из каталога, НЕ `category`.
    """
    lib = Path(library)
    cat = yaml.safe_load((lib / "catalog.yaml").read_text(encoding="utf-8"))
    for b in cat.get("blocks", []):
        if b["id"] == block_id:
            if b.get("path"):
                return lib / b["path"]
            return lib / b.get("folder", b["category"]) / block_id
    raise SystemExit(f"ERROR: block {block_id} not in catalog")


if __name__ == "__main__":
    main()

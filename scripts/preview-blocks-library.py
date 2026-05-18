#!/usr/bin/env python3
"""Render ALL blocks from block-library/ into one HTML gallery.

Supports BOTH block formats:
  - NEW (imported / scaffolded): <block>/index.html + <block>/styles.css
    Uses {{slot:NAME}} text placeholders.
  - LEGACY (ru-*): <block>/assets/template.html
    Self-contained: <style> + HTML with data-slot attributes.

Each block gets dummy content substituted for slots so the rendered preview
makes visual sense.

Top of page has a sticky nav with category links + a radio filter:
  - Все
  - Только новые импортированные
  - Только legacy ru-*

Output: /tmp/block-library-gallery.html

Usage:
  python3 scripts/preview-blocks-library.py
"""
import re
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "block-library"
OUT = Path("/tmp/block-library-gallery.html")

# Dummy content for typical slot names (used by both formats).
DUMMY = {
    "hero-image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1920&q=80",
    "hero-image-mobile": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=768&q=80",
    "hero-image-alt": "Premium",
    "hero-badge": "PREMIUM 2026",
    "hero-title": "Премиум продукт для требовательных",
    "hero-subhead": "Эксклюзивная подборка с гарантией. Доступ в день обращения.",
    "primary-cta-url": "#contact",
    "primary-cta-label": "Получить предложение →",
    "secondary-cta-url": "#learn",
    "secondary-cta-label": "Узнать больше",
    "hero-panel-label": "В наличии",
    "hero-panel-value": "47",
    "hero-panel-text": "позиций готовы прямо сейчас",
    "heading": "Заголовок секции",
    "title": "Главный заголовок",
    "subtitle": "Подзаголовок секции",
    "subhead": "Подзаголовок секции",
    "description": "Описание раздела с деталями для пользователя.",
    "text": "Текст блока с описанием особенностей",
    "cta-label": "Действие",
    "cta-url": "#",
    "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=1200&q=80",
    "image-alt": "Image",
    "icon": "★",
    "label": "Метка",
    "value": "100",
    "name": "Иван Петров",
    "role": "Директор",
    "company": "Компания",
    "quote": "Отличный сервис, рекомендую",
    "phone": "+7 (495) 000-00-00",
    "email": "info@example.com",
    "address": "Москва, ул. Примерная 1",
    "eyebrow": "ПРЕМИУМ",
    "portrait-image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&q=80",
    "portrait-image-alt": "Эксперт",
    "portrait-caption": "Анна Иванова, эксперт",
}

# Patterned dummies for "feature-N-*", "item-N-*", "step-N-*" etc.
FEATURE_DUMMIES_TITLE = [
    "Безупречное качество", "Гарантия результата", "Опытная команда",
    "Прозрачная цена", "Быстрая работа", "Полное сопровождение",
    "Личный менеджер", "Доступ 24/7", "Бесплатная консультация",
    "Без скрытых платежей", "Поддержка после", "Адаптация под клиента",
]
FEATURE_DUMMIES_TEXT = [
    "Каждый этап работы построен на проверенных стандартах премиум-сегмента.",
    "Заключаем договор и фиксируем сроки. Все обязательства документально.",
    "С вами работают специалисты с 10+ годами опыта в отрасли.",
    "Стоимость определяется в начале — никаких сюрпризов и доплат.",
    "Реакция за 5 минут. Первый результат — в течение суток.",
    "Сопровождаем от заявки до получения результата.",
]

TOKENS = """
:root {
  --lp-bg: #0a0a0a; --lp-text: #f5f5f5; --lp-text-muted: #aaa;
  --lp-primary: #d4af37; --lp-accent: #c9a961;
  --lp-radius: 8px; --lp-spacing-sm: 0.75rem; --lp-spacing-md: 1.5rem;
  --lp-spacing-lg: 2.5rem; --lp-spacing-xl: 4rem;
  --lp-font-body: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
  --lp-font-display: 'Playfair Display', Georgia, serif;
  --lp-card-bg: #1a1a1a; --lp-border: rgba(255,255,255,0.1);
}
"""

_SLOT_RE = re.compile(r"\{\{slot:([^}]+)\}\}")


def fill_slot(name: str) -> str:
    """Return a dummy value for a slot name (handles patterned slots)."""
    if name in DUMMY:
        return DUMMY[name]

    # feature-N-title / feature-N-text / feature-N-badge / item-N-*
    m = re.match(
        r"^(?:feature|item|step|stage|faq|tier|plan|card|metric|stat|fact|"
        r"benefit|advantage|service|testimonial|review|model|tab|point|reason)"
        r"[-_](\d+)(?:[-_](.+))?$",
        name,
    )
    if m:
        idx = max(0, int(m.group(1)) - 1)
        field = (m.group(2) or "title").strip()
        if field in ("title", "name", "label", "heading", "q", "question"):
            return FEATURE_DUMMIES_TITLE[idx % len(FEATURE_DUMMIES_TITLE)]
        if field in ("text", "description", "body", "a", "answer", "lead"):
            return FEATURE_DUMMIES_TEXT[idx % len(FEATURE_DUMMIES_TEXT)]
        if field in ("badge", "marker", "step", "number"):
            return str(idx + 1).zfill(2)
        if field in ("icon",):
            return "★"
        if field in ("image", "photo"):
            return "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800&q=80"
        if field in ("price",):
            return f"{(idx + 1) * 10_000} ₽"
        if field in ("cta", "cta-label"):
            return "Подробнее →"
        return DUMMY.get(field, f"[{name}]")

    # Direct dash↔underscore fallbacks
    for alt in (name.replace("-", "_"), name.replace("_", "-")):
        if alt in DUMMY:
            return DUMMY[alt]

    return f"[{name}]"


def substitute_slots(html: str) -> str:
    """Replace {{slot:NAME}} with dummy values; leftover slots become gray text."""
    def _repl(m):
        val = fill_slot(m.group(1).strip())
        if val.startswith("[") and val.endswith("]"):
            return f'<span style="color:#888;font-style:italic;">{val}</span>'
        return val
    return _SLOT_RE.sub(_repl, html)


def render_block(block_dir):
    """Detect format and return {html, css, name, kind} or None.

    kind: "new" → uses index.html + styles.css and {{slot:*}} placeholders
          "legacy" → uses assets/template.html (self-contained, data-slot attrs)
    """
    # --- New format ---
    new_html = block_dir / "index.html"
    new_css = block_dir / "styles.css"
    if new_html.exists() and new_css.exists():
        html_raw = new_html.read_text(encoding="utf-8")
        css_raw = new_css.read_text(encoding="utf-8")
        html_filled = substitute_slots(html_raw)
        return {
            "html": html_filled,
            "css": css_raw,
            "name": block_dir.name,
            "kind": "new",
        }

    # --- Legacy ru-* format ---
    legacy_tpl = block_dir / "assets" / "template.html"
    if legacy_tpl.exists():
        raw = legacy_tpl.read_text(encoding="utf-8")
        # template.html is a full HTML document with its own <style>.
        # Embed it via iframe srcdoc so its CSS doesn't leak into the gallery.
        return {
            "iframe": True,
            "srcdoc": raw,
            "css": "",
            "name": block_dir.name,
            "kind": "legacy",
        }

    return None


# --- Collect all blocks ---
groups: dict[str, list[dict]] = {}
for cat_dir in sorted(LIB.iterdir()):
    if not cat_dir.is_dir() or cat_dir.name.startswith(("_", ".")):
        continue
    blocks: list[dict] = []
    for block_dir in sorted(cat_dir.iterdir()):
        if not block_dir.is_dir():
            continue
        rendered = render_block(block_dir)
        if rendered:
            blocks.append(rendered)
    if blocks:
        groups[cat_dir.name] = blocks

total = sum(len(v) for v in groups.values())
new_count = sum(1 for v in groups.values() for b in v if b["kind"] == "new")
legacy_count = sum(1 for v in groups.values() for b in v if b["kind"] == "legacy")

# --- Assemble HTML ---
import html as html_lib

parts: list[str] = [f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Block Library Gallery — {total} блоков</title>
<style>
{TOKENS}
body {{ margin: 0; background: #060606; color: #eaeaea; font-family: var(--lp-font-body); }}
nav.gallery-nav {{ position: sticky; top: 0; background: rgba(10,10,10,0.95); backdrop-filter: blur(12px); padding: 16px 24px; border-bottom: 1px solid #222; z-index: 1000; }}
nav.gallery-nav h1 {{ margin: 0 0 8px; font-size: 16px; color: var(--lp-primary); }}
nav.gallery-nav .filters {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 8px 0; font-size: 12px; }}
nav.gallery-nav .filters label {{ cursor: pointer; color: #ccc; }}
nav.gallery-nav .filters input {{ margin-right: 4px; }}
nav.gallery-nav .cats {{ display: flex; flex-wrap: wrap; gap: 8px; }}
nav.gallery-nav a {{ color: #aaa; text-decoration: none; font-size: 12px; padding: 4px 10px; border: 1px solid #333; border-radius: 4px; }}
nav.gallery-nav a:hover {{ background: var(--lp-primary); color: #000; }}
.category {{ padding: 40px 24px 24px; border-top: 2px solid var(--lp-primary); }}
.category h2 {{ font-size: 24px; color: var(--lp-primary); margin: 0 0 24px; }}
.block-wrap {{ margin-bottom: 60px; background: #1a1a1a; border-radius: 12px; overflow: hidden; box-shadow: 0 12px 32px rgba(0,0,0,0.4); }}
.block-meta {{ padding: 12px 20px; background: #0d0d0d; font-size: 13px; color: #aaa; border-bottom: 1px solid #222; display: flex; align-items: center; gap: 10px; }}
.block-meta b {{ color: var(--lp-primary); font-family: monospace; }}
.block-meta .kind-badge {{ font-size: 10px; padding: 2px 6px; border-radius: 3px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; }}
.block-meta .kind-badge.new {{ background: #1a4d2e; color: #6ee7b7; }}
.block-meta .kind-badge.legacy {{ background: #4a3a1c; color: #fcd34d; }}
.block-render {{ background: var(--lp-bg); }}
.block-render iframe {{ width: 100%; border: 0; min-height: 600px; background: #fff; display: block; }}

/* Filter behaviour */
body.filter-new .block-legacy {{ display: none; }}
body.filter-legacy .block-new {{ display: none; }}
body.filter-new .category[data-only-legacy="true"],
body.filter-legacy .category[data-only-new="true"] {{ display: none; }}
</style>
</head>
<body>
<nav class="gallery-nav">
<h1>📦 Block Library Gallery — {total} блоков в {len(groups)} категориях</h1>
<div class="filters">
  <label><input type="radio" name="filter" value="all" checked> Все ({total})</label>
  <label><input type="radio" name="filter" value="new"> Только новые импортированные ({new_count})</label>
  <label><input type="radio" name="filter" value="legacy"> Только legacy ru-* ({legacy_count})</label>
</div>
<div class="cats">
"""]

for cat, blks in groups.items():
    n_new = sum(1 for b in blks if b["kind"] == "new")
    n_leg = sum(1 for b in blks if b["kind"] == "legacy")
    label = f"{cat} ({len(blks)})"
    parts.append(f'<a href="#cat-{cat}" title="new: {n_new} / legacy: {n_leg}">{label}</a>')

parts.append('</div></nav>')

for cat, blocks in groups.items():
    only_new = all(b["kind"] == "new" for b in blocks)
    only_legacy = all(b["kind"] == "legacy" for b in blocks)
    cat_attrs = (
        f' data-only-new="{"true" if only_new else "false"}"'
        f' data-only-legacy="{"true" if only_legacy else "false"}"'
    )
    parts.append(f'<div class="category" id="cat-{cat}"{cat_attrs}><h2>📁 {cat} ({len(blocks)})</h2>')
    for b in blocks:
        kind = b["kind"]
        badge_label = "new" if kind == "new" else "legacy"
        parts.append(
            f'<div class="block-wrap block-{kind}">'
            f'<div class="block-meta">'
            f'<span class="kind-badge {kind}">{badge_label}</span>'
            f'📌 <b>{b["name"]}</b>'
            f'</div>'
        )
        if b.get("iframe"):
            # Legacy — sandbox the self-contained document
            parts.append(
                f'<div class="block-render">'
                f'<iframe sandbox srcdoc="{html_lib.escape(b["srcdoc"], quote=True)}"></iframe>'
                f'</div>'
            )
        else:
            parts.append(
                f'<div class="block-render"><style>{b["css"]}</style>{b["html"]}</div>'
            )
        parts.append('</div>')
    parts.append('</div>')

parts.append("""
<script>
document.querySelectorAll('input[name="filter"]').forEach(r => {
  r.addEventListener('change', e => {
    document.body.classList.remove('filter-new', 'filter-legacy');
    if (e.target.value !== 'all') document.body.classList.add('filter-' + e.target.value);
  });
});
</script>
</body></html>""")

OUT.write_text("\n".join(parts), encoding="utf-8")
print(f"✅ Gallery: {OUT}")
print(f"   Categories: {len(groups)}, Blocks: {total} (new: {new_count}, legacy: {legacy_count})")

---
name: wp-gutenberg-block-builder
description: Generate Lazy-Blocks-based Gutenberg blocks + theme scaffold + page content for a landing project (stage 08).
---

# wp-gutenberg-block-builder

Generates stage-08 WordPress artifacts using **Lazy Blocks (free)** — blocks live
under the `lazyblock/` namespace and are registered at runtime via
`lazyblocks()->add_block()`. This is **NOT** ACF Pro Blocks (`acf/` namespace) —
we migrated off that in 2026-05-13 to stay on free plugins.

## Prerequisites

Before running any generator the project must have:

1. Stage 05 complete — `05_ДИЗАЙН-СИСТЕМА/tokens.json` exists.
2. Stage 06 complete — `06_СТЕК/design-stack.yaml` exists.
3. Stage 07 complete — `07_КОНТЕНТ/final-copy.md` reviewed.
4. `08_КОД/block-spec.yaml` filled in (см. шаблон `template/08_КОД/block-spec.example.yaml`).
   Generators 2–5 read this file; without it they fail fast with a clear message.

## Pipeline (5 generators, dependency order)

Run them all via the orchestrator:

```bash
python scripts/generate-wp-blocks.py --project <project-dir>
```

Or invoke individually:

| # | Script | Purpose |
|---|--------|---------|
| 1 | `generate-theme.py <project>` | wp-theme scaffold: `style.css`, `functions.php`, `blocks/` dir, base `assets/css/main.css`. |
| 2 | `generate-lzb-templates.py --project <path>` | One `wp-theme/blocks/lazyblock-<slug>/block.php` per block. **Never overwrites** existing — safe for manager hand-edits. |
| 3 | `generate-lzb-registration.py --project <path>` | `lzb/init` `add_block()` block injected into `functions.php` between `AUTO-GENERATED` markers. |
| 4 | `generate-css-patches.py --project <path>` | `display: contents` rules in `assets/css/main.css` (AUTO-GENERATED block) for InnerBlocks wrappers in section+card blocks. |
| 5 | `generate-page-content.py --project <path>` | `08_КОД/page-content.html` with Gutenberg block markup + image placeholders for deploy substitution. |

Step 1 takes the project path as a positional argument; steps 2–5 use `--project`.

## Outputs

- `08_КОД/wp-theme/style.css`
- `08_КОД/wp-theme/functions.php` — contains AUTO-GENERATED `lzb/init` section
- `08_КОД/wp-theme/assets/css/main.css` — contains AUTO-GENERATED inner-blocks CSS patches
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — one per block
- `08_КОД/page-content.html` — Gutenberg markup seed for the front page

## What this skill does NOT produce

- **No `acf-fields.json`** — ACF Blocks are deprecated here. ACF Free is still installed
  for potential page-level meta but plays no role in block rendering.
- **No `block.json` files** — Lazy Blocks reads block config from the
  `lazyblocks()->add_block()` PHP call, not from JSON.
- **No `front-page.php`** — the front page is a regular Gutenberg page set via
  `page_on_front`. Deploy seeds it from `page-content.html`.
- **No `template-parts/` directory** — block PHP lives under `blocks/lazyblock-<slug>/block.php`.

## Visual Patterns Library (block-library/_patterns/)

После PR-A.X — при генерации WP-темы (`generate-theme.py`), автоматически
подключаются переиспользуемые patterns из OpenDesign (Apache-2.0):

| Pattern | Что даёт | Когда применять |
|---|---|---|
| `scroll-reveal` | Плавное появление блоков на скролле | Везде — главный visual upgrade |
| `paper-texture` | Бумажная текстура body::before | Editorial / премиум-проекты |
| `ambient-mesh-bg` | Живой mesh-фон без Three.js | Hero для tech/SaaS проектов |
| `marquee-fade` | Бегущая строка с fade-краями | Логотипы клиентов, бегущие новости |
| `floating-pill-nav` | Sticky nav с backdrop-blur | Apple-style premium nav |
| `headroom-nav` | Nav прячется при скролле вниз | Мобильный UX |
| `dot-grid-bg` | Editorial dot-pattern фон | Magazine / portfolio проекты |
| `conic-ring` | Прогресс-кольцо без canvas | Stats / KPI секции |
| `bento-grid-hairline` | Notion/Linear-style 6-col grid | Features секция |

**Какие patterns включать автоматически** (зависит от `animation_mode` в tokens.json):

| animation_mode | Auto-included patterns |
|---|---|
| `none` | Никаких |
| `smooth` (default) | scroll-reveal, headroom-nav |
| `cinematic` | scroll-reveal, headroom-nav, ambient-mesh-bg, paper-texture |
| `editorial` | scroll-reveal, paper-texture, dot-grid-bg |

**Как использовать в generate-theme.py:**

```python
# Подключить snippet в style.css темы:
patterns_dir = SYSTEM_ROOT / "block-library" / "_patterns"
scroll_reveal_css = (patterns_dir / "scroll-reveal" / "snippet.css").read_text()
style_css_content += scroll_reveal_css

# Подключить snippet JS в assets/js/animations.js:
scroll_reveal_js = (patterns_dir / "scroll-reveal" / "snippet.js").read_text()
animations_js_content += scroll_reveal_js
```

## Anti-AI-Slop правила (craft/anti-ai-slop.md)

См. `vendor/opendesign-extracts/craft/anti-ai-slop.md` — 7 паттернов
которые ВЫДАЮТ AI-сгенерированный сайт. При генерации темы НЕЛЬЗЯ:

- Использовать indigo (#6366f1, #4f46e5, #4338ca, #8b5cf6, #7c3aed) или purple→blue gradient в hero
- Blob backgrounds (svg organic shapes)
- Emoji в feature icons (✨ 🚀 🎯) — только SVG с `currentColor`
- Generic stock illustrations
- Dark mode toggle без явного запроса в DESIGN.md
- Chat bubble UI в hero
- Лозунги типа "AI-powered", "Revolutionize", "Game-changing"
- Выдуманные метрики ("10× faster", "99.9% uptime") без реального источника

Если в `tokens.json` указан accent_color близкий к #6366f1 — wp-builder агент
должен предложить альтернативу.

## Animation Discipline (craft/animation-discipline.md)

При написании CSS-анимаций и JS-эффектов соблюдать:

- Default duration: 150ms (UI feedback) / 300ms (page transitions) / 500ms (hero reveal)
- Easing: `cubic-bezier(0.2, 0, 0, 1)` для material-style smooth
- Stagger gap: 80-120ms между элементами
- ScrollTrigger start: top 85% (НЕ top top для блоков ниже hero)
- ВСЕГДА: respect `prefers-reduced-motion` (CSS fallback + JS skip)
- Spring для position/scale/rotation; curve для opacity/color
- Мобильные анимации: 20-30% короче desktop

## Honest scope

- **Flat repeaters only.** Lazy Blocks Free does not support nested repeaters.
  For "list of cards with sub-items" use the **section+card** pattern
  (parent block with InnerBlocks of a child card block).
- **Toggle defaults must be YAML boolean** (`true` / `false`), not the strings
  `"true"`/`"false"`. The generator rejects strings.
- **Image control defaults** are placeholders like
  `__IMAGE_ATTACHMENT_ID__<file>__`; deploy substitutes them with real Media
  Library attachment IDs after `wp media import`.
- **Existing `block.php` is not overwritten** on regeneration — managers can
  safely edit a block template by hand and re-run the orchestrator.
- Does NOT register form integrations, analytics, or SEO — those are separate
  generators invoked later in `/landing-build`.

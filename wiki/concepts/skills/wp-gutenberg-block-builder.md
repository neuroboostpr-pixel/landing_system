---
type: skill
name: wp-gutenberg-block-builder
sources: ["skills/wp-gutenberg-block-builder/SKILL.md"]
updated: 2026-05-16
triggers: []
stage: "08"
uses: ["wp-builder", "design-tokens-generation", "design-system-generator", "frontend-builder", "block-composition", "block-library-management", "landing-build"]
tags: ["wordpress", "gutenberg", "lazy-blocks", "stage-08", "theme", "css", "animations"]
---

# WP Gutenberg Block Builder — генератор WordPress-темы

## Что делает
Генерирует полноценную WordPress-тему на базе **Lazy Blocks (free)**: скаффолдинг темы, регистрацию блоков, CSS-патчи и готовый контент страницы. Превращает дизайн-систему и финальный текст в рабочий код для деплоя на WordPress.

## Когда вызывать / в каком этапе
Этап **08 (КОД)**. Активируется командой `/landing-build` или агентом `wp-builder` после завершения этапов 05 (дизайн-система), 06 (стек), 07 (контент) и наличия заполненного `08_КОД/block-spec.yaml`. Запускается единым оркестратором:
```bash
python scripts/generate-wp-blocks.py --project <project-dir>
```

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, типографика, `style_mood`, `animation_mode`
- `06_СТЕК/design-stack.yaml` — стек плагинов и библиотек
- `07_КОНТЕНТ/final-copy.md` — финальные тексты
- `08_КОД/block-spec.yaml` — описание блоков (slug, поля, тип)

**Выход (5 генераторов):**
| Файл | Генератор |
|---|---|
| `wp-theme/style.css` | generate-theme.py |
| `wp-theme/functions.php` | generate-theme.py + generate-lzb-registration.py |
| `wp-theme/assets/css/main.css` | generate-css-patches.py |
| `wp-theme/blocks/lazyblock-<slug>/block.php` | generate-lzb-templates.py |
| `08_КОД/page-content.html` | generate-page-content.py |

**Важно:** существующий `block.php` **никогда не перезаписывается** — ручные правки безопасны.

## Ключевые правила генерации

- **Только Lazy Blocks (free)** — namespace `lazyblock/`, регистрация через `lazyblocks()->add_block()`. Не ACF Pro.
- **Visual Patterns** подключаются автоматически по значению `animation_mode` в `tokens.json` (smooth → scroll-reveal + headroom-nav; cinematic → +ambient-mesh-bg, paper-texture и др.).
- **Style Moods** (6 вариантов: `brutalist`, `editorial-warm`, `swiss-modernist`, `retro-windows`, `coral-soft`, `monochrome-precision`) переопределяют паттерны animation_mode и подключают три CSS-файла (`palette.css`, `typography.css`, `motion.css`).
- **Anti-AI-Slop:** запрещены indigo/purple градиенты в hero, blob-фоны, emoji-иконки, выдуманные метрики, generic stock-иллюстрации.
- **Animation discipline:** соблюдать длительности (150/300/500 мс), easing `cubic-bezier(0.2, 0, 0, 1)`, stagger 80–120 мс, `prefers-reduced-motion`.
- **Блок-лоадер** `scripts/block-loader.py` — единственный способ читать блоки из `block-library/`; прямые пути к `assets/template.html` запрещены.

## Что скилл НЕ генерирует
- `acf-fields.json`, `block.json`, `front-page.php`, `template-parts/`
- Форм-интеграции, аналитику, SEO — отдельные этапы `/landing-build`
- Вложенные repeater-поля (Lazy Blocks Free не поддерживает nested repeaters)

## Связанные концепты
- [[wp-builder]] — агент, который вызывает этот скилл на этапе 08
- [[design-tokens-generation]] — поставляет `tokens.json` с цветами и `style_mood`
- [[frontend-builder]] — дописывает CSS после генерации темы
- [[block-composition]] — предшествующий этап 07b, откуда берётся composed.html
- [[block-library-management]] — библиотека готовых блоков и паттернов
- [[landing-build]] — команда, запускающая всю цепочку этапа 08

## Источник
- `skills/wp-gutenberg-block-builder/SKILL.md`
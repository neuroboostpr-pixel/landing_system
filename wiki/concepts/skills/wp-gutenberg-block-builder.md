---
type: skill
name: wp-gutenberg-block-builder
sources: ["skills/wp-gutenberg-block-builder/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "08"
uses:
  - landing-build
  - landing-compose
  - landing-design
tags: ["wordpress", "gutenberg", "lazy-blocks", "stage-08", "codegen"]
---

# WP Gutenberg Block Builder — генератор WordPress-темы на Lazy Blocks

## Что делает

Автоматически собирает полноценную WordPress-тему для лендинга: регистрирует Gutenberg-блоки через плагин Lazy Blocks (бесплатный), генерирует PHP-шаблоны каждого блока, CSS-стили и финальный Gutenberg-разметку страницы. Результат — готовый к деплою WP-тема со всеми блоками по утверждённому дизайну.

## Когда вызывать / в каком этапе

Этап **08 (Код)**. Запускается автоматически через `/landing-build` или вручную:

```bash
python scripts/generate-wp-blocks.py --project <project-dir>
```

**Обязательные условия:**
- Этап 05 завершён — `05_ДИЗАЙН-СИСТЕМА/tokens.json` существует
- Этап 06 завершён — `06_СТЕК/design-stack.yaml` существует
- Этап 07 завершён — `07_КОНТЕНТ/final-copy.md` проверен
- `08_КОД/block-spec.yaml` заполнен

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, `style_mood`, `animation_mode`
- `06_СТЕК/design-stack.yaml` — технический стек проекта
- `07_КОНТЕНТ/final-copy.md` — финальные тексты
- `08_КОД/block-spec.yaml` — спецификация блоков (slug, атрибуты, тип)

**Выход (5 генераторов в цепочке):**
- `08_КОД/wp-theme/style.css` — точка входа темы
- `08_КОД/wp-theme/functions.php` — регистрация блоков через `lazyblocks()->add_block()`
- `08_КОД/wp-theme/assets/css/main.css` — CSS-патчи для InnerBlocks
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по одному на каждый блок
- `08_КОД/page-content.html` — Gutenberg-разметка для seed страницы при деплое

**Что НЕ генерируется:** `acf-fields.json`, `block.json`, `front-page.php`, `template-parts/`.

## Дополнительные возможности

**Visual Patterns:** в зависимости от `animation_mode` (none / smooth / cinematic / editorial) скилл автоматически подключает CSS/JS-сниппеты из `block-library/_patterns/` (scroll-reveal, ambient-mesh-bg, paper-texture и др.).

**Style Moods:** при наличии `style_mood` в `tokens.json` подключаются готовые CSS-наборы из `block-library/_styles/` (palette + typography + motion) — переопределяют animation_mode.

**Anti-AI-Slop:** запрещено использовать indigo-акценты, blob-фоны, emoji-иконки и выдуманные метрики.

**Защита ручных правок:** повторный запуск НЕ перезаписывает существующие `block.php`.

## Связанные концепты

- [[landing-build]] — вызывает этот скилл как часть полного цикла этапа 08
- [[landing-design]] — этап 05, создаёт `tokens.json` который читает этот скилл
- [[landing-compose]] — этап 07b, `composed.html` служит визуальным ориентиром для блоков
- [[landing-deploy]] — следующий этап, заменяет image-плейсхолдеры из `page-content.html` реальными ID

## Источник

- `skills/wp-gutenberg-block-builder/SKILL.md`
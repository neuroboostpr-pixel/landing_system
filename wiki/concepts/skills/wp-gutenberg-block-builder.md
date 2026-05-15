---
type: skill
name: wp-gutenberg-block-builder
sources: ["skills/wp-gutenberg-block-builder/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["wp-builder", "design-tokens-generation", "block-library-management", "design-system-generator", "stack-planner", "content-writer"]
tags: ["wordpress", "lazy-blocks", "gutenberg", "stage-08", "theme", "build"]
---

# WP Gutenberg Block Builder — генератор WordPress-темы на Lazy Blocks

## Что делает
Берёт дизайн-токены, описание блоков и готовый текст — и генерирует полноценную WordPress-тему с Gutenberg-блоками на плагине **Lazy Blocks (бесплатный)**. На выходе — папка `08_КОД/wp-theme/` с PHP-шаблонами каждого блока, подключением CSS/JS анимаций и контентной разметкой страницы.

## Когда вызывать / в каком этапе
Этап **08 — Сборка (Build)**. Запускается командой `/landing-build` или через `landing-orchestrator` после того, как завершены этапы 05 (дизайн-система), 06 (стек), 07 (контент) и заполнен `08_КОД/block-spec.yaml`.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, animation_mode, style_mood
- `06_СТЕК/design-stack.yaml` — выбранный стек плагинов
- `07_КОНТЕНТ/final-copy.md` — утверждённый текст
- `08_КОД/block-spec.yaml` — описание каждого блока (поля, типы, дефолты)

**Выход:**
- `08_КОД/wp-theme/style.css` — главный CSS с подключёнными mood-стилями и patterns
- `08_КОД/wp-theme/functions.php` — регистрация блоков через `lazyblocks()->add_block()` (секция `AUTO-GENERATED`)
- `08_КОД/wp-theme/assets/css/main.css` — CSS-патчи для InnerBlocks-обёрток
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — PHP-шаблон на каждый блок
- `08_КОД/page-content.html` — Gutenberg-разметка страницы для деплоя

## Ключевые ограничения
- Используется **Lazy Blocks**, не ACF Pro — блоки в неймспейсе `lazyblock/`, без `block.json`.
- Вложенные repeater-поля не поддерживаются. Для «список карточек» — паттерн section+card (родительский блок с InnerBlocks).
- Существующий `block.php` **не перезаписывается** при повторной генерации.
- Не регистрирует формы, аналитику и SEO — это отдельные шаги в `/landing-build`.

## Visual Patterns и Style Moods
Скилл автоматически подключает визуальные patterns из `block-library/_patterns/` в зависимости от `animation_mode` или `style_mood` в `tokens.json`. Например, `editorial-warm` → paper-texture + dot-grid-bg; `cinematic` → ambient-mesh-bg + scroll-reveal. Действуют правила **anti-ai-slop** (запрет indigo-акцентов, blob-фонов, emoji-иконок).

## Связанные концепты
- [[wp-builder]] — агент, который запускает этот скилл на этапе 08
- [[design-tokens-generation]] — поставляет `tokens.json`, обязательный вход
- [[design-system-generator]] — предшествующий этап (05), без него нет токенов
- [[stack-planner]] — поставляет `design-stack.yaml` (этап 06)
- [[content-writer]] — поставляет `final-copy.md` (этап 07)
- [[block-library-management]] — библиотека паттернов и стилей, используемых при генерации темы

## Источник
- `skills/wp-gutenberg-block-builder/SKILL.md`
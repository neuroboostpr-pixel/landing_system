---
type: agent
name: frontend-builder
sources: ["docs/superpowers/specs/2026-05-13-frontend-builder-task-brief.md"]
updated: 2026-05-18
triggers: []
stage: "08b"
uses: ["wp-builder", "wp-gutenberg-block-builder", "wp-theme-assembler", "design-tokens-generation", "landing-build"]
tags: ["css", "block.php", "lazy-blocks", "gutenberg", "visual", "stage-08", "layout"]
---

# Frontend Builder — визуализация WordPress-темы

## Что делает

Превращает механический skeleton WordPress-темы в визуально правильную вёрстку: добавляет per-block layout (2-колоночный Hero grid, карточки Pricing, аккордеон FAQ), реальные CSS-правила для BEM-классов и minor JS-поведение (бургер, аккордеон, sticky CTA).

## Когда вызывать / в каком этапе

Запускается **после `wp-builder`** на этапе 08 (кодирование). `wp-builder` генерирует skeleton — controls зарегистрированы, BEM-классы проставлены, контент сохраняется. Но визуал остаётся плоским: дизайн-токены прописаны в `style.css`, однако нигде не применяются; `block.php` — generic обёртка без layout-awareness. Именно frontend-builder закрывает этот разрыв.

Точка вызова пока не финализирована (открытый вопрос в spec): либо фаза внутри `/landing-build`, либо отдельная команда `/landing-style`.

## Что на вход / на выход

**Вход:**
- `08_КОД/block-spec.yaml` — список блоков, controls, css_class, wrapper_html (read-only)
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — wireframes §5, токены §2, layout-примитивы §3–4, состояния §9, motion §7, a11y §8
- `04_БРЕНД/brand-kit.md` — дополнительный брендовый контекст
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — контракт блоков
- `wp-theme/blocks/lazyblock-<slug>/block.php` — существующие skeleton'ы

**Выход:**
- `wp-theme/blocks/lazyblock-<slug>/block.php` — layout-aware HTML (перезаписывает skeleton)
- `wp-theme/assets/css/blocks.css` — реальные CSS-rules для всех BEM-классов из DESIGN.md §5
- `wp-theme/assets/js/<feature>.js` — minor JS (аккордеон, sticky observer) по необходимости

**Не трогает:** `block-spec.yaml`, lzb/init registration в `functions.php`, `page-content.html`.

## Связанные концепты

- [[wp-builder]] — предыдущий агент, генерирует skeleton темы; frontend-builder работает поверх его вывода
- [[wp-gutenberg-block-builder]] — скилл pipeline-генерации `block.php`; frontend-builder переписывает этот вывод
- [[design-system-generator]] — создаёт DESIGN.md с wireframes и токенами; главный input для frontend-builder
- [[design-tokens-generation]] — скилл, порождающий `tokens.json`; дополнительный источник CSS-переменных
- [[landing-build]] — команда stage-08, в которую будет встроен frontend-builder
- [[wp-theme-assembler]] — скилл сборки WP-темы; frontend-builder расширяет его результат

## Источник

- `docs/superpowers/specs/2026-05-13-frontend-builder-task-brief.md`
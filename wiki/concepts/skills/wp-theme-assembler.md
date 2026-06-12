---
slug: wp-theme-assembler
type: skill
name: "Сборщик WordPress-темы"
stage: "08"
tags: [wp, theme, assets, preview, stage-08, bundle, build]
triggers: []
inputs:
  - tokens.json
  - design-stack.yaml
  - block-spec.yaml
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/
  - 08_КОД/wp-theme/blocks/lazyblock-*/
outputs:
  - assets/fonts/
  - assets/icons/
  - assets/images/
  - 08_КОД/build-preview.html
  - 08_КОД/wp-theme/assets/css/palettes.css
  - 08_КОД/wp-theme/inc/lp-preview-panel-axes.php
pre_reqs: [wp-builder, integrations-engineer, analytics-engineer, seo-optimizer]
related:
  - wp-builder
  - design-tokens-generation
  - wp-gutenberg-block-builder
  - frontend-builder
  - icon-generator
  - photo-curator
sources: ["skills/wp-theme-assembler/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Сборщик WordPress-темы

## Что делает

Финализирует сборку WordPress-темы после завершения кодирования блоков. Запускает два последовательных скрипта: `bundle-assets.py` загружает шрифты (CDN-заглушки), скачивает SVG-иконки с Iconify API и копирует обработанные фото клиента в `assets/`; `render-build-preview.py` читает дизайн-токены, стек и спецификацию блоков, генерирует статичный `build-preview.html` через Jinja2. Дополнительно интегрирует плагин `lp-preview-panel` — генерирует `palettes.css` и PHP-фильтр осей для переключения вариантов героя прямо в превью.

## Когда вызывается

Вызывается на этапе 08 после того, как `wp-builder` собрал Lazy Blocks, `integrations-engineer` добавил формы в `functions.php`, `analytics-engineer` — код Метрики, `seo-optimizer` — мета-теги. Скиллом управляет `landing-orchestrator` в рамках pipeline этапа 08.

## Вход → выход

**Вход:** `tokens.json`, `design-stack.yaml`, `block-spec.yaml`, папка с обработанными фото клиента (`02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/`), готовые директории Lazy Blocks (`08_КОД/wp-theme/blocks/lazyblock-*/`).

**Выход:** папки `assets/fonts/`, `assets/icons/`, `assets/images/` с загруженными ресурсами; `08_КОД/build-preview.html` — статичный HTML-превью темы; `palettes.css` и `lp-preview-panel-axes.php` для плагина панели предпросмотра. По завершении — HARD GATE: `build-preview.html` показывается пользователю для ручного подтверждения.

## Failure modes

- Iconify API недоступен или slug иконки не найден — скрипт падает без скаченного SVG, `assets/icons/` остаётся неполным.
- Папка `photos/processed/` отсутствует или пустая — `images_copied: 0` в stdout, фото не попадают в тему.
- Отсутствует `block-spec.yaml` или директории `lazyblock-*/` — `render-build-preview.py` не может отрендерить список блоков и завершается с ошибкой.
- `lp-preview-panel` не скопирован перед запуском `generate-axes-filter.py` — PHP-файл генерируется, но `functions.php` не подключает его (требуется ручное добавление `require_once`).
- Неверный `--default-palette` или несуществующий variant hero — фильтр осей генерируется некорректно, переключатель вариантов героя в preview работает неправильно.

## Related

- [[wp-builder]] — собирает Lazy Blocks и CSS/JS до передачи в assembler
- [[design-tokens-generation]] — поставляет `tokens.json`, который читает `render-build-preview.py`
- [[wp-gutenberg-block-builder]] — смежный скилл сборки блоков Gutenberg/Lazy Blocks
- [[frontend-builder]] — общий контекст frontend-слоя темы
- [[icon-generator]] — альтернативный путь генерации иконок через codex вместо Iconify
- [[photo-curator]] — поставляет `photos/processed/` на вход bundle-assets
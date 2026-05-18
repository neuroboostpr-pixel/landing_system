---
type: stage
name: stage-08-acf-gutenberg
sources: ["docs/superpowers/specs/2026-05-12-stage-08-acf-gutenberg-design.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-gutenberg-block-builder", "wp-cli-deployer", "wp-builder", "stage-gates", "landing-build"]
tags: ["gutenberg", "acf", "wordpress", "hard-gate", "content-parser"]
---

# Stage 08 — Verifiable WP Build (ACF Blocks + Gutenberg)

## Что делает

Генерирует настоящие Gutenberg-блоки и ACF-поля по содержимому `final-copy.md`, чтобы менеджер мог заходить в WP-админку и редактировать тексты через форму — без правки PHP-файлов и редеплоя.

## Когда вызывать / в каком этапе

Этап 08. Запускается автоматически в рамках `/landing-build` после того как утверждён контент (`07_КОНТЕНТ/final-copy.md`). Hard-gate этапа 08 блокирует переход на deploy (этап 09), если артефакты отсутствуют. Проекты, созданные до внедрения этой архитектуры, помечаются `legacy: true` в `.landing-state.yaml` и gate для них пропускается.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/final-copy.md` — каждый заголовок `## H2` становится одним блоком.
- `scripts/lib/slug-aliases.yaml` — таблица перевода русских заголовков в kebab-slug.
- `scripts/lib/block-icons.yaml` — dashicon по slug-у блока.

**Выход (три слоя):**
- **Layer A — ContentParser** (`scripts/lib/content_parser.py`): парсит `final-copy.md` → список `Block` с полями и типами. Один источник истины для всех генераторов.
- **Layer B — Generators:**
  - `08_КОД/acf-fields.json` — ACF Local JSON с группой полей на каждый H2-блок.
  - `08_КОД/gutenberg-blocks/<slug>/block.json` — описание блока (apiVersion 3, категория `lp-blocks`).
  - AUTO-GENERATED секция в `functions.php` с `register_block_type()` для каждого блока.
  - Заглушки `template-parts/block-<slug>.php` (не перезаписываются если уже существуют).
- **Layer C — Hard Gate** (`scripts/lib/gate-checks/stage-08.sh`): 8 hard-проверок + 2 warning. Деплой падает явно, если `wp acf import` завершился с ошибкой или ACF-плагин не активен на сервере.

## Связанные концепты

- [[wp-gutenberg-block-builder]] — скилл, который содержит генераторы B1–B4 и ContentParser
- [[wp-cli-deployer]] — деплой-скрипт, который выполняет `wp acf import` (теперь без silent fail)
- [[wp-builder]] — агент этапа 08, вызывающий оркестратор генераторов
- [[stage-gates]] — система hard-gate проверок между этапами; stage-08.sh — один из модулей
- [[landing-build]] — команда-точка входа в этап 08

## Источник

- `docs/superpowers/specs/2026-05-12-stage-08-acf-gutenberg-design.md`
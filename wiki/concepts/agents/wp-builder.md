---
slug: wp-builder
type: agent
name: "WP-сборщик (Lazy Blocks)"
stage: "08"
tags: [wordpress, lazy-blocks, php, css, js, stage-08, build, legal]
triggers: [landing-build]
inputs:
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 06_СТЕК/design-stack.yaml
  - 07_КОНТЕНТ/final-copy.md
  - 08_КОД/block-spec.yaml
  - 01a_АНАЛИЗ_НИШИ/landing-structure.md
  - 01a_АНАЛИЗ_НИШИ/market-profile.md
  - 01a_АНАЛИЗ_НИШИ/positioning.md
outputs:
  - 08_КОД/wp-theme/blocks/lazyblock-*/block.php
  - 08_КОД/wp-theme/functions.php
  - 08_КОД/wp-theme/assets/css/main.css
  - 08_КОД/wp-theme/assets/js/main.js
  - 08_КОД/page-content.html
gates: []
pre_reqs: [design-system-generator, content-writer]
related:
  - design-system-generator
  - content-writer
  - landing-orchestrator
  - frontend-builder
  - block-composer
  - analytics-engineer
  - integrations-engineer
  - icon-generator
  - infographic-builder
sources: ["agents/wp-builder.md"]
updated: 2026-05-26
confidence:
  triggers: low
---

# WP-сборщик (Lazy Blocks)

## Что делает

Генерирует полный PHP-код WordPress-темы на базе Lazy Blocks Free: по одному `block.php` на каждый блок из `block-spec.yaml`, регистрацию блоков через `lzb/init` в `functions.php`, финальную Gutenberg-разметку `page-content.html` для импорта в WP-страницу, а также CSS и JS с поддержкой токенов дизайна. Учитывает режим позиционирования (emotional / trust / rational / cinematic), ценовой тир из market-profile, требования 152-ФЗ (cookie-banner, legal-block в формах, страницы /policy и /consent) и визуальные ограничения из visual-requirements.md.

## Когда вызывается

Вызывается автоматически через `landing-orchestrator` или вручную командой `/landing-build` на этапе `08_build`, при условии что этапы 05 (дизайн-система), 06 (стек) и 07 (контент) закрыты и утверждены. Физически заблокирован хуком `enforce_stage_gate.py`, если предшественники не закрыты.

## Вход → выход

**Вход:** `tokens.json`, `design-stack.yaml`, `final-copy.md`, `block-spec.yaml`, `landing-structure.md`, `market-profile.md`, `positioning.md`. При cinematic-режиме дополнительно читает `scenes.md`.

**Выход:** `wp-theme/blocks/lazyblock-<slug>/block.php` (по одному на блок), обновлённые `functions.php`, `main.css`, `main.js`, готовый `page-content.html`. После деплоя темы отдельный скрипт создаёт WP-страницы `/policy` и `/consent` через wp-cli.

## Failure modes

- `block-spec.yaml` отсутствует или не заполнен — пайплайн `generate-wp-blocks.py` упадёт с ошибкой до создания каких-либо файлов.
- Токены не найдены или `tokens.json` содержит хардкод цветов вместо переменных — CSS окажется с жёстко зашитыми значениями, что нарушает правило CSS-переменных.
- Не закрыты предшественники (05/06/07) — `enforce_stage_gate.py` заблокирует Write/Edit; агент обязан остановиться, а не обходить хук.
- Отсутствие ## Legal в `brand-kit.md` — скрипт `install_legal_pages.sh` бросает ошибку и блокирует деплой; этап 08 не может быть закрыт без `/policy` и `/consent` страниц.
- В heroes/catalog попадают fallback-ссылки на Pexels/Unsplash без разрешения в `visual-requirements.md` — нарушение правил визуальных проверок, grep по теме обязателен.

## Related

- [[design-system-generator]] — поставляет `tokens.json` и `scenes.md` для stage 08
- [[content-writer]] — поставляет `final-copy.md`, обязательный prereq
- [[landing-orchestrator]] — диспатчит wp-builder в нужный момент pipeline
- [[frontend-builder]] — смежная роль по CSS/JS, может дополнять cinematic-сборку
- [[block-composer]] — создаёт `composed.html` (этап 07b), служит источником структуры блоков
- [[analytics-engineer]] — подключается после wp-builder для интеграции GTM/Metrica
- [[integrations-engineer]] — добавляет CRM-адаптеры поверх собранной темы
- [[icon-generator]] — генерирует SVG-иконки, которые wp-builder встраивает в block.php
- [[infographic-builder]] — поставляет PNG-инфографику для каталогных блоков
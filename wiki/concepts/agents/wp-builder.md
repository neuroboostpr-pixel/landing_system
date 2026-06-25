---
slug: wp-builder
type: agent
name: "WP-сборщик"
stage: "08"
tags: [wordpress, lazy-blocks, php, css, js, codegen, stage-08]
triggers: [landing-build]
inputs: [05-dizayn-sistema, 06-stek, 07-kontent, 07b-composed, 01a-analiz-nishi]
outputs: [08-kod]
pre_reqs: [design-system-generator, content-writer, 05-dizayn-sistema, 06-stek, 07-kontent, 07b-composed]
related: [wp-theme-assembler, wp-gutenberg-block-builder, landing-build, landing-style, wp-cli-deployer, block-composer]
sources: ["agents/wp-builder.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# WP-сборщик

## Что делает

Генерирует полный PHP/CSS/JS-код WordPress-лендинга на Lazy Blocks Free. Запускает пятишаговый пайплайн (`generate-wp-blocks.py`): создаёт scaffold темы, один `block.php` на каждый блок из `block-spec.yaml`, секцию `lzb/init` в `functions.php`, готовую Gutenberg-разметку `page-content.html` и ассеты CSS/JS. Адаптирует вывод под positioning-mode проекта (`emotional_aspiration`, `trust_authority`, `rational`) и tier ценового сегмента (`luxury_status` → цена скрыта, `mass_consumer` → цена на первом экране). Также подключает юридическую инфраструктуру 152-ФЗ: legal-block в каждую форму, страницы /policy и /consent.

## Когда вызывается

Вызывается скилом `landing-build` на этапе `08_build`, после того как утверждены дизайн-система (05), стек (06), финальный контент (07) и макет `composed.html` (07b). Перед запуском `gate-check.sh --stage 08_build` должен вернуть exit 0; иначе агент останавливается.

## Вход → выход

**Вход:** `05_ДИЗАЙН-СИСТЕМА/tokens.json`, `06_СТЕК/design-stack.yaml`, `07_КОНТЕНТ/final-copy.md`, `08_КОД/block-spec.yaml` (генерируется конвертером `composed-to-build.py`), `01a_АНАЛИЗ_НИШИ/landing-structure.md`, `market-profile.md`, `positioning.md`.

**Выход:** `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по файлу на блок; `wp-theme/functions.php` с `lzb/init`; `wp-theme/assets/css/main.css` и `main.js`; `08_КОД/page-content.html` для импорта в WP-страницу.

## Failure modes

- `block-spec.yaml` не создан конвертером `composed-to-build.py` — пайплайн падает на первом шаге; нужно запустить конвертер вручную.
- В `block.php` попадают хардкод-цвета или inline-стили — нарушает CSS-токенизацию; верификация `verify_tokens.py` выдаст ошибку.
- Отсутствует legal-block в форме заявки — `stage-08_build-checklist` не закрывается, страницы /policy и /consent дают 404.
- Positioning-mode не прочитан или указан несуществующий — агент работает как `legacy_v1` без mode-аугментации блоков.
- `lint-composed-vs-spec.py` возвращает ненулевой код — структура `block-spec.yaml` расходится с `composed.html`; нужно пересобрать spec конвертером.

## Related

- [[landing-build]] — скил, который вызывает агента и управляет hard gate утверждения
- [[wp-gutenberg-block-builder]] — низкоуровневая библиотека скриптов (generate-wp-blocks.py, composed-to-build.py, lint)
- [[wp-theme-assembler]] — scaffold темы, создаваемый в шаге 1 пайплайна
- [[landing-style]] — этап 08b, дополняет CSS блоков после wp-builder
- [[wp-cli-deployer]] — следующий агент (09), принимает output этапа 08
- [[block-composer]] — автор `composed.html`, чей макет конвертируется в `block-spec.yaml`
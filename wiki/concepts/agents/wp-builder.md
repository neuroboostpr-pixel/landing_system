---
type: agent
name: wp-builder
sources: ["agents/wp-builder.md"]
updated: 2026-05-25
triggers: []
stage: "08"
uses: ["landing-orchestrator", "design-system-generator", "content-writer", "landing-style", "wp-cli-deployer"]
tags: ["wordpress", "lazy-blocks", "php", "css", "stage-08", "build"]
---

# wp-builder (WP-сборщик)

## Что делает

Генерирует готовый PHP-код WordPress-темы на основе дизайн-токенов и финального контента: создаёт Lazy Blocks-шаблоны для каждого блока лендинга, подключает их в `functions.php`, собирает CSS/JS-ассеты и формирует Gutenberg-разметку для импорта в страницу сайта.

## Когда вызывать / в каком этапе

Запускается на **этапе 08 (08_build)** после того, как утверждены:
- этап 05 — дизайн-система и токены,
- этап 06 — стек (standard или cinematic),
- этап 07 — финальный текст по блокам.

Оркестратор диспатчит агента автоматически через `/landing-go`. Ручной запуск — только если `current_stage == 08_build` в `.landing-state.yaml`. Перед любыми действиями агент обязан выполнить Stage Execution Protocol: прочитать state, показать Mermaid-карту, запустить `gate-check.sh`.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены
- `06_СТЕК/design-stack.yaml` — стек и режим сборки
- `07_КОНТЕНТ/final-copy.md` — финальный контент
- `08_КОД/block-spec.yaml` — **источник истины**: список блоков и поля каждого блока
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — контракт списка блоков
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — тир продукта (влияет на отображение цены)
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим (`emotional_aspiration`, `trust_authority`, `rational` и др.)

**Выход:**
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по одному файлу на блок
- `08_КОД/wp-theme/functions.php` — секция `lzb/init` с регистрацией всех блоков
- `08_КОД/wp-theme/assets/css/main.css` — стили через CSS-переменные
- `08_КОД/wp-theme/assets/js/main.js` — интеракции (FAQ-аккордеон, GSAP при cinematic-режиме)
- `08_КОД/page-content.html` — Gutenberg-разметка для импорта в WP-страницу

Дополнительно: файлы cookie-banner (152-ФЗ), legal-block для форм, юридические страницы `/policy` и `/consent`.

## Связанные концепты

- [[landing-orchestrator]] — диспатчит агента на этапе 08, управляет stage-gate
- [[design-system-generator]] — поставляет `tokens.json` и `scenes.md` (cinematic)
- [[content-writer]] — поставляет `final-copy.md` с текстами по блокам
- [[landing-style]] — этап 08b, дополняет CSS после wp-builder (stage 08b)
- [[wp-cli-deployer]] — следующий этап 09: деплоит собранную тему на Бегет

## Источник

- `agents/wp-builder.md`
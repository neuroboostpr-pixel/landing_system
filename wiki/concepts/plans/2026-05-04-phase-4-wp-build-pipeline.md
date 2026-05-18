---
type: stage
name: phase-4-wp-build-pipeline
sources: ["docs/superpowers/plans/2026-05-04-phase-4-wp-build-pipeline.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses:
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - wp-gutenberg-block-builder
  - wp-theme-assembler
  - landing-build
  - design-tokens-generation
  - landing-content
  - landing-deploy
tags: [wordpress, build, php, acf, stage-08]
---

# Phase 4 — WP Build Pipeline (Этап 08: Код)

## Что делает

Превращает токены дизайна и финальный текст в готовую WordPress-тему: генерирует PHP-шаблоны, CSS-переменные, ACF-поля, подключает формы, аналитику и SEO, собирает иконки/фото и рендерит статический HTML-preview для утверждения.

## Когда вызывать / в каком этапе

Запускается командой `/landing-build` после того, как утверждены:
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` (этап 05)
- `06_СТЕК/design-stack.yaml` (этап 06)
- `07_КОНТЕНТ/final-copy.md` (этап 07)

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, типографика, отступы, радиус, тени
- `06_СТЕК/design-stack.yaml` — режим (standard/cinematic), шрифты, плагины, JS-библиотеки
- `07_КОНТЕНТ/final-copy.md` — финальный текст по секциям (H2-заголовки = секции лендинга)
- `04_БРЕНД/extracted/icons.yaml` — иконки для скачивания с Iconify API
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` — обработанные фото

**Выход:**
- `08_КОД/wp-theme/` — полная WP-тема: `style.css` с CSS-переменными, `functions.php` с enqueue/Metrika/SEO/webhooks, `template-parts/section-*.php`, `assets/{css,js,fonts,icons,images}/`
- `08_КОД/acf-fields.json` — конфигурация ACF-полей по секциям
- `08_КОД/gutenberg-blocks/`, `08_КОД/generateblocks-templates.json`
- `08_КОД/build-preview.html` — статический preview для HARD GATE
- `11_АНАЛИТИКА/metrika-config.md`, `goals-and-events.json`, `utm-templates.md`
- `12_SEO/meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`

**Ключевые скрипты:**
| Скрипт | Назначение |
|---|---|
| `generate-theme.py` | Детерминированный scaffold темы из tokens.json + design-stack.yaml |
| `generate-acf.py` | ACF-поля из секций final-copy.md (поддерживает русские имена секций) |
| `bundle-assets.py` | CDN-заглушки шрифтов, Iconify-иконки, копирование фото |
| `render-build-preview.py` | Jinja2-рендер build-preview.html для визуального утверждения |

Cinematic-режим: если `design-stack.yaml` содержит `js_libraries: [gsap, ...]` — `functions.php` добавляет GSAP/ScrollTrigger/Lenis, а `wp-builder` вносит GSAP-анимации по `scenes.md`.

**HARD GATE:** после рендера preview пользователь утверждает `08_КОД/build-preview.html`, только потом разрешён переход к `/landing-deploy`.

## Связанные концепты

- [[wp-builder]] — заполняет template-parts PHP+CSS+JS кодом блоков
- [[integrations-engineer]] — добавляет Fluent Forms вебхуки (Telegram/CRM) в functions.php
- [[analytics-engineer]] — добавляет Яндекс.Метрику и создаёт 11_АНАЛИТИКА/ файлы
- [[seo-optimizer]] — добавляет мета-теги, Schema.org, robots.txt и создаёт 12_SEO/ файлы
- [[wp-gutenberg-block-builder]] — скилл, содержащий generate-theme.py и generate-acf.py
- [[wp-theme-assembler]] — скилл, содержащий bundle-assets.py и render-build-preview.py
- [[landing-build]] — slash-команда, запускающая весь пайплайн этапа 08
- [[design-tokens-generation]] — поставляет tokens.json (этап 05)
- [[landing-content]] — поставляет final-copy.md (этап 07)
- [[landing-deploy]] — следующий этап после утверждения build-preview.html

## Источник

- `docs/superpowers/plans/2026-05-04-phase-4-wp-build-pipeline.md`
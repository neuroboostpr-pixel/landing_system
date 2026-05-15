---
type: agent
name: wp-builder
sources: ["agents/wp-builder.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["design-system-generator", "content-writer", "integrations-engineer", "landing-build", "frontend-builder"]
tags: ["wordpress", "lazy-blocks", "php", "css", "stage-08"]
---

# wp-builder — WP-сборщик (Этап 08)

## Что делает
Генерирует готовый PHP-код WordPress-темы: Lazy Blocks для каждого блока лендинга, CSS с дизайн-токенами и JS-интеракции. На выходе — рабочий WP-шаблон, который можно задеплоить на Бегет.

## Когда вызывать / в каком этапе
Этап **08**. Запускается после того, как утверждены:
- `design-system-generator` (этап 05 — токены готовы)
- `content-writer` (этап 07 — финальный текст готов)

Команда-триггер: `/landing-build`. Агент диспатчится `landing-orchestrator` автоматически.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, отступы)
- `06_СТЕК/design-stack.yaml` — режим сборки (standard / cinematic)
- `07_КОНТЕНТ/final-copy.md` — финальные тексты по блокам
- `08_КОД/block-spec.yaml` — источник истины: список блоков и поля каждого
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — перечень блоков лендинга
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ценовой тир (luxury → mass)
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (rational / emotional_aspiration / trust_authority)

**Выход:**
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по одному PHP-файлу на блок
- `08_КОД/wp-theme/functions.php` — регистрация блоков через `lzb/init`
- `08_КОД/wp-theme/assets/css/main.css` — стили через CSS-переменные
- `08_КОД/wp-theme/assets/js/main.js` — интеракции (FAQ-аккордеон, GSAP в cinematic-режиме)
- `08_КОД/page-content.html` — Gutenberg-разметка с `<!-- wp:lazyblock/<slug> -->` для импорта в WP

**Не создаётся:** `acf-fields.json`, `template-parts/section-*.php` — устаревшие артефакты ACF-Blocks.

## Ключевые правила генерации
- Все цвета — только через `var(--token-name)`, хардкод запрещён
- Каждый PHP-файл начинается с provenance-комментария (`/* wp-builder: source=DESIGN.md, block=... */`)
- Все строки экранируются через `esc_html()` или `wp_kses_post()`
- Mobile-first CSS: базовые стили → `@media (min-width: 768px)` → `1440px`
- В cinematic-режиме (gsap в стеке) — GSAP ScrollTrigger по `scenes.md`
- Luxury/ultra-luxury тир: цена в Hero скрыта, CTA — «Связаться», не «Купить»
- **HARD GATE**: после генерации показывает список файлов и ждёт утверждения

## Связанные концепты
- [[design-system-generator]] — производит `tokens.json`, обязателен перед запуском
- [[content-writer]] — производит `final-copy.md` с текстами для блоков
- [[integrations-engineer]] — следующий этап 08, настраивает формы и вебхуки
- [[frontend-builder]] — переписывает `block.php` по CSS из `DESIGN.md §5`
- [[landing-build]] — slash-команда, триггерящая этот агент
- [[landing-orchestrator]] — диспатчит wp-builder в нужный момент

## Источник
- `agents/wp-builder.md`
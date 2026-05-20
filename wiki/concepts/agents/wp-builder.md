---
type: agent
name: wp-builder
sources: ["agents/wp-builder.md"]
updated: 2026-05-20
triggers: []
stage: "08"
uses:
  - design-system-generator
  - content-writer
  - niche-analyst
  - stack-planner
  - scene-director
  - landing-orchestrator
  - integrations-engineer
tags: [wordpress, lazy-blocks, php, css, js, stage-08]
---

# wp-builder (WP-сборщик)

## Что делает

Генерирует готовый WordPress-код лендинга: PHP-шаблоны блоков на Lazy Blocks Free, регистрацию блоков в `functions.php`, CSS со стилями через дизайн-токены и JS с интеракциями. На выходе — тема, которую можно сразу загрузить на сервер и импортировать контент в WordPress.

## Когда вызывать / в каком этапе

Этап **08_build**. Запускается после того, как утверждены этап 05 (дизайн-система), этап 06 (стек), этап 07 (финальный контент) и заполнен `08_КОД/block-spec.yaml`. Вызывается командой `/landing-build` через `landing-orchestrator`. Перед любым действием проверяет `.landing-state.yaml` и запускает `gate-check.sh --stage 08_build` — при ошибке полностью останавливается.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, отступы
- `06_СТЕК/design-stack.yaml` — режим (standard / cinematic) и стек плагинов
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам
- `08_КОД/block-spec.yaml` — источник истины: список блоков и поля каждого
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — контракт: какие блоки создавать
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — уровень продукта (luxury → утилитарный), влияет на отображение цен
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (rational / emotional_aspiration / trust_authority / hybrid)

**Выход:**
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — один файл на блок
- `08_КОД/wp-theme/functions.php` — регистрация всех блоков через `lzb/init`
- `08_КОД/wp-theme/assets/css/main.css` — стили через CSS-переменные
- `08_КОД/wp-theme/assets/js/main.js` — интеракции (FAQ, scroll-to-form, GSAP если cinematic)
- `08_КОД/page-content.html` — Gutenberg-разметка для импорта в WP-страницу

## Связанные концепты

- [[design-system-generator]] — поставляет `tokens.json` (этап 05), без него wp-builder не запускается
- [[content-writer]] — поставляет `final-copy.md` (этап 07)
- [[stack-planner]] — поставляет `design-stack.yaml` с выбором режима и библиотек
- [[niche-analyst]] — поставляет `market-profile.md` и `positioning.md`, управляет поведением блоков
- [[scene-director]] — поставляет `scenes.md` при cinematic-режиме для GSAP-анимаций
- [[landing-orchestrator]] — диспатчит wp-builder в нужный момент pipeline
- [[integrations-engineer]] — следующий агент после wp-builder: добавляет Fluent Forms, Telegram webhook

## Источник

- `agents/wp-builder.md`
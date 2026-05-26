---
type: agent
name: wp-builder
sources: ["agents/wp-builder.md"]
updated: 2026-05-26
triggers: []
stage: "08"
uses: ["landing-orchestrator", "landing-build", "landing-style", "landing-deploy"]
tags: ["wordpress", "lazy-blocks", "php", "stage-08", "code-generation"]
---

# wp-builder (WP-сборщик)

## Что делает

Генерирует готовый PHP-код WordPress-лендинга: Lazy Blocks блоки, функции регистрации, CSS/JS ассеты и Gutenberg-разметку страницы. На входе — одобренные дизайн-токены и контент, на выходе — рабочая тема, которую можно задеплоить на Beget.

## Когда вызывать / в каком этапе

Запускается на **этапе 08 (build)** командой `/landing-build` через `landing-orchestrator`. Обязательное условие: этапы 05 (дизайн-система), 06 (стек), 07 (контент) утверждены и закрыты. Перед любым действием агент читает `.landing-state.yaml` и проверяет `current_stage == 08_build`; если нет — останавливается. Физический блок на запись — `scripts/hooks/enforce_stage_gate.py` (PreToolUse hook).

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, отступы)
- `06_СТЕК/design-stack.yaml` — стек и режим (`standard` / `cinematic`)
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам
- `08_КОД/block-spec.yaml` — список блоков и поля каждого (источник истины)
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — контракт блоков с wp-builder
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — ценовой тир (luxury / premium / mass)
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим блоков (`emotional_aspiration`, `trust_authority`, `rational`, `hybrid`)

**Выход:**
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по файлу на каждый блок
- `08_КОД/wp-theme/functions.php` — секция `lzb/init` с регистрацией всех блоков
- `08_КОД/wp-theme/assets/css/main.css` — стили только через CSS-переменные
- `08_КОД/wp-theme/assets/js/main.js` — базовые интеракции (FAQ-аккордеон, scroll-to-form); GSAP ScrollTrigger если cinematic-режим
- `08_КОД/page-content.html` — готовая Gutenberg-разметка (`<!-- wp:lazyblock/<slug> -->`) для импорта в WP-страницу
- В каждой форме — legal-block (checkbox ПД согласия, 152-ФЗ), cookie-banner в footer/header

**HARD GATE:** после генерации агент показывает список файлов и ждёт явного утверждения пользователя перед закрытием этапа.

## Связанные концепты

- [[landing-build]] — slash-команда, которая запускает этот агент
- [[landing-orchestrator]] — диспетчер, вызывающий wp-builder на этапе 08
- [[landing-style]] — этап 08b, дополняет CSS-стили по wireframe-блокам
- [[landing-deploy]] — следующий этап (09) после закрытия 08
- [[landing-design]] — этап 05, поставляет tokens.json
- [[landing-content]] — этап 07, поставляет final-copy.md

## Источник

- `agents/wp-builder.md`
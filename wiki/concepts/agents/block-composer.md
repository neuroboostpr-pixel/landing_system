---
type: agent
name: block-composer
sources: ["agents/block-composer.md"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: ["landing-wireframe", "landing-design", "landing-prototype", "premium-07b-checklist", "stage-execution-protocol", "landing-photos", "landing-visuals"]
tags: ["compose", "html", "design-tokens", "07b", "stage"]
---

# block-composer — Сборка composed.html (этап 07b)

## Что делает

Собирает финальный HTML-макет лендинга (`composed.html`) из утверждённых пользователем вариантов блоков, подставляет реальные тексты из прототипа и применяет дизайн-токены (цвета, шрифты, тени). Визуальные материалы — фото, иконки, инфографика — остаются видимыми placeholder-метками: их заполнят этапы PR-B и PR-C.

## Когда вызывать / в каком этапе

Вызывается на этапе **07b** (Block Compose) командой `/landing-compose`. Предшественники должны быть закрыты:
- `07a_WIREFRAME/selections.yaml` — пользователь выбрал варианты блоков в wireframe.html
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-система утверждена
- `07_ПРОТОТИП/prototype.yaml` — прототип разобран и зафиксирован

Агент читает `.landing-state.yaml` и проверяет `current_stage == 07c_composed`. Если предшественник не закрыт — harness-хук `enforce_stage_gate.py` физически блокирует запись файлов.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — тексты, заголовки, CTA (неприкосновенны, переносятся дословно)
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — CSS-переменные бренда
- `block-library/` — общая библиотека wireframe-блоков
- `docs/standards/premium-07b-checklist.md` — обязательный стандарт качества (13 фич)

**Выход:**
- `<project>/07b_COMPOSED/composed.html` — итоговый макет с токенами и текстами
- `<project>/07b_COMPOSED/composed-mobile.html` — мобильная версия
- `<project>/07b_COMPOSED/composed-mobile-preview.html` — iframe-превью iPhone/iPad
- `<project>/07b_COMPOSED/composed-explained.md` — RU-документация по сборке

## Ключевые ограничения

**Контент прототипа неприкосновенен (PR-H):** заголовки, CTA и тексты из `prototype.yaml` переносятся дословно. Любое изменение — только после явного разрешения пользователя с обновлением `prototype.yaml`.

**HARD GATE 07b:** этап не закрывается, пока `verify-composed-premium.sh` не вернёт exit 0. Обязательные 13 премиум-фич: CSS-переменные, `clamp()`-типографика, glassmorphism-навигация, parallax-фон, анимации через `IntersectionObserver`, градиентный текст, hover-lift на карточках, слайдер, lightbox, count-up, smooth scroll, pulse-dot.

## Связанные концепты

- [[landing-wireframe]] — поставляет `selections.yaml` с выбором блоков на входе
- [[landing-prototype]] — поставляет `prototype.yaml` с финальными текстами
- [[landing-design]] — поставляет `tokens.json` с дизайн-токенами
- [[premium-07b-checklist]] — definition of done: 13 обязательных фич
- [[stage-execution-protocol]] — обязательный протокол перед каждым Write/Edit
- [[landing-photos]] — этап PR-B, заполняет photo-placeholders после compose
- [[landing-visuals]] — этап PR-C, заполняет icon/infographic-placeholders после compose

## Источник

- `agents/block-composer.md`
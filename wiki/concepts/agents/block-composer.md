---
type: agent
name: block-composer
sources: ["agents/block-composer.md"]
updated: 2026-05-26
triggers: []
stage: "07b"
uses: ["stage-execution-protocol", "premium-07b-checklist", "landing-wireframe", "landing-compose", "landing-photos", "landing-visuals"]
tags: ["compose", "07b", "html", "design-tokens", "premium"]
---

# Block Composer — Агент сборки composed.html

## Что делает
Собирает финальный цветной макет лендинга (`composed.html`) из утверждённых вариантов блоков, вставляет реальные тексты из прототипа и дизайн-токены из бренд-кита. Визуальные элементы (фото, иконки, инфографика) оставляет как именованные плейсхолдеры — их заполнят следующие этапы PR-B и PR-C.

## Когда вызывать / в каком этапе
Этап **07b (Block Compose)**. Вызывается командой `/landing-compose` после того, как пользователь выбрал варианты блоков в `wireframe.html` и положил `selections.yaml` в папку `07a_WIREFRAME/`. Перед запуском агент проверяет, что `.landing-state.yaml` показывает `current_stage == 07c_composed`, прогоняет `gate-check.sh` и рисует Mermaid-карту pipeline.

## Что на вход / на выход

**Входные артефакты:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — финальные тексты и CTA (неприкосновенны)
- `<project>/07a_WIREFRAME/selections.yaml` — выбор вариантов блоков пользователем
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, тени
- `block-library/` — общая библиотека блоков
- `docs/standards/premium-07b-checklist.md` — 13 обязательных премиум-фич

**Выходные артефакты:**
- `07b_COMPOSED/composed.html` — полный макет с токенами и текстами
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/composed-mobile-preview.html` — iframe-превью для iPhone/iPad
- `07b_COMPOSED/composed-explained.md` — описание сборки на русском

## Ключевые правила

**Тексты прототипа неприкосновенны (PR-H):** заголовки, CTA и абзацы переносятся дословно. Любое изменение — только с явного разрешения пользователя, и сначала обновляется `prototype.yaml`.

**HARD GATE:** этап не закрывается, пока `scripts/verify-composed-premium.sh` не вернёт exit 0. Обязательны все 13 премиум-фич: CSS-переменные, `clamp()` типографика, glassmorphism nav, parallax hero, IntersectionObserver, gradient text, hover-lift, слайдер, lightbox, count-up, smooth scroll, pulse-dot.

**Блокирующий хук:** `scripts/hooks/enforce_stage_gate.py` физически запрещает Write/Edit к файлам этапа, если предшественники не закрыты — обходить нельзя.

## Связанные концепты
- [[stage-execution-protocol]] — обязательный протокол перед любым действием агента
- [[premium-07b-checklist]] — definition of done для 13 премиум-фич
- [[landing-wireframe]] — предшествующий этап 07a, источник selections.yaml
- [[landing-compose]] — slash-команда, запускающая этого агента
- [[landing-photos]] — PR-B: заполняет фото-плейсхолдеры после 07b
- [[landing-visuals]] — PR-C: заполняет иконки/инфографику после 07b

## Источник
- `agents/block-composer.md`
---
type: agent
name: scene-director
sources: ["agents/scene-director.md"]
updated: 2026-05-20
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-architect", "stage-execution-protocol", "landing-orchestrator"]
tags: ["cinematic", "motion", "gsap", "premium", "stage-05"]
---

# scene-director — Режиссёр кинематографических сцен

## Что делает

Проектирует анимационную архитектуру лендинга: разбивает страницу на 6–8 кинематографических сцен со своей логикой параллакса, GSAP-движения и mobile-fallback. Нужен только в «cinematic»-режиме — для премиальных проектов с богатым motion-дизайном.

## Когда вызывать / в каком этапе

Активируется **только при флаге `--cinematic`** или явном запросе пользователя, строго после того как `design-system-generator` завершил этап `05_design` и создал `DESIGN.md`. Предшественник должен быть закрыт через `gate-state.sh approve` — иначе Pre-Tool-Use хук заблокирует запись файлов.

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и убедиться, что `current_stage == 05_design`.
2. Показать Mermaid-карту pipeline через `render-pipeline-map.sh`.
3. Запустить `gate-check.sh --stage 05_design` и дождаться exit 0.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — ниша, целевая аудитория, тональность
- `04_БРЕНД/brand-kit.md` — цвета, motion-стиль, фирменные токены
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — motion-токены дизайн-системы

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar для каждой из 6–8 сцен: название, тип, визуальное описание, инструкции GSAP / ScrollTrigger / Lenis, параллакс-логика, mobile-упрощение

**Запрещено:**
- Scroll hijacking
- Particle systems
- Fade-up на каждом блоке (однообразие)

## Типовые сцены (8 штук)

| # | Сцена | Суть |
|---|---|---|
| 1 | Hero Film Frame | Full-height, layered planes, медленный параллакс |
| 2 | Chaos to Clarity | Текстовые слои, фоновые орбиты |
| 3 | What You Get | Карточки с controlled stagger |
| 4 | The Diagnostic Process | Quasi-timeline с параллаксом |
| 5 | About the Expert | Portrait scene, light-depth эффект |
| 6 | Proof / Trust | Цифры и кейсы, сдержанный motion |
| 7 | FAQ | Лёгкие взаимодействия |
| 8 | Final Call | Кульминация, contrast shift |

## Связанные концепты

- [[design-system-generator]] — обязательный предшественник: даёт `DESIGN.md` с motion-токенами
- [[brand-architect]] — источник `brand-kit.md` с цветами и motion-стилем
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit действием
- [[landing-orchestrator]] — управляет порядком этапов и проверяет gate-check перед запуском агента
- [[block-composer]] — использует `scenes.md` на этапе 07b при сборке composed.html в cinematic-режиме

## Источник

- `agents/scene-director.md`
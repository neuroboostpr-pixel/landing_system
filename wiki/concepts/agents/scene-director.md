---
type: agent
name: scene-director
sources: ["agents/scene-director.md"]
updated: 2026-05-26
triggers: []
stage: "05"
uses: ["landing-design", "design-system-generator", "stage-execution-protocol"]
tags: ["cinematic", "motion", "gsap", "premium", "stage-05"]
---

# Scene Director (Режиссёр сцен — Cinematic Premium)

## Что делает
Проектирует кинематографическую архитектуру лендинга: разбивает страницу на 6–8 визуальных сцен, задаёт для каждой из них GSAP-анимации, параллакс-логику и мобильные fallback'и. Результат — готовый motion-план, которым руководствуется разработчик при вёрстке.

## Когда вызывать / в каком этапе
Только на этапе **05_design** и исключительно при флаге `--cinematic` (либо по явному запросу пользователя). Активируется **после** завершения `design-system-generator`. Перед началом работы агент обязан пройти Stage Execution Protocol: прочитать `.landing-state.yaml`, убедиться что `current_stage == 05_design`, показать Mermaid-карту pipeline, создать TodoWrite-список и дождаться exit 0 от `gate-check.sh`.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — ниша, целевая аудитория, тон
- `04_БРЕНД/brand-kit.md` — цвета, motion-гайдлайны
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — motion-токены дизайн-системы

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — полный scene grammar: названия и типы сцен, описание визуала и глубины, GSAP / ScrollTrigger / Lenis инструкции, parallax-логика, мобильные упрощения

## Архитектура сцен (8 типовых)

| # | Сцена | Ключевое качество |
|---|---|---|
| 1 | Hero Film Frame | Full-height split, slow parallax |
| 2 | Chaos to Clarity | Текстовые слои + фоновые орбиты |
| 3 | What You Get | Карточки с controlled stagger |
| 4 | Diagnostic Process | Quasi-timeline + parallax |
| 5 | About the Expert | Portrait, premium light-depth |
| 6 | Proof / Trust | Цифры, кейсы, restrained motion |
| 7 | FAQ | Лёгкие clear interactions |
| 8 | Final Call | Кульминация, contrast shift |

**Motion Rules (запрещено):** scroll hijack, particle systems, fade-up на каждом блоке.

## Связанные концепты
- [[landing-design]] — родительский скилл этапа 05, внутри которого вызывается scene-director
- [[design-system-generator]] — предшественник: должен завершиться до активации агента
- [[stage-execution-protocol]] — обязательный протокол, которому следует агент перед любыми изменениями файлов

## Источник
- `agents/scene-director.md`
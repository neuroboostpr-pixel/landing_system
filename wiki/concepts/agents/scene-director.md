---
type: agent
name: scene-director
sources: ["agents/scene-director.md"]
updated: 2026-05-15
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-kit-build", "niche-analysis"]
tags: ["cinematic", "motion", "gsap", "premium", "stage-05"]
---

# scene-director (Режиссёр сцен — Cinematic Premium)

## Что делает
Проектирует кинематографическую архитектуру лендинга: делит страницу на 6–8 сцен с описанием визуала, анимаций и параллакса. Результат — готовый motion-план, по которому фронтенд-разработчик подключает GSAP и ScrollTrigger.

## Когда вызывать / в каком этапе
Этап **05 (Дизайн-система)**, только при флаге `--cinematic` при создании проекта или при явном запросе пользователя. Запускается строго **после** того, как `design-system-generator` создал `DESIGN.md` с motion-токенами.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — ниша, целевая аудитория, тон
- `04_БРЕНД/brand-kit.md` — цвета, motion-параметры
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — motion-токены

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar (название, тип, визуал, глубина), GSAP / ScrollTrigger / Lenis-инструкции, parallax-логика, mobile fallback для каждой из 6–8 сцен

**Жёсткие запреты (Motion Rules):**
- ❌ scroll hijack
- ❌ particle systems
- ❌ fade-up на каждом блоке

**8 типовых сцен-шаблонов:**
1. Hero Film Frame — full-height split, слоевый параллакс
2. Chaos to Clarity — текстовые слои, фоновые орбиты
3. What You Get — карточки с controlled stagger
4. The Diagnostic Process — псевдо-таймлайн с параллаксом
5. About the Expert — портретная сцена, световая глубина
6. Proof / Trust — цифры, кейсы, сдержанный motion
7. FAQ — лёгкие взаимодействия
8. Final Call — кульминация, контрастный сдвиг

## Связанные концепты
- [[design-system-generator]] — должен отработать первым и поставить motion-токены в `DESIGN.md`
- [[brand-kit-build]] — поставляет цвета и motion-параметры через `brand-kit.md`
- [[niche-analysis]] — через `brief.md` определяет тон и ЦА, которые влияют на выбор сцен

## Источник
- `agents/scene-director.md`
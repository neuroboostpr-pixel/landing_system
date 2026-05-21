---
type: agent
name: scene-director
sources: ["agents/scene-director.md"]
updated: 2026-05-20
triggers: []
stage: "05"
uses: ["design-system-generator", "brand-architect", "landing-orchestrator"]
tags: ["cinematic", "motion", "gsap", "stage-05", "premium"]
---

# scene-director — Режиссёр кинематографических сцен

## Что делает
Проектирует анимационную архитектуру лендинга: разбивает страницу на 6–8 кинематографических сцен и описывает, как каждая из них должна двигаться при скролле. Результат — пошаговый план с инструкциями для GSAP/ScrollTrigger, который потом ложится в основу верстки.

## Когда вызывать / в каком этапе
Активируется **только в cinematic-режиме** — при создании проекта с флагом `--cinematic` или по явному запросу пользователя. Запускается на этапе **05_design**, строго после того, как `design-system-generator` создал `DESIGN.md` с motion-токенами. Вызывается агентом `landing-orchestrator` или вручную.

Предусловия (обязательные перед любым действием):
- `current_stage == 05_design` в `.landing-state.yaml`
- `gate-check.sh --stage 05_design` возвращает exit 0
- показана Mermaid-карта pipeline через `render-pipeline-map.sh`

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — ниша, целевая аудитория, тон коммуникации
- `04_БРЕНД/brand-kit.md` — цвета, motion-принципы бренда
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — motion-токены дизайн-системы

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — полный scene grammar: название, тип, описание визуала, GSAP/ScrollTrigger/Lenis инструкции, parallax-логика и mobile fallback для каждой из 6–8 сцен

**Motion Rules (строгие ограничения):**
- ❌ Scroll hijack запрещён
- ❌ Particle systems запрещены
- ❌ Fade-up на каждом блоке запрещён

## Восемь типовых сцен

| # | Тип сцены | Суть |
|---|-----------|------|
| 1 | Hero Film Frame | Full-height split, layered planes, slow parallax |
| 2 | Chaos to Clarity | Текстовые слои + фоновые орбиты разной скоростью |
| 3 | What You Get | Карточки с controlled stagger |
| 4 | Diagnostic Process | Quasi-timeline с parallax |
| 5 | About the Expert | Portrait scene, premium light-depth |
| 6 | Proof / Trust | Цифры, кейсы, restrained motion |
| 7 | FAQ | Лёгкая сцена, чёткие взаимодействия |
| 8 | Final Call | Кульминация, contrast shift |

## Связанные концепты
- [[design-system-generator]] — предоставляет DESIGN.md с motion-токенами; обязателен перед запуском
- [[brand-architect]] — создаёт brand-kit.md, из которого берутся цветовые и motion-принципы
- [[landing-orchestrator]] — диспатчит scene-director при cinematic-режиме в рамках этапа 05

## Источник
- `agents/scene-director.md`
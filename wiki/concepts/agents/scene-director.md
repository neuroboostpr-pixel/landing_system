---
type: agent
name: scene-director
sources: ["agents/scene-director.md"]
updated: 2026-05-25
triggers: []
stage: "05"
uses: ["landing-design", "brand-kit", "stage-execution-protocol", "landing-orchestrator"]
tags: ["cinematic", "motion", "gsap", "design", "premium"]
---

# scene-director (Режиссёр сцен — Cinematic Premium)

## Что делает

Проектирует кинематографическую архитектуру лендинга: разбивает страницу на 6–8 смысловых сцен и описывает для каждой визуальный план, анимации GSAP/ScrollTrigger и поведение на мобильных устройствах. Результат — готовый сценарий движения, по которому верстальщик (или автоматика) собирает живой прокручиваемый лендинг.

## Когда вызывать / в каком этапе

Активируется **только на этапе 05 (дизайн-система)** и **только при наличии флага `--cinematic`** — либо при явном запросе пользователя. Должен запускаться после `design-system-generator`, когда `brand-kit.md`, `DESIGN.md` и `brief.md` уже готовы. Перед любым действием агент обязан убедиться, что `.landing-state.yaml` показывает `current_stage == 05_design`, пройти `gate-check.sh` и отрисовать Mermaid-карту пайплайна.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — ниша, целевая аудитория, тон
- `04_БРЕНД/brand-kit.md` — цвета, motion-гайдлайны
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — motion-токены

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar (6–8 сцен) с GSAP/ScrollTrigger/Lenis инструкциями, parallax-логикой и mobile fallback для каждой сцены

## Типовые сцены

Агент использует библиотеку из 8 архетипов:

| # | Сцена | Суть |
|---|-------|------|
| 1 | Hero Film Frame | Полноэкранный сплит, слоистые планы, slow parallax |
| 2 | Chaos to Clarity | Текст слоями, фоновые орбиты с разной скоростью |
| 3 | What You Get | Карточки с controlled stagger |
| 4 | The Diagnostic Process | Квази-таймлайн с parallax |
| 5 | About the Expert | Портрет, premium light-depth |
| 6 | Proof / Trust | Цифры и кейсы, restrained motion |
| 7 | FAQ | Лёгкие clear interactions |
| 8 | Final Call | Кульминация, contrast shift |

Запрещённые паттерны: scroll hijack, particle systems, повсеместные fade-up на каждом блоке.

## Связанные концепты

- [[landing-design]] — предшественник; агент читает его выходной `DESIGN.md`
- [[brand-kit]] — источник цветов и motion-гайдлайнов
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit действием
- [[landing-orchestrator]] — диспатчит агента в составе общего пайплайна

## Источник

- `agents/scene-director.md`
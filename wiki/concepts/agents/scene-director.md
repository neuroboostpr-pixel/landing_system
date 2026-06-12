---
slug: scene-director
type: agent
name: "Режиссёр сцен (Cinematic Premium)"
stage: "05"
tags: [cinematic, design, motion, gsap, animation, parallax, scrolltrigger]
triggers: []
inputs:
  - 00_БРИФ/brief.md
  - 04_БРЕНД/brand-kit.md
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
outputs:
  - 05_ДИЗАЙН-СИСТЕМА/scenes.md
gates: []
pre_reqs: [design-system-generator]
related: [brand-architect, design-system-generator, block-composer]
sources: ["agents/scene-director.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# Режиссёр сцен (Cinematic Premium)

## Что делает

Проектирует кинематографическую структуру лендинга из 6–8 сцен. На входе — бриф, бренд-кит и motion-токены из DESIGN.md. На выходе — `scenes.md` с детализированной scene grammar: тип сцены, описание визуала, инструкции GSAP/ScrollTrigger/Lenis, parallax-логика и мобильный фоллбек. Соблюдает запреты: без scroll hijack, без particle systems, без monotone fade-up на каждом блоке.

## Когда вызывается

Активируется только при флаге `--cinematic` при создании проекта или при явном вызове пользователя. Работает исключительно в рамках этапа `05_design` — если `current_stage` в `.landing-state.yaml` отличается, агент останавливается и сообщает об ошибке. Обязательна закрытая gate предшественника `design-system-generator`.

## Вход → выход

**Вход:** `brief.md` (ниша, ЦА, тон), `brand-kit.md` (цвета, motion-настройки), `DESIGN.md` (motion-токены этапа 05). Требуется пройденный stage-gate `05_design` (exit 0 от `gate-check.sh`).

**Выход:** `05_ДИЗАЙН-СИСТЕМА/scenes.md` — полная scene grammar: название и тип каждой из 6–8 сцен, GSAP-план, parallax-инструкции, mobile fallback.

## Failure modes

- Агент запущен без флага `--cinematic` — не активируется, что может быть неочевидно при ручном вызове.
- `current_stage` в `.landing-state.yaml` не равен `05_design` — жёсткая остановка, пользователю нужно вручную закрыть предшественника.
- `DESIGN.md` не содержит motion-токенов (этап 05 прошёл без кинематографических настроек) — scenes.md генерируется с неполными или дефолтными параметрами GSAP.
- Конфликт между motion-токенами brand-kit и выбранным типом сцены — агент не предупреждает, просто перекрывает одно другим.
- Mobile fallback прописан формально, но не верифицируется скриптом — на реальных устройствах могут появляться тяжёлые анимации.

## Related

- [[design-system-generator]] — обязательный предшественник, создаёт DESIGN.md с motion-токенами
- [[brand-architect]] — формирует brand-kit.md, из которого берутся цвета и motion-настройки
- [[block-composer]] — использует scenes.md при сборке composed.html на этапе 07b
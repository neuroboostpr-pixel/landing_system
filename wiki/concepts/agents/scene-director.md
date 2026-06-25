---
slug: scene-director
type: agent
name: "Режиссёр сцен (Cinematic Premium)"
stage: "05"
tags: [cinematic, motion, gsap, scenes, design-system]
triggers: []
inputs:
  - 00_БРИФ/brief.md
  - 04_БРЕНД/brand-kit.md
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
outputs:
  - 05_ДИЗАЙН-СИСТЕМА/scenes.md
gates: []
pre_reqs: [design-system-generator, 04-brend, 05-dizayn-sistema]
related: [design-system-generator, brand-architect, landing-design, 05-dizayn-sistema]
sources: ["agents/scene-director.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Режиссёр сцен (Cinematic Premium)

## Что делает

Проектирует кинематографическую архитектуру лендинга: разбивает страницу на 6–8 сцен и описывает для каждой визуальный характер, глубину слоёв, GSAP/ScrollTrigger/Lenis-инструкции и parallax-логику. Работает только в режиме `--cinematic` — стандартным проектам этот агент не нужен. Результат — `scenes.md` в папке дизайн-системы, который затем использует `block-composer` при создании `composed.html`.

## Когда вызывается

Активируется только при флаге `--cinematic` во время создания проекта или при явном вызове пользователя. Обязательное предусловие: этап `05_design` активен (`.landing-state.yaml::current_stage == 05_design`) и `design-system-generator` уже завершён. Без этих условий агент останавливается и сообщает об ошибке.

## Вход → выход

**Вход:** `00_БРИФ/brief.md` (ниша, ЦА, тон), `04_БРЕНД/brand-kit.md` (цвета, motion-правила), `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` (motion-токены).

**Выход:** `05_ДИЗАЙН-СИСТЕМА/scenes.md` — scene grammar для 6–8 сцен: название, тип, визуальное описание, GSAP-инструкции, parallax-параметры, mobile fallback для каждой сцены.

## Failure modes

- Агент запускается без закрытого предшественника (`design-system-generator`) — hook `enforce_stage_gate.py` блокирует Write, задача виснет.
- `DESIGN.md` не содержит motion-токенов — сцены генерируются без привязки к реальному бренду, визуал расходится с дизайн-системой.
- Нарушение Motion Rules: scroll-hijack, particle-системы или fade-up на каждом блоке — явно запрещены спекой, но агент может нарушить их при недостаточном контексте из brief.
- `brief.md` не заполнен — агент не может определить тон и ЦА, сцены получаются обезличенными.
- `scenes.md` генерируется для не-cinematic проекта — лишний артефакт ломает ожидания `block-composer`.

## Related

- [[design-system-generator]] — обязательный предшественник; даёт motion-токены и DESIGN.md
- [[brand-architect]] — создаёт brand-kit.md с цветами и motion-правилами, которые читает этот агент
- [[05-dizayn-sistema]] — этап, в рамках которого работает агент
- [[landing-design]] — slash-команда, через которую запускается cinematic-режим
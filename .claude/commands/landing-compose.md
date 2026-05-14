---
description: Stage 07b — assemble composed.html with design-tokens injected and prototype content substituted. Visual placeholders remain.
---

# /landing-compose

Запускает этап **07b_COMPOSED**.

## Что делает

1. Проверяет наличие `07_ПРОТОТИП/prototype.yaml`, `07a_WIREFRAME/selections.yaml`, `05_ДИЗАЙН-СИСТЕМА/tokens.json`.
2. Передаёт работу агенту `block-composer`.
3. Сообщает путь к артефакту.

## Артефакты

- `07b_COMPOSED/composed.html`
- `07b_COMPOSED/composed-mobile.html`
- `07b_COMPOSED/block-injection-log.md`

## Условия запуска

- selections.yaml в `07a_WIREFRAME/` существует
- tokens.json в `05_ДИЗАЙН-СИСТЕМА/` существует

## NOTE (PR-A scope)

Не интегрировано в `landing-orchestrator` — задача PR-D.
Финальный визуальный контент (фото/иконки/инфографика) добавит PR-B/PR-C.

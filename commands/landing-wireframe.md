---
description: Stage 07a — render interactive wireframe.html with 2-3 block-library candidates per prototype block. User picks variants via radio buttons.
---

# /landing-wireframe

Запускает этап **07a_WIREFRAME**.

## Что делает

1. Проверяет наличие `07_ПРОТОТИП/prototype.yaml`.
2. Передаёт работу агенту `ux-composer`.
3. После рендера сообщает путь к `07a_WIREFRAME/wireframe.html` и инструкцию по выбору вариантов.

## Артефакты

- `07a_WIREFRAME/wireframe.html` — интерактивный preview
- `07a_WIREFRAME/candidates.yaml` — список кандидатов на блок

После выбора пользователем:
- `07a_WIREFRAME/selections.yaml` (создаётся пользователем через кнопку Confirm)

## Условия запуска

- `07_ПРОТОТИП/prototype.yaml` существует и валиден

## После одобрения

Запускай `/landing-compose`.

## NOTE (PR-A scope)

Не интегрировано в `landing-orchestrator` и `.landing-state.yaml` — задача PR-D.

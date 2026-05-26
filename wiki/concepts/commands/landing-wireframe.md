---
type: command
name: landing-wireframe
sources: ["commands/landing-wireframe.md"]
updated: 2026-05-26
triggers:
  - "сделай wireframe для лендинга"
  - "покажи варианты блоков"
  - "запусти этап 07a"
  - "создай интерактивный wireframe"
stage: "07a"
uses:
  - landing-go
  - landing-compose
  - ux-composer
  - landing-prototype
tags:
  - wireframe
  - этап-07a
  - блоки
  - прототип
---

# Landing Wireframe — Интерактивный Wireframe (Этап 07a)

## Что делает

Генерирует интерактивный HTML-файл, в котором для каждого блока прототипа предлагается 2–3 варианта из библиотеки блоков. Маркетолог выбирает нужный вариант через радио-кнопки прямо в браузере и нажимает «Confirm» — система сохраняет выбор.

## Когда вызывать / в каком этапе

Этап **07a**. Запускается после того, как `/landing-prototype` успешно создал `prototype.yaml`. Вызывается автоматически через `/landing-go` (рекомендуется) или вручную командой `/landing-wireframe`. Агент `ux-composer` берёт управление и рендерит wireframe.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — структура прототипа, обязан существовать и быть валидным

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный HTML-preview с вариантами блоков
- `07a_WIREFRAME/candidates.yaml` — машинный список кандидатов на каждый блок
- `07a_WIREFRAME/selections.yaml` — создаётся пользователем через кнопку «Confirm» после выбора вариантов

**Следующий шаг:** после того как `selections.yaml` сохранён в `07a_WIREFRAME/`, запускать `/landing-compose`.

## Связанные концепты

- [[landing-go]] — главная команда-оркестратор, вызывает этот этап автоматически
- [[landing-prototype]] — предшествующий этап, создаёт `prototype.yaml` как входной артефакт
- [[landing-compose]] — следующий этап (07b), собирает `composed.html` на основе выбранных вариантов
- [[ux-composer]] — агент, которому передаётся рендеринг wireframe
- [[landing-orchestrator]] — оркестратор, интегрирующий этап в `.landing-state.yaml`

## Источник

- `commands/landing-wireframe.md`
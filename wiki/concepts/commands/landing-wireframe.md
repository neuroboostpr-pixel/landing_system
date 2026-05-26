---
type: command
name: landing-wireframe
sources: ["commands/landing-wireframe.md"]
updated: 2026-05-26
triggers:
  - "сгенерировать вайрфрейм"
  - "показать варианты блоков"
  - "интерактивный wireframe"
  - "выбрать блоки для лендинга"
  - "запустить этап 07a"
stage: "07a"
uses:
  - ux-composer
  - landing-compose
  - landing-go
  - landing-orchestrator
tags:
  - wireframe
  - prototype
  - block-library
  - stage-07a
---

# Landing Wireframe — Интерактивный выбор блоков

## Что делает

Генерирует интерактивную HTML-страницу, где для каждого блока прототипа предлагается 2–3 варианта из библиотеки блоков. Маркетолог или дизайнер выбирает подходящий вариант через радио-кнопки и нажимает «Confirm» — система сохраняет выбор.

## Когда вызывать / в каком этапе

Этап **07a**. Вызывается после того, как существует и валиден файл `07_ПРОТОТИП/prototype.yaml` (результат команды `/landing-prototype`). Запускается автоматически через `/landing-go` или вручную через `/landing-wireframe`. После одобрения выбора — следующий шаг `/landing-compose`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — структурированный прототип с перечнем блоков

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный HTML-preview с 2–3 кандидатами на каждый блок
- `07a_WIREFRAME/candidates.yaml` — список всех кандидатов для каждого блока

**После действия пользователя:**
- `07a_WIREFRAME/selections.yaml` — файл с выбранными вариантами (создаётся кнопкой «Confirm» в браузере, затем кладётся вручную в папку `07a_WIREFRAME/`)

## Связанные концепты

- [[ux-composer]] — агент, которому передаётся работа по рендеру вариантов блоков
- [[landing-compose]] — следующая команда после одобрения wireframe (этап 07b)
- [[landing-go]] — основная точка входа, вызывает wireframe автоматически в нужный момент
- [[landing-orchestrator]] — оркестратор, в который интегрирован этот этап
- [[landing-prototype]] — предшествующая команда, создающая `prototype.yaml`

## Источник

- `commands/landing-wireframe.md`
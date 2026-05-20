---
type: command
name: landing-wireframe
sources: ["commands/landing-wireframe.md"]
updated: 2026-05-20
triggers:
  - "запусти wireframe"
  - "сделай каркас страницы"
  - "покажи варианты блоков"
  - "начни этап 07a"
  - "нарисуй wireframe"
stage: "07a"
uses:
  - ux-composer
  - landing-compose
  - landing-go
  - prototype-importer
tags:
  - wireframe
  - stage-07a
  - ux
  - block-library
---

# /landing-wireframe — Интерактивный вайрфрейм

## Что делает

Превращает машиночитаемый прототип (`prototype.yaml`) в интерактивный HTML-вайрфрейм, где для каждого блока страницы предлагается 2–3 визуальных варианта. Маркетолог выбирает подходящий вариант через радио-кнопки прямо в браузере, нажимает «Confirm» — и скачивается файл выбора `selections.yaml`.

## Когда вызывать / в каком этапе

Этап **07a_WIREFRAME**. Команда запускается после успешного импорта прототипа (`/landing-prototype`) — в папке проекта должен существовать валидный файл `07_ПРОТОТИП/prototype.yaml`. Вызывается автоматически через `/landing-go` (рекомендуется) или вручную. Этап зафиксирован в `.landing-state.yaml`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемый прототип лендинга (результат `/landing-prototype`)

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный браузерный preview (desktop + mobile, CSS-переключатель вариантов)
- `07a_WIREFRAME/candidates.yaml` — список блоков-кандидатов из block-library на каждую секцию прототипа

**После действия пользователя:**
- `07a_WIREFRAME/selections.yaml` — файл выборов, скачивается кнопкой «Confirm» в wireframe.html; пользователь кладёт его обратно в папку `07a_WIREFRAME/`

## Связанные концепты

- [[ux-composer]] — агент, который выполняет рендер wireframe.html; строго выбирает блоки из block-library, не изобретает новые
- [[prototype-importer]] — предшествующий этап; создаёт `prototype.yaml`, без которого команда не запустится
- [[landing-compose]] — следующий этап после одобрения вайрфрейма; получает `selections.yaml` и рендерит `composed.html` с токенами и текстами
- [[landing-go]] — мастер-оркестратор; автоматически вызывает `/landing-wireframe` в нужный момент пайплайна
- [[block-library-management]] — управляет пулом блоков-кандидатов, из которых ux-composer составляет варианты

## Источник

- `commands/landing-wireframe.md`
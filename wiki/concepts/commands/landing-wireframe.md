---
type: command
name: landing-wireframe
sources: ["commands/landing-wireframe.md"]
updated: 2026-05-15
triggers:
  - "запусти wireframe"
  - "сделай wireframe для лендинга"
  - "хочу выбрать блоки для лендинга"
  - "интерактивный wireframe"
  - "этап 07a"
stage: "07a"
uses:
  - ux-composer
  - prototype-import
  - landing-compose
  - wireframe-rendering
tags: ["wireframe", "stage-07a", "ux", "block-selection"]
---

# /landing-wireframe — Интерактивный wireframe с вариантами блоков

## Что делает

Генерирует интерактивный HTML-файл, в котором каждый блок лендинга представлен в 2–3 вариантах оформления из библиотеки блоков. Маркетолог открывает файл в браузере, выбирает понравившийся вариант для каждого раздела и нажимает «Confirm» — система сохраняет выбор.

## Когда вызывать / в каком этапе

Вызывается **после** завершения этапа 07 (импорт прототипа). Обязательное условие: файл `07_ПРОТОТИП/prototype.yaml` должен существовать и быть валидным. Типичный триггер — после того как `/landing-prototype` завершил работу и пользователь проверил `prototype.md`.

Команда вызывается **вручную**; в `landing-orchestrator` и `.landing-state.yaml` пока не интегрирована (задача PR-D).

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемый прототип, подготовленный командой `/landing-prototype`

**Выход:**
- `07a_WIREFRAME/wireframe.html` — интерактивный preview с radio-переключателями между вариантами блоков (desktop + mobile)
- `07a_WIREFRAME/candidates.yaml` — список кандидатов из block-library для каждого блока прототипа
- `07a_WIREFRAME/selections.yaml` — создаётся самим пользователем через кнопку «Confirm» в браузере; содержит финальный выбор вариантов

## Как использовать

1. Открой `07a_WIREFRAME/wireframe.html` в браузере.
2. Для каждого раздела выбери подходящий вариант блока через radio-кнопки.
3. Нажми «Confirm» — скачается `selections.yaml`.
4. Положи скачанный файл обратно в `07a_WIREFRAME/`.
5. Запусти `/landing-compose` для следующего этапа.

## Связанные концепты

- [[ux-composer]] — агент, который непосредственно рендерит `wireframe.html` и `candidates.yaml`
- [[prototype-import]] — предшествующий этап; формирует входной `prototype.yaml`
- [[landing-compose]] — следующий этап (07b): вставляет токены дизайна и тексты в выбранные блоки
- [[wireframe-rendering]] — скилл, описывающий логику рендера wireframe
- [[block-composition]] — скилл этапа 07b, следует после одобрения wireframe

## Источник

- `commands/landing-wireframe.md`
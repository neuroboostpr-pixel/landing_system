---
slug: landing-prototype
type: command
name: "/landing-prototype — Импорт прототипа"
stage: "07"
tags: [prototype, import, stage-07, pdf, yaml]
triggers: [landing-prototype]
inputs:
  - 07_ПРОТОТИП/source/prototype.pdf
  - 07_ПРОТОТИП/source/prototype.md
outputs:
  - 07_ПРОТОТИП/prototype.md
  - 07_ПРОТОТИП/prototype.yaml
  - 07_ПРОТОТИП/import-log.md
pre_reqs: [landing-project-init]
related:
  - prototype-importer
  - prototype-import
  - landing-orchestrator
  - wireframe-rendering
sources: ["commands/landing-prototype.md"]
updated: 2026-05-26
---

# /landing-prototype — Импорт прототипа

## Что делает

Запускает этап 07_ПРОТОТИП: забирает пользовательский прототип (PDF или Markdown) из папки `07_ПРОТОТИП/source/`, передаёт его агенту `prototype-importer`, который нормализует структуру в машиночитаемые форматы `prototype.md` и `prototype.yaml`. После завершения агента команда автоматически валидирует результат скриптом `validate-prototype.py` и формирует `import-log.md` с протоколом импорта. Итог — задокументированная блочная структура лендинга, готовая к следующему шагу — интерактивному wireframe.

## Когда вызывается

Вызывается вручную командой `/landing-prototype` или автоматически оркестратором через `/landing-go`. Условие: текущая папка является проектом-лендингом (содержит `00_БРИФ/brief.md` или `.landing-state.yaml`), а в `07_ПРОТОТИП/source/` лежит хотя бы один файл `prototype.pdf` или `prototype.md`.

## Вход → выход

**Вход:** файл прототипа (`prototype.pdf` или `prototype.md`) в папке `07_ПРОТОТИП/source/` внутри корня проекта-лендинга.

**Выход:** три артефакта — `07_ПРОТОТИП/prototype.md` (читаемое описание блоков), `07_ПРОТОТИП/prototype.yaml` (машиночитаемая структура, проходит валидацию), `07_ПРОТОТИП/import-log.md` (протокол импорта с диагностикой).

## Failure modes

- Файл прототипа отсутствует в `07_ПРОТОТИП/source/` — команда завершается с ошибкой до вызова агента.
- Текущая папка не является проектом-лендингом (нет `brief.md` / `.landing-state.yaml`) — проверка на входе не пройдена.
- `validate-prototype.py` возвращает ненулевой код — `prototype.yaml` не соответствует схеме; этап не считается завершённым, wireframe запускать нельзя.
- PDF с нечитаемым или сканированным текстом — агент `prototype-importer` может пропустить блоки; ревью `import-log.md` обязательно.
- `.landing-state.yaml` не обновляется после сбоя валидатора — gate-check.sh будет блокировать последующие этапы.

## Related

- [[prototype-importer]] — агент, который выполняет фактический разбор и нормализацию прототипа
- [[prototype-import]] — скилл с валидатором `validate-prototype.py`, используется после работы агента
- [[landing-orchestrator]] — может вызывать эту команду автоматически в рамках общего pipeline
- [[wireframe-rendering]] — следующий этап после успешного импорта прототипа
---
slug: ux-composer
type: agent
name: "UX Composer — интерактивный wireframe-генератор"
stage: "07a"
tags: [wireframe, ux, block-library, prototype, stage-07a]
triggers: [landing-wireframe]
inputs:
  - 07_ПРОТОТИП/prototype.yaml
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 04_БРЕНД/brand-kit.md
  - block-library/catalog.yaml
outputs:
  - 07a_WIREFRAME/wireframe.html
  - 07a_WIREFRAME/candidates.yaml
  - 07a_WIREFRAME/selections.yaml
gates: [selections_yaml_exists]
pre_reqs: []
related:
  - block-composer
  - design-system-generator
  - landing-orchestrator
sources: ["agents/ux-composer.md"]
updated: 2026-05-26
confidence: {triggers: medium, pre_reqs: low}
---

# UX Composer — интерактивный wireframe-генератор

## Что делает

Берёт `prototype.yaml` (список блоков прототипа) и подбирает для каждого блока 2–3 кандидата из `block-library`. Результат — `wireframe.html`: интерактивная HTML-страница с radio-кнопками, где пользователь выбирает вариант на каждый блок. Дополнительно инжектирует в wireframe UX-паттерны, цветовые палитры и типографику из `ui-ux-pro-max` для обоснованного выбора. Агент строго ограничен библиотекой: придумывать несуществующие блоки запрещено — при отсутствии подходящих вариантов он явно сигнализирует о необходимости добавить новый блок через `scaffold-block.py`.

## Когда вызывается

Запускается командой `/landing-wireframe` когда проект достиг стадии `07b_wireframe` в `.landing-state.yaml`. Предусловие — наличие и валидность `07_ПРОТОТИП/prototype.yaml`; если стадия не совпадает или prototype отсутствует — агент останавливается с диагностическим сообщением.

## Вход → выход

**Вход:** валидный `prototype.yaml`, `tokens.json` из дизайн-системы, `brand-kit.md`, каталог блоков `block-library/catalog.yaml`, 6 CSV-файлов из плагина `ui-ux-pro-max` (UX-паттерны, правила, палитры, типографика, стили, цвета).

**Выход:** `07a_WIREFRAME/wireframe.html` — интерактивная страница выбора вариантов; `07a_WIREFRAME/candidates.yaml` — список кандидатов по блокам; `07a_WIREFRAME/selections.yaml` — файл, который пользователь скачивает из браузера и кладёт обратно в папку.

## Чем закрывается этап (gates)

- `selections_yaml_exists` — файл `07a_WIREFRAME/selections.yaml` должен существовать в проекте. Пока пользователь не подтвердил выбор вариантов и не положил файл — переход к следующему этапу заблокирован.

## Failure modes

- **Отсутствует `ui-ux-pro-max`** — агент останавливается и требует установки плагина; рендер не запустится.
- **Нет кандидатов для блока** — `candidates.yaml` содержит пустые массивы; агент сообщает об этом, но не переходит к следующему блоку самостоятельно.
- **Стадия не совпадает** — `current_stage` в `.landing-state.yaml` не равен `07b_wireframe`; hook `enforce_stage_gate.py` блокирует Write/Edit.
- **`prototype.yaml` невалиден** — `validate-prototype.py` возвращает ошибку; агент останавливается до исправления.
- **`selections.yaml` не положен обратно** — пользователь скачал файл, но не скопировал в папку; gate не закрывается, `block-composer` не запустится.

## Related

- [[block-composer]] — следующий этап: принимает `selections.yaml` и собирает `composed.html`
- [[design-system-generator]] — поставляет `tokens.json`, который инжектируется в wireframe-контекст
- [[landing-orchestrator]] — координирует запуск `ux-composer` в рамках общего pipeline
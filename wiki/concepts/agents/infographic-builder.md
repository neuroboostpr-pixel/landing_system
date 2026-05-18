---
type: agent
name: infographic-builder
sources: ["agents/infographic-builder.md"]
updated: 2026-05-15
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation"]
tags: ["visuals", "infographics", "codex", "image-gen", "stage-07d"]
---

# infographic-builder — генератор одного инфографика

## Что делает

Генерирует **один PNG-файл инфографики** для конкретного слота в лендинге через codex image_gen. Работает с числовыми, столбчатыми, линейными и кольцевыми диаграммами. Чтобы не тратить API-запросы повторно — кэширует результат по хэшу параметров.

## Когда вызывать / в каком этапе

Вызывается **только агентом [[visual-curator]]** на этапе **07d (Visual Generation)**. Пользователь напрямую не запускает этот агент — он запускает `/landing-visuals`, а `visual-curator` диспатчит `infographic-builder` для каждого инфографического слота по очереди.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `<slot_name>` — имя слота, например `kpi-clients`
- `<chart_type>` — тип диаграммы: `number`, `bar`, `line`, `donut`
- `<data_json>` — JSON-строка с данными для инфографики

**Выход:**
- PNG-файл `<project>/07d_VISUALS/infographics/<slot_name>.png`
- Запись атрибуции в `07d_VISUALS/prompts.yaml` (если источник — OpenDesign)
- Обновление `STATE.yaml` при ошибках

**Логика исполнения:**
1. Вычислить хэш-ключ из `(hint, chart_type, brand_accent, niche)`.
2. Если кэш-хит — скопировать из `.cache/<hash>.png`, выйти.
3. Если кэш-мисс — запустить `codex-generate-infographic.sh`.
4. После генерации — сохранить в `.cache/<hash>.png`.

**Fallback-логика:**
- Если codex падает после повтора → SVG-плейсхолдер вместо PNG.
- Если `data_json` невалиден → использовать заглушку-данные, предупреждение в `STATE.yaml`.

## Связанные концепты

- [[visual-curator]] — оркестратор этапа 07d, вызывает этого агента для каждого слота
- [[icon-generator]] — аналогичный агент, но для иконок (не инфографики)
- [[visual-generation]] — скилл, содержащий скрипты генерации, в том числе `codex-generate-infographic.sh`

## Источник

- `agents/infographic-builder.md`
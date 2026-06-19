---
slug: infographic-builder
type: agent
name: "Генератор инфографики"
stage: "07d"
tags: [visual, infographic, codex, image-gen, cache]
triggers: []
inputs: [07b-composed, 05-dizayn-sistema]
outputs: [07d-visuals]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [visual-curator, visual-generation, icon-generator, 07d-visuals]
sources: ["agents/infographic-builder.md"]
updated: 2026-06-19
confidence: {stage: low, triggers: low}
---

# Генератор инфографики

## Что делает

Генерирует один PNG-файл инфографики для конкретного слота в `composed.html`. Получает имя слота, тип диаграммы (number, bar, line, donut) и данные в JSON, вычисляет хэш-ключ кэша, и либо возвращает готовый PNG из кэша, либо вызывает `codex-generate-infographic.sh` для генерации через codex image_gen. После генерации записывает результат в кэш и фиксирует атрибуцию в `prompts.yaml`. Является helper-агентом — вызывается только родительским агентом `visual-curator`, не напрямую.

## Когда вызывается

Диспатчится агентом `visual-curator` в ходе этапа 07d (генерация визуалов). Вызывается по одному разу на каждый слот инфографики из `composed.html`. Прямой вызов пользователем не предусмотрен.

## Вход → выход

**Вход:** путь к папке проекта (`<project_dir>`), имя слота (`slot_name`), тип диаграммы (`chart_type`), данные диаграммы в JSON (`data_json`), бренд-токены из `tokens.json` (цвет акцента, ниша).

**Выход:** файл `<project>/07d_VISUALS/infographics/<slot_name>.png`. При cache-хите — копия из `.cache/<hash>.png`. При ошибке codex — SVG-placeholder; при невалидном `data_json` — placeholder с generic-данными и предупреждение в `STATE.yaml`.

## Failure modes

- **codex недоступен или вернул ошибку** — после ретрая применяется SVG-placeholder; слот остаётся непустым, но без реальных данных.
- **Невалидный `data_json`** — агент использует generic-заглушку и пишет предупреждение в STATE.yaml; инфографика визуально ложная.
- **Промах кэша при повторном запуске** — если изменился цвет акцента или ниша, хэш меняется и codex вызывается заново; лишние траты токенов.
- **Отсутствует `tokens.json`** — генерация без бренд-цветов; инфографика не соответствует дизайн-системе.
- **Прямой вызов без `visual-curator`** — пропускается stage execution protocol родителя; результат может не попасть в `composed.html`.

## Related

- [[visual-curator]] — родительский агент, который диспатчит infographic-builder по слотам
- [[icon-generator]] — аналогичный helper для иконок, работает в паре в том же этапе
- [[07d-visuals]] — этап, в котором происходит вся генерация визуалов
- [[visual-generation]] — скилл с инструментами для codex image_gen
- [[05-dizayn-sistema]] — источник бренд-токенов (цвет акцента, шрифты) для промптов
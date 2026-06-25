---
slug: infographic-builder
type: agent
name: "Генератор инфографики"
stage: "07e"
tags: [visual-generation, infographics, codex, cache, image-gen]
triggers: []
inputs: [07b-composed, 05-dizayn-sistema]
outputs: [07d-visuals]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [visual-curator, icon-generator, visual-generation, 07d-visuals]
sources: ["agents/infographic-builder.md"]
updated: 2026-06-19
confidence: {triggers: low, stage: low}
---

# Генератор инфографики

## Что делает

Хелпер-агент, генерирующий **один** PNG с инфографикой для конкретного слота в проекте. Работает через codex image_gen с каскадом подбора промптов: сначала из каталога OpenDesign (90 JSON-пресетов), затем generic-промпт. Перед генерацией проверяет хэш-кэш по ключу `(hint, chart_type, brand_accent, niche)` — повторный прогон не вызывает API для уже сгенерированных слотов. При успехе записывает атрибуцию в `07d_VISUALS/prompts.yaml`. Работает только под руководством `visual-curator`; самостоятельный вызов не предусмотрен.

## Когда вызывается

Диспатчится агентом `visual-curator` в рамках этапа 07d/07e, когда нужно заполнить слот инфографики в `composed.html`. Прямой вызов пользователем не поддерживается — этап и протокол выполнения контролирует родительский агент.

## Вход → выход

**Вход:** путь к папке проекта (`project_dir`), имя слота (`slot_name`, например `kpi-clients`), тип диаграммы (`chart_type`: number / bar / line / donut), данные в виде JSON-строки (`data_json`).

**Выход:** `<project>/07d_VISUALS/infographics/<slot_name>.png`. При cache-попадании файл копируется из `.cache/<hash>.png` без запроса к API. При ошибке генерации — SVG-placeholder с предупреждением в STATE.yaml.

## Failure modes

- **codex timeout или API error** — после retry агент падает на SVG-плейсхолдер; инфографика остаётся визуально заглушкой до следующего прогона.
- **Невалидный `data_json`** — агент не прерывается, подставляет generic placeholder-данные; реальные цифры теряются молча — предупреждение в STATE.yaml.
- **Кэш-мисс при неизменном слоте** — если ключ кэша изменился (сменили brand_accent или niche), все слоты перегенерируются, даже утверждённые.
- **Отсутствие tokens.json или market-profile.md** — промпт-пикер не может взять цвета/нишу; генерируется обобщённая инфографика без брендинга.
- **Нарушение image-pipeline.md** — если генерация идёт без фазы rembg/оверлея акцента, финальный PNG не вписывается в палитру темы.

## Related

- [[visual-curator]] — родительский агент, диспатчит infographic-builder по слотам
- [[icon-generator]] — параллельный хелпер для иконок (этап 07e/07d)
- [[visual-generation]] — скилл-обёртка над codex image_gen, содержит shell-скрипты
- [[07d-visuals]] — этап, в рамках которого создаётся весь визуальный контент
---
slug: infographic-builder
type: agent
name: "Infographic Builder"
stage: "07d"
tags: [visuals, infographic, codex, image-gen, cache, helper-agent]
triggers: []
inputs: [07d_VISUALS, brand-kit, market-profile]
outputs: [07d_VISUALS/infographics]
gates: []
pre_reqs: [landing-visuals]
related: [landing-visuals]
sources: ["agents/infographic-builder.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Infographic Builder

## Что делает

Вспомогательный агент, который генерирует **один** PNG-инфографик для одного слота визуала на этапе 07d. Принимает тип графика и JSON с данными, проверяет хэш-кэш и либо возвращает закэшированный результат, либо вызывает `codex image_gen` через shell-скрипт. Если в базе OpenDesign есть подходящий промпт — использует его; иначе применяет generic-промпт. Фиксирует атрибуцию источника в `prompts.yaml`.

## Когда вызывается

Диспатчится родительским агентом `landing-visuals` (visual-curator) в ходе этапа 07d — **не вызывается напрямую пользователем**. Получает управление однократно на каждый незакрытый слот инфографики.

## Вход → выход

**Вход:** путь к папке проекта, имя слота (`slot_name`, например `kpi-clients`), тип графика (`number`, `bar`, `line`, `donut`) и JSON-спецификация данных (`data_json`).

**Выход:** готовый PNG по пути `<project>/07d_VISUALS/infographics/<slot_name>.png`; запись кэша `.cache/<hash>.png`; строка атрибуции в `07d_VISUALS/prompts.yaml` (если источник — OpenDesign).

## Failure modes

- **Codex API недоступен или исчерпаны ретраи** — агент создаёт SVG-заглушку вместо PNG; слот остаётся помечен в `STATE.yaml` как fallback.
- **Некорректный `data_json`** — агент подставляет generic-данные-шаблон и продолжает, выводит предупреждение в `STATE.yaml`.
- **Кэш повреждён или устарел** — без флага `--force` агент отдаст старый файл; обновление только через принудительный прогон.
- **Неизвестный `chart_type`** — промпт-пикер не найдёт шаблон в OpenDesign и упадёт в generic, итоговый PNG может не совпадать с ожиданием.
- **Прямой вызов в обход visual-curator** — Stage Execution Protocol не применяется, состояние проекта не обновляется, слот не будет зарегистрирован корректно.

## Related

- [[landing-visuals]] — родительский агент (visual-curator), который диспатчит infographic-builder для каждого слота инфографики
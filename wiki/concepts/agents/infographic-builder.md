---
type: agent
name: infographic-builder
sources: ["agents/infographic-builder.md"]
updated: 2026-05-25
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-cache", "visual-generation"]
tags: ["codex", "image-gen", "infographic", "png", "cache"]
---

# Infographic Builder — Генератор инфографики

## Что делает
Генерирует один PNG-файл инфографики для конкретного слота через codex image_gen. Умеет кешировать результат — повторный запрос с теми же параметрами не расходует API.

## Когда вызывать / в каком этапе
Этап **07d (Visuals)**. Агент является вспомогательным (helper) — вызывается **только родительским агентом `visual-curator`**, не напрямую пользователем. Stage Execution Protocol контролирует родитель.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `<slot_name>` — имя слота, например `kpi-clients`
- `<chart_type>` — тип чарта: `number`, `bar`, `line`, `donut`
- `<data_json>` — данные для инфографики в формате JSON-строки

**Выход:**
- `<project>/07d_VISUALS/infographics/<slot_name>.png` — готовый PNG
- Запись атрибуции в `07d_VISUALS/prompts.yaml` (если источник OpenDesign)

**Процесс:**
1. Вычисляет хеш-ключ кеша по `(hint, chart_type, brand_accent, niche)`.
2. При попадании в кеш — копирует из `.cache/<hash>.png`, выходит без обращения к API.
3. При промахе — запускает `codex-generate-infographic.sh`, затем сохраняет результат в кеш.

**Обработка ошибок:**
- Сбой codex после retry → SVG-placeholder вместо PNG.
- Невалидный `data_json` → используются generic-данные-заглушки, предупреждение пишется в `STATE.yaml`.

## Связанные концепты
- [[visual-curator]] — родительский агент, единственный легитимный вызывающий
- [[visual-generation]] — скилл, содержит скрипт `codex-generate-infographic.sh`
- [[visual-cache]] — механизм хеш-кеша для пропуска повторных генераций
- [[landing-visuals]] — команда, запускающая весь этап 07d включая этот агент

## Источник
- `agents/infographic-builder.md`
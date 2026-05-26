---
type: agent
name: infographic-builder
sources: ["agents/infographic-builder.md"]
updated: 2026-05-26
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-cache", "visual-generation"]
tags: ["codex", "infographic", "image-gen", "png", "cache"]
---

# Infographic Builder — генератор инфографики

## Что делает
Генерирует один PNG-файл инфографики для конкретного слота через codex image_gen. Использует хэш-кэш, чтобы не вызывать codex повторно для одинаковых данных.

## Когда вызывать / в каком этапе
Этот агент — вспомогательный. Его **нельзя вызывать напрямую**. Он диспатчится родительским агентом `visual-curator` на этапе **07d (Visuals)**. Один вызов = один слот инфографики.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `<slot_name>` — имя слота, например `kpi-clients`
- `<chart_type>` — тип графика: `number`, `bar`, `line`, `donut`
- `<data_json>` — JSON-строка с данными для визуализации

**Выход:**
- PNG-файл: `<project>/07d_VISUALS/infographics/<slot_name>.png`
- Запись атрибуции в `07d_VISUALS/prompts.yaml` (если источник OpenDesign)
- Обновление кэша в `.cache/<hash>.png`

**Процесс:**
1. Вычисляет хэш-ключ по `(hint, chart_type, brand_accent, niche)`.
2. При попадании в кэш — копирует файл и завершается без вызова codex.
3. При промахе — запускает `codex-generate-infographic.sh`.
4. После генерации — сохраняет результат в кэш.

**Обработка ошибок:**
- Codex упал после retry → SVG-плейсхолдер.
- Невалидный `data_json` → заглушка с типовыми данными + предупреждение в STATE.yaml.

## Связанные концепты
- [[visual-curator]] — родительский агент, который диспатчит этот helper
- [[visual-generation]] — скилл, содержащий bash-скрипт `codex-generate-infographic.sh`
- [[visual-cache]] — механизм хэш-кэширования сгенерированных PNG

## Источник
- `agents/infographic-builder.md`
---
type: agent
name: infographic-builder
sources: ["agents/infographic-builder.md"]
updated: 2026-05-20
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation"]
tags: ["infographic", "codex", "image-gen", "visuals", "07d"]
---

# infographic-builder — генератор инфографики

## Что делает

Генерирует один PNG-файл инфографики (числовые показатели, бар-чарты, линейные и donut-графики) через codex image_gen. Работает только по одному слоту за раз и использует хэш-кэш, чтобы не тратить API-вызовы повторно для одинаковых данных.

## Когда вызывать / в каком этапе

**Этап 07d** — генерация визуальных элементов. Агент является вспомогательным (helper) и **не вызывается напрямую** — его диспатчит только родительский агент [[visual-curator]]. Самостоятельный запуск не предусмотрен.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — путь к папке проекта
- `<slot_name>` — идентификатор слота, например `kpi-clients`
- `<chart_type>` — тип чарта: `number`, `bar`, `line`, `donut`
- `<data_json>` — JSON-строка со спецификацией данных

**Выход:**
- `<project>/07d_VISUALS/infographics/<slot_name>.png` — готовый PNG

**Сопутствующие артефакты:**
- `.cache/<hash>.png` — копия в кэше для повторного использования
- `07d_VISUALS/prompts.yaml` — атрибуция (если источник OpenDesign)
- `STATE.yaml` — предупреждение при невалидном `data_json`

## Процесс работы

1. Вычисляется ключ кэша по комбинации `hint + chart_type + brand_accent + niche`.
2. **Cache hit** → файл копируется из `.cache/`, генерация пропускается.
3. **Cache miss** → запускается `codex-generate-infographic.sh` с параметрами слота.
4. Успешный PNG сохраняется в кэш.
5. Если источник промпта — OpenDesign 90 JSON, фиксируется атрибуция.

**Fallback-логика:**
- codex упал после повторных попыток → создаётся SVG-placeholder.
- Невалидный `data_json` → используются обобщённые данные-заглушки, предупреждение идёт в `STATE.yaml`.

## Связанные концепты

- [[visual-curator]] — родительский агент, единственный, кто вызывает `infographic-builder`
- [[visual-generation]] — скилл, содержащий скрипты и логику prompt-picker waterfall
- [[icon-generator]] — соседний helper-агент для иконок (тот же этап 07d)

## Источник

- `agents/infographic-builder.md`
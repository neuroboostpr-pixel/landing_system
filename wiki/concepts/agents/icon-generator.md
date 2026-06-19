---
slug: icon-generator
type: agent
name: "Генератор иконки"
stage: "07d"
tags: [icons, visual-generation, codex, image-gen, cache]
triggers: []
inputs: [07d-visuals]
outputs: [07d-visuals]
gates: []
pre_reqs: [05-dizayn-sistema, 07b-composed]
related: [visual-curator, visual-generation, 07d-visuals, photo-curator]
sources: ["agents/icon-generator.md"]
updated: 2026-06-19
confidence: {stage: low, triggers: low}
---

# Генератор иконки

## Что делает
Вспомогательный агент — генерирует ровно один файл PNG-иконки для заданного слота через codex image_gen. Работает с хеш-кешем: если иконка с теми же параметрами (hint + style + brand-color + niche) уже генерировалась, берёт результат из `.cache/` без повторного вызова codex. При сбое API падает на SVG-заглушку. Все результаты размещаются в `07d_VISUALS/icons/`.

## Когда вызывается
Диспатчится родительским агентом `visual-curator` в рамках этапа 07d (генерация визуалов). Прямой вызов пользователем не предусмотрен. Вызывается по одному разу на каждый незакешированный слот иконки в `composed.html`.

## Вход → выход
**Вход:** абсолютный путь к папке проекта (`project_dir`), имя слота (`slot_name`, например `feature-1-icon`), необязательный hint (например `shield`). Требуются утверждённые этапы 05 (design-system с токенами цвета) и 07b (существующий `composed.html`).

**Выход:** `<project>/07d_VISUALS/icons/<slot_name>.png` — готовая PNG-иконка, вырезанная из фона. Копия сохраняется в `.cache/<hash>.png` для ускорения повторных прогонов.

## Failure modes
- **codex API недоступен или завис** — агент делает retry, при повторном сбое пишет SVG-заглушку через `svg-placeholder.py`.
- **Chroma-key fringe (артефакты зелёного экрана)** — retry с флагом `--edge-contract 1` или альтернативным цветом `#ff00ff`.
- **Кеш-файл повреждён / меньше 1 КБ** — кеш игнорируется, запускается полная генерация.
- **Несовпадение стиля с brand-kit** — hint или style-параметр не передан от `visual-curator`; результат не соответствует палитре темы.
- **Невалидный `slot_name`** — файл создаётся, но в `composed.html` placeholder не заменяется (ответственность `visual-curator`).

## Related
- [[visual-curator]] — родительский агент, диспатчит `icon-generator` по списку слотов
- [[visual-generation]] — скилл с bash-скриптами (`codex-generate-icon.sh`, `visual-cache.py`)
- [[07d-visuals]] — этап, в котором происходит генерация иконок и инфографики
- [[photo-curator]] — аналогичный паттерн helper-агента из PR-B (photo pipeline)
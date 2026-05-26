---
slug: icon-generator
type: agent
name: "Генератор иконок"
stage: "07d"
tags: [icons, codex, image-gen, visuals, cache, helper]
triggers: []
inputs: ["project_dir", "slot_name", "hint"]
outputs: ["07d_VISUALS/icons/<slot_name>.png"]
gates: []
pre_reqs: []
related: ["visual-curator", "landing-visuals"]
sources: ["agents/icon-generator.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Генератор иконок

## Что делает
Вспомогательный агент: генерирует один PNG-файл иконки для заданного слота через codex image_gen. Работает в рамках этапа 07d и всегда запускается из-под родительского агента `visual-curator` — самостоятельный прямой вызов не предусмотрен. Перед генерацией проверяет хэш-кэш: если идентичный запрос уже выполнялся, копирует готовый файл без обращения к codex. Stage Execution Protocol контролирует родительский агент.

## Когда вызывается
Запускается агентом `visual-curator` на этапе 07d для каждого иконочного слота, у которого нет кэшированного результата. Условие вызова — слот типа `*-icon` присутствует в `composed.html`, а файл иконки ещё не сгенерирован или истёк кэш.

## Вход → выход
**Вход:** абсолютный путь к директории проекта (`project_dir`), имя слота (`slot_name`, например `feature-1-icon`), необязательная подсказка для промпта (`hint`, например `shield`).

**Выход:** файл `<project>/07d_VISUALS/icons/<slot_name>.png`. Параллельно копия сохраняется в `.cache/<hash>.png` для повторного использования.

## Failure modes
- **codex API недоступен или упал после retry** — агент откатывается к SVG-placeholder через `skills/photo-curation/scripts/svg-placeholder.py` (механизм из PR-B).
- **Chroma-key fringe-артефакты** — повторный запуск с флагом `--edge-contract 1` или альтернативным ключом `#ff00ff`.
- **Кэш-попадание с битым файлом** — если `.cache/<hash>.png` существует, но размер < 1KB, файл считается невалидным и генерация запускается заново.
- **Некорректный `hint`** — агент использует waterfall: сначала ищет промпт в `icons.csv`, при отсутствии — переходит к generic-шаблону.
- **Прямой вызов без `visual-curator`** — отсутствует контекст stage-протокола; результат может оказаться не синхронизирован с `composed.html`.

## Related
- [[visual-curator]] — родительский агент, диспатчит `icon-generator` для каждого слота этапа 07d
- [[landing-visuals]] — slash-команда, запускающая весь пайплайн визуальной генерации этапа 07d
---
type: agent
name: icon-generator
sources: ["agents/icon-generator.md"]
updated: 2026-05-20
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation", "photo-curation"]
tags: ["icons", "codex", "image-gen", "07d", "helper-agent"]
---

# Icon Generator — генератор иконок через codex

## Что делает

Генерирует **один** PNG-файл иконки для указанного слота лендинга. Использует codex image_gen с умным кэшированием: если иконка с такими же параметрами уже генерировалась — берёт из кэша без повторного обращения к API.

## Когда вызывать / в каком этапе

Используется на этапе **07d (Visuals)**. Это вспомогательный агент — его вызывает только [[visual-curator]], никогда напрямую пользователем. Протокол выполнения этапа контролирует родительский агент.

## Что на вход / на выход

**Вход:**
- `<project_dir>` — абсолютный путь к папке проекта
- `<slot_name>` — имя слота, например `feature-1-icon`
- `<hint>` — опциональная подсказка для промпта, например `shield`

**Выход:**
- `<project>/07d_VISUALS/icons/<slot_name>.png`

**Процесс:**
1. Вычисляет хэш-ключ кэша по параметрам: hint + icon_style + brand_color + niche через `visual-cache.py`.
2. Если кэш-хит (`.cache/<hash>.png` существует, размер ≥ 1 КБ) — копирует файл в `icons/<slot>.png` и завершает работу.
3. Если кэш-мисс — запускает `codex-generate-icon.sh` для генерации нового PNG.
4. После успешной генерации сохраняет результат в кэш для будущих прогонов.

**При ошибке:**
- Если codex упал после повтора — создаёт SVG-заглушку через `svg-placeholder.py` (из PR-B).
- При проблемах chroma-key fringe — повтор с `--edge-contract 1` или альтернативным цветом `#ff00ff`.

**Доступные инструменты агента:** Bash, Read.

## Связанные концепты

- [[visual-curator]] — родительский агент-оркестратор этапа 07d, который диспатчит icon-generator для каждого иконочного слота
- [[visual-generation]] — скилл, содержащий скрипты `visual-cache.py` и `codex-generate-icon.sh`
- [[photo-curation]] — скилл, предоставляющий `svg-placeholder.py` как fallback при ошибке codex
- [[infographic-builder]] — соседний helper-агент, генерирует инфографику (тот же этап 07d)

## Источник

- `agents/icon-generator.md`
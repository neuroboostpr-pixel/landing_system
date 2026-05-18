---
type: agent
name: icon-generator
sources: ["agents/icon-generator.md"]
updated: 2026-05-15
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation", "photo-curation"]
tags: ["visuals", "icons", "codex", "image-gen", "cache"]
---

# icon-generator — генератор одного PNG-иконки

## Что делает

Генерирует **один** файл иконки в формате PNG для конкретного слота лендинга. Работает через codex image_gen с умным кэшированием: если иконка с такими же параметрами уже была создана ранее — берёт из кэша без повторного запроса к API.

## Когда вызывать / в каком этапе

Вызывается агентом [[visual-curator]] на этапе **07d** (Visual Generation). Не вызывается напрямую пользователем — только как субагент в рамках команды `/landing-visuals`.

## Что на вход / на выход

**Входные данные:**
- `project_dir` — абсолютный путь к папке проекта
- `slot_name` — имя слота, например `feature-1-icon`
- `hint` (опционально) — текстовая подсказка для генерации, например `shield`

**Процесс:**
1. Вычисляет хэш-ключ кэша по параметрам: `hint`, `icon_style`, `brand-color`, `niche` через скрипт `visual-cache.py`.
2. Если файл с таким хэшем уже есть в `.cache/` (размер ≥ 1 КБ) — копирует его в целевую папку и завершает работу.
3. Если кэш-промах — запускает `codex-generate-icon.sh` для генерации.
4. После успешной генерации сохраняет результат в `.cache/<hash>.png` для будущих прогонов.

**Выходной артефакт:**
- `<project>/07d_VISUALS/icons/<slot_name>.png`

**При ошибках:**
- Если codex падает после повтора — создаёт SVG-заглушку через `svg-placeholder.py` (из PR-B).
- При проблемах с цветовой рамкой (chroma-key fringe) — повторяет с флагом `--edge-contract 1`.

## Связанные концепты

- [[visual-curator]] — оркестратор этапа 07d, который диспатчит icon-generator для каждого слота
- [[visual-generation]] — скилл и набор скриптов (visual-cache.py, codex-generate-icon.sh), на которые опирается агент
- [[photo-curation]] — предоставляет svg-placeholder.py как fallback при ошибках генерации
- [[infographic-builder]] — аналогичный агент, но для инфографики (а не иконок)

## Источник

- `agents/icon-generator.md`
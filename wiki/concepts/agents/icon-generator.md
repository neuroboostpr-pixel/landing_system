---
type: agent
name: icon-generator
sources: ["agents/icon-generator.md"]
updated: 2026-05-26
triggers: []
stage: "07d"
uses: ["visual-curator", "visual-generation", "photo-curation"]
tags: ["icons", "image-gen", "codex", "cache", "visuals"]
---

# Icon Generator — генератор одного PNG-иконки

## Что делает
Генерирует один PNG-файл иконки для заданного слота через codex image_gen. Использует хеш-кэш, чтобы не тратить API-вызовы на уже созданные иконки.

## Когда вызывать / в каком этапе
Вызывается **только как вспомогательный агент** из [[visual-curator]] на этапе **07d (VISUALS)**. Напрямую пользователем не вызывается. За соблюдение Stage Execution Protocol отвечает родительский агент [[visual-curator]].

## Что на вход / на выход

**Вход:**
- `<project_dir>` — абсолютный путь к папке проекта
- `<slot_name>` — имя слота, например `feature-1-icon`
- `<hint>` — необязательная текстовая подсказка для промпта, например `shield`

**Выход:**
- Файл `<project>/07d_VISUALS/icons/<slot_name>.png`

## Процесс работы

1. **Кэш-проверка** — вычисляет ключ через `visual-cache.py` (на основе hint + icon_style + brand_color + niche). Если `.cache/<hash>.png` уже существует и весит ≥ 1 КБ — просто копирует его в целевую папку и завершает работу без обращения к codex.

2. **Генерация** — если кэша нет, запускает `codex-generate-icon.sh` с параметрами проекта, слота и подсказки.

3. **Сохранение в кэш** — после успешной генерации копирует результат в `.cache/<hash>.png` для будущих запусков.

4. **Fallback** — если codex вернул ошибку после повторной попытки, агент создаёт SVG-заглушку через `svg-placeholder.py` (из пайплайна PR-B). При проблемах с chroma-key каймой — повторяет попытку с флагом `--edge-contract 1` или альтернативной хромой `#ff00ff`.

**Доступные инструменты:** Bash, Read.

## Связанные концепты
- [[visual-curator]] — родительский агент, который диспатчит icon-generator для каждого слота в этапе 07d
- [[visual-generation]] — скилл, содержащий скрипты `visual-cache.py` и `codex-generate-icon.sh`
- [[photo-curation]] — скилл, предоставляющий `svg-placeholder.py` для fallback-заглушек

## Источник
- `agents/icon-generator.md`
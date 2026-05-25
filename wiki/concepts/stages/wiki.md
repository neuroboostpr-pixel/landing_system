---
type: block
name: project-wiki-folder
sources: ["template/wiki/README.md"]
updated: 2026-05-25
triggers: []
stage: ""
uses: ["landing-orchestrator", "gate-check"]
tags: ["wiki", "auto-generated", "project-graph", "template"]
---

# Project Wiki Folder — папка граф-структуры проекта

## Что делает
Хранит автоматически генерируемый граф текущего состояния лендинг-проекта: этапы, блоки, бренд-кит и карту фото-слотов. Файлы создаются компайлером и **не редактируются вручную** — при каждом запуске перезаписываются.

## Когда вызывать / в каком этапе
Папка наполняется автоматически в двух случаях:
1. После успешного закрытия любого этапа командой `gate-check.sh exit 0`.
2. Вручную через команду:
   ```bash
   python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>
   ```
Никаких ручных триггеров slash-командой не предусмотрено — это сервисный артефакт pipeline.

## Что на вход / на выход

**Вход:**
- Текущее состояние `.landing-state.yaml` проекта.
- Артефакты завершённых этапов (design-tokens, выбранные блоки, фото-слоты, бренд-кит).

**Выход (файлы папки `wiki/`):**

| Файл | Содержимое |
|---|---|
| `index.md` | Главный индекс — читать первым |
| `log.md` | Хронология обновлений wiki |
| `concepts/stage-current.md` | Текущий активный этап pipeline |
| `concepts/blocks.md` | Выбранные блоки из block-library |
| `concepts/brand.md` | Цвета и шрифты (из brand-kit) |
| `concepts/photos.md` | Карта фото-слотов проекта |

## Связанные концепты
- [[landing-orchestrator]] — основной агент pipeline, закрытие этапов которого запускает обновление wiki
- [[gate-check]] — скрипт проверки этапов; его `exit 0` триггерит автоматическую перезапись

## Источник
- `template/wiki/README.md`
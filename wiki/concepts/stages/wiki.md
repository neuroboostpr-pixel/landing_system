---
type: block
name: project-wiki
sources: ["template/wiki/README.md"]
updated: 2026-05-26
triggers: []
stage: ""
uses: ["landing-orchestrator", "gate-check", "wiki-compile"]
tags: ["wiki", "graph", "auto-generated", "project-state"]
---

# Project Wiki — граф состояния проекта-лендинга

## Что делает
Папка `wiki/` внутри каждого проекта-лендинга — это живой граф: автоматически собираемый срез текущего состояния проекта (этап, блоки, бренд, фото). Не нужно открывать десятки файлов — вся ключевая информация собрана в одном месте.

## Когда вызывать / в каком этапе
Папка обновляется автоматически в двух случаях:
1. После успешного прохождения гейта этапа (`gate-check.sh exit 0`) — orchestrator запускает пересборку.
2. Вручную — командой `python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>` в любой момент.

Редактировать файлы внутри `wiki/` вручную запрещено — компайлер перезапишет изменения.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` текущего проекта (этапы, флаги, сегменты)
- Артефакты pipeline: `brand-kit.md`, `selections.yaml` блоков, `photo-board` слоты

**Выход:**
- `wiki/index.md` — главный индекс проекта (читать первым)
- `wiki/log.md` — хронология обновлений по этапам
- `wiki/concepts/stage-current.md` — текущий активный этап
- `wiki/concepts/blocks.md` — выбранные wireframe-блоки
- `wiki/concepts/brand.md` — цвета и шрифты из бренд-кита
- `wiki/concepts/photos.md` — карта фото-слотов (слот → файл)

## Связанные концепты
- [[landing-orchestrator]] — триггерит обновление wiki после закрытия каждого этапа
- [[gate-check]] — при `exit 0` запускает пересборку wiki
- [[wiki-compile]] — Python-скрипт `scripts/wiki/compile.py`, основной движок сборки

## Источник
- `template/wiki/README.md`
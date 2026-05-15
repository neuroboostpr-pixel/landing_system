---
type: rule
name: project-wiki-folder
sources: ["template/wiki/README.md"]
updated: 2026-05-15
triggers: []
stage: "все этапы (обновляется после каждого gate-check)"
uses: ["landing-orchestrator", "lifecycle-keeper"]
tags: ["wiki", "project-graph", "auto-generated", "template"]
---

# project-wiki-folder — граф структуры проекта (папка wiki/)

## Что делает
Папка `wiki/` внутри каждого лендинг-проекта хранит авто-сгенерированный граф состояния проекта: текущий этап, выбранные блоки, бренд-цвета и карту фото-слотов. Не редактируется вручную — содержимое перезаписывается компайлером после каждого закрытого этапа.

## Когда вызывать / в каком этапе
Папка существует во всех проектах с самого начала (часть `template/`). Наполняется автоматически:
- после каждого `gate-check.sh exit 0` (закрытие этапа pipeline),
- вручную командой `python -m scripts.wiki.compile --source-mode=project-graph --project=<slug>`.

Никакой ручной команды для вызова нет — это фоновый артефакт оркестратора.

## Что на вход / на выход

**Вход:**
- Закрытый gate-check этапа (сигнал от `gate-check.sh`)
- Данные проекта: `.landing-state.yaml`, артефакты этапов (brand-kit, selections.yaml, prototype.yaml и т.д.)

**Выход (файлы внутри `wiki/`):**
- `index.md` — главный индекс проекта, читать первым
- `log.md` — хронология обновлений по этапам
- `concepts/stage-current.md` — текущий активный этап
- `concepts/blocks.md` — выбранные wireframe-блоки
- `concepts/brand.md` — цвета и шрифты бренда
- `concepts/photos.md` — карта фото-слотов и их статус

## Связанные концепты
- [[landing-orchestrator]] — главный оркестратор, закрывает gate-check и инициирует обновление wiki
- [[lifecycle-keeper]] — управляет снапшотами/версиями; wiki фиксирует состояние на момент каждой версии
- [[landing-status]] — читает данные состояния, отчасти перекрывается с `wiki/index.md`

## Источник
- `template/wiki/README.md`
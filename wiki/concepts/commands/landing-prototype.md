---
type: command
name: landing-prototype
sources: ["commands/landing-prototype.md"]
updated: 2026-05-25
triggers:
  - "импортировать прототип"
  - "загрузить прототип лендинга"
  - "парсить PDF прототипа"
  - "начать этап 07 прототип"
uses:
  - prototype-importer
  - landing-wireframe
  - landing-go
  - landing-orchestrator
tags:
  - stage-07
  - prototype
  - import
---

# /landing-prototype — Импорт пользовательского прототипа

## Что делает
Берёт файл прототипа (PDF или Markdown), который клиент положил в папку проекта, и превращает его в структурированные артефакты `prototype.md` и `prototype.yaml`, готовые для дальнейших этапов системы.

## Когда вызывать / в каком этапе
Этап **07_ПРОТОТИП**. Вызывается после того, как в папке `07_ПРОТОТИП/source/` появился файл `prototype.pdf` или `prototype.md`. Обычно запускается автоматически через `/landing-go`, но можно вызвать вручную этой командой. Является первым шагом цепочки: prototype → wireframe → compose.

## Что на вход / на выход

**Вход:**
- Текущая директория — папка проекта-лендинга (должны быть `00_БРИФ/brief.md` или `.landing-state.yaml`)
- Файл `07_ПРОТОТИП/source/prototype.pdf` **или** `07_ПРОТОТИП/source/prototype.md`

**Выход:**
- `07_ПРОТОТИП/prototype.md` — нормализованное текстовое описание прототипа
- `07_ПРОТОТИП/prototype.yaml` — машино-читаемая структура блоков
- `07_ПРОТОТИП/import-log.md` — лог импорта с деталями обработки

**Побочный эффект:** обновляет `.landing-state.yaml` через `scripts/gate-check.sh`; после успеха предлагает запустить `/landing-wireframe`.

## Связанные концепты
- [[prototype-importer]] — агент, который выполняет фактический разбор и нормализацию прототипа
- [[landing-wireframe]] — следующий этап: создаёт интерактивный wireframe на основе `prototype.yaml`
- [[landing-go]] — главная точка входа, вызывает этот этап автоматически в нужной последовательности
- [[landing-orchestrator]] — enforce'ит порядок этапов и не даёт пропустить шаги

## Источник
- `commands/landing-prototype.md`
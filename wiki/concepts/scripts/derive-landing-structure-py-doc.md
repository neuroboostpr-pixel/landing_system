---
type: unknown
name: derive-landing-structure
sources: ["scripts/derive-landing-structure.py"]
updated: 2026-05-18
triggers: []
stage: "07/08"
uses: ["prototype-importer", "wp-builder", "niche-analyst", "landing-go"]
tags: ["script", "python", "prototype-first", "bridge", "pr-d"]
---

# derive-landing-structure — мост прототип → структура сборки

## Что делает

Скрипт читает `07_ПРОТОТИП/prototype.yaml` и автоматически генерирует файл `01a_АНАЛИЗ_НИШИ/landing-structure.md` — карту блоков лендинга, которую затем использует `wp-builder` для генерации PHP-шаблонов. Нужен в prototype-first потоке, когда этап анализа ниши (01a) пропускается.

## Когда вызывать / в каком этапе

Запускается автоматически в рамках PR-D workflow (`/landing-go`) между этапом **07 (Прототип)** и **08 (Код)**. Актуален только при prototype-first подходе — когда пользователь начинает с готового прототипа, минуя стандартный этап 01a niche-analysis.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машино-читаемый прототип, сгенерированный `prototype-importer`

**Выход:**
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — файл со списком блоков лендинга, нужный `wp-builder` для генерации `template-parts/*.php`

## Связанные концепты

- [[prototype-importer]] — создаёт `prototype.yaml`, который является входом для этого скрипта
- [[wp-builder]] — читает `landing-structure.md` на этапе 08 для генерации PHP-шаблонов
- [[niche-analyst]] — в стандартном потоке именно он создаёт `landing-structure.md`; этот скрипт заменяет его в prototype-first режиме
- [[landing-go]] — главная команда PR-D, в чьём оркестрируемом потоке вызывается скрипт

## Источник

- `scripts/derive-landing-structure.py`
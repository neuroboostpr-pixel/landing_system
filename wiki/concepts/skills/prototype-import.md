---
type: skill
name: prototype-import
sources: ["skills/prototype-import/SKILL.md"]
updated: 2026-05-15
triggers: ["импортировать прототип", "загрузить прототип", "распарсить PDF лендинга", "/landing-prototype"]
stage: "07"
uses: ["prototype-importer", "landing-prototype", "landing-orchestrator"]
tags: ["prototype", "pdf", "yaml", "stage-07", "import"]
---

# prototype-import — Импорт прототипа лендинга

## Что делает
Принимает пользовательский прототип в формате PDF или Markdown, парсит его и преобразует в два нормализованных файла: читаемый `prototype.md` и машиночитаемый `prototype.yaml`. Это точка входа в производственный цикл лендинга — без утверждённого прототипа дальнейшие этапы не запускаются.

## Когда вызывать / в каком этапе
Этап **07 (Прототип)**. Активируется командой `/landing-prototype` или агентом [[prototype-importer]]. Запускать после того, как пользователь положил файл (`prototype.pdf` или `prototype.md`) в папку `<project>/07_ПРОТОТИП/source/`. Должен выполняться до [[landing-wireframe]] (этап 07a).

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` — скан или экспорт из Figma/Notion/Word
- или `<project>/07_ПРОТОТИП/source/prototype.md` — уже структурированный текстовый прототип

**Процесс (скрипты):**
- `scripts/extract-pdf-text.py` — извлекает текст из PDF, при необходимости использует OCR через `anthropic-skills:pdf`
- `scripts/md-to-yaml.py` — конвертирует структурированный MD в YAML
- `scripts/validate-prototype.py` — проверяет YAML по схеме

**Выход:**
- `07_ПРОТОТИП/prototype.md` — нормализованный человекочитаемый прототип
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемая структура для последующих агентов
- `07_ПРОТОТИП/import-log.md` — лог импорта с замечаниями и допущениями

**Схема YAML (кратко):**
- `project`: slug, niche (`services|b2c|local`), source_file
- `blocks[]`: position (уникальный int), type (`hero|features|...`), headline, subhead, cta, slots, items, mobile_notes

## Связанные концепты
- [[prototype-importer]] — агент, который выполняет этот скилл
- [[landing-prototype]] — slash-команда, запускающая импорт
- [[landing-wireframe]] — следующий этап (07a), потребляет `prototype.yaml`
- [[landing-orchestrator]] — мастер-оркестратор, вызывает этот скилл в рамках `/landing-go`
- [[block-composition]] — этап 07b, также зависит от `prototype.yaml`

## Источник
- `skills/prototype-import/SKILL.md`
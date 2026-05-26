---
type: skill
name: prototype-import
sources: ["skills/prototype-import/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "07"
uses: ["prototype-importer", "landing-prototype"]
tags: ["prototype", "import", "pdf", "yaml", "stage-07"]
---

# Prototype Import — Импорт прототипа лендинга

## Что делает
Принимает файл прототипа лендинга (PDF или Markdown), разбирает его структуру и сохраняет в два артефакта: читаемый `prototype.md` для человека и машинный `prototype.yaml` для дальнейшей автоматической обработки.

## Когда вызывать / в каком этапе
Запускается на **этапе 07** командой `/landing-prototype`. Перед запуском пользователь должен положить файл `prototype.pdf` или `prototype.md` в папку `<project>/07_ПРОТОТИП/source/`. Команда вызывает агента `prototype-importer`, который и применяет этот скилл.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/source/prototype.pdf` — PDF-прототип (поддерживается OCR-fallback через `anthropic-skills:pdf`)
- или `<project>/07_ПРОТОТИП/source/prototype.md` — уже структурированный Markdown

**Выход:**
- `prototype.md` — нормализованное человекочитаемое описание структуры лендинга
- `prototype.yaml` — машинный файл со схемой блоков для последующих этапов (wireframe, compose)
- `import-log.md` — лог импорта с замечаниями и предупреждениями

**Схема `prototype.yaml`:**
- `project`: slug проекта, ниша (`services` | `b2c` | `local`), имя исходного файла
- `blocks[]`: список блоков с полями `position` (уникальный номер), `type` (`hero`, `features` и др.), `headline`, `subhead`, `cta`, `slots`, `items`, `mobile_notes`

**Скрипты:**
- `scripts/extract-pdf-text.py` — извлечение текста из PDF
- `scripts/md-to-yaml.py` — конвертация MD → YAML
- `scripts/validate-prototype.py` — валидация схемы YAML

## Связанные концепты
- [[prototype-importer]] — агент, который оркеструет вызов скриптов этого скилла
- [[landing-prototype]] — slash-команда, запускающая импорт прототипа
- [[landing-wireframe]] — следующий этап: строит интерактивный wireframe.html на основе `prototype.yaml`
- [[landing-compose]] — использует `prototype.yaml` для сборки `composed.html`

## Источник
- `skills/prototype-import/SKILL.md`
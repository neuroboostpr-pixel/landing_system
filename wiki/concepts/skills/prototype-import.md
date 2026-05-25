---
type: skill
name: prototype-import
sources: ["skills/prototype-import/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "07"
uses: ["prototype-importer", "landing-prototype"]
tags: ["prototype", "import", "pdf", "yaml", "parse"]
---

# Prototype Import — импорт прототипа лендинга

## Что делает
Принимает пользовательский прототип в формате PDF или Markdown, извлекает структуру блоков и сохраняет два артефакта: человекочитаемый `prototype.md` и машинный `prototype.yaml`. Это стартовая точка всего pipeline сборки лендинга.

## Когда вызывать / в каком этапе
Этап **07 — ПРОТОТИП**. Вызывается командой `/landing-prototype`, которая запускает агента `prototype-importer`. Перед запуском пользователь должен положить файл (`prototype.pdf` или `prototype.md`) в папку `<project>/07_ПРОТОТИП/source/`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/source/prototype.pdf` — отсканированный или цифровой прототип
- `07_ПРОТОТИП/source/prototype.md` — структурированный Markdown-прототип (альтернатива PDF)

**Выход:**
- `prototype.md` — нормализованный человекочитаемый прототип
- `prototype.yaml` — машинная версия по схеме (`project` + `blocks[]`)
- `import-log.md` — лог импорта (ошибки, предупреждения, статистика)

**Схема `prototype.yaml`:**
- `project`: slug, niche (`services` | `b2c` | `local`), source_file
- `blocks[]`: position (уникальный int), type (`hero` | `features` | ...), headline, subhead, cta, slots, items, mobile_notes

## Процесс (внутри скилла)
1. `scripts/extract-pdf-text.py` — извлечение текста из PDF с OCR-fallback через `anthropic-skills:pdf`.
2. `scripts/md-to-yaml.py` — конвертация структурированного MD в YAML.
3. `scripts/validate-prototype.py` — валидация результирующего YAML по схеме.

## Связанные концепты
- [[prototype-importer]] — агент, который непосредственно выполняет импорт (вызывается скиллом)
- [[landing-prototype]] — slash-команда, запускающая этот скилл
- [[landing-wireframe]] — следующий этап после успешного импорта: строит интерактивный wireframe из `prototype.yaml`
- [[landing-compose]] — этап 07b, использует `prototype.yaml` как источник контента для composed.html

## Источник
- `skills/prototype-import/SKILL.md`
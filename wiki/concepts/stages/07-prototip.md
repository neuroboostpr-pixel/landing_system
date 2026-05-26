---
type: stage
name: 07-prototype
sources: ["template/07_ПРОТОТИП/README.md"]
updated: 2026-05-26
triggers: []
stage: "07"
uses: ["landing-prototype", "ux-composer"]
tags: ["prototype", "stage", "input", "source-of-truth"]
---

# 07 Прототип — Источник правды клиента

## Что делает
Хранит и нормализует прототип лендинга от клиента или маркетолога: принимает PDF или Markdown, преобразует в структурированные форматы для дальнейшей работы агентов.

## Когда вызывать / в каком этапе
Этап 07 — перед wireframe и compose. Активируется командой `/landing-prototype` после того как клиент положил исходный прототип (`prototype.pdf` или `prototype.md`) в папку `source/`.

## Что на вход / на выход

**Вход:**
- `source/prototype.pdf` или `source/prototype.md` — исходник от клиента/маркетолога

**Выход:**
- `prototype.md` — человеко-читаемая нормализация прототипа (правки вносятся вручную именно сюда)
- `prototype.yaml` — машинно-читаемая версия для агента `ux-composer` (перегенерируется автоматически из `prototype.md`)
- `import-log.md` — лог: что агент понял, какие задавал уточняющие вопросы

## Связанные концепты
- [[landing-prototype]] — slash-команда, запускающая разбор и нормализацию прототипа
- [[ux-composer]] — агент, потребляющий `prototype.yaml` на следующих этапах (wireframe, compose)
- [[landing-wireframe]] — следующий шаг после подтверждения `prototype.md`
- [[landing-compose]] — использует результат этапа при сборке `composed.html`

## Источник
- `template/07_ПРОТОТИП/README.md`
---
type: script
name: generate-blocks
sources: ["scripts/import-blocks/generate-blocks.py", "scripts/import-blocks/generate-blocks.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "landing-import-blocks"]
tags: ["codex", "block-generation", "html", "css", "python"]
---

# generate-blocks.py — генератор HTML/CSS блоков через Codex

## Что делает

Скрипт читает файл `structure.json`, перебирает каждый описанный в нём блок и для каждого вызывает Codex — чтобы тот сгенерировал готовый HTML + CSS. Результат — новые блоки для библиотеки лендингов.

## Когда вызывать / в каком этапе

Запускается при наполнении или обновлении библиотеки блоков (`block-library/`). Обычно запускается вручную разработчиком системы или через команду `/landing-import-blocks`, когда нужно добавить новые шаблонные блоки. Не является частью основного 12-этапного пайплайна производства лендинга — это инструмент обслуживания самой системы.

## Что на вход / на выход

**Вход:**
- `structure.json` — описание блоков, которые нужно сгенерировать (название, тип, параметры)
- Доступ к Codex API для генерации кода

**Выход:**
- HTML и CSS файлы для каждого блока
- Готовые блоки пополняют `block-library/`

## Связанные концепты

- [[block-library-management]] — скилл управления библиотекой блоков, частью которой являются сгенерированные блоки
- [[landing-import-blocks]] — команда, вероятно использующая этот скрипт для импорта новых блоков

## Источник

- `scripts/import-blocks/generate-blocks.py`
- `scripts/import-blocks/generate-blocks.py.doc.md`
---
type: rule
name: migrate-blocks-to-wireframe-format
sources: ["scripts/migrate-blocks-to-wireframe-format.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wireframe-rendering", "block-library-management"]
tags: ["migration", "script", "block-library", "wireframe"]
---

# migrate-blocks-to-wireframe-format — Миграция блоков в wireframe-формат

## Что делает
Скрипт конвертирует новые блоки из библиотеки (с файлами `index.html` + `styles.css` в корне папки блока) в формат, который ожидает движок `wireframe-rendering`: файлы `assets/template.html` и `assets/template-mobile.html`. Старые файлы при этом не удаляются — создаётся параллельная структура `assets/`.

## Когда вызывать / в каком этапе
Запускается вручную, когда в `block-library/` появились новые блоки в «новом» формате (index.html + styles.css в корне), а wireframe-рендерер их не видит. Обычно нужен после добавления batch-блоков или импорта из внешних источников. Не является частью автоматического pipeline — вызывается разработчиком напрямую через `python3 scripts/migrate-blocks-to-wireframe-format.py`.

## Что на вход / на выход

**Вход:**
- Блоки в `block-library/` с файловой структурой:
  ```
  block-library/<category>/<block-name>/index.html
  block-library/<category>/<block-name>/styles.css
  ```

**Выход:**
- Параллельная `assets/`-структура рядом с существующими файлами:
  ```
  block-library/<category>/<block-name>/assets/template.html
  block-library/<category>/<block-name>/assets/template-mobile.html
  ```
- Исходные `index.html` и `styles.css` остаются нетронутыми.

## Связанные концепты
- [[wireframe-rendering]] — потребитель формата `assets/template.html`; именно под этот скилл выполняется миграция
- [[block-library-management]] — управляет структурой и стандартами block-library, в рамках которой работает скрипт

## Источник
- `scripts/migrate-blocks-to-wireframe-format.py`
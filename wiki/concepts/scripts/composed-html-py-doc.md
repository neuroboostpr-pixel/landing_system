Теперь у меня достаточно контекста. Формирую wiki-страницу:

---
type: rule
name: composed-html-parser
sources: ["scripts/wiki/parsers/composed_html.py", "scripts/wiki/parsers/composed_html.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["project-graph-compiler", "07b-composed"]
tags: ["parser", "wiki", "script", "python"]
---

# composed_html — парсер скомпонованного HTML

## Что делает

Читает файл `composed.html` из этапа 07b и вытаскивает из него два типа данных: список блоков страницы (по атрибуту `data-block`) и список локальных ссылок на фотографии (теги `<img>` с относительными src). Результат используется wiki-компилятором для построения карты проекта.

## Когда вызывать / в каком этапе

Вызывается автоматически внутри `project_graph_compiler.py` — не требует ручного запуска. Срабатывает при сборке project-graph wiki (режим `--source-mode=project`), если файл `07b_COMPOSED/composed.html` существует в папке проекта.

## Что на вход / на выход

**Вход:**
- `Path` — абсолютный путь к `composed.html` (обычно `<project>/07b_COMPOSED/composed.html`)

**Выход (словарь):**
- `blocks` — список объектов с полями `block_id`, `tag`, `classes` для каждого элемента с атрибутом `data-block`
- `photo_references` — список относительных путей к изображениям (внешние URL и data-URI исключаются)

Результат передаётся в `_photos_md()` внутри project_graph_compiler, которая генерирует `wiki/concepts/photos.md` для проектной wiki.

## Связанные концепты

- [[07b-composed]] — источник файла `composed.html`, который парсит этот скрипт
- [[block-composer]] — агент, создающий `composed.html` на этапе 07b
- [[photo-curator]] — агент этапа 07c, работающий с фото-слотами, которые парсер помогает обнаружить

## Источник

- `scripts/wiki/parsers/composed_html.py`
- `scripts/wiki/parsers/composed_html.py.doc.md`
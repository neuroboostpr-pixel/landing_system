---
type: unknown
name: preview-py
sources: ["scripts/wiki/preview.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["scripts.wiki.utils", "wiki"]
tags: ["wiki", "script", "python", "html", "preview"]
---

# preview.py — генератор HTML-превью wiki

## Что делает

Читает все wiki-концепты из папки `wiki/concepts/` и рендерит единую HTML-страницу `wiki/preview.html` для быстрого визуального просмотра всей wiki прямо в браузере. Группирует концепты по типу (agent, skill, command, stage, rule, block и т.д.).

## Когда вызывать / в каком этапе

Вызывается **вручную** после сборки wiki, когда нужно глазами просмотреть все концепты. Запускается из корня проекта:

```bash
python -m scripts.wiki.preview
# или с кастомной папкой:
python -m scripts.wiki.preview --wiki path/to/wiki
```

Также может вызываться автоматически из `compile.py` как финальный шаг после `--source-mode=system`. Хук `.githooks/post-commit` запускает пересборку wiki, после чего preview можно обновить.

## Что на вход / на выход

**Вход:**
- `wiki/concepts/*.md` — markdown-файлы концептов с YAML frontmatter (поля: `name`, `type`, тело)
- `scripts/wiki/templates/preview.html.j2` — Jinja2-шаблон страницы
- `scripts/wiki/templates/styles.css` — встроенные стили (инлайнятся в HTML)

**Выход:**
- `wiki/preview.html` — единый HTML-файл, открываемый в браузере. Содержит все концепты, сгруппированные по типу, с заголовком проекта, датой обновления и общим счётчиком концептов. Файл пишется атомарно через `utils.atomic_write`.

**Параметры CLI:**
- `--wiki <dir>` — путь к папке wiki (по умолчанию `wiki/`)

**Ограничение:** тело каждого концепта обрезается до 3000 символов, чтобы HTML не раздувался.

## Связанные концепты

- [[wiki]] — папка, куда пишется `preview.html`
- [[scripts.wiki.utils]] — парсинг frontmatter, атомарная запись файлов

## Источник

- `scripts/wiki/preview.py`
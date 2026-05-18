Теперь у меня достаточно контекста. Составляю wiki-страницу:

---
type: rule
name: tokens-json-parser
sources: ["scripts/wiki/parsers/tokens_json.py", "scripts/wiki/parsers/tokens_json.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["design-system-generator", "project-graph-compiler"]
tags: ["parser", "design-tokens", "wiki", "brand"]
---

# tokens_json.py — Парсер дизайн-токенов

## Что делает

Читает файл `tokens.json` и возвращает его содержимое как Python-словарь. Это входная точка для любого скрипта, которому нужны дизайн-токены проекта: цвета бренда, шрифты, отступы и прочие переменные из этапа 05.

## Когда вызывать / в каком этапе

Парсер не вызывается вручную. Он импортируется `project_graph_compiler.py` (wiki-компайлер) на шаге «токены → brand.md». Запускается автоматически при вызове `python -m scripts.wiki.compile --source-mode=project-graph` — то есть при каждом git-коммите, если проект уже прошёл этап 05 (design-system).

## Что на вход / на выход

**Вход:**
- Путь (`pathlib.Path`) к файлу `04_БРЕНД/tokens.json` конкретного проекта.

**Выход:**
- Python `dict` с полным содержимым `tokens.json`. Типичная структура: ключи `colors` (словарь имя→hex) и `fonts` (словарь роль→font-family).

**Побочный эффект (через компайлер):**
- `project_graph_compiler.py` передаёт результат в `_brand_md()` → пишет `wiki/<project>/concepts/brand.md` с таблицей цветов и шрифтов.

## Связанные концепты

- [[design-system-generator]] — агент этапа 05, который создаёт `tokens.json` в папке `04_БРЕНД/`
- [[design-tokens-generation]] — скилл, описывающий формат и содержимое `tokens.json`
- [[brand-architect]] — агент, который синтезирует `brand-kit.md`, предшествующий `tokens.json`

## Источник

- `scripts/wiki/parsers/tokens_json.py`
- `scripts/wiki/parsers/tokens_json.py.doc.md`
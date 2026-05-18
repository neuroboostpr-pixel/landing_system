---
type: command
name: import-from-url
sources: ["scripts/import-blocks/import-from-url.sh", "scripts/import-blocks/import-from-url.sh.doc.md"]
updated: 2026-05-18
triggers: ["импортировать блоки с сайта", "добавить блоки из URL", "скачать блоки по ссылке", "import-from-url"]
stage: ""
uses: ["block-library-management", "landing-import-blocks", "visual-generation"]
tags: ["script", "bash", "import", "block-library", "codex"]
---

# import-from-url — Импорт блоков с внешнего сайта

## Что делает
Скачивает скриншот страницы по URL, анализирует её через codex, генерирует готовые блоки и кладёт их в общую `block-library/`. Позволяет пополнять библиотеку блоков образцами с реальных сайтов без ручной вёрстки.

## Когда вызывать / в каком этапе
Вызывается вручную в любой момент, когда нужно добавить новые референсные блоки в систему. Обычно используется до начала или параллельно с этапами 03–07, чтобы пополнить пул вариантов для wireframe. Также вызывается командой `/landing-import-blocks`.

Синтаксис:
```bash
bash scripts/import-blocks/import-from-url.sh <url> [niche]
```
- `<url>` — обязательный: адрес страницы-донора
- `[niche]` — опциональный: ниша (например `auto`, `medical`, `realty`) — помогает codex точнее классифицировать блоки

## Что на вход / на выход

**Вход:**
- URL страницы-донора
- (опционально) строка ниши

**Выход:**
- Скриншот страницы (временный)
- Результат анализа codex (структура и тип каждого блока)
- Сгенерированные блоки в `block-library/` — готовы к использованию в `/landing-wireframe` и `/landing-compose`

## Связанные концепты
- [[block-library-management]] — управляет структурой и индексом библиотеки, куда кладёт блоки этот скрипт
- [[landing-import-blocks]] — slash-команда, которая вызывает этот скрипт через интерфейс Claude Code
- [[visual-generation]] — codex также используется в pipeline генерации иконок и инфографики
- [[ux-composer]] — потребляет блоки из `block-library/` при рендере wireframe

## Источник
- `scripts/import-blocks/import-from-url.sh`
- `scripts/import-blocks/import-from-url.sh.doc.md`
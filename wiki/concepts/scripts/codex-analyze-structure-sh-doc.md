---
type: rule
name: codex-analyze-structure
sources: ["scripts/import-blocks/codex-analyze-structure.sh", "scripts/import-blocks/codex-analyze-structure.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "landing-import-blocks"]
tags: ["codex", "vision", "import-blocks", "json", "screenshot"]
---

# codex-analyze-structure.sh

## Что делает
Bash-скрипт, который передаёт скриншот блока в Codex CLI через vision-API и получает обратно JSON-описание структуры блока: секции, элементы, тип компоновки. Используется в пайплайне импорта готовых блоков в библиотеку.

## Когда вызывать / в каком этапе
Вызывается внутри пайплайна `/landing-import-blocks` — когда нужно автоматически распознать структуру нового блока по его скриншоту, прежде чем записать `meta.yaml` в `block-library/`. Не предназначен для прямого ручного вызова маркетологом.

## Что на вход / на выход

**Вход:**
- Путь к PNG/JPG-скриншоту блока (передаётся аргументом или через pipe).
- Опционально — подсказка (prompt) для уточнения контекста анализа.

**Выход:**
- JSON-объект в stdout со структурой блока: предполагаемый тип (`hero`, `features`, `cta` и т.д.), список видимых элементов, схема компоновки (grid / split / stacked / centered).
- При ошибке — ненулевой exit-код и сообщение в stderr.

## Связанные концепты
- [[block-library-management]] — скрипт является частью инфраструктуры пополнения библиотеки блоков
- [[landing-import-blocks]] — слеш-команда, в рамках которой запускается этот скрипт
- [[visual-generation]] — смежный скилл, также использующий Codex CLI image_gen, но для генерации, а не анализа

## Источник
- `scripts/import-blocks/codex-analyze-structure.sh`
- `scripts/import-blocks/codex-analyze-structure.sh.doc.md`
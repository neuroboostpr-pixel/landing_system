---
type: rule
name: pr-o-tests
sources: ["tests/pr-o/README.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-import-blocks", "block-library-management"]
tags: ["tests", "bats", "block-library", "import-blocks"]
---

# Тесты PR-O — инфраструктура импорта блоков

## Что делает
Проверяет корректность работы инфраструктуры импорта новых блоков в библиотеку: парсинг HTML-структуры с лендинга, создание скриншота-референса и idempotent-генерацию (пропуск уже существующих блоков).

## Когда вызывать / в каком этапе
Тесты относятся к утилите `/landing-import-blocks` и скриптам `scripts/import-blocks/`. Запускать при любых изменениях в pipeline импорта блоков: `import-from-url.sh`, промптах анализа структуры (`structure-analysis-prompt.md`) и промптах генерации (`block-generation-prompt.md`).

## Что на вход / на выход

**Вход:**
- Bash-тесты (`*.bats`) в папке `tests/pr-o/`
- Окружение: установленный `bats-core`, `codex` CLI, инструмент для скриншотов (Playwright/Puppeteer)

**Выход:**
- Результат прохождения 3 тест-кейсов (PASS / FAIL):
  - `test_block_generation_skips_existing` — повторный запуск не перезаписывает уже созданный блок
  - `test_screenshot_works` — скриншот референсного URL сохраняется как `reference.png`
  - `test_structure_parse_works` — codex vision корректно разбирает HTML-структуру блока

## Запуск

```bash
# Все bats-тесты группы
bats tests/pr-o/

# Если добавлены pytest-файлы
pytest tests/pr-o/
```

## Связанные концепты
- [[landing-import-blocks]] — слеш-команда, которую тесты покрывают
- [[block-library-management]] — скилл управления библиотекой блоков, куда импортируются новые блоки

## Источник
- `tests/pr-o/README.md`
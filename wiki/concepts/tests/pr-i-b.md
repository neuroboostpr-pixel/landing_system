---
type: unknown
name: pr-i-b
sources: ["tests/pr-i-b/README.md", "docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md"]
updated: 2026-05-18
triggers: []
stage: "10"
uses: ["visual-qa", "landing-qa", "qa-auditor", "gpt5-prompting-engine"]
tags: ["tests", "bats", "visual-qa", "playwright", "codex-vision"]
---

# Тесты PR-I.b — Visual QA (Playwright + codex vision + auto-fix)

## Что делает

Набор bats-тестов, проверяющих скилл `visual-qa`: снятие скриншотов через Playwright, парсинг JSON-отчёта от codex vision и применение CSS-фиксов к HTML-файлу лендинга.

## Когда вызывать / в каком этапе

Запускаются в рамках CI или вручную при разработке и доработке скилла `visual-qa` (PR-I.b). Относятся к этапу 10 (QA). Перед деплоем — smoke-прогон на реальном `composed.html` проекта (например, `dubai-avto-liza`).

```bash
# Все bats-тесты
bats tests/pr-i-b/

# Если появятся Python-тесты
pytest tests/pr-i-b/
```

## Что на вход / на выход

**Вход:**
- `skills/visual-qa/scripts/take-screenshots.py` — скрипт Playwright
- `skills/visual-qa/scripts/visual-qa-loop.py` — главный цикл с mock-режимом (`MOCK_CODEX=1`)
- `skills/visual-qa/scripts/apply-fix.py` — применение CSS-фикса

**Три теста:**

| Файл | Что проверяет |
|---|---|
| `test_screenshots.bats` | Playwright генерирует `desktop.png` и `mobile.png` размером >5 КБ |
| `test_review_parse.bats` | Парсер mock-JSON корректно разделяет critical / warning / info |
| `test_apply_fix.bats` | `apply-fix.py` добавляет инлайн-стиль `overflow: hidden` в указанный selector |

**Выход:**
- Статусы pass/fail для каждого теста
- На smoke — файлы `10_QA/screenshots/` и `10_QA/visual-qa-report.md`

## Связанные концепты

- [[visual-qa]] — скилл, тесты которого покрывают эти файлы
- [[landing-qa]] — слеш-команда, вызывающая `visual-qa-loop.py`
- [[qa-auditor]] — агент этапа 10, использует visual-qa как часть проверки
- [[gpt5-prompting-engine]] — генерирует `review-prompt.md` для codex vision (Task 0 PR-I.b)

## Источник

- `tests/pr-i-b/README.md`
- `docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md`
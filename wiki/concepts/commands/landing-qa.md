---
type: command
name: landing-qa
sources: ["commands/landing-qa.md"]
updated: 2026-05-25
triggers:
  - "запустить визуальный QA"
  - "проверить composed.html перед деплоем"
  - "сделать скриншоты и найти баги вёрстки"
  - "visual qa перед этапом 09"
stage: "07c / 07f / 09"
uses:
  - visual-qa
tags:
  - qa
  - visual
  - playwright
  - codex
  - screenshots
---

# /landing-qa — Визуальный QA перед деплоем

## Что делает

Делает автоматические скриншоты лендинга (desktop + mobile), анализирует их через codex CLI и выдаёт читаемый отчёт со списком визуальных проблем. При желании может сразу попробовать исправить найденные баги.

## Когда вызывать / в каком этапе

Вызывать вручную в трёх ситуациях:
- после закрытия этапа **07c** (`composed.html`) или **07f** (`composed_final`);
- перед деплоем на этапе **09**;
- после любых ручных правок в HTML/CSS.

Поддерживает три режима запуска:
```
/landing-qa <project>            # диагностика без ошибок
/landing-qa <project> --strict   # exit с ошибкой при critical issues
/landing-qa <project> --iterate  # auto-fix цикл, максимум 3 итерации
```

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` (или `07f_COMPOSED_FINAL/`) — HTML-файл лендинга

**Выход:**
- `<project>/10_QA/screenshots/iter-N/desktop.png` — скриншот 1280×800
- `<project>/10_QA/screenshots/iter-N/mobile.png` — скриншот 375×812
- `<project>/10_QA/screenshots/iter-N/desktop-review.json` — JSON с issues от codex
- `<project>/10_QA/screenshots/iter-N/mobile-review.json` — аналогично для mobile
- `<project>/10_QA/visual-qa-report.md` — финальный читаемый отчёт

**Стоимость:** ~$0.10 за один скриншот-ревью; полный прогон (desktop + mobile) — около $0.20–0.40.

## Как работает внутри

1. Открывает HTML через Playwright.
2. Делает скриншоты desktop и mobile.
3. Отправляет каждый скриншот в `codex exec -i screenshot.png` с промптом QA-инженера.
4. Получает JSON-ответ `{"issues": [...], "summary": "..."}`.
5. Сохраняет артефакты и генерирует `visual-qa-report.md`.
6. При флаге `--iterate` — запускает `apply-fix.py`, применяет исправления и повторяет цикл (до 3 раз).

## Связанные концепты

- [[visual-qa]] — скилл, реализующий логику скриншотов и анализа через codex

## Источник

- `commands/landing-qa.md`
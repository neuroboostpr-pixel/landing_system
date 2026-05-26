---
type: skill
name: visual-qa
sources: ["skills/visual-qa/SKILL.md"]
updated: 2026-05-26
triggers:
  - "проверь визуально лендинг"
  - "сделай скриншоты и отчёт"
  - "запусти visual QA"
  - "проверь composed.html на баги вёрстки"
stage: "07c, 07f, 08, 09"
uses:
  - codex-process-photo
  - stage-07c-composed
tags: [qa, visual, playwright, codex, screenshot, auto-fix]
---

# Visual QA — Автоматический визуальный контроль лендинга

## Что делает

Делает скриншоты лендинга (desktop + mobile), анализирует их через codex vision и выдаёт отчёт о визуальных дефектах. При запуске с флагом `--iterate` пытается сам исправить критические проблемы — до трёх раз по кругу.

## Когда вызывать / в каком этапе

Используется после завершения стадий сборки или композиции. Применяется на этапах **07c** (photos), **07f** (финальный composed), **08** (build) и **09** (deploy). Мягкая проверка `visual_qa_passed` включена в stage-gate этапа 07c. Запускается командой `/landing-qa`.

Флаги:
- без флагов — один прогон: скриншоты + анализ + отчёт
- `--strict` — возвращает exit 1 при наличии critical issues
- `--iterate` — включает auto-fix цикл (до 3 итераций)

## Что на вход / на выход

**Вход:**
- `composed.html` или задеплоенный сайт проекта
- Промпт-шаблон `templates/review-prompt.md` (сгенерирован через `gpt5-prompting-engine`)

**Выход:**
- Desktop-скриншот (1280×800) и mobile-скриншот (375×812) через Playwright
- JSON со списком issues: уровень (`critical` / `warning` / `info`), тип, CSS-selector, подсказка по фиксу
- Итоговый отчёт: `<project>/10_QA/visual-qa-report.md`

## Pipeline внутри

1. `take-screenshots.py` — Playwright делает оба скриншота
2. `codex-review-screenshot.sh` — каждый скриншот уходит в `codex exec -i` с промптом
3. Codex возвращает JSON с issues
4. `visual-qa-loop.py` — при `--iterate` вызывает `apply-fix.py` для critical issues

**Границы auto-fix:**
- ✅ Разрешено: `css_tweak` (inline-стили на конкретный selector)
- ❌ Запрещено: `text_*` (защита контента, правило PR-H content-preserve), `block_*` (структурные изменения)
- 🟡 Прочее — попадает в отчёт как warning, не правится автоматически

## Связанные концепты

- [[codex-process-photo]] — тот же codex CLI, используется для AI-генерации фото
- [[stage-07c-composed]] — этап, где `visual_qa_passed` является soft-gate условием

## Источник

- `skills/visual-qa/SKILL.md`
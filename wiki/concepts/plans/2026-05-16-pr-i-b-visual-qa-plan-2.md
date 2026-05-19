---
type: skill
name: visual-qa
sources: ["docs/superpowers/plans/2026-05-16-pr-i-b-visual-qa-plan 2.md"]
updated: 2026-05-19
triggers: []
stage: "07c, 07f, 08, 09"
uses:
  - gpt5-prompting-engine
  - paralaximus-codex
  - photo-curation
  - block-composition
  - landing-qa
tags: [qa, playwright, codex, screenshots, auto-fix]
---

# Visual QA — Автоматический визуальный контроль качества лендинга

## Что делает

Делает desktop и mobile скриншоты готового `composed.html`, отправляет их в codex CLI на анализ через AI-зрение, получает список визуальных проблем (JSON) и пробует автоматически исправить критичные — до трёх итераций подряд. Финал — читаемый отчёт `10_QA/visual-qa-report.md`.

## Когда вызывать / в каком этапе

Вызывается вручную командой `/landing-qa <project>` перед закрытием этапов `07c` (photos) и `07f` (composed final), а также перед деплоем (этап 09). В `config/stage-gates.yaml` добавлен мягкий гейт (`soft_check`) на этапах 07c и 07f — система напоминает запустить QA, но не блокирует при отсутствии отчёта.

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` или `07f_COMPOSED_FINAL/composed.html`
- `skills/visual-qa/templates/review-prompt.md` — промпт для codex, сгенерированный через [[gpt5-prompting-engine]] (валидация ≥ 8/10)

**Выход:**
- `10_QA/screenshots/iter-N/desktop.png` + `mobile.png` (Playwright, 1280×800 и 375×812)
- `10_QA/screenshots/iter-N/desktop-review.json` + `mobile-review.json` — JSON от codex
- `10_QA/visual-qa-report.md` — финальный читаемый отчёт с issues по severity

**Структура скилла:**
- `take-screenshots.py` — Playwright, full_page, networkidle wait
- `codex-review-screenshot.sh` — `codex exec -i screenshot.png` по паттерну [[paralaximus-codex]]
- `visual-qa-loop.py` — главный цикл (screenshot → review → fix → repeat)
- `apply-fix.py` — применяет `css_tweak` через inline style; блокирует `text_*` и `block_*` (контент и структура неприкосновенны)
- `scripts/verify-visual-qa.sh` + `verify_visual_qa.py` — проверка отчёта для gate-check

**JSON-схема issue от codex:**
```json
{"severity": "critical|warning|info", "type": "...", "description": "...",
 "selector": "...", "fix_hint": "..."}
```

**Флаги `/landing-qa`:**
- `--strict` — exit 1 если есть critical issues
- `--iterate` — включить auto-fix цикл до 3 итераций
- (без флагов) — разовый прогон, только диагностика

## Связанные концепты

- [[gpt5-prompting-engine]] — генерирует `review-prompt.md` для codex vision; не пишется руками
- [[paralaximus-codex]] — тот же паттерн `stdin prompt + -i image` для codex CLI
- [[photo-curation]] — аналогичное использование `codex exec` для обработки изображений
- [[block-composition]] — производит `composed.html`, который QA проверяет
- [[landing-qa]] — слеш-команда, точка входа пользователя в скилл

## Источник

- `docs/superpowers/plans/2026-05-16-pr-i-b-visual-qa-plan 2.md`
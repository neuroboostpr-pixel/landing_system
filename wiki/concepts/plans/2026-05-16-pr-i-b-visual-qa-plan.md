---
type: skill
name: visual-qa
sources: ["docs/superpowers/plans/2026-05-16-pr-i-b-visual-qa-plan.md"]
updated: 2026-05-18
triggers: ["/landing-qa", "визуальный QA", "проверить лендинг перед деплоем", "запустить QA", "скриншоты composed.html"]
stage: "07c, 07f, 08, 09"
uses: ["gpt5-prompting-engine", "paralaximus-codex", "block-composer", "photo-curator", "stage-gates"]
tags: ["qa", "visual", "playwright", "codex", "screenshot", "auto-fix"]
---

# Visual QA — автоматическая визуальная проверка лендинга

## Что делает

Делает скриншоты готового лендинга в браузере (desktop + mobile), отправляет их в codex AI для анализа и получает список визуальных проблем. Если включён режим `--iterate` — автоматически пробует исправить критичные баги через CSS-правки.

## Когда вызывать / в каком этапе

Запускается вручную командой `/landing-qa <project>` после завершения этапов 07c (photos) или 07f (composed final). Также рекомендован перед деплоем (этап 09). В `config/stage-gates.yaml` добавлен мягкий (soft) чек на этапах 07c и 07f — не блокирует, но напоминает запустить проверку.

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` (или `07f_COMPOSED_FINAL/composed.html`)
- `skills/visual-qa/templates/review-prompt.md` — промпт для codex, сгенерированный через [[gpt5-prompting-engine]] (валидирован ≥ 8/10)

**Выход:**
- `<project>/10_QA/screenshots/iter-N/desktop.png` — скриншот desktop 1280×800
- `<project>/10_QA/screenshots/iter-N/mobile.png` — скриншот mobile 375×812
- `<project>/10_QA/screenshots/iter-N/{desktop,mobile}-review.json` — JSON с issues от codex
- `<project>/10_QA/visual-qa-report.md` — читаемый отчёт по итогам всех итераций

**Опции запуска:**
- без флагов — один прогон, только диагностика
- `--strict` — exit 1 если есть critical issues (для CI/автоматики)
- `--iterate` — цикл auto-fix до 3 итераций

## Ключевые скрипты (pipeline)

| Скрипт | Роль |
|---|---|
| `take-screenshots.py` | Playwright: открывает HTML, ждёт networkidle, делает full_page PNG |
| `codex-review-screenshot.sh` | Отправляет PNG в `codex exec -i`, парсит JSON из ответа |
| `visual-qa-loop.py` | Главный цикл: скриншот → ревью → фикс → повтор |
| `apply-fix.py` | CSS-tweak по selector из fix_hint; блокирует `text_*`, `block_*` |
| `scripts/verify-visual-qa.sh` | Bash-обёртка для stage-gates (soft check) |

**Категории issues от codex:** `critical` (обрезанное фото, overflow, невидимый CTA), `warning` (контраст, мелкий шрифт), `info` (spacing, анимация).

**Auto-fix scope:** разрешён только `css_tweak` (inline style). Текстовые и структурные правки — запрещены (content-preserve).

## Связанные концепты

- [[gpt5-prompting-engine]] — сгенерировал review-prompt.md, валидация ≥ 8/10
- [[paralaximus-codex]] — тот же паттерн `codex exec -i` для visual tasks
- [[photo-curator]] — предыдущий этап (07c), после которого рекомендуется запускать QA
- [[block-composer]] — производит composed.html, который проверяется QA
- [[stage-gates]] — мягкий чек `visual_qa_passed` на 07c и 07f
- [[landing-qa]] — слеш-команда, точка входа пользователя

## Источник

- `docs/superpowers/plans/2026-05-16-pr-i-b-visual-qa-plan.md`
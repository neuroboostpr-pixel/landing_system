---
slug: visual-qa
type: skill
name: "Visual QA"
stage: "07c"
tags: [qa, playwright, codex, screenshots, visual, auto-fix]
triggers: [landing-qa]
inputs: [07b-composed]
outputs: [10-qa]
pre_reqs: [07b-composed]
related: [landing-qa, gpt5-prompting-engine, 10-qa, landing-compose, landing-photos, landing-visuals]
sources: ["skills/visual-qa/SKILL.md"]
updated: 2026-06-19
confidence: {stage: low}
---

# Visual QA

## Что делает

Автоматизированный визуальный контроль качества лендинга после этапа композиции. Скилл делает скриншоты `composed.html` через Playwright (desktop 1280×800 и mobile 375×812), отправляет их в codex vision для анализа, получает JSON со списком проблем и при необходимости запускает цикл авто-фикса (до 3 итераций). Результат — отчёт в папке `10_QA/`. Применяется на этапах 07c, 07f, 08 и 09.

## Когда вызывается

Вызывается командой `/landing-qa <project>` после того, как готов `composed.html`. Флаг `--strict` даёт exit 1 при наличии критических проблем, флаг `--iterate` включает цикл авто-фикса.

## Вход → выход

**Вход:** готовый `composed.html` (этап 07b/07c), доступный Playwright и codex CLI, шаблон промпта `templates/review-prompt.md`.

**Выход:** файл `<project>/10_QA/visual-qa-report.md` со списком issues (critical/warning/info), типом проблемы, selector'ом и подсказкой по фиксу.

## Failure modes

- Playwright не установлен или не может открыть `composed.html` — скриншоты не создаются, пайплайн падает на шаге 1.
- codex CLI недоступен или возвращает невалидный JSON — анализ прерывается, отчёт не создаётся.
- Auto-fix пробует исправить структуру блоков (`block_*`) или тексты (`text_*`) — запрещено; фикс молча пропускается, issue остаётся в warning-секции отчёта.
- После 3 итераций цикла критические проблемы не устранены — скилл завершается с предупреждением, не входит в бесконечный цикл.
- Промпт `templates/review-prompt.md` устарел и не отражает новые правила дизайна — codex выдаёт нерелевантные findings; решение: перегенерировать через `gpt5-prompting-engine`.

## Related

- [[landing-qa]] — slash-команда, точка входа для этого скилла
- [[07b-composed]] — composed.html, который проверяется скиллом
- [[10-qa]] — директория с выходными артефактами (отчёт)
- [[gpt5-prompting-engine]] — генерирует `templates/review-prompt.md`, не пишется вручную
- [[landing-compose]] — этап 07c, где `visual_qa_passed` является soft-check гейтом
- [[landing-visuals]] — этап 07d, один из этапов где скилл также применяется
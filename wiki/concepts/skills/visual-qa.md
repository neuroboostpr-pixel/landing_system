---
slug: visual-qa
type: skill
name: "Visual QA — автоматический визуальный контроль"
stage: "07c"
tags: [qa, screenshot, playwright, codex, visual, auto-fix]
triggers: [landing-qa]
inputs: [07b_COMPOSED/composed.html]
outputs: [10_QA/visual-qa-report.md]
gates: [visual_qa_passed]
pre_reqs: [block-composer]
related: [gpt5-prompting-engine, qa-auditor]
sources: ["skills/visual-qa/SKILL.md"]
updated: 2026-05-26
confidence: {stage: low, pre_reqs: low}
---

# Visual QA — автоматический визуальный контроль

## Что делает

Запускает автоматизированный цикл визуального QA для скомпонованного лендинга. Playwright делает скриншоты `composed.html` в desktop (1280×800) и mobile (375×812) разрешениях, затем каждый скриншот отправляется в `codex exec -i` с промптом из `templates/review-prompt.md` (сгенерированным через `gpt5-prompting-engine`). Codex возвращает структурированный JSON со списком визуальных проблем (уровень critical/warning/info, тип, CSS-селектор, подсказка по фиксу). При флаге `--iterate` скилл запускает до трёх итераций auto-fix для critical-issues типа `css_tweak`.

## Когда вызывается

Вызывается вручную командой `/landing-qa <project>` на этапах 07c, 07f, 08 и 09 — после того как `composed.html` готов и визуальная сборка считается завершённой. Может использоваться с флагом `--strict` (exit 1 при наличии критических проблем) или `--iterate` (авто-цикл фикса).

## Вход → выход

**Вход:** `composed.html` в папке `07b_COMPOSED/` (или актуальный для этапа 07f/08/09); установленный Playwright и доступный codex CLI.

**Выход:** `10_QA/visual-qa-report.md` с полным списком issues по уровням. JSON-источник хранится рядом. При `--iterate` — также исправленный `composed.html` (только CSS-твики).

## Чем закрывается этап (gates)

- `visual_qa_passed` — soft_check на этапе 07c; этап не считается пройденным, пока в отчёте есть нефиксированные critical issues

## Failure modes

- Playwright не установлен или не находит браузер — скриншоты не создаются, пайплайн падает на первом шаге
- Codex CLI недоступен или не отвечает — анализ скриншотов не проходит, issues не генерируются
- codex возвращает не-JSON или невалидный JSON — `visual-qa-loop.py` не может распарсить, auto-fix цикл не запускается
- Auto-fix меняет только `css_tweak`-issues; структурные и текстовые проблемы остаются в отчёте без применения фикса (intentional — content-preserve блокирует `text_*`)
- После 3 итераций auto-fix критические проблемы могут остаться — отчёт генерируется, но gate не пройден

## Related

- [[gpt5-prompting-engine]] — генерирует промпт `review-prompt.md`; обновлять промпт только через engine
- [[qa-auditor]] — смежная роль финального QA; visual-qa — инструментарий, qa-auditor — агент
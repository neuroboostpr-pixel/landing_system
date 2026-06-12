---
slug: landing-qa
type: command
name: "/landing-qa — Визуальный QA лендинга"
stage: "10"
tags: [qa, visual, playwright, codex, screenshot, auto-fix]
triggers: [landing-qa]
inputs: []
outputs: ["<project>/10_QA/screenshots/iter-N/desktop.png", "<project>/10_QA/screenshots/iter-N/mobile.png", "<project>/10_QA/screenshots/iter-N/desktop-review.json", "<project>/10_QA/screenshots/iter-N/mobile-review.json", "<project>/10_QA/visual-qa-report.md"]
gates: []
pre_reqs: [landing-compose]
related: [visual-qa, landing-deploy, landing-final-check, landing-build]
sources: ["commands/landing-qa.md"]
updated: 2026-05-26
confidence: {stage: low, gates: low}
---

# /landing-qa — Визуальный QA лендинга

## Что делает

Запускает финальный визуальный контроль лендинга перед деплоем. Открывает `composed.html` через Playwright, снимает скриншоты в desktop (1280×800) и mobile (375×812) разрешениях, затем анализирует каждый через codex CLI с промптом QA-инженера. Формирует структурированный JSON с найденными issues и сводный читаемый отчёт. В режиме `--iterate` пытается автоматически исправить проблемы (до трёх циклов).

## Когда вызывается

Вызывается вручную оператором перед закрытием этапа 07b/07f или перед деплоем (этап 09). Также применяется после любых ручных правок в HTML/CSS, чтобы убедиться, что правки не сломали визуал. При флаге `--strict` возвращает ошибку, если найдены критические issues — это позволяет встроить команду в автоматизированный pipeline с жёсткими гейтами.

## Вход → выход

**Вход:** файл `<project>/07b_COMPOSED/composed.html` (или `07f_COMPOSED_FINAL/`), установленный Playwright и доступный codex CLI.

**Выход:** скриншоты desktop и mobile по итерациям, JSON-отчёты с перечнем visual issues, итоговый `visual-qa-report.md` с читаемой сводкой. При `--iterate` — дополнительно патченный HTML после auto-fix попыток.

## Failure modes

- **Playwright не установлен или браузер не запускается** — команда падает на шаге скриншотов; нужна установка `npx playwright install`.
- **codex CLI недоступен или квота исчерпана** — анализ не выполняется, отчёт не формируется; стоимость ~$0.20–0.40 за прогон.
- **composed.html не найден** — команда не знает, какой файл брать, если оба пути `07b_COMPOSED/` и `07f_COMPOSED_FINAL/` отсутствуют.
- **Auto-fix цикл не сходится** — за 3 итерации issues не исчезают; скрипт `apply-fix.py` может применить регрессионные правки.
- **Мобильный скриншот не отражает реальный рендер** — Playwright эмулирует viewport, но не все CSS медиа-фичи работают идентично реальным устройствам.

## Related

- [[visual-qa]] — скилл, реализующий логику Playwright + codex анализа
- [[landing-deploy]] — следующий этап после прохождения QA
- [[landing-final-check]] — смежный финальный контроль перед деплоем
- [[landing-build]] — этап сборки WordPress-темы, предшествует QA
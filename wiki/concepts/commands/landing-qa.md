---
type: command
name: landing-qa
sources: ["commands/landing-qa.md"]
updated: 2026-05-16
triggers:
  - "запустить визуальный контроль лендинга"
  - "проверить composed.html перед деплоем"
  - "сделать скриншоты и QA-анализ"
  - "найти визуальные проблемы в макете"
stage: "10"
uses:
  - visual-qa
tags:
  - qa
  - visual
  - codex
  - playwright
  - screenshot
---

# /landing-qa — Визуальный контроль перед деплоем

## Что делает

Делает скриншоты текущего макета (desktop + mobile), отправляет их на анализ через codex CLI и выдаёт читаемый отчёт со списком визуальных проблем. Помогает поймать баги вёрстки до того, как они уйдут на живой сайт.

## Когда вызывать / в каком этапе

Этап **10 QA**. Вызывать вручную:

- перед закрытием этапа `07b_COMPOSED` или `07f_COMPOSED_FINAL`;
- перед деплоем (этап 09);
- после любых ручных правок в HTML/CSS.

Три режима запуска:

```
/landing-qa <project>            # диагностика, только отчёт
/landing-qa <project> --strict   # падает с ошибкой при critical issues
/landing-qa <project> --iterate  # auto-fix цикл, максимум 3 итерации
```

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` или `07f_COMPOSED_FINAL/` — финальный макет лендинга.

**Выход:**
- `10_QA/screenshots/iter-N/desktop.png` + `mobile.png` — скриншоты (1280×800 и 375×812).
- `10_QA/screenshots/iter-N/desktop-review.json` + `mobile-review.json` — JSON с issues от codex.
- `10_QA/visual-qa-report.md` — читаемый отчёт со списком всех найденных проблем и summary.

При флаге `--iterate` — дополнительно: попытка авто-исправления через `apply-fix.py` с повтором цикла (до 3 раз).

**Стоимость:** ~$0.10 за один скриншот, ~$0.20–0.40 за полный прогон (desktop + mobile).

## Связанные концепты

- [[visual-qa]] — скилл, реализующий логику Playwright + codex-анализа
- [[block-composer]] — генерирует `composed.html`, который QA проверяет
- [[wp-deployer]] — следующий этап после прохождения QA

## Источник

- `commands/landing-qa.md`
---
type: command
name: landing-qa
sources: ["commands/landing-qa.md"]
updated: 2026-05-26
triggers:
  - "запустить визуальный контроль перед деплоем"
  - "проверить composed.html скриншотами"
  - "visual QA лендинга"
  - "проверить вёрстку на мобильном и десктопе"
stage: "07c / 07f / 09"
uses:
  - visual-qa
tags: [qa, screenshots, codex, visual-review, composed]
---

# /landing-qa — Визуальный QA перед деплоем

## Что делает

Автоматически делает скриншоты страницы на desktop и mobile, анализирует их через codex CLI и выдаёт отчёт с визуальными проблемами. Позволяет поймать вёрстку-баги до того, как сайт уйдёт на прод.

## Когда вызывать / в каком этапе

Вызывается вручную в трёх ситуациях:
- После закрытия этапа **07c** (composed) или **07f** (composed final) — убедиться, что всё выглядит правильно;
- Перед деплоем на этапе **09** — финальная проверка;
- После любых ручных правок в HTML/CSS.

Команда имеет три режима:
- `/landing-qa <project>` — обычная диагностика;
- `/landing-qa <project> --strict` — возвращает ошибку, если найдены critical issues;
- `/landing-qa <project> --iterate` — запускает цикл auto-fix до 3 итераций.

## Что на вход / на выход

**Вход:**
- `<project>/07b_COMPOSED/composed.html` или `07f_COMPOSED_FINAL/` — HTML-страница для анализа.

**Выход:**
- `10_QA/screenshots/iter-1/desktop.png` + `mobile.png` — скриншоты (1280×800 и 375×812);
- `10_QA/screenshots/iter-1/desktop-review.json` + `mobile-review.json` — JSON с найденными issues от codex;
- `10_QA/visual-qa-report.md` — читаемый отчёт для маркетолога/разработчика.

При флаге `--iterate` скрипт `apply-fix.py` пытается автоматически исправить найденные проблемы и повторяет цикл (максимум 3 раза).

**Стоимость:** ~$0.10 за один скриншот-ревью через codex CLI; полный прогон (desktop + mobile) — $0.20–0.40.

## Связанные концепты

- [[visual-qa]] — скилл, на котором строится логика анализа скриншотов через codex

## Источник

- `commands/landing-qa.md`
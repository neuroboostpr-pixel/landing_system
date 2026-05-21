---
description: Запустить Visual QA на текущем composed.html — Playwright скриншоты + codex анализ + опциональный auto-fix.
---

# /landing-qa

Финальный визуальный контроль перед деплоем. Делает desktop+mobile скриншоты, анализирует через codex CLI, выдаёт отчёт со списком visual issues.

## Использование

```
/landing-qa <project>            # обычный прогон, диагностика
/landing-qa <project> --strict   # ошибка если найдены critical issues
/landing-qa <project> --iterate  # с auto-fix циклом (макс 3 итерации)
```

## Что делает

1. Открывает `<project>/07b_COMPOSED/composed.html` (или `07f_COMPOSED_FINAL/`) через Playwright
2. Делает скриншоты desktop (1280×800) и mobile (375×812)
3. Анализирует каждый через `codex exec -i screenshot.png` с промптом QA-инженера
4. Получает JSON: `{"issues": [...], "summary": "..."}`
5. Сохраняет:
   - `<project>/10_QA/screenshots/iter-1/desktop.png` + `mobile.png`
   - `<project>/10_QA/screenshots/iter-1/desktop-review.json` + `mobile-review.json`
   - `<project>/10_QA/visual-qa-report.md` (читаемый отчёт)
6. При `--iterate` — пробует auto-fix через `apply-fix.py`, повторяет цикл

## Стоимость

Codex CLI: ~$0.10 за один screenshot review. На полный прогон ~$0.20-0.40.

## Когда использовать

- Перед закрытием этапа `07c_composed` или `07f_composed_final`
- Перед деплоем (этап 09)
- После любых ручных правок в HTML/CSS

## Связанные

- Skill: [[visual-qa]]
- Spec: [`docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md`](../docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md)

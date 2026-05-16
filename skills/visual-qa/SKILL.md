---
name: visual-qa
description: Стадия пост-композа QA через Playwright + codex CLI. Делает desktop+mobile скриншоты композита, анализирует через codex vision (codex exec -i screenshot.png), выдаёт JSON со списком visual issues, пробует auto-fix цикл (макс 3 итерации). Используется на этапах 07c/07f/08/09.
---

# visual-qa

Финальный визуальный контроль качества лендинга через автоматизированный QA-цикл.

## Использование

```bash
/landing-qa <project>            # один раз: скриншоты + анализ + отчёт
/landing-qa <project> --strict   # exit 1 если critical issues
/landing-qa <project> --iterate  # с auto-fix циклом до 3 итераций
```

## Pipeline

1. `take-screenshots.py` — Playwright делает desktop (1280×800) + mobile (375×812) скриншоты `composed.html`
2. `codex-review-screenshot.sh` — каждый скриншот → `codex exec -i` с промптом из `templates/review-prompt.md`
3. Codex возвращает JSON со списком issues: critical/warning/info, type, selector, fix_hint
4. `visual-qa-loop.py` парсит, при `--iterate` запускает `apply-fix.py` для critical issues
5. Финальный отчёт в `<project>/10_QA/visual-qa-report.md`

## Auto-fix scope

✅ Разрешено: `css_tweak` (inline style на selector)
❌ Запрещено: `text_*` (PR-H content-preserve), `block_*` (структура)
🟡 Не auto-fix: всё остальное — попадает в warning отчёта

## Промпт для codex

`templates/review-prompt.md` — **сгенерирован через `gpt5-prompting-engine`**, не пишется руками.
Если требует обновления — вызвать engine с новым брифом.

## Связанные

- [[codex-process-photo]] — тот же codex CLI, но для генерации фото
- [[content-preserve]] (PR-H) — блокирует text-fix
- [[stage-07c-composed]] — где soft_check `visual_qa_passed`

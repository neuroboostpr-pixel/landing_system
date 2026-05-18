---
type: skill
name: visual-qa
sources: ["docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md"]
updated: 2026-05-18
triggers: []
stage: "07c / 07f / 08"
uses: ["gpt5-prompting-engine", "landing-qa", "photo-curator", "block-composer", "landing-orchestrator"]
tags: ["qa", "visual", "playwright", "codex", "auto-fix", "screenshots"]
---

# Visual QA — визуальная проверка лендинга скриншотами

## Что делает
Открывает `composed.html` в браузере через Playwright, делает скриншоты desktop и mobile, затем анализирует их через codex vision. Находит визуальные дефекты (обрезанные фото, текст вылезающий за блок, пустые секции) и автоматически исправляет CSS или перекадрирует фото — до 3 итераций.

## Когда вызывать / в каком этапе
Вызывается командой `/landing-qa` после завершения этапа 07c (photos) и перед деплоем. По умолчанию — мягкая рекомендация (warning). При флаге `--strict` становится жёстким гейтом: если есть критичные проблемы, следующий этап не откроется. `landing-orchestrator` предлагает запустить QA после 07c, но не принуждает.

## Что на вход / на выход

**Вход:**
- `07b_COMPOSED/composed.html` — финальная сборка
- `07c_PHOTOS/processed/` — обработанные фото (из PR-I.a / photo-curator)
- `04_БРЕНД/tokens.json` — токены для контекста анализа

**Выход:**
- `10_QA/screenshots/iter-N/desktop.png` и `mobile.png` — скриншоты каждой итерации
- `10_QA/screenshots/final/` — финальные скриншоты
- `10_QA/visual-qa-report.md` — итоговый отчёт: список issues (critical / warning / info), что исправлено, что осталось вручную
- Обновлённый `composed.html` — если auto-fix применял CSS-правки

**Auto-fix умеет:**
- `css_tweak` — добавить инлайн-стиль в нужный селектор
- `photo_recrop` — перекадрировать фото через photo-pipeline
- `photo_reprocess` — перегенерировать через codex с уточнённым промптом

**Auto-fix запрещено:**
- Менять текст (блокирован проверкой PR-H content-preserve)
- Менять структуру блоков

## Связанные концепты
- [[gpt5-prompting-engine]] — генерирует промпт для codex vision (Task 0 PR-I.b), не пишется вручную
- [[landing-qa]] — slash-команда, точка входа: `/landing-qa`, `/landing-qa --strict`, `/landing-qa --iterate`
- [[photo-curator]] — поставляет обработанные фото перед QA (этап 07c, PR-I.a)
- [[block-composer]] — создаёт composed.html, который QA проверяет
- [[landing-orchestrator]] — рекомендует запустить `/landing-qa` после этапа 07c

## Источник
- `docs/superpowers/specs/2026-05-16-pr-i-b-visual-qa-design.md`
---
type: command
name: landing-final-check
sources: ["commands/landing-final-check.md"]
updated: 2026-05-25
triggers:
  - "финальная проверка лендинга перед деплоем"
  - "запустить все проверки качества проекта"
  - "проверить лендинг перед публикацией"
  - "bundle-проверка перед деплоем"
stage: ""
uses:
  - landing-deploy
  - landing-compose
  - landing-photos
  - landing-visuals
tags: ["qa", "deploy", "check", "bundle", "final"]
---

# Landing Final Check — финальная авто-проверка перед деплоем

## Что делает

Запускает все встроенные проверки качества лендинга одной командой и формирует сводный отчёт. Если хоть одна обязательная проверка упала — команда сигнализирует об ошибке и не даёт двигаться на деплой.

## Когда вызывать / в каком этапе

Вызывается вручную перед этапом 09 (деплой), когда уже готовы: composed.html (07b), фото (07c), визуалы (07d). Идеальная точка — непосредственно перед `/landing-deploy`, когда все контентные этапы утверждены.

## Что на вход / на выход

**Вход:**
- `<project>` — slug проекта в `~/Lendings/`
- Должны существовать артефакты: `07b_COMPOSED/composed.html`, `07c_PHOTOS/processed/`, `07d_VISUALS/`, опционально — `wiki/` и `10_QA/visual-qa/`

**Выход:**
- stdout — краткая сводка по каждой проверке (pass / fail / optional-skip)
- `<project>/10_QA/final-check-report.md` — детальный отчёт с разбивкой по всем шести проверкам
- exit 0 — все обязательные проверки прошли
- exit 1 — хотя бы одна обязательная проверка провалилась

**Состав bundle-проверок:**

| Проверка | Обязательная |
|---|---|
| Wiki sync | опционально |
| Composed premium (13 фич) | ✅ |
| Content preserved (текст прототипа) | ✅ |
| Photo pipeline (processed/, no placeholders, hero no-crop) | ✅ |
| Identity preserved (manifest без violations) | ✅ |
| Visual QA | опционально |

## Связанные концепты

- [[landing-deploy]] — следующий этап; `/landing-final-check` является его мягким prerequisite
- [[landing-compose]] — формирует `composed.html`, который проверяет composed-premium и content-preserved
- [[landing-photos]] — формирует `07c_PHOTOS/processed/`, который проверяет photo-pipeline
- [[landing-visuals]] — формирует `07d_VISUALS/`, входит в состав visual QA

## Источник

- `commands/landing-final-check.md`
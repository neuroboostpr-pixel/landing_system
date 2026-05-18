---
type: command
name: landing-final-check
sources: ["commands/landing-final-check.md"]
updated: 2026-05-16
triggers:
  - "проверить лендинг перед деплоем"
  - "финальная проверка проекта"
  - "запустить все проверки качества"
  - "готов ли лендинг к деплою"
stage: "10"
uses:
  - premium-07b-checklist
  - photo-curator
  - visual-qa
  - wiki
  - landing-deploy
  - qa-auditor
tags: ["qa", "deploy", "bundle", "verify"]
---

# /landing-final-check — Финальная проверка перед деплоем

## Что делает

Запускает все проверки качества проекта одной командой — bundle всех verify-скриптов системы. Показывает, готов ли лендинг к деплою, и сохраняет детальный отчёт.

## Когда вызывать / в каком этапе

Вызывается вручную **перед** `/landing-deploy` (этап 10). Используется как последний рубеж контроля качества — если хоть одна обязательная проверка падает, деплой не стоит запускать.

Запуск:
```
/landing-final-check <project>
```

## Что на вход / на выход

**Вход:**
- Имя (или путь) папки проекта
- Все артефакты предыдущих этапов: `07b_COMPOSED/composed.html`, `07c_PHOTOS/`, `07d_VISUALS/`, `07_ПРОТОТИП/prototype.md`, `wiki/` (опц.)

**Выход:**
- `stdout` — краткая сводка: статус каждой проверки (pass / fail)
- `<project>/10_QA/final-check-report.md` — детальный отчёт по каждой проверке
- `exit 0` — все обязательные проверки прошли; `exit 1` — хотя бы одна упала

**Проверки (по порядку):**

| Проверка | Обязательная |
|---|---|
| Wiki sync | опционально |
| Composed premium (13 фич) | ✅ |
| Content preserved (текст прототипа) | ✅ |
| Photo pipeline (processed/, no placeholders, hero no-crop) | ✅ |
| Identity preserved (manifest без violations) | ✅ |
| Visual QA | опционально |

## Связанные концепты

- [[premium-07b-checklist]] — стандарт composed premium (13 фич), который проверяется в bundle
- [[photo-curator]] — photo pipeline, результаты которого проверяются на корректность
- [[visual-qa]] — визуальная проверка, входит в bundle как опциональный шаг
- [[wiki]] — синхронность wiki с исходниками (опциональная проверка)
- [[qa-auditor]] — агент post-deploy QA (следующий этап после финальной проверки)
- [[landing-deploy]] — команда деплоя, которой предшествует эта проверка

## Источник

- `commands/landing-final-check.md`
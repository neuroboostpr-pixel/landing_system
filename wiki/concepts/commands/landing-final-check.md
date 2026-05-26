---
type: command
name: landing-final-check
sources: ["commands/landing-final-check.md"]
updated: 2026-05-26
triggers:
  - "проверить лендинг перед деплоем"
  - "финальная проверка проекта"
  - "запустить все проверки качества"
  - "убедиться что всё готово к деплою"
stage: ""
uses:
  - landing-deploy
  - landing-compose
  - landing-photos
  - landing-visuals
  - landing-qa
tags:
  - quality
  - pre-deploy
  - gate
---

# /landing-final-check — Финальная проверка лендинга

## Что делает

Запускает все обязательные проверки качества проекта одной командой — своеобразный «чек-лист перед взлётом». Если хотя бы одна обязательная проверка не прошла, команда сигнализирует об ошибке и не позволяет двигаться к деплою.

## Когда вызывать / в каком этапе

Вызывается вручную перед этапом 09 (деплой на Бегет). Это финальный барьер качества — после всех этапов pipeline: compose готов, фото обработаны, визуалы сгенерированы, контент утверждён. Обычно предшествует `/landing-deploy`.

## Что на вход / на выход

**Вход:**
- Имя проекта `<project>` — slug папки в `~/Lendings/`
- Собранный проект: `07b_COMPOSED/composed.html`, обработанные фото в `07c_PHOTOS/processed/`, визуалы в `07d_VISUALS/`

**Выход:**
- Краткая сводка в stdout — быстрый обзор статуса каждой проверки
- `<project>/10_QA/final-check-report.md` — детальный отчёт с результатом каждой проверки
- Exit-код: `0` — все обязательные проверки прошли, `1` — есть хотя бы один провал

**Проверки в bundle:**

| Проверка | Обязательность |
|---|---|
| Wiki sync | Опционально |
| Composed premium (13 фич) | Обязательно |
| Content preserved (текст прототипа) | Обязательно |
| Photo pipeline (фото в processed/, нет placeholder, hero без кадрирования) | Обязательно |
| Identity preserved (manifest без violations) | Обязательно |
| Visual QA | Опционально |

## Связанные концепты

- [[landing-deploy]] — следующий шаг после успешной финальной проверки
- [[landing-compose]] — формирует `composed.html`, который проверяет composed-premium
- [[landing-photos]] — обрабатывает фото, результат проверяется photo-pipeline гейтом
- [[landing-visuals]] — генерирует иконки/инфографику, проходят visual-qa
- [[landing-qa]] — связанная QA-команда для частичных проверок

## Источник

- `commands/landing-final-check.md`
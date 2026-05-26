---
type: command
name: landing-compose
sources: ["commands/landing-compose.md"]
updated: 2026-05-26
triggers:
  - "собрать composed.html"
  - "запустить этап 07b"
  - "собрать страницу с токенами и текстами"
  - "скомпоновать wireframe с контентом"
stage: "07b"
uses:
  - block-composer
  - landing-wireframe
  - landing-photos
  - landing-visuals
  - landing-go
tags:
  - compose
  - stage-07b
  - html
  - tokens
---

# /landing-compose — Сборка composed.html (этап 07b)

## Что делает
Собирает финальный HTML-файл лендинга: берёт выбранные wireframe-варианты, подставляет дизайн-токены и тексты из прототипа. Визуальные заглушки для фото и иконок остаются — их заполняют следующие этапы.

## Когда вызывать / в каком этапе
Запускается на этапе **07b** — после того как пользователь выбрал варианты блоков в wireframe (появился `selections.yaml`) и готова дизайн-система (`tokens.json`). Вызывается автоматически через `/landing-go` или вручную этой командой.

## Что на вход / на выход

**Вход (обязательно):**
- `07_ПРОТОТИП/prototype.yaml` — структура и тексты прототипа
- `07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, отступы)

**Выход:**
- `07b_COMPOSED/composed.html` — основная сборка десктоп
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/block-injection-log.md` — лог подстановок по блокам

## Связанные концепты
- [[block-composer]] — агент, выполняющий сборку composed.html
- [[landing-wireframe]] — предыдущий этап (07a), формирует selections.yaml
- [[landing-photos]] — следующий этап (07c), заменяет фото-заглушки
- [[landing-visuals]] — следующий этап (07d), заменяет иконки и инфографику
- [[landing-go]] — оркестратор, запускающий этот этап автоматически

## Источник
- `commands/landing-compose.md`
---
type: command
name: landing-compose
sources: ["commands/landing-compose.md"]
updated: 2026-05-25
triggers:
  - "собрать composed.html"
  - "запустить этап 07b"
  - "скомпоновать лендинг с токенами"
  - "подставить контент из прототипа в wireframe"
stage: "07b"
uses:
  - landing-wireframe
  - landing-prototype
  - block-composer
  - landing-photos
  - landing-visuals
  - landing-go
tags:
  - compose
  - stage-07b
  - html
  - design-tokens
---

# /landing-compose — Сборка composed.html (этап 07b)

## Что делает

Собирает финальный HTML-документ лендинга: берёт выбранные варианты блоков из wireframe, подставляет реальные тексты из прототипа и инжектирует дизайн-токены (цвета, шрифты, отступы). Визуальные заглушки (фото, иконки) на этом этапе остаются — они заполняются позже командами `/landing-photos` и `/landing-visuals`.

## Когда вызывать / в каком этапе

Вызывается на этапе **07b** после того, как:
- пользователь выбрал варианты блоков в `wireframe.html` и сохранил `selections.yaml` в папку `07a_WIREFRAME/`;
- дизайн-система (этап 05) завершена и `tokens.json` присутствует в `05_ДИЗАЙН-СИСТЕМА/`.

Рекомендуется запускать через `/landing-go` (оркестратор сам вызовет команду в нужный момент). Допустим и ручной вызов.

## Что на вход / на выход

**Входные артефакты:**
- `07_ПРОТОТИП/prototype.yaml` — структура и тексты блоков
- `07a_WIREFRAME/selections.yaml` — выбор пользователя по вариантам блоков
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены проекта

**Выходные артефакты:**
- `07b_COMPOSED/composed.html` — главный HTML лендинга с токенами и текстами
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/block-injection-log.md` — лог подстановки блоков

## Связанные концепты

- [[landing-wireframe]] — предыдущий этап: генерирует wireframe.html с вариантами блоков и `selections.yaml`
- [[landing-prototype]] — ещё раньше: парсит прототип клиента в `prototype.yaml`
- [[block-composer]] — агент, выполняющий фактическую сборку composed.html
- [[landing-photos]] — следующий этап 07c: заменяет фото-заглушки реальными снимками
- [[landing-visuals]] — следующий этап 07d: заменяет иконки и инфографику AI-генерацией
- [[landing-go]] — главная команда-оркестратор, вызывающая `/landing-compose` автоматически

## Источник

- `commands/landing-compose.md`
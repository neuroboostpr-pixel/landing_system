---
type: command
name: landing-compose
sources: ["commands/landing-compose.md"]
updated: 2026-05-15
triggers:
  - "собери composed.html"
  - "запусти compose"
  - "этап 07b"
  - "сборка блоков с токенами"
stage: "07b"
uses:
  - block-composer
  - prototype-import
  - wireframe-rendering
  - design-tokens-generation
tags:
  - compose
  - stage-07b
  - html
  - design-tokens
---

# /landing-compose — сборка composed.html

## Что делает

Собирает финальный HTML-файл лендинга с подставленными дизайн-токенами и текстами из прототипа. Визуальный контент (фото, иконки, инфографика) пока остаётся в виде именованных placeholder-ов — они заполняются на этапах PR-B и PR-C.

## Когда вызывать / в каком этапе

Вызывается вручную на **этапе 07b** после того, как:
- пользователь выбрал варианты блоков в `wireframe.html` и сохранил `selections.yaml` в папку `07a_WIREFRAME/`;
- в папке `05_ДИЗАЙН-СИСТЕМА/` лежит готовый `tokens.json`.

Команда **не интегрирована в `landing-orchestrator`** — это задача PR-D. До выхода PR-D запускается вручную через `/landing-compose`.

## Что на вход / на выход

**Вход:**
- `07_ПРОТОТИП/prototype.yaml` — машинное представление прототипа с текстами блоков
- `07a_WIREFRAME/selections.yaml` — выбор вариантов блоков, сделанный пользователем в wireframe.html
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, отступы)

**Выход:**
- `07b_COMPOSED/composed.html` — основной файл: блоки со стилями и реальными текстами, визуальные слоты — placeholder-ы
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/block-injection-log.md` — лог подстановки блоков

## Связанные концепты

- [[block-composer]] — агент, выполняющий фактическую сборку; команда делегирует работу ему
- [[prototype-import]] — поставляет `prototype.yaml`, без которого команда не запустится
- [[wireframe-rendering]] — поставляет `selections.yaml` с выбором вариантов блоков
- [[design-tokens-generation]] — поставляет `tokens.json` с брендовыми переменными
- [[landing-photos]] — этап PR-B, заменяет фото-placeholder-ы реальными снимками
- [[landing-visuals]] — этап PR-C, заменяет icon/infographic-placeholder-ы сгенерированными PNG

## Источник

- `commands/landing-compose.md`
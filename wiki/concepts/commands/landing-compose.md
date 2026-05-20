---
type: command
name: landing-compose
sources: ["commands/landing-compose.md"]
updated: 2026-05-20
triggers:
  - "собрать composed.html"
  - "запустить этап 07b"
  - "скомпоновать блоки с токенами"
  - "вставить дизайн-токены в wireframe"
stage: "07b"
uses:
  - block-composer
  - prototype-importer
  - ux-composer
  - design-system-generator
tags:
  - compose
  - 07b
  - tokens
  - wireframe
---

# /landing-compose — Сборка composed.html (этап 07b)

## Что делает

Собирает финальный HTML-файл страницы: берёт выбранные блоки из wireframe, подставляет дизайн-токены (цвета, шрифты, отступы) и тексты из прототипа. Визуальный контент — фото, иконки, инфографика — остаётся в виде плейсхолдеров и заполняется позже на этапах 07c и 07d.

## Когда вызывать / в каком этапе

Вызывается на **этапе 07b** — после того как пользователь выбрал варианты блоков в `wireframe.html` и положил скачанный `selections.yaml` в папку `07a_WIREFRAME/`. Также должен быть готов `tokens.json` из этапа 05.

Запускается автоматически через `/landing-go` (рекомендуется) или вручную командой `/landing-compose`.

## Что на вход / на выход

**Вход (все три обязательны):**
- `07_ПРОТОТИП/prototype.yaml` — машиночитаемый прототип с текстами
- `07a_WIREFRAME/selections.yaml` — выбор вариантов блоков пользователем
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, типографика, отступы)

**Выход:**
- `07b_COMPOSED/composed.html` — десктопная версия страницы с токенами и текстами
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/block-injection-log.md` — лог инъекции блоков (какой блок куда вставлен)

## Связанные концепты

- [[block-composer]] — агент, который выполняет фактическую сборку composed.html
- [[ux-composer]] — предшествующий агент этапа 07a, производит wireframe.html и selections.yaml
- [[prototype-importer]] — агент этапа 07, создаёт prototype.yaml как один из входов
- [[design-system-generator]] — агент этапа 05, создаёт tokens.json
- [[photo-curator]] — этап 07c, заполняет фото-плейсхолдеры после compose
- [[visual-curator]] — этап 07d, заполняет иконки и инфографику после compose
- [[landing-go]] — основная команда-оркестратор, вызывает /landing-compose автоматически
- [[block-composition]] — скилл, реализующий логику сборки

## Источник

- `commands/landing-compose.md`
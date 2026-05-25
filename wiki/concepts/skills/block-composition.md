---
type: skill
name: block-composition
sources: ["skills/block-composition/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: ["landing-compose", "block-composer", "landing-wireframe", "landing-prototype", "landing-design"]
tags: ["compose", "tokens", "html", "blocks", "07b"]
---

# Block Composition — Сборка composed.html

## Что делает
Собирает финальный HTML-файл лендинга из утверждённых блоков, подставляя дизайн-токены (цвета, шрифты) и реальные тексты из прототипа. Результат — готовый к вёрстке `composed.html` с мобильной версией.

## Когда вызывать / в каком этапе
Этап **07b**. Вызывается командой `/landing-compose` или агентом `block-composer` после того, как пользователь утвердил варианты блоков в `wireframe.html` и сохранил `selections.yaml`. До этого должны быть готовы: прототип (07a), дизайн-система (05).

## Что на вход / на выход

**Входные артефакты:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура и тексты прототипа
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, отступы)
- `block-library/` — общая библиотека шаблонов блоков

**Выходные артефакты:**
- `<project>/07b_COMPOSED/composed.html` — десктопная версия
- `<project>/07b_COMPOSED/composed-mobile.html` — мобильная версия
- `<project>/07b_COMPOSED/block-injection-log.md` — лог подстановки блоков

## Связанные концепты
- [[landing-compose]] — slash-команда, которая запускает этот скилл
- [[landing-wireframe]] — предыдущий этап (07a), формирует `selections.yaml`
- [[landing-prototype]] — этап разбора прототипа, даёт `prototype.yaml`
- [[landing-design]] — этап дизайн-системы (05), даёт `tokens.json`
- [[block-composer]] — агент, использующий этот скилл для сборки

## Источник
- `skills/block-composition/SKILL.md`
---
type: skill
name: block-composition
sources: ["skills/block-composition/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "07b"
uses: ["landing-compose", "block-composer", "landing-wireframe", "landing-prototype", "landing-design"]
tags: ["compose", "tokens", "html", "blocks", "stage-07b"]
---

# Block Composition — Сборка composed.html

## Что делает
Берёт выбранные блоки из wireframe, подставляет в них дизайн-токены и тексты из прототипа, и собирает итоговый HTML-файл страницы — готовый к визуальной проверке перед вёрсткой.

## Когда вызывать / в каком этапе
Этап **07b**. Вызывается командой `/landing-compose` или агентом `block-composer` после того, как пользователь подтвердил выбор вариантов блоков в `wireframe.html` и положил `selections.yaml` в папку `07a_WIREFRAME/`.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура и тексты страницы
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, отступы
- `block-library/` — общая библиотека блоков

**Выход:**
- `<project>/07b_COMPOSED/composed.html` — десктопная версия страницы
- `<project>/07b_COMPOSED/composed-mobile.html` — мобильная версия
- `<project>/07b_COMPOSED/block-injection-log.md` — лог подстановки блоков

## Скрипты

| Скрипт | Что делает |
|---|---|
| `validate-selections.py` | Проверяет корректность `selections.yaml` |
| `inject-tokens.py` | Заменяет CSS-переменные в шаблонах на значения из `tokens.json` |
| `inject-content.py` | Подставляет тексты, заголовки и CTA из `prototype.yaml` |
| `compose-blocks.py` | Финальная сборка `composed.html` и `composed-mobile.html` |

## Связанные концепты
- [[landing-compose]] — slash-команда, которая запускает этот скилл
- [[landing-wireframe]] — предыдущий этап, где пользователь выбирает варианты блоков
- [[landing-prototype]] — этап парсинга прототипа, поставляет `prototype.yaml`
- [[landing-design]] — этап дизайн-системы, поставляет `tokens.json`
- [[block-composer]] — агент, использующий этот скилл внутри оркестратора

## Источник
- `skills/block-composition/SKILL.md`
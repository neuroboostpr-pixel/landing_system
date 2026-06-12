---
slug: block-composition
type: skill
name: "Block Composition — сборка composed.html"
stage: "07b"
tags: [compose, tokens, blocks, html, wireframe, prototype]
triggers: [landing-compose]
inputs:
  - "<project>/07_ПРОТОТИП/prototype.yaml"
  - "<project>/07a_WIREFRAME/selections.yaml"
  - "<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json"
  - "block-library/"
outputs:
  - "<project>/07b_COMPOSED/composed.html"
  - "<project>/07b_COMPOSED/composed-mobile.html"
  - "<project>/07b_COMPOSED/block-injection-log.md"
pre_reqs: [design-system-generator]
related: [block-composer, design-system-generator]
sources: ["skills/block-composition/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Block Composition — сборка composed.html

## Что делает

Скилл собирает финальный `composed.html` (и мобильную версию) из блоков, которые пользователь выбрал на этапе wireframe. Последовательно валидирует `selections.yaml`, подставляет CSS-переменные из `tokens.json` в шаблоны блоков, затем заменяет визуальные плейсхолдеры реальными текстами и CTA из `prototype.yaml`. На выходе — готовый к ревью HTML-файл с правильной дизайн-системой и прототипными текстами; реальные фото и иконки на этом этапе ещё не вставлены.

## Когда вызывается

Вызывается вручную командой `/landing-compose` после того как пользователь выбрал варианты блоков в `wireframe.html` и положил скачанный `selections.yaml` в папку `07a_WIREFRAME/`. Также используется агентом `block-composer` внутри оркестратора (этап PR-D).

## Вход → выход

**Вход:** `prototype.yaml` с контентом, `selections.yaml` с выбранными вариантами блоков, `tokens.json` дизайн-системы, исходные HTML-шаблоны из общего `block-library/`.

**Выход:** `composed.html` (десктоп) и `composed-mobile.html` — полноценная сборка с применёнными токенами и прототипными текстами; `block-injection-log.md` — лог подстановок для отладки.

## Failure modes

- `selections.yaml` не прошёл валидацию (`validate-selections.py` → exit non-0) — сборка прерывается, нужно перепровести wireframe или исправить файл руками.
- Отсутствует или повреждён `tokens.json` — `inject-tokens.py` не может подставить CSS-переменные, composed.html генерируется без брендинга.
- Блок из `selections.yaml` не найден в `block-library/` — `compose-blocks.py` выбрасывает ошибку, итоговый файл не создаётся.
- Поле из `prototype.yaml` не совпадает с плейсхолдером в шаблоне блока — текст остаётся как плейсхолдер, ошибка не всегда заметна без проверки `block-injection-log.md`.
- Hard gate 07b не закрывается, если `verify-composed-premium.sh` возвращает exit non-0 — 13 premium-фич должны присутствовать в `composed.html`.

## Related

- [[block-composer]] — агент, который вызывает скилл в контексте оркестратора и доводит composed.html до соответствия premium-чеклисту
- [[design-system-generator]] — генерирует `tokens.json`, без которого невозможна токен-подстановка на этом этапе
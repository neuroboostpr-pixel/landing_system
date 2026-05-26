---
slug: landing-compose
type: command
name: "/landing-compose — Сборка composed.html"
stage: "07b"
tags: [compose, wireframe, tokens, html, stage-07b]
triggers: [landing-compose]
inputs:
  - 07_ПРОТОТИП/prototype.yaml
  - 07a_WIREFRAME/selections.yaml
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
outputs:
  - 07b_COMPOSED/composed.html
  - 07b_COMPOSED/composed-mobile.html
  - 07b_COMPOSED/block-injection-log.md
pre_reqs: [wireframe-rendering, design-tokens-generation, prototype-import]
related:
  - block-composer
  - block-composition
  - wireframe-rendering
  - design-tokens-generation
  - prototype-import
  - landing-orchestrator
sources: ["commands/landing-compose.md"]
updated: 2026-05-26
---

# /landing-compose — Сборка composed.html

## Что делает

Команда запускает этап **07b_COMPOSED**: собирает финальный HTML-файл лендинга, подставляя в него токены дизайн-системы (`tokens.json`) и контент из выбранных wireframe-блоков (`selections.yaml`). Передаёт основную работу агенту `block-composer`, который инжектирует шрифты, цвета, отступы и текстовый контент из прототипа. Визуальные плейсхолдеры (фото, иконки, инфографика) на этом этапе **не заменяются** — они остаются как `[SLOT: ...]` до прохождения этапов 07c и 07d.

## Когда вызывается

Вызывается вручную командой `/landing-compose` или автоматически через `/landing-go`. Условие запуска: в папке `07a_WIREFRAME/` должен лежать `selections.yaml` (результат утверждения вариантов в wireframe.html), а в `05_ДИЗАЙН-СИСТЕМА/` — `tokens.json`. Без этих файлов команда завершится с ошибкой.

## Вход → выход

**Вход:** `prototype.yaml` (структура блоков и тексты), `selections.yaml` (выбранные варианты wireframe-блоков), `tokens.json` (цвета, типографика, отступы дизайн-системы).

**Выход:** `07b_COMPOSED/composed.html` — полная страница лендинга с токенами и текстами, но с визуальными плейсхолдерами; `composed-mobile.html` — мобильная версия; `block-injection-log.md` — лог того, какие блоки были инжектированы и с каким результатом.

## Failure modes

- `selections.yaml` отсутствует или не скачан из `wireframe.html` — команда останавливается с требованием пройти этап 07a.
- `tokens.json` не найден или повреждён — блоки собираются без CSS-переменных, визуальный результат неверный.
- `prototype.yaml` содержит блоки без соответствий в `selections.yaml` — `block-composer` логирует пропущенные блоки, плейсхолдер остаётся пустым.
- `verify-composed-premium.sh` возвращает ненулевой exit-код — этап 07b не закрывается (HARD GATE), нужна доработка `composed.html`.
- Команда запущена вручную при незавершённых предыдущих этапах — `landing-orchestrator` может перезаписать артефакты при следующем `/landing-go`.

## Related

- [[block-composer]] — агент, выполняющий сборку блоков
- [[block-composition]] — скилл сборки composed.html
- [[wireframe-rendering]] — предыдущий этап (07a), поставляет selections.yaml
- [[design-tokens-generation]] — поставляет tokens.json
- [[prototype-import]] — поставляет prototype.yaml
- [[landing-orchestrator]] — вызывает команду автоматически в рамках полного pipeline
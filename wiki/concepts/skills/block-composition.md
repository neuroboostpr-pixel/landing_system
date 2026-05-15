---
type: skill
name: block-composition
sources: ["skills/block-composition/SKILL.md"]
updated: 2026-05-15
triggers: ["/landing-compose", "собрать composed.html", "скомпоновать лендинг", "этап 07b"]
stage: "07b"
uses: ["block-composer", "prototype-import", "wireframe-rendering", "design-tokens-generation", "landing-compose"]
tags: ["compose", "blocks", "tokens", "html", "07b", "assembly"]
---

# Block Composition — сборка итогового HTML лендинга

## Что делает

Берёт утверждённые блоки из wireframe, дизайн-токены и тексты из прототипа — и собирает из них единый HTML-файл лендинга (`composed.html`). Это финальная сборка перед тем, как добавить реальные фото и иконки.

## Когда вызывать / в каком этапе

Этап **07b**. Запускается командой `/landing-compose` после того, как:
1. Пользователь выбрал варианты блоков в `wireframe.html` и сохранил `selections.yaml` в `07a_WIREFRAME/`.
2. Готовы дизайн-токены (`tokens.json`) из этапа 05.
3. Импортирован прототип (`prototype.yaml`) из этапа 07.

Выполняется агентом **block-composer**. HARD GATE 07b не закрывается, пока скрипт `scripts/verify-composed-premium.sh` не вернёт exit 0 (13 premium-фич обязательны).

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура и тексты лендинга
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, отступы
- `block-library/` — общая библиотека HTML-шаблонов блоков

**Выход:**
- `<project>/07b_COMPOSED/composed.html` — desktop-версия лендинга
- `<project>/07b_COMPOSED/composed-mobile.html` — мобильная версия
- `<project>/07b_COMPOSED/block-injection-log.md` — лог подстановок

Визуальный контент (фото, иконки, инфографика) на этом этапе остаётся в виде подписанных плейсхолдеров — они заполняются на этапах 07c (PR-B) и 07d (PR-C).

## Скрипты

Скилл использует четыре вспомогательных скрипта:
- `scripts/validate-selections.py` — проверить корректность `selections.yaml`
- `scripts/inject-tokens.py` — подставить CSS-переменные из `tokens.json`
- `scripts/inject-content.py` — вставить заголовки, тексты и CTA из `prototype.yaml`
- `scripts/compose-blocks.py` — собрать финальный `composed.html`

## Связанные концепты

- [[block-composer]] — агент, выполняющий сборку на этапе 07b
- [[prototype-import]] — поставляет `prototype.yaml` со структурой и текстами
- [[wireframe-rendering]] — этап 07a, производит `selections.yaml` с выбранными блоками
- [[design-tokens-generation]] — этап 05, производит `tokens.json` с дизайн-токенами
- [[landing-compose]] — slash-команда, запускающая этот скилл
- [[photo-curation]] — этап 07c, заполняет фото-плейсхолдеры в `composed.html`
- [[visual-generation]] — этап 07d, заполняет иконки и инфографику

## Источник

- `skills/block-composition/SKILL.md`
---
type: agent
name: block-composer
sources: ["agents/block-composer.md"]
updated: 2026-05-20
triggers: []
stage: "07b"
uses:
  - block-composition
  - prototype-importer
  - ux-composer
  - photo-curator
  - visual-curator
  - landing-compose
  - landing-orchestrator
tags: ["compose", "html", "design-tokens", "premium", "07b"]
---

# block-composer — Сборка финального макета (Stage 07b)

## Что делает

Собирает `composed.html` и `composed-mobile.html` — цветной HTML-макет лендинга с реальными текстами из прототипа и дизайн-токенами бренда. Фотографии, иконки и инфографика остаются в виде пронумерованных заглушек — их заполняют PR-B (фото) и PR-C (визуалы).

## Когда вызывать / в каком этапе

Запускается автоматически через `/landing-compose` или `/landing-go` на **этапе 07b**. Предусловия:
- `.landing-state.yaml` → `current_stage == 07c_composed`
- Этап 07a (wireframe) закрыт: в `07a_WIREFRAME/` лежит `selections.yaml`
- Этап 05 (design-system) закрыт: в `05_ДИЗАЙН-СИСТЕМА/` лежит `tokens.json`
- Прототип импортирован: в `07_ПРОТОТИП/` лежит `prototype.yaml`

Физический HARD GATE: хук `enforce_stage_gate.py` заблокирует Write/Edit, если предшественники не закрыты.

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — тексты и структура блоков (неприкосновенны!)
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (цвета, шрифты, тени)
- `block-library/` — общая библиотека HTML-шаблонов блоков
- `docs/standards/premium-07b-checklist.md` — 13 обязательных премиум-фич

**Выход:**
- `07b_COMPOSED/composed.html` — главный полноцветный макет
- `07b_COMPOSED/composed-mobile.html` — мобильная версия
- `07b_COMPOSED/composed-mobile-preview.html` — iframe iPhone/iPad для визуальной проверки
- `07b_COMPOSED/composed-explained.md` — отчёт что собрано и какие фичи добавлены

**HARD GATE выхода:** `scripts/verify-composed-premium.sh` должен вернуть `exit 0`. Если хоть одна из 13 фич отсутствует (glassmorphism nav, parallax, IntersectionObserver, слайдер, lightbox, count-up и др.) — этап не закрывается.

## Правило сохранения контента (PR-H)

Все тексты из `prototype.yaml` переносятся **дословно**. Заголовки, CTA, абзацы нельзя «улучшать» молча. Если агент хочет что-то изменить — обязан спросить пользователя. При закрытии этапа `scripts/verify-content-preserved.sh` проверяет соответствие.

## Связанные концепты

- [[block-composition]] — скилл с compose-скриптами (validate-selections.py, compose-blocks.py)
- [[ux-composer]] — предшественник: генерирует selections.yaml на этапе 07a
- [[prototype-importer]] — готовит prototype.yaml на этапе 07
- [[photo-curator]] — PR-B: заполняет фото-заглушки после 07b
- [[visual-curator]] — PR-C: заполняет иконки/инфографику после 07b
- [[landing-compose]] — команда-триггер для этого агента
- [[landing-orchestrator]] — вызывает агента в рамках общего pipeline

## Источник

- `agents/block-composer.md`
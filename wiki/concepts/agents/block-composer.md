---
slug: block-composer
type: agent
name: "Block Composer (Сборка composed.html)"
stage: "07b"
tags: [compose, html, design-tokens, prototype, wireframe, premium]
triggers: [landing-compose]
inputs:
  - 07_ПРОТОТИП/prototype.yaml
  - 07a_WIREFRAME/selections.yaml
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - block-library/
outputs:
  - 07b_COMPOSED/composed.html
  - 07b_COMPOSED/composed-mobile.html
  - 07b_COMPOSED/composed-explained.md
gates:
  - verify-composed-premium
  - content-preserved
pre_reqs:
  - landing-wireframe
  - landing-design
related:
  - landing-compose
  - landing-prototype
  - landing-photos
  - landing-visuals
  - landing-build
sources:
  - agents/block-composer.md
  - docs/standards/premium-07b-checklist.md
updated: 2026-05-26
confidence:
  triggers: low
---

# Block Composer (Сборка composed.html)

## Что делает

Собирает финальный HTML-макет лендинга из трёх утверждённых артефактов: варианты блоков из `selections.yaml`, тексты из `prototype.yaml` и дизайн-токены из `tokens.json`. Подставляет реальные заголовки, CTA и параграфы в выбранные wireframe-блоки, инъектирует CSS-переменные бренда. Визуальный контент (фото, иконки, инфографика) остаётся visible-placeholder'ами — их заполнят PR-B и PR-C. Дополнительно проверяет соответствие 13 обязательным премиум-фичам (glassmorphism, parallax, слайдеры, lightbox, count-up и др.) через `verify-composed-premium.sh`.

## Когда вызывается

Запускается командой `/landing-compose` (скилл `landing-compose`), когда `.landing-state.yaml` фиксирует `current_stage == 07c_composed`. Предусловие: этапы 05 (design-system, наличие `tokens.json`) и 07a (wireframe, наличие `selections.yaml`) должны быть закрыты. Harness-хук `enforce_stage_gate.py` физически блокирует Write/Edit, если предшественники не approved.

## Вход → выход

**Вход:** `prototype.yaml` с дословными текстами всех блоков, `selections.yaml` с выбранными вариантами из wireframe, `tokens.json` с дизайн-токенами (цвета, шрифты, тени), блоки из общей `block-library/`.

**Выход:** `07b_COMPOSED/composed.html` — полноцветный макет с токенами и текстами; `composed-mobile.html` — iframe-превью для iPhone/iPad; `composed-explained.md` — RU-описание что собрано и какие премиум-фичи добавлены.

## Чем закрывается этап (gates)

- **verify-composed-premium** — `verify-composed-premium.sh` возвращает exit 0: все 13 премиум-фич присутствуют (CSS-переменные, clamp(), sticky nav, parallax, IntersectionObserver, градиентный текст, hover-lift, слайдер, lightbox, count-up, smooth scroll, pulse-dot, reveal-классы).
- **content-preserved** — `verify-content-preserved.sh` подтверждает: тексты в composed.html совпадают с `prototype.yaml` дословно, порядок блоков не нарушен.

## Failure modes

- `selections.yaml` ссылается на блок, отсутствующий в `catalog.yaml` — агент останавливается, сообщает пользователю.
- `current_stage` в `.landing-state.yaml` не равен `07c_composed` — агент останавливается до устранения.
- Premim-verify возвращает ненулевой код — этап не закрывается, агент дорабатывает `composed.html` и прогоняет снова.
- Тексты в HTML расходятся с `prototype.yaml` (тихое «улучшение») — HARD GATE content-preserved блокирует закрытие этапа.
- `tokens.json` содержит неполный набор переменных — CSS-переменные в `:root` будут неполными, визуал деградирует.

## Related

- [[landing-compose]] — скилл/команда, которая вызывает этого агента
- [[landing-prototype]] — создаёт `prototype.yaml`, который агент читает дословно
- [[landing-wireframe]] — создаёт `selections.yaml` с выбранными вариантами блоков
- [[landing-photos]] — PR-B, заполняет фото-placeholder'ы после compose
- [[landing-visuals]] — PR-C, заполняет иконки и инфографику после compose
- [[landing-build]] — следующий этап: сборка WP-темы из готового composed.html
---
type: agent
name: block-composer
sources: ["agents/block-composer.md"]
updated: 2026-05-15
triggers: []
stage: "07b"
uses: ["block-composition", "ui-ux-pro-max", "prototype-importer", "ux-composer", "photo-curator", "visual-curator"]
tags: ["compose", "html", "design-tokens", "landing", "stage-07b"]
---

# block-composer — сборка финального макета (этап 07b)

## Что делает

Собирает `composed.html` — итоговый цветной макет лендинга с реальными текстами, CTA и дизайн-токенами. Фото, иконки и инфографика на этом этапе остаются в виде подписанных заглушек: их заполнят агенты PR-B и PR-C позже.

## Когда вызывать / в каком этапе

Запускается на **этапе 07b** командой `/landing-compose` или оркестратором `landing-orchestrator`.  
Вызывать только после того, как утверждены:
- этап 07a (wireframe + `selections.yaml` от пользователя),
- этап 05 (дизайн-система, `tokens.json`),
- этап 07 (прототип, `prototype.yaml`).

## Что на вход / на выход

**Вход:**
- `<project>/07_ПРОТОТИП/prototype.yaml` — структура прототипа с текстами
- `<project>/07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков
- `<project>/05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, тени
- `block-library/` — общая библиотека блоков
- `docs/standards/premium-07b-checklist.md` — обязательный чеклист из 13 премиум-фич

**Выход:**
- `07b_COMPOSED/composed.html` — десктопный макет
- `07b_COMPOSED/composed-mobile.html` — мобильный макет
- `07b_COMPOSED/composed-mobile-preview.html` — iframe-превью iPhone/iPad
- `07b_COMPOSED/composed-explained.md` — описание что собрано и какие фичи включены

**Hard gate:** перед завершением этапа агент обязан прогнать `scripts/verify-composed-premium.sh`. Если скрипт вернул exit code ≠ 0 — этап не закрыт, агент дорабатывает `composed.html`.

## Ключевые правила

Агент реализует 13 обязательных премиум-фич: CSS-переменные в `:root`, `clamp()` для типографики, glassmorphism-навигация, parallax-герой, `IntersectionObserver`, `.reveal`-анимации, gradient-text, hover lift на карточках, JS-слайдер, lightbox с клавиатурой, count-up анимация, smooth scroll, pulse-dot на live-бейджах.

Если `selections.yaml` ссылается на блок, отсутствующий в `catalog.yaml` — агент останавливается и сообщает пользователю.

## Связанные концепты

- [[block-composition]] — скилл с Python-скриптами `compose-blocks.py` и `validate-selections.py`
- [[ui-ux-pro-max]] — источник стилевых hint'ов из `meta.yaml` блоков
- [[ux-composer]] — создаёт `selections.yaml` на этапе 07a (wireframe)
- [[prototype-importer]] — создаёт `prototype.yaml` на этапе 07
- [[photo-curator]] — PR-B: заполняет photo-placeholders после 07b
- [[visual-curator]] — PR-C: заполняет icon/infographic-placeholders после 07b

## Источник

- `agents/block-composer.md`
---
type: agent
name: block-composer
sources: ["agents/block-composer.md"]
updated: 2026-05-15
triggers: []
stage: "07b"
uses: ["prototype-importer", "ux-composer", "design-system-generator", "photo-curator", "visual-curator", "block-composition"]
tags: ["compose", "html", "design-tokens", "premium", "07b"]
---

# block-composer — Сборка цветного макета лендинга

## Что делает

Берёт утверждённые блоки из wireframe, подставляет в них реальные тексты из прототипа и цвета/шрифты из дизайн-системы — и собирает финальный цветной HTML-макет (`composed.html`). Фото, иконки и инфографика пока остаются текстовыми плейсхолдерами — их заполнят агенты PR-B и PR-C на следующих этапах.

## Когда вызывать / в каком этапе

Этап **07b (Block Compose)**. Вызывается после того, как пользователь утвердил wireframe и в папке `07a_WIREFRAME/` появился `selections.yaml`. Запускается командой `/landing-compose` или через `landing-orchestrator`.

## Что на вход / на выход

**Входные артефакты:**
- `07_ПРОТОТИП/prototype.yaml` — финальные тексты и CTA (неприкосновенны)
- `07a_WIREFRAME/selections.yaml` — выбранные пользователем варианты блоков
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, шрифты, отступы
- `block-library/` — общая библиотека шаблонов блоков

**Выходные артефакты:**
- `07b_COMPOSED/composed.html` — цветной макет с реальными текстами и плейсхолдерами для визуала
- `07b_COMPOSED/composed-mobile-preview.html` — превью для iPhone/iPad
- `07b_COMPOSED/composed-explained.md` — текстовый отчёт о собранных фичах (RU)

## Ключевые правила

**Контент прототипа — неприкосновенен (PR-H).** Заголовки, CTA и абзацы переносятся дословно. Любое изменение текста — только с явного разрешения пользователя после открытого вопроса. HARD GATE 07c проверяет это скриптом `verify-content-preserve.sh`.

**Премиум-стандарт обязателен.** Каждый `composed.html` должен содержать 13 обязательных фич: CSS-переменные в `:root`, `clamp()` для типографики, glassmorphism nav, parallax hero, IntersectionObserver, `.reveal`-классы, gradient text, hover lift на карточках, слайдер, lightbox с keyboard navigation, count-up анимация, smooth scroll, pulse-dot на бейджах. Проверяется скриптом `verify-composed-premium.sh` — HARD GATE 07b не закрывается при exit code ≠ 0.

## Связанные концепты

- [[prototype-importer]] — поставляет `prototype.yaml` с неизменяемыми текстами
- [[ux-composer]] — поставляет `selections.yaml` из wireframe-этапа
- [[design-system-generator]] — поставляет `tokens.json` с цветами и шрифтами
- [[block-composition]] — скилл с Python-скриптами `compose-blocks.py` и `validate-selections.py`
- [[photo-curator]] — PR-B: заменяет фото-плейсхолдеры реальными изображениями
- [[visual-curator]] — PR-C: заменяет icon/infographic-плейсхолдеры PNG-файлами

## Источник

- `agents/block-composer.md`
---
slug: wp-gutenberg-block-builder
type: skill
name: "WP Gutenberg Block Builder"
stage: "08"
tags: [wordpress, lazy-blocks, gutenberg, theme, stage-08, code-generation]
triggers: [landing-build]
inputs:
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 06_СТЕК/design-stack.yaml
  - 07_КОНТЕНТ/final-copy.md
  - 08_КОД/block-spec.yaml
outputs:
  - 08_КОД/wp-theme/style.css
  - 08_КОД/wp-theme/functions.php
  - 08_КОД/wp-theme/assets/css/main.css
  - 08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php
  - 08_КОД/page-content.html
pre_reqs: [design-system-generator, stack-planner, content-writer]
related:
  - wp-builder
  - frontend-builder
  - block-composer
  - landing-orchestrator
  - wp-deployer
  - design-system-generator
sources: ["skills/wp-gutenberg-block-builder/SKILL.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# WP Gutenberg Block Builder

## Что делает

Скилл генерирует все WordPress-артефакты для этапа 08: каркас темы (`style.css`, `functions.php`, `assets/css/main.css`), PHP-шаблоны блоков в пространстве имён `lazyblock/` через Lazy Blocks Free, регистрацию блоков через `lazyblocks()->add_block()` и итоговый файл `page-content.html` с Gutenberg-разметкой для деплоя. Дополнительно подключает visual patterns (`scroll-reveal`, `ambient-mesh-bg`, `paper-texture` и др.) и style moods (`editorial-warm`, `swiss-modernist` и т.д.) в зависимости от `animation_mode` и `style_mood` в `tokens.json`. Строго Lazy Blocks Free — без ACF Pro и без `block.json`.

## Когда вызывается

Запускается оркестратором (`landing-orchestrator`) в составе команды `/landing-build` после того, как утверждены этапы 05 (дизайн-система), 06 (стек), 07 (контент) и заполнен `08_КОД/block-spec.yaml`. Может вызываться повторно при регенерации темы — существующие `block.php` не перезаписываются.

## Вход → выход

**Вход:** `tokens.json` с цветами и `animation_mode`/`style_mood`, `design-stack.yaml`, `final-copy.md`, `block-spec.yaml` с описанием всех блоков лендинга.

**Выход:** готовая WP-тема в `08_КОД/wp-theme/` (scaffold + один `block.php` на каждый блок) и `08_КОД/page-content.html` — seed-разметка фронтальной страницы с плейсхолдерами изображений для последующей замены при деплое.

## Failure modes

- **Отсутствует `block-spec.yaml`** — все генераторы 2–5 падают с явным сообщением об ошибке.
- **Вложенные repeaters в блоке** — Lazy Blocks Free не поддерживает их; нужен паттерн section+card с InnerBlocks.
- **Значение toggle-поля строкой `"true"`** вместо YAML-булева `true` — генератор отклоняет спеку.
- **Accent-цвет близок к #6366f1 (indigo)** — нарушает anti-AI-slop правила; скилл обязан предложить альтернативу.
- **Блок читается напрямую из `assets/template.html`** минуя `block-loader.py` — сломает чтение новых блоков в формате `index.html + styles.css`.

## Related

- [[wp-builder]] — агент, вызывающий генераторы этапа 08 и управляющий всей сборкой темы
- [[frontend-builder]] — общий термин для фронтенд-сборки; wp-gutenberg-block-builder — его конкретная реализация
- [[block-composer]] — составляет `composed.html` на этапе 07b, из которого вырастает `block-spec.yaml`
- [[landing-orchestrator]] — диспатчит скилл в нужный момент pipeline
- [[wp-deployer]] — принимает результат (`page-content.html`, тему) и деплоит на Beget
- [[design-system-generator]] — производит `tokens.json`, от которого зависит выбор patterns и style mood
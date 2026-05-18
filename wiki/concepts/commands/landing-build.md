---
type: command
name: landing-build
sources: ["commands/landing-build.md"]
updated: 2026-05-15
triggers:
  - "собрать WordPress-тему"
  - "сгенерировать код лендинга"
  - "запустить этап 08"
  - "build после content"
  - "сгенерировать блоки Gutenberg"
stage: "08"
uses:
  - wp-builder
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - landing-content
  - landing-design
  - landing-stack
tags:
  - wordpress
  - build
  - lazy-blocks
  - gutenberg
  - stage-08
---

# /landing-build — Сборка WordPress-темы и кода лендинга

## Что делает

Генерирует полноценную WordPress-тему с Lazy Blocks, подключает формы и CRM-интеграции, настраивает аналитику и SEO. На выходе — готовый к деплою код и статический `build-preview.html` для финального утверждения.

## Когда вызывать / в каком этапе

Этап **08_build**. Вызывается после того, как `content-writer` создал `07_КОНТЕНТ/final-copy.md` и пользователь его одобрил. Перед запуском система проверяет: пройден onboarding, закрыты гейты предыдущих этапов, присутствует `08_КОД/block-spec.yaml`.

## Что на вход / на выход

**Обязательные входные артефакты:**
- `07_КОНТЕНТ/final-copy.md` — финальные тексты (от `/landing-content`)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (от `/landing-design`)
- `06_СТЕК/design-stack.yaml` — выбранный стек (от `/landing-stack`)
- `08_КОД/block-spec.yaml` — спецификация блоков (заполняется из шаблона)

**Выходные артефакты:**
- `08_КОД/wp-theme/` — полная WP-тема (PHP, CSS, JS, ресурсы)
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — PHP-шаблон на каждый блок
- `08_КОД/wp-theme/functions.php` — с регистрацией блоков и аналитикой
- `08_КОД/wp-theme/assets/css/main.css` — CSS с патчами InnerBlocks
- `08_КОД/wp-theme/assets/js/main.js`, `sliders.js`, `animations.js`, `counters.js` — JS-инициализация
- `08_КОД/wp-theme/assets/js/popup.js` — встроенный попап
- `08_КОД/page-content.html` — Gutenberg-разметка для seed страницы
- `08_КОД/build-preview.html` — статический превью для утверждения
- `11_АНАЛИТИКА/` — конфиги Яндекс.Метрики, цели, UTM-шаблоны
- `12_SEO/` — meta-tags, Schema.org JSON-LD, robots.txt, ключевые слова

**Pipeline (11 шагов):**
1. `generate-wp-blocks.py` — scaffold темы и Lazy Blocks
2. Агент `integrations-engineer` — Fluent Forms + Telegram/CRM webhook
3. Агент `analytics-engineer` — Яндекс.Метрика в functions.php
4. Агент `seo-optimizer` — SEO-мета и Schema.org
5. `bundle-assets.py` — шрифты, иконки, фото
6. `render-build-preview.py` — статический превью
7. `generate-popup.py` — попап-система
8. `generate-js-init.py` — JS-файлы
9. `generate-analytics.py` — YM + GTM
10. `generate-integrations.py` — CRM-интеграции
11. **HARD GATE** — показ превью и ожидание одобрения перед этапом 09

## Связанные концепты

- [[landing-content]] — предшествующий этап, поставляет `final-copy.md`
- [[landing-design]] — поставляет `tokens.json`
- [[landing-stack]] — поставляет `design-stack.yaml`
- [[wp-builder]] — агент, генерирующий PHP-шаблоны блоков
- [[integrations-engineer]] — агент форм и CRM-вебхуков
- [[analytics-engineer]] — агент аналитики Яндекс.Метрика
- [[seo-optimizer]] — агент SEO-разметки и Schema.org
- [[landing-deploy]] — следующий этап после одобрения превью

## Источник

- `commands/landing-build.md`
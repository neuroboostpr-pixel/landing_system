---
type: command
name: landing-build
sources: ["commands/landing-build.md"]
updated: 2026-05-25
triggers:
  - "сгенерировать WordPress-тему"
  - "собрать код лендинга"
  - "запустить билд"
  - "построить wp-тему и блоки"
  - "этап 08"
stage: "08"
uses:
  - landing-content
  - landing-design
  - landing-stack
  - landing-deploy
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - landing-orchestrator
tags: [build, wordpress, lazy-blocks, gutenberg, stage-08]
---

# /landing-build — Генерация WordPress-темы и кода лендинга

## Что делает

Автоматически собирает полноценную WordPress-тему: PHP-шаблоны Lazy Blocks, CSS/JS, попапы, аналитику, SEO и интеграции с CRM — всё из утверждённого контента и дизайн-системы. В конце выдаёт статический preview для финального одобрения перед деплоем.

## Когда вызывать / в каком этапе

Этап **08_КОД**. Вызывается после того, как пользователь утвердил контент (`/landing-content`) и дизайн-систему (`/landing-design`). Перед запуском система проверяет:

- пройден onboarding (`setup-flag.sh`);
- предыдущие этапы закрыты (`gate-check.sh --stage 08_build`);
- существует `08_КОД/block-spec.yaml` — без него генераторы 2–5 падают с ошибкой.

После утверждения пользователем результата вызывается `gate-check.sh --approve`, закрывающий этап и открывающий путь к [[landing-deploy]].

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/final-copy.md` — финальные тексты от [[landing-content]]
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены от [[landing-design]]
- `06_СТЕК/design-stack.yaml` — стек от [[landing-stack]]
- `08_КОД/block-spec.yaml` — спецификация блоков (заполняется из примера)

**Выход:**
- `08_КОД/wp-theme/` — полная WP-тема (PHP + CSS + JS + ассеты)
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — шаблоны блоков Lazy Blocks
- `08_КОД/wp-theme/functions.php` — с регистрацией блоков и хуками
- `08_КОД/wp-theme/assets/css/main.css` — патчи InnerBlocks
- `08_КОД/wp-theme/assets/js/` — `main.js`, `sliders.js`, `animations.js`, `counters.js`, `popup.js`
- `08_КОД/page-content.html` — Gutenberg-разметка для seed-страницы
- `08_КОД/build-preview.html` — статический превью для HARD GATE
- `11_АНАЛИТИКА/` — конфиги Метрики, UTM-шаблоны, цели
- `12_SEO/` — мета-теги, structured-data, robots.txt

## Связанные концепты

- [[landing-content]] — поставляет `final-copy.md`, обязателен перед билдом
- [[landing-design]] — поставляет `tokens.json` и дизайн-систему
- [[landing-stack]] — поставляет `design-stack.yaml` с выбором стека
- [[landing-deploy]] — следующий этап после одобрения build-preview
- [[integrations-engineer]] — AI-агент, добавляет webhooks форм (Telegram/CRM)
- [[analytics-engineer]] — AI-агент, подключает Яндекс Метрику и GTM
- [[seo-optimizer]] — AI-агент, прописывает meta-теги и Schema.org
- [[landing-orchestrator]] — запускает landing-build в рамках полного pipeline

## Источник

- `commands/landing-build.md`
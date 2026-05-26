---
type: command
name: landing-build
sources: ["commands/landing-build.md"]
updated: 2026-05-26
triggers:
  - "собрать WordPress тему"
  - "сгенерировать код лендинга"
  - "запустить этап 08"
  - "сгенерировать блоки Lazy Blocks"
  - "собрать тему после контента"
stage: "08"
uses:
  - landing-content
  - landing-design
  - landing-stack
  - landing-orchestrator
  - integrations-engineer
  - analytics-engineer
  - seo-optimizer
  - landing-deploy
tags: ["build", "wordpress", "lazy-blocks", "stage-08", "theme"]
---

# Landing Build — сборка WordPress-темы (этап 08)

## Что делает

Генерирует полноценный WordPress-сайт из утверждённого контента и дизайн-системы: создаёт PHP-тему, регистрирует блоки Lazy Blocks, подключает CRM-интеграции, аналитику, SEO-разметку и выдаёт статический превью для финального утверждения перед деплоем.

## Когда вызывать / в каком этапе

Этап **08_КОД**. Вызывается после того, как пользователь утвердил `07_КОНТЕНТ/final-copy.md` (команда `/landing-content`). Запускать из папки проекта. Перед стартом автоматически проверяется онбординг, гейт этапа 08 и наличие `08_КОД/block-spec.yaml` — без него сборка останавливается.

Флаг `--cinematic` подключает GSAP/ScrollTrigger для кино-анимаций.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/final-copy.md` — финальный копирайтинг (этап 07)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — дизайн-токены (этап 05)
- `06_СТЕК/design-stack.yaml` — выбранный стек (этап 06)
- `08_КОД/block-spec.yaml` — спецификация блоков (заполняется из примера)

**Выход:**
- `08_КОД/wp-theme/` — полная WP-тема (PHP + CSS + JS + assets)
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — PHP-шаблон на каждый блок
- `08_КОД/wp-theme/functions.php` — регистрация блоков + аналитика + интеграции
- `08_КОД/wp-theme/assets/css/main.css` — стили с патчами InnerBlocks
- `08_КОД/page-content.html` — Gutenberg-разметка для главной страницы
- `08_КОД/wp-theme/assets/js/` — popup.js, main.js, sliders.js, animations.js, counters.js
- `08_КОД/build-preview.html` — статический превью для утверждения
- `11_АНАЛИТИКА/` — конфиг Метрики, цели, UTM-шаблоны
- `12_SEO/` — мета-теги, структурированные данные, robots.txt, ключевые слова

Финальный **HARD GATE** — команда показывает путь к `build-preview.html` и ждёт явного одобрения пользователя перед переходом к этапу 09 (деплой).

## Связанные концепты

- [[landing-content]] — поставляет `final-copy.md`, обязательный входной артефакт
- [[landing-design]] — поставляет `tokens.json` для генерации CSS
- [[landing-stack]] — поставляет `design-stack.yaml` с выбором технологий
- [[landing-deploy]] — следующий этап после утверждения превью
- [[integrations-engineer]] — агент, подключающий Fluent Forms и CRM-webhook
- [[analytics-engineer]] — агент, добавляющий Яндекс.Метрику и GTM
- [[seo-optimizer]] — агент, генерирующий Schema.org и мета-теги
- [[landing-orchestrator]] — вызывает `/landing-build` как часть общего pipeline

## Источник

- `commands/landing-build.md`
---
type: rule
name: premium-07b-checklist
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-15
triggers: []
stage: "07b"
uses:
  - block-composer
  - design-tokens-generation
  - content-writer
  - ux-composer
  - photo-curator
tags: ["quality", "checklist", "07b", "composed", "premium", "hard-gate"]
---

# Premium 07b — Чек-лист сборки composed.html

## Что делает

Устанавливает обязательные стандарты качества для этапа 07b: агент `block-composer` собирает `composed.html` только при выполнении всех пунктов. Гарантирует уровень «dubai-avto-liza», а не «средний AI-лендинг».

## Когда вызывать / в каком этапе

Передаётся агенту `block-composer` **перед** запуском сборки 07b. HARD GATE 07b не закрывается, пока скрипт `scripts/verify-composed-premium.sh` не вернёт `exit 0`. Если хотя бы один пункт не выполнен — сборка не начинается, оркестратор возвращает управление на предыдущий этап.

## Что на вход / на выход

**Вход (обязательные артефакты):**
- `00_БРИФ/brief.md` — ниша, ЦА, тон голоса
- `04_БРЕНД/brand-kit.md` — палитра + типографика
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — все CSS-переменные
- `07_КОНТЕНТ/final-copy.md` — реальные тексты по блокам
- `07a_WIREFRAME/selections.yaml` — список блоков с ID из библиотеки
- `07c_PHOTOS/photo-mapping.yaml` — привязка фото к слотам

**Выход (что должен создать `block-composer`):**
- `07b_COMPOSED/composed.html` — 60–150 KB, HTML+CSS+JS inline, ноль фреймворков
- `composed-mobile-preview.html` — iframe iPhone+iPad
- `composed-explained.md` — описание принятых решений

## Ключевые требования (сжато)

| Раздел | Что проверяется |
|---|---|
| **Архитектура** | Один файл, без React/Vue/jQuery/Bootstrap, только Google Fonts |
| **CSS-переменные** | Полный `:root` из `tokens.json`; хардкод цветов — запрещён |
| **Типографика** | `clamp()` на всех заголовках; Inter 300–900; gradient-text на акцентах |
| **Структура** | 11 обязательных блоков: nav→hero→social proof→models→features→why us→process→testimonials→FAQ→CTA form→footer |
| **Интерактив** | 10 эффектов: parallax, reveal-on-scroll, count-up, per-product slider, lightbox+keyboard, glassmorphism nav, hover-lift, scroll-top, smooth scroll, pulse-dot |
| **Mobile** | Breakpoints 768/1024px; все grid → 1 колонка; `clamp()` без ступенек |
| **Accessibility** | Семантические теги, `aria-label`, `alt`, контраст ≥ 4.5:1 |
| **Запрещено** | Эмодзи-иконки, inline-стили, хардкод цветов, сторонние JS-библиотеки |

Эталон-референс: `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` (1757 строк, 13 premium-фич).

## Связанные концепты

- [[block-composer]] — агент, который собирает `composed.html` по этому чек-листу
- [[design-tokens-generation]] — поставляет `tokens.json` с CSS-переменными
- [[content-writer]] — поставляет `final-copy.md` с текстами
- [[ux-composer]] — поставляет `selections.yaml` с выбранными блоками
- [[photo-curator]] — поставляет `photo-mapping.yaml` с привязкой фото
- [[block-composition]] — скилл, реализующий сборку composed.html
- [[landing-compose]] — команда, запускающая этап 07b

## Источник

- `docs/standards/premium-07b-checklist.md`
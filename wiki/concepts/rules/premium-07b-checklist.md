---
type: rule
name: premium-07b-checklist
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-26
triggers: []
stage: "07b"
uses: ["landing-compose", "landing-wireframe", "landing-photos", "landing-design", "landing-content"]
tags: ["07b", "composed", "premium", "checklist", "hard-gate", "css", "javascript", "responsive"]
---

# Premium 07b — Чек-лист сборки composed.html

## Что делает

Определяет обязательные стандарты качества для этапа 07b: как должен выглядеть и работать файл `composed.html`, чтобы лендинг соответствовал уровню премиум-продакшна, а не «среднего AI-лендинга».

## Когда вызывать / в каком этапе

Применяется на этапе **07b_COMPOSED** — перед запуском агента-сборщика и как HARD GATE перед закрытием этапа. `block-composer` обязан пройти все пункты чек-листа; этап не закрывается, пока `verify-composed-premium.sh` не вернёт exit 0. Если агент пропускает пункты — он обязан доработать `composed.html`, а не предлагать «и так сойдёт».

## Что на вход / на выход

**Вход (обязателен весь набор — иначе 07b не начинаем):**
- `00_БРИФ/brief.md` — ниша, ЦА, KPI, тон голоса
- `04_БРЕНД/brand-kit.md` — палитра и типографика
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — CSS-переменные
- `07_КОНТЕНТ/final-copy.md` — реальные тексты
- `07a_WIREFRAME/selections.yaml` — список блоков из библиотеки
- `02_МАТЕРИАЛЫ_КЛИЕНТА/inbox/` — минимум 15 реальных фото
- `07c_PHOTOS/photo-mapping.yaml` — привязка фото к слотам

**Выход:**
- `07b_COMPOSED/composed.html` — единый HTML+CSS+JS файл, 60–150 KB, без фреймворков
- `composed-explained.md` — описание принятых решений
- `composed-mobile-preview.html` — iframe-превью iPhone+iPad

## Ключевые требования

Чек-лист охватывает **20 групп требований**:

1. **Архитектура** — один inline-файл, только vanilla JS, Google Fonts, относительные пути к фото
2. **CSS-переменные** — полный набор `:root` из `tokens.json`, никаких хардкод-цветов
3. **Типографика** — `clamp()` на всех заголовках, Inter 300–900, letter-spacing
4. **Структура страницы** — 11 обязательных секций: sticky nav, hero, social proof, модели, фичи, «почему мы», процесс, отзывы, FAQ, CTA-форма, футер
5. **Сетка** — конкретные Grid/Flexbox правила для каждого блока
6. **10 интерактивных эффектов** — glassmorphism nav, parallax hero, IntersectionObserver reveal, count-up, per-product slider, lightbox с клавиатурой, hover lift, scroll-to-top, smooth scroll, pulse-dot бейдж
7. **Премиум-типографика** — gradient text, eyebrow, font-weight 900 на hero
8. **Hero** — полный список из 9 обязательных элементов
9. **Кнопки** — gold gradient + translateY hover
10. **Mobile responsive** — breakpoints 768px и 1024px, все grid → 1 колонка
11. **Семантика / accessibility** — `<nav>`, `<section>`, aria-label, контраст 4.5:1
12. **Запреты** — эмодзи как иконки, inline-стили, Bootstrap/jQuery/AOS
13–20. **PR-P дополнения** — scroll-driven анимации, backdrop-filter, mesh gradient, mix-blend-mode, `prefers-reduced-motion`, clip-path

**Эталон-референс:** `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` — 1757 строк, ~130 KB, все 20 premium-фич, реальные фото.

## Связанные концепты

- [[landing-compose]] — агент-сборщик, выполняющий требования этого чек-листа
- [[landing-wireframe]] — поставляет `selections.yaml` (список блоков) на вход 07b
- [[landing-photos]] — поставляет `photo-mapping.yaml` (привязка фото к слотам)
- [[landing-design]] — поставляет `tokens.json` с CSS-переменными
- [[landing-content]] — поставляет `final-copy.md` с реальными текстами

## Источник

- `docs/standards/premium-07b-checklist.md`
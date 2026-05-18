---
type: rule
name: premium-07b-checklist
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "design-system-generator", "content-writer", "ux-composer", "photo-curator"]
tags: ["quality", "checklist", "composed", "frontend", "premium"]
---

# Premium 07b Checklist — стандарт сборки composed.html

## Что делает
Обязательный чек-лист из 20 разделов, который задаёт планку качества для этапа **07b_COMPOSED**: если хоть один пункт не выполнен, HARD GATE не закрывается и агент не переходит к следующему этапу.

## Когда вызывать / в каком этапе
Применяется на этапе **07b** — перед тем как [[block-composer]] начинает сборку `composed.html`. Передаётся агенту на вход явно. Финальная проверка — через скрипт `scripts/verify-composed-premium.sh` (exit 0 = ОК).

## Что на вход / на выход

**Входные артефакты (все обязательны — иначе сборка не стартует):**
- `00_БРИФ/brief.md` — ниша, ЦА, тон голоса
- `04_БРЕНД/brand-kit.md` — палитра и типографика
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — CSS-переменные
- `07_КОНТЕНТ/final-copy.md` — реальные тексты
- `07a_WIREFRAME/selections.yaml` — выбранные блоки
- `02_МАТЕРИАЛЫ_КЛИЕНТА/inbox/` — минимум 15 реальных фото
- `07c_PHOTOS/photo-mapping.yaml` — маппинг фото к слотам

**Что проверяет чек-лист (13 секций + 7 PR-P):**
1. Архитектура — один HTML-файл 60–150 KB, без фреймворков
2. CSS-переменные (`:root`) — полный набор токенов цвета, теней, радиусов, анимаций
3. Типографика — `clamp()` на всех заголовках, Inter 300–900
4. Минимальный набор блоков — 11 секций (nav, hero, social proof, products, features, why us, process, testimonials, FAQ, CTA-form, footer)
5. Сетка — Grid + Flexbox с указанными пропорциями для каждого блока
6. Интерактивность — 10 обязательных эффектов: glassmorphism nav, parallax, reveal-on-scroll, count-up, per-product slider, lightbox, hover lift, scroll-to-top, smooth scroll, pulse-dot
7. Премиум-типографика — gradient text, eyebrow, font-weight 900
8. Hero — 9 обязательных элементов включая savings-строку и 2 CTA
9. Кнопки — gold gradient + translateY на hover
10. Mobile — breakpoints 768px и 1024px, все grid → 1 column
11. Семантика и accessibility — `<nav>`, aria-label, alt, контраст 4.5:1
12. Запреты — никаких эмодзи-иконок, inline-стилей, хардкод-цветов, jQuery/Swiper/AOS
13. Финальная проверка — Lighthouse Performance > 85, Accessibility > 90
14–20. PR-P (2026-05-16) — scroll-driven анимации, hover на всех интерактивах, backdrop-filter, mesh-gradient, mix-blend-mode, prefers-reduced-motion, clip-path

**Эталон-референс:** `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` — 1757 строк, 15 premium-фич.

## Связанные концепты
- [[block-composer]] — агент, который собирает `composed.html` по этому чек-листу
- [[design-system-generator]] — поставляет `tokens.json` (вход п.2)
- [[content-writer]] — поставляет `final-copy.md` (вход п.4)
- [[ux-composer]] — поставляет `selections.yaml` (вход п.5)
- [[photo-curator]] — поставляет `photo-mapping.yaml` (вход п.7)
- [[07b-composed]] — этап, к которому относится этот стандарт

## Источник
- `docs/standards/premium-07b-checklist.md`
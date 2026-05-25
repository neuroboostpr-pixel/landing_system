---
type: rule
name: premium-07b-checklist
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: ["landing-compose", "landing-orchestrator", "landing-wireframe", "landing-photos", "landing-visuals"]
tags: ["07b", "composed", "premium", "checklist", "hard-gate", "quality"]
---

# Premium 07b — Чек-лист сборки composed.html

## Что делает

Определяет обязательные стандарты качества для этапа 07b: перечисляет что должно быть на входе, как строить HTML-файл, какие интерактивные эффекты реализовать и что проверить перед закрытием hard gate. Цель — лендинг уровня эталона `dubai-avto-liza`, а не «средний AI-лендинг».

## Когда вызывать / в каком этапе

Передаётся агенту `landing-compose` (скилл `/landing-compose`) перед запуском сборки `07b_COMPOSED/composed.html`. Также используется `landing-orchestrator` при проверке hard gate этапа 07b — gate не закрывается, пока скрипт `verify-composed-premium.sh` не вернёт `exit 0`.

## Что на вход / на выход

**Вход (обязательно перед сборкой):**
- `00_БРИФ/brief.md` — ниша, ЦА, KPI
- `04_БРЕНД/brand-kit.md` — палитра и типографика
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — CSS-переменные
- `07_КОНТЕНТ/final-copy.md` — тексты для всех блоков
- `07a_WIREFRAME/selections.yaml` — список блоков с ID
- `02_МАТЕРИАЛЫ_КЛИЕНТА/inbox/` — минимум 15 реальных фото
- `07c_PHOTOS/photo-mapping.yaml` — маппинг фото по слотам

**Выход (артефакты этапа 07b):**
- `07b_COMPOSED/composed.html` — один файл, HTML+CSS+JS inline, 60–150 KB
- `composed-mobile-preview.html` — превью для iPhone/iPad
- `composed-explained.md` — описание принятых решений
- `07c_PHOTOS/photo-mapping.yaml` — обновлённый маппинг

## Ключевые требования

Чек-лист содержит **20 разделов** обязательных требований:

1. **Архитектура** — один HTML-файл без фреймворков (React/Vue/Bootstrap/jQuery запрещены), только Google Fonts через `<link preconnect>`.
2. **CSS-переменные** — полный набор в `:root` из `tokens.json`; хардкод цветов в блоках запрещён.
3. **Типографика** — `clamp()` на всех заголовках, Inter с весами 300–900, `font-weight: 900` на hero.
4. **Структура страницы** — 11 обязательных блоков: sticky-nav, hero, social-proof, models, features, why-us, process, testimonials, FAQ, CTA-форма, footer.
5. **Сетка** — конкретные grid-раскладки для каждого блока (auto-fit, reverse-чередование и т.д.).
6. **10 интерактивных эффектов** — glassmorphism nav, parallax hero, reveal-on-scroll через IntersectionObserver, count-up статистики, per-product vanilla slider, lightbox с клавиатурой, hover lift на карточках, scroll-to-top, smooth scroll, pulse-dot бейдж.
7. **Премиум-приёмы** — gradient text, eyebrow-метки, line-height 1.05 на hero.
8. **Mobile responsive** — breakpoints 768px и 1024px, все grid → 1 колонка.
9. **Accessibility** — семантические теги, aria-label, alt, контраст ≥ 4.5:1, `<details>/<summary>` для FAQ.
10. **PR-P дополнения** — scroll-driven анимации (≥3 блока), `@media prefers-reduced-motion`, `clip-path` для нестандартных форм, complex gradient mesh.

## Связанные концепты

- [[landing-compose]] — скилл, который собирает `composed.html` по данному чек-листу
- [[landing-wireframe]] — поставляет `selections.yaml` — обязательный входной артефакт
- [[landing-photos]] — поставляет `photo-mapping.yaml` — обязательный входной артефакт
- [[landing-orchestrator]] — применяет hard gate 07b, запускает `verify-composed-premium.sh`
- [[landing-visuals]] — поставляет иконки/инфографику для слотов `composed.html`

## Источник

- `docs/standards/premium-07b-checklist.md`
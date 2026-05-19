---
type: rule
name: premium-07b-checklist
sources: ["docs/standards/premium-07b-checklist.md"]
updated: 2026-05-19
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "design-tokens-generation", "landing-compose", "visual-qa"]
tags: ["composed", "premium", "checklist", "hard-gate", "07b"]
---

# Premium 07b — Чек-лист сборки composed.html

## Что делает

Определяет обязательные стандарты качества для этапа **07b_COMPOSED**: какой должна быть собранная HTML-страница, чтобы она выглядела как дорогой лендинг, а не «средний AI-результат». Используется агентом [[block-composer]] как руководство и скриптом `verify-composed-premium.sh` как автоматическая проверка (HARD GATE).

## Когда вызывать / в каком этапе

Применяется на этапе **07b** — при запуске `/landing-compose` и перед закрытием HARD GATE 07b. Агент [[block-composer]] обязан пройти все пункты чек-листа до передачи результата на утверждение. Если `verify-composed-premium.sh` возвращает exit ≠ 0 — этап не считается пройденным.

## Что на вход / на выход

**Вход (без этого 07b не собирается):**
- `00_БРИФ/brief.md` — ниша, ЦА, тон голоса
- `04_БРЕНД/brand-kit.md` — палитра и типографика
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — CSS-переменные
- `07_КОНТЕНТ/final-copy.md` — реальные тексты
- `07a_WIREFRAME/selections.yaml` — выбранные блоки
- `07c_PHOTOS/photo-mapping.yaml` + минимум 15 фото клиента

**Выход:**
- `07b_COMPOSED/composed.html` — единый inline-файл (60–150 KB, без фреймворков)
- `composed-explained.md` — описание изменений и таблица контраста (WCAG)
- `composed-mobile-preview.html` — iframe-превью iPhone+iPad

## Ключевые требования (по секциям)

Чек-лист содержит **29 секций** (нумерация до §29), охватывающих:

1. **Архитектура** — один HTML+CSS+JS файл, без jQuery/Swiper/Bootstrap/Tailwind CDN.
2. **CSS-переменные** — полный набор `:root` токенов, никаких хардкод цветов в блоках.
3. **Типографика** — `clamp()` на всех заголовках, modular type scale (≤8 уникальных размеров), `text-wrap: balance`, неразрывные пробелы, кавычки-«ёлочки».
4. **Структура страницы** — 11 обязательных блоков от sticky-nav до footer.
5. **10 интерактивных эффектов** — glassmorphism nav, parallax hero, IntersectionObserver reveal, count-up, per-product slider, lightbox с клавиатурой, hover-lift, scroll-to-top, smooth scroll, pulse-dot badge.
6. **Hero** — 100vh, overlay, badge, gradient-text, savings-строка, 2 CTA, 3 stat-числа.
7. **Mobile** — breakpoints 768px и 1024px, `100dvh` вместо `100vh`, `env(safe-area-inset-*)`, `theme-color`.
8. **Accessibility** — семантика HTML5, `:focus-visible`, контраст ≥4.5:1, `prefers-reduced-motion`.
9. **Performance** — `width`/`height` на всех `<img>`, `loading="lazy"`, `fetchpriority="high"` на hero, WebP через `<picture>`, Lighthouse ≥85.
10. **Формы** — корректный `type=` (tel/email), `autocomplete=`, inline-валидация, никакого `onpaste="return false"`.
11. **OpenGraph/Meta** — `og:image`, `twitter:card`, favicon с инициалом бренда, `<html lang="ru">`.

**Anti-patterns (auto-fail):** `transition: all`, `user-scalable=no`, `<div onclick>`, `outline: none` без замены, `onpaste` с `preventDefault`.

**Эталон-референс:** `~/Lendings/dubai-avto-liza/07b_COMPOSED/composed.html` — 1757 строк, ~130 KB, все 15+ premium-фич.

## Связанные концепты

- [[block-composer]] — агент, который собирает `composed.html` по этому чек-листу
- [[ux-composer]] — создаёт wireframe, на основе которого block-composer работает
- [[design-tokens-generation]] — производит `tokens.json`, обязательный вход для 07b
- [[landing-compose]] — команда, запускающая сборку этапа 07b
- [[visual-qa]] — финальный QA-скилл, который проверяет выход в том числе по этому стандарту
- [[block-composition]] — скилл, реализующий логику сборки composed.html

## Источник

- `docs/standards/premium-07b-checklist.md`
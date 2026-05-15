# Editorial Warm Style Mood

**Inspiration:** `kami-landing` + `taste-soft-editorial` (OpenDesign), журнальная подача

## Когда применять

- Психологи, коучи, консультанты — экспертный, тёплый
- Премиум-услуги с личным брендом
- Авторские курсы и обучающие программы
- Дизайн-студии, архитекторы
- Когда клиент говорит: "Хочу выглядеть как French Vogue или The Atlantic"

## НЕ применять

- Tech-стартапы (нужна остроту и модернизм)
- Ecommerce с большим каталогом (editorial не масштабируется)
- Массовый продукт (слишком элитарно)

## Что подключать

**Patterns:** `scroll-reveal`, `paper-texture`, `dot-grid-bg`, `cursor-aura` (warm variant), `marquee-3d-perspective`, `text-reveal-mask`
**НЕ подключать:** `bento-grid-hairline` (слишком tech), `conic-ring` (слишком playful)

## Правила дизайна

1. **Цвет:** Parchment `#f5f4ed` — базовый фон для всего
2. **Акцент:** ОДИН — ink-blue `#1B365D`, используется сдержанно
3. **Типографика:** Cormorant Garamond для display, Source Serif 4 для body
4. **Italic:** допускается mid-sentence для выделения (editorial приём)
5. **Grid:** Asymmetric — `1.45fr 0.55fr` hero, `1fr 1.85fr` manifesto
6. **Border-radius:** 6-12px максимум (мягкие, не округлые)
7. **Shadows:** только `--shadow: whisper` (0 4px 24px rgba(0,0,0,0.05))
8. **Whitespace:** generous — контент дышит
9. **Drop cap:** уместен на ключевых параграфах (`:first-letter`)

## Типичная структура секции

```html
<!-- Eyebrow strip: thin line top, mono metadata -->
<!-- Hero: asymmetric grid, large serif display, token cards right -->
<!-- Manifesto: border-left quote, 2-column grid -->
<!-- Features: 2-3 col with border-top hairlines -->
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Source+Serif+4:wght@400;500&family=Source+Sans+3:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

# Brutalist Style Mood

**Inspiration:** `web-prototype-taste-brutalist` (OpenDesign), Swiss punk design

## Когда применять

- Бренды с сильным характером и нон-конформистским позиционированием
- Стартапы, которые хотят выделиться на фоне конкурентов
- Инди-продукты, медиа, творческие агентства
- Когда клиент говорит: "Мы не хотим быть похожи на всех"

## НЕ применять

- Медицина, юриспруденция, финансы (требуют доверия и консервативности)
- Premium luxury (нужна мягкость, не жёсткость)
- Женская аудитория beauty/wellness (слишком агрессивно)

## Что подключать

**Patterns:** `scroll-reveal`, `headroom-nav`, `bento-grid-hairline`, `marquee-3d-perspective`
**НЕ подключать:** `ambient-mesh-bg` (слишком soft), `paper-texture` (слишком нежный), `cursor-aura`

## Правила дизайна

1. **Цвета:** Только 3 — paper `#F4F4F0`, ink `#060606`, hazard `#E61919`
2. **Border-radius:** НОЛЬ. Всё — прямые углы
3. **Типографика:** Archivo Black 900, Uppercase, tight tracking
4. **Display text:** Используй как ГРАФИЧЕСКИЙ элемент (220px+), не только как текст
5. **Borders:** Всегда `1px solid #060606`, иногда `4px solid` для акцента
6. **Shadows:** Только `8px 8px 0 #000` (hard drop shadow, без blur)
7. **Mono:** JetBrains Mono для всех labels, UPPERCASE, `letter-spacing: 0.1em`
8. **Accent:** Hazard red ТОЛЬКО для 1-2 элементов на странице

## Типичная структура секции

```html
<!-- Nav: full-width, 4px border-bottom, mono labels -->
<!-- Hero: massive display number/word as background, meta-col right -->
<!-- Abstract: 3-column grid, drop-cap on lead text -->
<!-- Index/Table: 1px gap grid with ink background (like a spreadsheet) -->
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

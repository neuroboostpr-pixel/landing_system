# Coral Soft Style Mood

**Inspiration:** `taste-coral` + `sakura-chroma` + `taste-soft-editorial` (OpenDesign), lifestyle и beauty эстетика

## Когда применять

- Beauty, wellness, spa, косметология
- Lifestyle coaching, women-led brands
- Детские продукты, уютные бренды
- Когда клиент говорит: "Хочу тепло, женственно, современно"

## НЕ применять

- B2B / enterprise (слишком playful)
- Tech (несерьёзно для разработчиков)
- Мужская аудитория (если не детские товары)

## Что подключать

**Patterns:** `scroll-reveal`, `ambient-mesh-bg`, `gradient-mesh-animated` (warm variant), `marquee-fade`, `cursor-aura` (warm variant)
**НЕ подключать:** `bento-grid-hairline` (слишком tech), `dot-grid-bg` (слишком cold)

## Правила дизайна

1. **Базовый фон:** Warm cream `#F5F0E8` — никакого чистого белого
2. **Coral акцент:** `#E85D5D` — для CTA кнопок, nav dots, progress bars
3. **Pastel palette:** 5 пастельных цветов для карточек и swatches
4. **Halftone texture:** `radial-gradient` dot pattern 4px*4px, opacity 0.16 — paper feel
5. **Cards:** `border-radius: 24-32px` (oval/rounded) + `frosted: rgba(255,255,255,0.55)`
6. **Nav dots:** вертикальные, справа, coral активный, ghost неактивный
7. **Display:** Bebas Neue UPPERCASE для заголовков — контраст с мягким фоном
8. **Serif:** Cormorant Garamond для цитат, кикеров, editorial моментов

## Halftone dot texture

```css
.section::before {
  content: '';
  position: absolute; inset: 0;
  background-image: radial-gradient(circle at 1px 1px, rgba(58,37,22,0.55) 1px, transparent 1.6px);
  background-size: 4px 4px;
  opacity: 0.16;
  pointer-events: none;
}
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
```

# Monochrome Precision Style Mood

**Inspiration:** `taste-monochrome` (Ivory Ledger) (OpenDesign), Swiss minimalism, luxury print

## Когда применять

- Архитекторы, дизайнеры интерьеров
- Fine art photography, портфолио
- Luxury-премиум услуги
- Когда клиент говорит: "Минимализм, дорого, без лишнего"

## НЕ применять

- Яркие consumer brands (потеряются без акцента)
- Образовательные платформы (нужен цвет для навигации)
- Массовые продукты (слишком сдержанно)

## Что подключать

**Patterns:** `scroll-reveal`, `dot-grid-bg`, `conic-ring` (monochrome variant), `text-reveal-mask`
**НЕ подключать:** `ambient-mesh-bg` (soft и цветной), `gradient-mesh-animated`, `cursor-aura`, `marquee-3d-perspective`

## Правила дизайна

1. **НОЛЬ дополнительных цветов** — только cream `#fafadf` + black ink `#1a1a16`
2. **Whitespace = дизайн** — padding 8vw horizontal, gaps 5vh
3. **Jost Light** (weight 200-300) для body — геометрический, утончённый
4. **Lora Italic** для serif moments — цитаты, insight titles
5. **data-anim system:** все элементы входят через fade-up/fade-in + data-delay stagger
6. **vw-типографика:** display 8.5vw, body 1.1vw — пропорционально
7. **НЕТ border-radius** — только 0px или минимальный
8. **Dividers:** черные, тонкие (1px), через `::before`/`::after`

## data-anim stagger system

```html
<!-- Все элементы секции получают data-anim и data-delay -->
<h2 data-anim="fade-up" data-delay="0">Заголовок</h2>
<p data-anim="fade-up" data-delay="1">Подзаголовок</p>
<div data-anim="fade-up" data-delay="2">Контент</div>
```

```css
[data-anim] { opacity: 0; }
.is-active [data-anim] {
  animation: kFadeUp var(--motion-duration-medium) var(--motion-easing-enter) forwards;
}
[data-delay="0"] { animation-delay: 0s; }
[data-delay="1"] { animation-delay: var(--motion-delay-1); }
/* ... etc */
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@200;300;400;500&family=Lora:ital,wght@0,400;0,500;1,400;1,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

# Swiss Modernist Style Mood

**Inspiration:** `taste-cobalt-grid` + `digits-fintech-swiss` (OpenDesign), International Typographic Style

## Когда применять

- Tech SaaS, fintech, enterprise software
- Финансовые сервисы, юридические платформы
- B2B продукты, которые хотят выглядеть как Linear или Notion
- Когда клиент говорит: "Нам нужен серьёзный, профессиональный вид"

## НЕ применять

- Consumer lifestyle brands (слишком холодно)
- Creative/artistic brands (слишком утилитарно)
- Young audience (слишком institutional)

## Что подключать

**Patterns:** `scroll-reveal`, `bento-grid-hairline`, `dot-grid-bg`, `headroom-nav`, `text-reveal-mask`
**НЕ подключать:** `paper-texture` (слишком органично), `ambient-mesh-bg` (слишком soft), `cursor-aura`

## Правила дизайна

1. **Background:** Graph paper через CSS — `linear-gradient` cobalt grid, `opacity: 0.10`
2. **Акцент:** Electric cobalt `#1F2BE0` — cobalt везде, не для точечного акцента
3. **Display:** Newsreader Italic — крупный, косой, commanding
4. **Hairlines:** `::before`/`::after` псевдоэлементы top и bottom каждой секции
5. **Labels:** `uppercase; letter-spacing: 0.16em; font-size: 11px` — всегда
6. **Border-radius:** 0-4px максимум (минималистичный)
7. **Данные:** Любые таблицы, статистика — приветствуются (swiss любит данные)
8. **Пустое пространство:** Generous — swiss дышит

## Graph paper фон

```css
background-image:
  linear-gradient(to right, var(--color-accent-grid) 1px, transparent 1px),
  linear-gradient(to bottom, var(--color-accent-grid) 1px, transparent 1px);
background-size: clamp(28px, 2.2vw, 44px) clamp(28px, 2.2vw, 44px);
```

## Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;1,300;1,400&family=Hanken+Grotesk:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
```

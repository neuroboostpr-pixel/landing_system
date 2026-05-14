# Style Moods — block-library/_styles/

Готовые "визуальные настроения" — сочетание палитры + типографики + motion-режима + рекомендованных паттернов.

## Что такое Style Mood

Один mood = 4 файла:
- `palette.css` — CSS-переменные цветов
- `typography.css` — font stack + type scale
- `motion.css` — timing, easing, интенсивность анимаций
- `style-guide.md` — когда применять, что подключать

## Доступные Moods

| Mood | Inspiration | Когда применять |
|---|---|---|
| `brutalist` | web-prototype-taste-brutalist | Бренды с характером, нон-конформизм, стартапы |
| `editorial-warm` | kami-landing + soft-editorial | Премиум-услуги, психология, эксперты, коучинг |
| `swiss-modernist` | cobalt-grid + digits-fintech-swiss | Tech, finance, SaaS, B2B |
| `retro-windows` | zhangzara-retro-windows | Геймификация, nostalgia, инди-продукты |
| `coral-soft` | zhangzara-coral, sakura-chroma, soft-editorial | Beauty, wellness, lifestyle, women-led brands |
| `monochrome-precision` | zhangzara-monochrome (Ivory Ledger) | Архитектура, фотография, luxury-премиум |

## Использование в generate-theme.py

В `tokens.json` добавь:
```json
{
  "style_mood": "editorial-warm"
}
```

`generate-theme.py` автоматически подключит все CSS-файлы mood к `style.css` темы.

## Использование вручную

```css
/* В style.css темы, после основных стилей: */
@import url('path/to/_styles/editorial-warm/palette.css');
@import url('path/to/_styles/editorial-warm/typography.css');
@import url('path/to/_styles/editorial-warm/motion.css');
```

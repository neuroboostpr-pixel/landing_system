# headroom-nav

**Что:** Nav прячется при скролле вниз, появляется при скролле вверх — освобождает экран для контента.

**Откуда:** Паттерн из open-design-landing + web-prototype-taste-soft (headroom-style behaviour)

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Мобильный UX — особенно важно на смартфонах где nav занимает 10%+ высоты. Рекомендуется всегда.

**Зависимости:** Vanilla JS (~30 строк). Работает с любым `id="lp-nav"` элементом.

## Как работает

1. Слушает `scroll` через `requestAnimationFrame` (не throttle)
2. При скролле вниз > 80px добавляет `.lp-nav--hidden` → CSS трансформирует nav вверх
3. При скролле вверх убирает `.lp-nav--hidden` → nav возвращается
4. `DELTA = 5px` фильтрует случайные микро-скроллы

## Настройка

```js
var NAV_SELECTOR = '#lp-nav';      // ID или class навигации
var HIDE_CLASS   = 'lp-nav--hidden'; // класс из CSS
var THRESHOLD    = 80;              // px от топа страницы перед активацией
var DELTA        = 5;               // минимальное движение для реакции
```

## Использование в WP-теме

JS автоматически подключается через `assets/js/animations.js`.
CSS через `style.css` (если используется отдельный nav, не floating-pill-nav).

Если floating-pill-nav уже включён — этот snippet только за JS.
Transition для `.lp-nav--hidden` уже есть в `floating-pill-nav/snippet.css`.

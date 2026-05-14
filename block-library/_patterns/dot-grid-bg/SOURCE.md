# dot-grid-bg

**Что:** Тонкая точечная сетка через `radial-gradient` — magazine/Notion/Figma-style фон.

**Откуда:** Паттерн из craft/typography-hierarchy-editorial.md + design-systems-refs (editorial стиль)

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Editorial, portfolio, архитектура, дизайн-студии. `animation_mode: editorial`.

**Зависимости:** Vanilla CSS only — 5 строк.

## Почему это работает

Один `radial-gradient` с размером фона создаёт бесшовную точечную плитку.
Никакого SVG, никаких изображений — только CSS custom properties.

## Когда использовать

- Нейтральные / кремовые фоны (#fafaf8, #f5f5f2)
- Когда нужна "сетка редактора" без явного grid-overlay
- Пары с `paper-texture` — точки + зерно = premium editorial

## Когда НЕ использовать

- Белый #fff на проекторе/телевизоре — точки теряются
- Тёмный фон — нужно менять `--dot-color`
- На фото-секциях — конфликт с текстурой изображений

## Использование в WP-теме

```php
// functions.php — через body_class
add_filter('body_class', function($classes) {
    $classes[] = 'has-dot-grid';
    return $classes;
});
```

Или в `style.css` прямо на `body`:
```css
body {
  background-image: radial-gradient(circle, var(--dot-color, rgba(0,0,0,0.1)) 1.5px, transparent 1.5px);
  background-size: 24px 24px;
}
```

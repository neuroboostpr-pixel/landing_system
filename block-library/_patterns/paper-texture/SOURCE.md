# paper-texture

**Что:** Тонкая органическая зернистость поверх фона — ощущение premium print-качества без растровых файлов.

**Откуда:** Вдохновение из `craft/typography-hierarchy-editorial.md` + паттерн из web-prototype-taste-editorial. SVG feTurbulence через data:URI.

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Editorial / премиум-проекты. Особенно эффектно на кремовых (#fafaf8) и бежевых фонах.

**Зависимости:** Vanilla CSS only — никакого JS.

## Когда использовать

- Студии, агентства, консалтинг, архитектура, дизайн-бюро
- Когда нужно "человеческое" ощущение вместо цифровой стерильности
- `animation_mode: cinematic` или `animation_mode: editorial`

## Когда НЕ использовать

- SaaS / tech / стартапы — там ожидают чистый digital
- Если основной цвет темный с хорошим contrast — текстура может мешать читаемости

## Использование в WP-теме

В `index.php` или `body` добавить класс:

```php
<body <?php body_class('has-paper-texture'); ?>>
```

Или в `functions.php`:

```php
add_filter('body_class', function($classes) {
    $classes[] = 'has-paper-texture';
    return $classes;
});
```

## Настройка

Изменить opacity в `:root` для тонкой или грубой текстуры:
- `opacity: 0.02` — едва заметная (luxury)
- `opacity: 0.035` — default (premium)
- `opacity: 0.06` — заметная (vintage/craft)

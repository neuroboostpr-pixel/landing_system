# ambient-mesh-bg

**Что:** Два размытых цветовых круга медленно двигаются в фоне — живой атмосферный эффект без Three.js, Canvas или библиотек.

**Откуда:** `/tmp/open-design/design-templates/web-prototype-taste-soft/example.html:44-66`

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Hero для tech/SaaS проектов, агентств, стартапов. Заменяет blob backgrounds и gradient overlays.

**Зависимости:** Vanilla CSS only — никакого JS.

## Когда использовать

- `animation_mode: cinematic` — включается автоматически
- Тёмные или нейтральные фоны (#0d0d0d, #fafaf7)
- Когда нужен "premium tech" вайб без стереотипного gradient

## Когда НЕ использовать

- Белый (#fff) фон — сферы не будут видны
- Если проект уже имеет сложный hero с фото — конфликт визуального веса
- `animation_mode: editorial` — там используется paper-texture

## Использование в WP-теме (index.php)

```php
<?php if (!defined('ABSPATH')) { exit; } ?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head><?php wp_head(); ?></head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="lp-mesh-bg" aria-hidden="true"></div>
<main id="main">
  <?php if (have_posts()) { while (have_posts()) { the_post(); the_content(); } } ?>
</main>
<?php wp_footer(); ?>
</body>
</html>
```

## Настройка цветов

В `05_ДИЗАЙН-СИСТЕМА/tokens.json` должен быть `accent_color`.
generate-theme.py передаёт его в `:root { --mesh-color-a: <accent>; }` автоматически.

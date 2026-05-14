# floating-pill-nav

**Что:** Sticky пилюля-навигация с backdrop-blur — центрирована, парит над контентом.

**Откуда:** `/tmp/open-design/design-templates/web-prototype-taste-soft/example.html:72-125`

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Премиум лендинги, агентства, portfolio-проекты. Apple/Linear-style UX.

**Зависимости:** Vanilla CSS. Совместима с headroom-nav (JS) для авто-скрытия.

## Headroom совместимость

Класс `.lp-nav--hidden` добавляется/убирается через `headroom-nav/snippet.js`:

```js
// headroom-nav добавляет .lp-nav--hidden на #lp-nav при скролле вниз
```

## Использование в WP-теме (header.php или index.php)

```php
<header class="lp-nav-shell" id="lp-nav">
  <nav class="lp-nav" aria-label="<?php esc_attr_e('Основная навигация', 'lp'); ?>">
    <a href="<?php echo esc_url(home_url('/')); ?>" class="lp-nav__brand">
      <?php bloginfo('name'); ?>
    </a>
    <ul class="lp-nav__links">
      <?php wp_nav_menu(['theme_location' => 'primary', 'items_wrap' => '%3$s', 'container' => false]); ?>
    </ul>
    <a href="#контакты" class="lp-nav__cta">
      <?php esc_html_e('Связаться', 'lp'); ?>
    </a>
  </nav>
</header>
```

## Заметки

- `max-width: calc(100% - 48px)` — всегда есть 24px поля по бокам на мобильном
- Без `overflow: hidden` — тень не обрезается
- `position: sticky` + `top: 16px` — nav остаётся видимой при скролле

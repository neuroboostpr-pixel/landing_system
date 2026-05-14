# scroll-reveal

**Что:** Блоки появляются снизу/слева/справа при входе в viewport — главный visual upgrade без GSAP.

**Откуда:** `/tmp/open-design/design-templates/open-design-landing/example.html:1732-1778`

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Везде — на всех секциях лендинга ниже hero. Hero лучше делать через CSS animation без scroll-reveal.

**Зависимости:** Vanilla JS (IntersectionObserver — поддержка 97%+, без полифилов)

## Варианты

| Атрибут | Эффект |
|---|---|
| `data-reveal` | Появление снизу (28px) |
| `data-reveal="left"` | Появление слева (-36px) |
| `data-reveal="right"` | Появление справа (36px) |
| `data-reveal="scale"` | Масштаб 0.96 → 1 |
| `data-reveal="rise-lg"` | Большой подъём 64px + лёгкий scale |
| `data-reveal-stagger` | На родителе — дети появляются с задержкой 90ms |

## Использование в WP-теме

```php
// functions.php — автоматически через generate-theme.py
wp_enqueue_script('lp-animations', get_template_directory_uri() . '/assets/js/animations.js', [], '1.0.0', true);
```

```css
/* style.css — автоматически через generate-theme.py append_patterns_css() */
/* @import block-library/_patterns/scroll-reveal/snippet.css */
```

В block.php добавить атрибут к секции:
```php
<section class="lp-features" data-reveal>
```

Или к сетке карточек:
```php
<div class="lp-cards" data-reveal-stagger>
  <?php foreach ($cards as $card): ?>
    <div class="lp-card" data-reveal><?php echo $card; ?></div>
  <?php endforeach; ?>
</div>
```

## Производительность

- `will-change: opacity, translate, scale` — только на скрытых элементах
- После reveal observer отключается (`unobserve`) — нет постоянного наблюдения
- Использует `translate` + `scale` longhand вместо `transform` — не ломает rotate() на карточках

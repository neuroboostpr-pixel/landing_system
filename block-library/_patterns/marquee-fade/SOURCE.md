# marquee-fade

**Что:** Бесконечно бегущая строка с плавным fade на краях. CSS-only, пауза при hover.

**Откуда:** `/tmp/open-design/design-templates/open-design-landing/example.html:698-718`

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Логотипы партнёров/клиентов, бегущие теги ниши, социальное доказательство (цифры, отзывы-короткие).

**Зависимости:** Vanilla CSS only — никакого JS.

## Ключевые правила

1. **Дублировать контент в track** — для бесшовного loop нужно 2 копии всех элементов
2. **mask-image** (не overflow: hidden) — для плавного fade на краях
3. `will-change: transform` — GPU acceleration
4. Обратная строка (`--reverse`) визуально сигнализирует о большом наборе контента

## Использование в WP-теме (block.php)

```php
<div class="lp-marquee" aria-label="<?php esc_attr_e('Наши клиенты', 'lp'); ?>">
  <div class="lp-marquee__track">
    <?php foreach (array_merge($clients, $clients) as $client): ?>
      <span class="lp-marquee__item"><?php echo esc_html($client['name']); ?></span>
      <span class="lp-marquee__sep" aria-hidden="true"></span>
    <?php endforeach; ?>
  </div>
</div>
```

## Производительность

- `animation` на `transform` — composited layer, не вызывает reflow
- `will-change: transform` — включить только на marquee (не глобально)
- Оставить `will-change: auto` на мобильных если строк много

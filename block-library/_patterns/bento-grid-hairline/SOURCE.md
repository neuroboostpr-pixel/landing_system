# bento-grid-hairline

**Что:** 6-колоночный CSS Grid с hairline разделителями — Notion/Linear/Linear-style features секция.

**Откуда:** `/tmp/open-design/design-templates/open-design-landing/example.html:1477-1520`

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Features, Advantages, Benefits секции. Особенно хорошо для 4+ фич.

**Зависимости:** Vanilla CSS only.

## Ключевой трюк

Gap между ячейками = 1px + фон контейнера = hairline-цвет.
Ячейки поверх — своего цвета.
Результат: тонкие разделители без `border` на ячейках.

```css
.lp-bento {
  gap: 1px;
  background: var(--hairline); /* видно через gap */
}
.lp-bento__cell {
  background: var(--bg); /* перекрывает hairline внутри ячейки */
}
```

## Типичные layouts

| Pattern | Grid |
|---|---|
| `4-2 / 2-4` | Большая + маленькая, потом маленькая + большая |
| `3-3 / 3-3` | Равные половины |
| `6 / 2-2-2` | Полная ширина + три равных |
| `2-2-2 / 6` | Три равных + полная ширина |

## Использование в WP-теме

```php
<div class="lp-bento lp-bento--features-4-2">
  <?php foreach ($features as $i => $feature): ?>
    <div class="lp-bento__cell" data-reveal style="--reveal-delay: <?php echo $i * 90; ?>ms">
      <p class="lp-bento__label">0<?php echo $i + 1; ?></p>
      <h3 class="lp-bento__title"><?php echo esc_html($feature['title']); ?></h3>
      <p class="lp-bento__desc"><?php echo esc_html($feature['desc']); ?></p>
    </div>
  <?php endforeach; ?>
</div>
```

## Accessibility

- Порядок в DOM = визуальный порядок (grid не переставляет элементы)
- Семантические `<h3>` в каждой ячейке
- Нет скрытого контента

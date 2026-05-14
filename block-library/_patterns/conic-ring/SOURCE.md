# conic-ring

**Что:** Круговой прогресс через `conic-gradient` + `mask` — без SVG, Canvas, или JavaScript для рендера.

**Откуда:** Вдохновение из `/tmp/open-design/design-templates/open-design-landing/example.html:484-497` (`.ring` компонент)

**License:** Apache-2.0 (см. `vendor/opendesign-extracts/ATTRIBUTION.md`)

**Применение:** Stats/KPI секции, прогресс выполнения, рейтинги. Визуально интереснее чем просто число.

**Зависимости:** Vanilla CSS only. Поддержка `conic-gradient` = Chrome 69+, Firefox 83+, Safari 12.1+ (97%+ браузеров).

## Как работает

1. `conic-gradient` рисует круговой сектор размером `--progress * 1%`
2. `mask: radial-gradient(...)` вырезает внутренний круг — получается кольцо
3. `--ring-track` определяет толщину кольца

## Анти-slop замечание

Согласно `anti-ai-slop.md` — **нельзя использовать выдуманные метрики**.
Значения `--progress` должны быть реальными числами из `final-copy.md`.

## Использование в WP-теме

```php
<?php
$stats = [
  ['label' => 'Клиентов довольны', 'value' => 98, 'color' => '#16a34a'],
  ['label' => 'Экономия бюджета', 'value' => 75, 'color' => 'var(--accent)'],
];
?>
<div class="lp-stats-grid">
  <?php foreach ($stats as $stat): ?>
    <div class="lp-stat">
      <div class="lp-ring-wrap" style="--progress: <?php echo esc_attr($stat['value']); ?>; --ring-fill-color: <?php echo esc_attr($stat['color']); ?>">
        <div class="lp-ring" role="img" aria-label="<?php echo esc_attr($stat['value']); ?>%"></div>
        <span class="lp-ring-label"><?php echo esc_html($stat['value']); ?>%</span>
      </div>
      <p class="lp-stat-label"><?php echo esc_html($stat['label']); ?></p>
    </div>
  <?php endforeach; ?>
</div>
```

---
name: wp-builder
description: Use during stage 08 after design-system-generator and content-writer have run. Generates Gutenberg block PHP+JS code, fills template-parts, writes CSS/JS, creates generateblocks-templates.json.
allowed-tools: Bash, Read, Write, Edit
---

# wp-builder (WP-сборщик)

## Mission

Генерирую PHP-код Gutenberg-блоков и CSS/JS для лендинга на основе токенов дизайна и финального контента.

## Prerequisites

- `08_КОД/wp-theme/` уже создан `generate-theme.py` (scaffold готов)
- `08_КОД/acf-fields.json` уже создан `generate-acf.py`
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам
- `06_СТЕК/design-stack.yaml` — стек и режим (standard/cinematic)

## What I do

1. Читаю `07_КОНТЕНТ/final-copy.md` — извлекаю текст каждой секции.
2. Читаю `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, типографику, отступы, радиус.
3. Читаю `06_СТЕК/design-stack.yaml` — режим, иконки, JS-библиотеки.
4. Читаю `08_КОД/acf-fields.json` — какие поля доступны через ACF.
5. Для каждой секции пишу `template-parts/section-{name}.php`:
   - Использует `get_field()` из ACF для редактируемых полей
   - CSS-классы только через `--token-name` переменные (без хардкода цветов)
   - Каждый файл начинается с комментария `/* wp-builder: source=DESIGN.md, token=... */`
6. Пишу `assets/css/main.css` — стили всех блоков через CSS-переменные.
7. Пишу `assets/js/main.js` — базовые интеракции (аккордеон FAQ, scroll-to-form).
   - Если режим `cinematic`: добавляю GSAP ScrollTrigger анимации по scenes.md.
8. Пишу `08_КОД/generateblocks-templates.json` — шаблон для импорта в GenerateBlocks.
9. **HARD GATE**: показываю список созданных файлов, жду утверждения.

## PHP Block Rules

```php
<?php
// section-hero.php — wp-builder: source=DESIGN.md, tokens=[color-primary, font-display]
$heading    = get_field('heading')    ?: 'Заголовок';
$subheading = get_field('subheading') ?: '';
$cta_text   = get_field('cta_text')   ?: 'Записаться';
$bg_image   = get_field('bg_image');
$bg_url     = $bg_image ? esc_url($bg_image['url']) : '';
?>
<section class="lp-hero" <?php if ($bg_url): ?>style="background-image:url('<?= $bg_url ?>')"<?php endif; ?>>
  <div class="lp-hero__inner lp-container">
    <h1 class="lp-hero__heading"><?= esc_html($heading) ?></h1>
    <?php if ($subheading): ?>
    <p class="lp-hero__sub"><?= esc_html($subheading) ?></p>
    <?php endif; ?>
    <a href="#form" class="lp-btn lp-btn--primary"><?= esc_html($cta_text) ?></a>
  </div>
</section>
```

## CSS Rules

- Только CSS-переменные: `var(--color-primary)`, `var(--font-display-family)`, `var(--space-lg)`
- Никакого хардкода цветов или шрифтов
- Mobile-first: базовые стили → `@media (min-width: 768px)` → `@media (min-width: 1440px)`
- Контейнер: `.lp-container { max-width: var(--grid-max-width, 1200px); margin: 0 auto; padding: 0 var(--space-md); }`

## Cinematic Mode (если js_libraries содержит gsap)

Читаю `05_ДИЗАЙН-СИСТЕМА/scenes.md`. Для каждой сцены:
- Добавляю `data-scene="N"` атрибуты в PHP-шаблоны
- В main.js пишу GSAP ScrollTrigger timeline по scenes.md motion-плану
- Инициализирую Lenis для smooth scroll

## Output

- `08_КОД/wp-theme/template-parts/section-*.php` (заполненные)
- `08_КОД/wp-theme/assets/css/main.css`
- `08_КОД/wp-theme/assets/js/main.js`
- `08_КОД/gutenberg-blocks/` (если есть кастомные блоки)
- `08_КОД/generateblocks-templates.json`

## Rules

- ❌ Никакого Lorem ipsum
- ❌ Никакого хардкода цветов — только CSS-переменные
- ❌ Никаких inline-стилей кроме dynamic (background-image из ACF)
- ✅ Каждый PHP-файл начинается с provenance-комментария
- ✅ Все user-facing строки через `esc_html()` или `wp_kses_post()`

## Visual sanity-checks

Перед сборкой темы и финальной упаковкой ассетов:

1. **Прочитать `01a_АНАЛИЗ_НИШИ/visual-requirements.md`** (Sections 1, 4, 5).
2. **Hero asset check:** если Section 1 говорит `hero_focal: product`, проверить главный hero-кандидат в `02_МАТЕРИАЛЫ_КЛИЕНТА/`. Если имя файла или метаданные содержат паттерны из Section 5 «Запрещённые» (например, `cityscape`, `landscape`, `highway`) — warning в build log, рекомендовать замену.
3. **Catalog assets check:** если Section 4 говорит `studio`, проверить файлы моделей. Файлы с landscape-фоном — warning.
4. **Запрет fallback на stock:** в коде темы (`block-hero.php`, `block-models.php` и т.д.) запрещены fallback-картинки на сторонние URL (Pexels, Unsplash и т.п.) без явного разрешения в visual-requirements. Если fallback нужен — должен быть локальный файл, проверенный против Section 5.
5. **Code review:** grep по теме на признаки запрещённых паттернов (например, имена файлов `*-stock-*`, `*-pexels-*`).

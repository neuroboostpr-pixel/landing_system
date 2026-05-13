---
name: wp-builder
description: Use during stage 08 after design-system-generator and content-writer have run. Generates Gutenberg block PHP+JS code, fills template-parts, writes CSS/JS, creates generateblocks-templates.json.
allowed-tools: Bash, Read, Write, Edit
---

# wp-builder (WP-сборщик)

## Mission

Генерирую PHP-код Gutenberg-блоков и CSS/JS для лендинга на основе токенов дизайна и финального контента.

## Prerequisites

- `08_КОД/wp-theme/` уже создан `scripts/generate-wp-blocks.py` (Lazy Blocks scaffold готов: theme + blocks/lazyblock-<slug>/block.php + lzb/init в functions.php + page-content.html)
- `08_КОД/block-spec.yaml` — источник правды для Lazy Blocks контролов (НЕ `acf-fields.json` — ACF Blocks deprecated)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — токены
- `07_КОНТЕНТ/final-copy.md` — финальный текст по блокам
- `06_СТЕК/design-stack.yaml` — стек и режим (standard/cinematic)
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — **источник истины** для списка template-parts. Раздел «Контракт с wp-builder» содержит точный список .php-файлов, которые нужно сгенерировать. Лишних блоков не создавать, отсутствующих не пропускать.
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — для адаптации поведения блоков (см. ниже).
- `01a_АНАЛИЗ_НИШИ/positioning.md` — заголовок `**Mode:** <режим>` определяет приоритеты блоков.

## What I do

1. Читаю `01a_АНАЛИЗ_НИШИ/landing-structure.md` → секция «Контракт с wp-builder». Это **полный** список template-parts, которые надо создать. Если в final-copy.md есть блок, которого нет в landing-structure — игнорировать; если в landing-structure есть блок, которого нет в final-copy — warning + создать заглушку.
2. Читаю `01a_АНАЛИЗ_НИШИ/positioning.md` → `**Mode:** <режим>` для Mode-aware behavior (см. ниже).
3. Читаю `01a_АНАЛИЗ_НИШИ/market-profile.md` → `accessibility_tier` для price-display поведения.
4. Читаю `07_КОНТЕНТ/final-copy.md` — извлекаю текст каждой секции.
5. Читаю `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цвета, типографику, отступы, радиус.
6. Читаю `06_СТЕК/design-stack.yaml` — режим, иконки, JS-библиотеки.
7. Читаю `08_КОД/acf-fields.json` — какие поля доступны через ACF.
8. Для каждой секции из landing-structure пишу `template-parts/section-{name}.php`:
   - Использует `get_field()` из ACF для редактируемых полей
   - CSS-классы только через `--token-name` переменные (без хардкода цветов)
   - Каждый файл начинается с комментария `/* wp-builder: source=DESIGN.md, token=... */`
9. Пишу `assets/css/main.css` — стили всех блоков через CSS-переменные.
10. Пишу `assets/js/main.js` — базовые интеракции (аккордеон FAQ, scroll-to-form).
    - Если режим `cinematic`: добавляю GSAP ScrollTrigger анимации по scenes.md.
11. Пишу `08_КОД/generateblocks-templates.json` — шаблон для импорта в GenerateBlocks.
12. **HARD GATE**: показываю список созданных файлов, жду утверждения.

## Mode-aware behavior

- **`emotional_aspiration`**: Hero — fullscreen image-driven, цена скрыта или в FAQ. Featured/Catalog — крупная сетка с минимумом текста. Trust-блоки компактные.
- **`trust_authority`**: Hero — заголовок + ключевая trust-метрика крупно, фото эксперта/команды. Process/Reviews/Risk-reversal блоки — приоритетные, с явной разметкой schema.org (Review, Person).
- **`rational`**: Hero — заголовок + ключевая цифра, spec-table сразу под Hero. Pricing — прозрачно, без скрытий.
- **`hybrid:X+Y`**: primary mode задаёт основные блоки, secondary добавляет 1–2 поддерживающих.
- **`legacy_v1`**: работать как раньше, без mode-аугментации.

## Accessibility tier behavior

Из `market-profile.md` поле `Tier:`:
- `luxury_status` / `ultra_luxury` → **не показывать price prominently в Hero**. Цена доступна только в Catalog или по запросу. CTA — «Связаться» / «Тест-драйв», не «Купить».
- `premium` → цена допустима, но через `<del>` (старая) и accent-color (новая) только если есть скидка; иначе нейтрально.
- `mid_premium` / `mass_consumer` / `utility_essential` → цена prominently в Hero/Catalog, как ключевой sales-driver.

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

# Cookie-banner Library — Design (B2)

**Status:** approved (interactive brainstorm 2026-05-22)
**Replaces:** B1 cookie-banner files (`template/08_КОД/template-parts/cookie-banner.{php,js,css}` + `consent-init.php`)
**Related:** [B1 spec](2026-05-21-b1-cookie-banner-pd-consent-design.md), [S2-A.3 spec](2026-05-19-s2a3-network-admin-unification-design.md)

## Problem

B1 поставил рабочий cookie-banner, но:

1. **Один layout** (bottom-bar), невозможно переключить под нишу/бренд лендинга.
2. **Тексты hardcoded** в PHP-шаблоне — каждый проект руками правит `cookie-banner.php`.
3. **Цвета через CSS-vars темы** работают, но нельзя override'ить через wp-admin (например, если маркетологу нужен brand-accent отличный от темы).
4. **Категории hardcoded** (necessary/analytics/marketing) — нельзя скрыть или добавить четвёртую.
5. **`functions.php` hooks теряются при regen** stage-08 — баг подтверждён на dubai-avto-liza.
6. **Нет admin UI** — маркетолог не может ничего поправить без разработчика.

## Goal

Cookie-banner становится **частью `landing-config` mu-plugin** (как CTA / Integrations / Snippets / Lead Statuses из S2-A.3):
- 5 визуальных layout-вариантов на выбор (top-bar / bottom-bar / floating-card-left / floating-card-right / center-modal)
- Network admin UI с cascade (network default + per-segment override)
- Тексты, категории, цвета редактируемы из wp-admin
- По умолчанию цвета наследуются из brand-kit theme через CSS-vars, опционально можно задать hex-override
- Mu-plugin рендерит сам (через `wp_head`/`wp_footer` хуки) — независим от темы и переживает `generate-wp-blocks.py` регенерацию

## Non-goals

- **Multi-language switcher для banner** — баннер на языке сайта (`get_locale()`). Если на лендинге N официальных языков — это про legal-pages (отдельная итерация), не про banner.
- **A/B-тестирование вариантов layout** — out of scope.
- **Автоматический cookie-scanner** (определение какие cookies устанавливаются) — это контентная задача маркетолога, не инфраструктурная.
- **Кастомные категории кроме 3 базовых** — repeater есть в admin (см. CPT model), но MVP только seed'ит 3 стандартные. Если клиенту нужна 4-я (например, "Специальные категории ПД" для медицины) — admin позволяет добавить.

## Architecture

Cookie-banner полностью живёт в `landing-config` mu-plugin. Никаких файлов в `wp-theme/` (B1-файлы удаляются).

```
skills/wp-landing-config/mu-plugin/landing-config/
├── includes/
│   └── cookie-banner/
│       ├── cpt.php                    # NEW: register lp_cookie_banner CPT
│       ├── resolver.php               # NEW: cascade::resolve_for_blog($blog_id)
│       ├── enqueue.php                # NEW: wp_head hook (consent-init + enqueue)
│       ├── render.php                 # NEW: wp_footer hook (echo DOM)
│       ├── layouts/                   # NEW: 5 per-layout PHP partials
│       │   ├── top-bar.php
│       │   ├── bottom-bar.php
│       │   ├── floating-card-left.php
│       │   ├── floating-card-right.php
│       │   └── center-modal.php
│       ├── admin-network.php          # NEW: editor UI
│       ├── admin-site-readonly.php    # NEW: read-only view on subsite
│       └── migrate.php                # NEW: seed network default on activation
└── assets/cookie-banner/
    ├── core.css                       # NEW: shared (vars, reset, typography, buttons, toggles)
    ├── layouts/                       # NEW: per-layout overrides (~30-50 lines each)
    │   ├── top-bar.css
    │   ├── bottom-bar.css
    │   ├── floating-card.css          # shared by left + right (mirrored)
    │   └── center-modal.css
    └── banner.js                      # NEW: vanilla JS — localStorage + gtag.consent.update
```

### Module: cpt.php

Регистрирует CPT `lp_cookie_banner`:
- `public: false` (не появляется в Posts/Pages меню сверху)
- `show_in_menu: false` (выводится через custom admin page, не auto-menu)
- `capability_type: post`, `capabilities` маппятся на `manage_network_options`
- Один record на network (`segment=0`) + по одному на subsite с overrides

### Module: resolver.php

Cascade-функция, повторяет паттерн `landing_config\cta\cascade::resolve_for_blog()`:

```php
function resolve_for_blog(int $blog_id): array {
    $network = get_record_for_segment(0);
    $site = get_record_for_segment($blog_id);
    if ($site === null && $network === null) {
        return DEFAULTS;
    }
    if ($site === null) {
        return $network;
    }
    if ($network === null) {
        return $site;
    }
    // Site overrides network field-by-field (non-empty wins)
    return merge_non_empty($site, $network);
}
```

`DEFAULTS` — baseline для случая «никто ничего не настроил» (bottom-bar, no categories, RU texts, all colors=inherit).

### Module: enqueue.php — `wp_head` hook

```php
add_action('wp_head', function () {
    $settings = resolver\resolve_for_blog(get_current_blog_id());
    if ($settings === null) return;  // banner disabled

    // 1. consent-init script (gtag default denied) — MUST run before analytics
    echo '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
       . 'gtag("consent","default",{"analytics_storage":"denied","ad_storage":"denied",'
       . '"ad_user_data":"denied","ad_personalization":"denied","wait_for_update":500});</script>';

    // 2. Color overrides (inline <style>)
    $color_overrides = compact_non_empty_colors($settings);
    if ($color_overrides) {
        echo '<style id="lp-cb-overrides">.lp-cb{' . $color_overrides . '}</style>';
    }

    // 3. Enqueue CSS + JS
    $base = plugin_dir_url(__FILE__) . '../../assets/cookie-banner';
    wp_enqueue_style('lp-cb-core', $base . '/core.css', [], LP_CB_VERSION);
    wp_enqueue_style('lp-cb-layout', $base . '/layouts/' . $settings['layout'] . '.css', ['lp-cb-core'], LP_CB_VERSION);
    wp_enqueue_script('lp-cb', $base . '/banner.js', [], LP_CB_VERSION, true);

    // 4. Pass config to JS
    wp_localize_script('lp-cb', 'LP_CB_CONFIG', [
        'version'      => (int) $settings['consent_version'],
        'storage_key'  => 'lp_cookie_consent',
        'categories'   => $settings['categories'],
        'gtag_map'     => GTAG_MAP,  // see Data Model below
        'show_categories' => (bool) $settings['show_categories'],
    ]);
}, 1);  // priority 1 = ASAP, before analytics-engineer's gtag.js
```

### Module: render.php — `wp_footer` hook

```php
add_action('wp_footer', function () {
    $settings = resolver\resolve_for_blog(get_current_blog_id());
    if ($settings === null) return;
    $layout = $settings['layout'];
    $tpl = __DIR__ . '/layouts/' . $layout . '.php';
    if (!file_exists($tpl)) {
        $tpl = __DIR__ . '/layouts/bottom-bar.php';  // safe fallback
    }
    // The layout template reads $settings array directly.
    include $tpl;
});
```

Каждый layout-template — это PHP с DOM-разметкой:

```php
<?php /* layouts/bottom-bar.php */ ?>
<div id="lp-cb" class="lp-cb lp-cb--bottom-bar" data-version="<?= esc_attr($settings['consent_version']) ?>" hidden>
    <div class="lp-cb__inner">
        <h2 class="lp-cb__title"><?= esc_html($settings['title']) ?></h2>
        <p class="lp-cb__desc"><?= esc_html($settings['description']) ?></p>

        <?php if ($settings['show_categories']): ?>
            <div class="lp-cb__categories">
                <?php foreach ($settings['categories'] as $cat): ?>
                    <label class="lp-cb__category">
                        <input type="checkbox"
                               data-slug="<?= esc_attr($cat['slug']) ?>"
                               <?= $cat['locked'] ? 'checked disabled' : '' ?>
                               <?= !empty($cat['default_on']) ? 'checked' : '' ?>>
                        <span class="lp-cb__category-name"><?= esc_html($cat['name']) ?></span>
                        <span class="lp-cb__category-desc"><?= esc_html($cat['desc']) ?></span>
                    </label>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <div class="lp-cb__actions">
            <?php if (!empty($settings['policy_link_text'])): ?>
                <a class="lp-cb__policy" href="<?= esc_url($settings['policy_link_url']) ?>" target="_blank">
                    <?= esc_html($settings['policy_link_text']) ?>
                </a>
            <?php endif; ?>
            <?php if ($settings['show_categories']): ?>
                <button class="lp-cb__btn lp-cb__btn--secondary" data-action="save">
                    <?= esc_html($settings['btn_save_text']) ?>
                </button>
            <?php endif; ?>
            <?php if (!empty($settings['btn_reject_text'])): ?>
                <button class="lp-cb__btn lp-cb__btn--ghost" data-action="reject">
                    <?= esc_html($settings['btn_reject_text']) ?>
                </button>
            <?php endif; ?>
            <button class="lp-cb__btn lp-cb__btn--primary" data-action="accept-all">
                <?= esc_html($settings['btn_accept_all_text']) ?>
            </button>
        </div>
    </div>
</div>
<button id="lp-cb-reopen" class="lp-cb-reopen" hidden><?= esc_html($settings['reopen_text']) ?></button>
```

Остальные 4 layouts (top-bar, floating-card-left/right, center-modal) — практически идентичны, отличие только в обёртывающем `class="lp-cb lp-cb--<layout>"` и (для center-modal) дополнительный `<div class="lp-cb__backdrop"></div>` для затемнения фона.

### Module: banner.js

Vanilla JS, ~150 строк. Чистая state-machine:

```javascript
(function(){
    const cfg = window.LP_CB_CONFIG;
    if (!cfg) return;
    const banner = document.getElementById('lp-cb');
    const reopen = document.getElementById('lp-cb-reopen');
    if (!banner) return;

    function loadConsent() { /* localStorage parse with version check */ }
    function saveConsent(consent) { /* localStorage set + applyGtag(consent) */ }
    function applyGtag(consent) {
        if (typeof window.gtag !== 'function') return;
        const update = {};
        for (const slug in consent) {
            const gtag_keys = cfg.gtag_map[slug] || [];
            for (const k of gtag_keys) update[k] = consent[slug] ? 'granted' : 'denied';
        }
        window.gtag('consent', 'update', update);
    }
    function showBanner() { banner.hidden = false; reopen.hidden = true; }
    function hideBanner() { banner.hidden = true; reopen.hidden = false; }

    // Initial check
    const existing = loadConsent();
    if (!existing || existing.version !== cfg.version) showBanner();
    else { hideBanner(); applyGtag(existing.consent); }

    // Wire buttons
    banner.querySelector('[data-action="accept-all"]').addEventListener('click', () => {
        const consent = {};
        for (const cat of cfg.categories) consent[cat.slug] = true;
        saveConsent({ version: cfg.version, consent, ts: Math.floor(Date.now()/1000) });
        hideBanner();
    });
    // ... reject, save, reopen — analogous
})();
```

## Data Model

### CPT `lp_cookie_banner` — post_meta keys

| Key | Type | Default | Description |
|---|---|---|---|
| `_lp_segment` | int | 0 | 0 = network default, N = override for blog_id N |
| `_lp_layout` | string | `"bottom-bar"` | one of: `top-bar`, `bottom-bar`, `floating-card-left`, `floating-card-right`, `center-modal` |
| `_lp_title` | string | `"Мы используем cookies"` | Banner heading |
| `_lp_description` | string (textarea) | (RU default) | Body text |
| `_lp_btn_accept_all_text` | string | `"Принять все"` | Primary CTA |
| `_lp_btn_save_text` | string | `"Сохранить настройки"` | Shown only if `show_categories=true` |
| `_lp_btn_reject_text` | string | `""` | Empty = button hidden |
| `_lp_policy_link_text` | string | `"Политика обработки персональных данных"` | Empty = link hidden |
| `_lp_policy_link_url` | string | `"/policy"` | Target URL |
| `_lp_reopen_text` | string | `"Настройки cookies"` | Footer reopener button label |
| `_lp_show_categories` | bool | `false` | If false, single Accept/Reject mode |
| `_lp_categories` | JSON array | (3 defaults) | List of `{slug, name, desc, locked, default_on}` |
| `_lp_color_bg` | string | `""` | Hex; empty = inherit `var(--color-bg-card)` from theme |
| `_lp_color_text` | string | `""` | Hex; empty = inherit `var(--color-text-primary)` |
| `_lp_color_accent` | string | `""` | Hex; empty = inherit `var(--color-accent)` |
| `_lp_color_border` | string | `""` | Hex; empty = inherit `var(--color-border)` |
| `_lp_consent_version` | int | `1` | Bump → all users see banner again |

### GTAG_MAP constant

```php
const GTAG_MAP = [
    'necessary' => [],
    'analytics' => ['analytics_storage'],
    'marketing' => ['ad_storage', 'ad_user_data', 'ad_personalization'],
];
```

Если маркетолог добавит кастомную категорию через repeater (e.g. `slug=functional`) — она не имеет gtag-маппинга и просто сохраняется в localStorage без побочных эффектов на gtag.

### Default categories (seed на activation)

```json
[
  { "slug": "necessary", "name": "Необходимые",
    "desc": "Обеспечивают базовую работу сайта. Не могут быть отключены.",
    "locked": true,  "default_on": true },
  { "slug": "analytics", "name": "Аналитика",
    "desc": "Помогают понять, как посетители используют сайт (Яндекс.Метрика, Google Analytics).",
    "locked": false, "default_on": false },
  { "slug": "marketing", "name": "Маркетинг",
    "desc": "Используются для показа релевантной рекламы и ретаргетинга.",
    "locked": false, "default_on": false }
]
```

### CSS variables — banner-local

В `core.css` объявлены **banner-local** CSS-vars, которые по умолчанию ссылаются на theme-vars:

```css
.lp-cb {
    --cb-bg:      var(--color-bg-card, #ffffff);
    --cb-text:    var(--color-text-primary, #1d2327);
    --cb-accent:  var(--color-accent, #2271b1);
    --cb-border:  var(--color-border, #c3c4c7);
    /* ... */
}
```

Color-override от admin перезаписывает их через inline-style:

```html
<style id="lp-cb-overrides">.lp-cb{ --cb-bg:#ff0; --cb-accent:#f00; }</style>
```

Это даёт **3 уровня каскада** для каждого цвета:
1. Override от admin (hex)
2. Theme CSS-var из brand-kit (`--color-accent`)
3. Hardcoded fallback внутри `var(..., fallback)`

## Admin UI

### Network admin → Лендинг → Cookie-banner (`landing-config-network-cookie-banner`)

Capability: `manage_network_options`. URL: `network/admin.php?page=landing-config-network-cookie-banner&segment=<N>`.

Layout (одна форма с 5 секциями — см. брейнсторм):

1. **Селектор сегмента** — same widget as CTA/Integrations
2. **Layout picker** — 5 radio-кнопок с превью-thumbnail'ами (SVG 200×120 для каждого layout варианта, лежат в `assets/cookie-banner/previews/`)
3. **Тексты** — text inputs / textareas для каждого `_lp_*_text` поля
4. **Категории** — checkbox `show_categories` + repeater table (slug/name/desc/locked) + кнопка `[+ Добавить категорию]`
5. **Цвета** — 4 color-picker'а (WP core `wp-color-picker` JS) для bg/text/accent/border. По умолчанию пусто = "inherit from theme"
6. **Версия согласия** — number input
7. **Live preview link** — открывает `/?lp_cookie_banner_preview=1&segment=<N>` в новой вкладке. Параметр распознаётся `enqueue.php` и (а) принудительно показывает banner, (б) использует превью-настройки (если страница рендерится для preview-режима).

### Site admin → Лендинг → Cookie-banner (read-only)

Capability: `manage_options`. Slug: `landing-config-site-cookie-banner`. Показывает:
- Resolved settings (output of `resolve_for_blog(current_blog_id)`) — read-only вид
- Источник каждого поля: `[network]` / `[site override]` / `[default]`
- Кнопка `[Override в network admin]` — deep-link с `?segment=<this_blog_id>`

## Migration

### From B1 (deprecation)

**Удаляются** из `template/08_КОД/template-parts/`:
- `cookie-banner.php`
- `cookie-banner.js`
- `cookie-banner.css`
- `consent-init.php`

**Сохраняется:** `legal-block.php` (это про формы, не cookies).

**Удаляются** из `template/08_КОД/wp-theme/functions.php` шаблона (тот, из которого `generate-theme.py` копирует в проекты):
- `wp_enqueue_style('lp-cookie-banner', ...)` + `wp_enqueue_script('lp-cookie-banner', ...)`
- `add_action('wp_head', function() { get_template_part('template-parts/consent-init'); }, 1);`
- `add_action('wp_footer', function() { get_template_part('template-parts/cookie-banner'); });`

После B2 ни одна тема не содержит cookie-banner код — mu-plugin делает всё.

### Existing deployments (dubai-avto-liza, russian.ailexi)

Migration runner в mu-plugin (`landing_config_migration_b2_cookie_banner`):
1. Если CPT `lp_cookie_banner` не существует — register'ит.
2. Если нет ни одной записи — seed'ит network default запись с DEFAULTS + 3 категориями.
3. Помечает marker `landing_config_migration_b2_cookie_banner = 1`.

После migration runner — старые B1-файлы в `wp-theme/template-parts/` всё ещё на диске (не трогаем), но `functions.php` уже не должен их подключать. Чистка после: удалить файлы при следующем `landing-build` (новый шаблон themes их не содержит).

### Stage-gate update

`scripts/checks/check_legal_blocks.sh` обновляется:
- **Удаляются** проверки: `cookie-banner.php`, `consent-init.php`, `footer.php` содержит `cookie-banner`, `header.php` содержит `consent-init`
- **Остаются** проверки: `legal-block.php` существует + хотя бы один block-template ссылается на legal-block
- **Добавляется** новая проверка: mu-plugin landing-config установлен на сервере + CPT `lp_cookie_banner` зарегистрирован (через WP-CLI: `wp post-type get lp_cookie_banner --network-id=1`)

## Error handling

| Условие | Поведение |
|---|---|
| Settings = null (никто не настроил) | Banner не показывается, consent-init не эмитится. Лендинг работает как до B2 (без consent). Корректно для greenfield. |
| Layout указан, но файл не найден | Fallback на `bottom-bar.php` + warning в error log |
| Категория без слага | Skip в JS (categories.filter(c => c.slug)) |
| Color hex невалидный | sanitize_hex_color() → empty → inherit from theme |
| Version downgrade (admin поменял version с 5 на 3) | Banner показывается всем (т.к. локальный version=5 ≠ 3) — это feature, маркетолог может «откатить» |
| Preview-режим без admin-прав | `current_user_can('manage_options')` guard на `?lp_cookie_banner_preview=1` |

## Testing

### Unit (PHP, в `skills/wp-landing-config/tests/`)

- `test_cookie_banner_resolver.php` — cascade resolve_for_blog:
  - network only → network values
  - site only → site values
  - both → site overrides network field-by-field
  - neither → DEFAULTS
- `test_cookie_banner_render.php` — render output:
  - все 5 layouts генерируют валидный HTML с `id="lp-cb"`
  - категории hidden если `show_categories=false`
  - reject button hidden если `btn_reject_text=""`
  - color-overrides попадают в inline-style
- `test_cookie_banner_cpt.php` — CPT registration + capabilities
- `test_cookie_banner_migration.php` — seed default запись, idempotent re-run

### Integration smoke (в `tests/integration/test_s2a3_smoke.sh`)

- T_CB_1: главная страница содержит `id="lp-cb"`
- T_CB_2: главная страница содержит `gtag("consent","default"`
- T_CB_3: `?lp_cookie_banner_preview=1&segment=0` отдаёт banner поверх главной
- T_CB_4: после смены `_lp_layout` через wp-cli — на главной meняется `class="lp-cb lp-cb--<new>"`

### Visual QA (manual)

Все 5 layouts на dubai-avto-liza:
- Mobile (≤600px): center-modal остаётся карточкой в центре, остальные адаптируются (full-width)
- Desktop: позиционирование корректное, не перекрывают важный контент
- Dark theme сайта: цвета читаемые (color contrast WCAG AA)
- Light theme сайта: то же

## Acceptance criteria

- [ ] CPT `lp_cookie_banner` зарегистрирован на dubai-avto-liza network
- [ ] Network admin страница editor работает, сохраняет все поля
- [ ] Live-preview ссылка показывает banner на главной
- [ ] Все 5 layouts рендерятся при выборе в admin (smoke test)
- [ ] Color override в admin меняет цвета на live
- [ ] Если color пустой — banner наследует цвета из brand-kit темы
- [ ] B1-файлы (cookie-banner.* + consent-init.php) удалены из template + wp-theme
- [ ] `functions.php` regen больше не содержит cookie-banner hooks (backlog решён)
- [ ] Migration marker `landing_config_migration_b2_cookie_banner` ставится
- [ ] `check_legal_blocks.sh` обновлён под новую схему
- [ ] Visual QA на 5 layouts × 2 размера (mobile + desktop) = 10 скриншотов сделаны и приняты

# S2-A.2: Snippets manager (replaces Head & SEO) + Network scope

> Status: rescoped 2026-05-19 — add network-level snippets so super-admin может
> настраивать GA4/Y.Metrika/CTA/credentials **один раз** на всю multisite-сеть,
> а subsite только перекрывает по необходимости.
> Branch: `worktree-s2a2-snippets-manager`
> Spec author: Claude (S2-A live UX testing на ailexi.ru показал, что 11 фиксированных полей Head & SEO слишком жёсткие; пользователи копируют готовые snippet'ы целиком, и не могут добавить произвольный счётчик/виджет/JSON-LD/chat-widget. Дополнительный UX-сигнал: пользователь не хочет править одни и те же снипеты на каждом subsite — нужны network defaults.)

## 1. Цель

Дать маркетологу/клиенту через wp-admin вставлять **произвольное количество HTML-snippet'ов** в `<head>`, начало `<body>` или footer любой страницы.

**Два уровня хранения:**

| Уровень | Где UI | Где хранится | Применяется к |
|---|---|---|---|
| **Network** | Network Admin → Лендинг (сеть) → Снипеты | CPT `lp_snippet` на blog_id=1 + meta `_lp_snippet_is_network=1` | ВСЕМ subsites (если не перекрыто) |
| **Site** | Subsite Admin → Лендинг → Снипеты | CPT `lp_snippet` на текущем subsite + meta `_lp_snippet_is_network=0` | только этому subsite |

**Cascade (override):**

- Снипет имеет опциональное поле `name` (machine-id, например `ga4`, `jivosite`).
- Если на site есть snippet с тем же `name` что и network → network скипается для этой position+name.
- Snippet без `name` (default) → всегда append (network и site сосуществуют).

**Дополнительные оси:**

- **Position:** `head` / `body_open` / `body_close`
- **Page-scope** (внутри site): `global` (все страницы subsite) / `local` (на выбранные Page/Post)
- **Enabled** (on/off)
- **Priority** (порядок вывода в той же position; меньшее = раньше)
- **Allow-list:** `<script>`, `<meta>`, `<link>`, `<style>`, `<noscript>`, `<iframe>`, `<div>` (любые виджеты, schema.org JSON-LD, font preload, chat-виджеты, Tag Manager и т.д.).

## 2. Удаление старой Head & SEO

Удаляется **полностью** (данных в проде нет — только что задеплоили без заполнения):

- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php` → удалить файл
- В `landing-config.php`: удалить `require_once .../admin-head-seo.php` и `add_action('wp_head', 'landing_render_head_extras', 5)`
- В `helpers.php`: удалить функцию `landing_render_head_extras()` (или оставить пустой стаб с deprecated-нотисом, если будут темы её вызывающие — на сегодня их нет)
- В админ-меню (admin-pages.php дашборд): обновить `<li>` Head & SEO → «Снипеты»

11 опций `wp_options::landing_<ga4_id|yandex_metrika_id|...>` — не созданы в production, удалять нечего. Если в будущем будут проекты с заполненными полями — отдельная migration; для текущего deploy не требуется.

## 3. Архитектура

### 3.1 Хранение — Custom Post Type `lp_snippet`

```php
register_post_type('lp_snippet', [
    'public'              => false,        // не показывается на сайте как URL
    'show_ui'             => false,        // мы строим свою admin страницу
    'show_in_menu'        => false,
    'show_in_rest'        => false,        // в дальнейшем можно открыть для headless
    'supports'            => ['title'],    // title = label в админке
    'capability_type'     => 'post',
    'map_meta_cap'        => true,
    'capabilities'        => [
        'edit_post'          => 'manage_options',
        'edit_posts'         => 'manage_options',
        'edit_others_posts'  => 'manage_options',
        'publish_posts'      => 'manage_options',
        'read_post'          => 'manage_options',
        'delete_post'        => 'manage_options',
    ],
]);
```

CPT регистрируется на каждом subsite (per-blog). post_meta:

| meta_key | type | description |
|---|---|---|
| `_lp_snippet_code` | longtext | RAW HTML/JS body |
| `_lp_snippet_position` | enum | `head` \| `body_open` \| `body_close` |
| `_lp_snippet_scope` | enum | `global` \| `local` |
| `_lp_snippet_target_post_ids` | array of int | при scope=local — список Page/Post IDs, на которых рендерить |
| `_lp_snippet_enabled` | bool | on/off (default true) |
| `_lp_snippet_priority` | int | порядок вывода в той же position (default 10, lower=earlier) |
| `_lp_snippet_is_network` | bool | `true` если это network-snippet (хранится на blog 1, render на всех subsites) |
| `_lp_snippet_name` | string | machine-id для override логики (например `ga4`, `jivosite`). Если на site есть snippet с тем же `name` → network snippet с этим name скипается. `''` (default) → всегда append, нет override |

### 3.2 Renderer

Три hook'а в `includes/snippets.php`:

```php
add_action('wp_head',       'LandingConfig\\Snippets\\render_head',       5);
add_action('wp_body_open',  'LandingConfig\\Snippets\\render_body_open',  5);
add_action('wp_footer',     'LandingConfig\\Snippets\\render_body_close', 99);
```

Логика `render($position)`:

1. **Собрать site snippets** для текущего subsite: enabled=true, position=$position, scope/target проверка.
2. **Собрать network snippets** через `switch_to_blog(1)`: enabled=true, position=$position, is_network=true. Restore_current_blog.
3. **Override**: построить set `$site_names = [name for site snippet if !empty(name)]`. Скипать network-snippet если `name in $site_names`.
4. **Page-scope filter**: для site snippets — оставить только `scope=global` ИЛИ (`scope=local` И `get_queried_object_id() in target_post_ids`). Network snippets всегда `scope=global` (page-scope для них не поддерживается в MVP).
5. **Sort by priority ASC** (network и site вместе в одном списке).
6. **Вывод**: для каждого — обёртка `<!-- lp_snippet:N "Title" [network|site] -->` + echo code + close-comment.

### 3.3 Sanitization при save

Расширенный wp_kses allow-list — определён в `includes/snippets.php` как константа:

```php
const ALLOWED_HTML = [
    'script'   => ['src' => true, 'async' => true, 'defer' => true, 'type' => true,
                   'crossorigin' => true, 'integrity' => true, 'nonce' => true,
                   'data-*' => true, 'id' => true, 'class' => true],
    'meta'     => ['name' => true, 'content' => true, 'property' => true,
                   'http-equiv' => true, 'charset' => true, 'itemprop' => true],
    'link'     => ['rel' => true, 'href' => true, 'type' => true, 'crossorigin' => true,
                   'sizes' => true, 'as' => true, 'media' => true, 'integrity' => true],
    'style'    => ['type' => true, 'media' => true, 'id' => true, 'class' => true],
    'noscript' => ['id' => true, 'class' => true],
    'iframe'   => ['src' => true, 'width' => true, 'height' => true, 'frameborder' => true,
                   'allowfullscreen' => true, 'allow' => true, 'loading' => true,
                   'sandbox' => true, 'id' => true, 'class' => true, 'style' => true,
                   'data-*' => true, 'title' => true, 'name' => true],
    'div'      => ['id' => true, 'class' => true, 'style' => true, 'data-*' => true,
                   'role' => true, 'aria-label' => true],
    'span'     => ['id' => true, 'class' => true, 'style' => true, 'data-*' => true],
    'img'      => ['src' => true, 'alt' => true, 'width' => true, 'height' => true,
                   'style' => true, 'class' => true, 'id' => true],
    'a'        => ['href' => true, 'target' => true, 'rel' => true, 'class' => true,
                   'id' => true, 'style' => true],
    'p'        => ['class' => true, 'id' => true],
    'br'       => [],
];
```

`wp_kses($code, ALLOWED_HTML)` сохраняет: GTM containers, schema.org JSON-LD (внутри `<script type="application/ld+json">`), Yandex.Metrika / GA4 / FB Pixel snippets, любые chat-виджеты (`<script src="https://...widget.js" async>`), font preload, Google Tag Manager `<noscript>`, и т.д.

⚠️ **Внимание:** `wp_kses` со script — это **признанно опасная поверхность**. Capability `manage_options` (только admin/super-admin) — единственная защита. Документируем в SETUP.md.

### 3.4 Admin UI

#### 3.4.1 Список — Site Admin (Лендинг → Снипеты)

URL: `admin.php?page=landing-config-snippets`

Две таблицы:

**A. Site snippets (этого subsite):**

| Name | Title | Position | Scope | Enabled | Priority | Actions |
|---|---|---|---|---|---|---|
| ga4 | GA4 main | head | global | ✅ | 5 | Edit / Delete |
| — | Schema HomePage | head | local (3 pages) | ✅ | 10 | Edit / Delete |

Кнопка «Добавить snippet» → форма.

**B. Inherited from network (read-only):**

| Name | Title | Position | Status | Action |
|---|---|---|---|---|
| ga4 | Sitewide GA4 | head | Overridden by site `ga4` | — |
| jivosite | JivoSite chat | body_close | Active (inherited) | «Override» (copy to site) |

Если у site есть snippet с тем же `name` — показываем «Overridden by site `<name>`». Иначе «Active (inherited)» + кнопка «Override» которая клонирует network snippet в site и открывает на редактирование.

#### 3.4.2 Список — Network Admin (Лендинг (сеть) → Снипеты)

URL: `network/admin.php?page=landing-config-network-snippets` (новая страница, добавляем).

Только одна таблица:

| Name | Title | Position | Enabled | Priority | Overridden by | Actions |
|---|---|---|---|---|---|---|
| ga4 | Sitewide GA4 | head | ✅ | 5 | russian.ailexi.ru | Edit / Delete |
| jivosite | JivoSite chat | body_close | ✅ | 10 | — | Edit / Delete |

«Overridden by» — список subsites где есть site snippet с тем же name (показ только при наличии).

Кнопка «Добавить network snippet» → форма (без поля «target pages» — network всегда global).

#### 3.4.3 Форма создания/редактирования (общая для site + network)

`admin.php?page=landing-config-snippets&action=edit&id=<N>` (site)
`network/admin.php?page=landing-config-network-snippets&action=edit&id=<N>` (network)

Поля:

- **Title** (text, required) — для админки
- **Name** (text, optional) — machine-id для override (например `ga4`). Пустое = всегда append
- **Position** (radio): `head` / `body_open` / `body_close`
- **Scope** (radio): `global (all pages of subsite)` / `local (selected pages)` — **скрыто на network** (всегда global)
- **Target pages** (multi-select, visible when scope=local) — список Page+Post; — **скрыто на network**
- **Enabled** (checkbox, default true)
- **Priority** (number, default 10) — для порядка вывода
- **Code** (textarea, monospace, ~15 rows)
- **Save** / **Cancel** / **Delete (if editing)**

#### 3.4.4 Meta-box в редакторе Page/Post

В Pages/Posts edit screen — meta-box «Лендинг: ad-hoc snippets»:

```
[+] Add snippet
  ↓
  Position: [head ▼]
  Code: [textarea]
  [Save snippet] (создаёт скрытый lp_snippet с scope=local + target_post_ids=[current_id])
```

Также показывает список существующих `lp_snippet` с `scope=local` где `target_post_ids` содержит текущий post_id, с inline edit/delete.

## 4. Меню

В `admin-pages.php`:
- Удалить пункт «Head & SEO»
- Добавить «Снипеты» (после «CTA-кнопки», перед «Интеграции»)

В dashboard описание разделов — заменить «Head & SEO» на «Снипеты — счётчики, мета-теги, виджеты, любой HTML в head/body/footer».

## 5. Файлы (новые/изменённые)

### 5.1 Новые

- `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php` — CPT registration + CRUD + renderer (с network-cascade)
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php` — site admin: list (own+inherited) + edit + Override action
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets-network.php` — network admin: list + edit + cross-subsite usage hints

### 5.2 Изменённые

- `landing-config.php` — убрать require admin-head-seo + add_action wp_head; добавить require snippets.php + admin-snippets.php
- `includes/helpers.php` — удалить `landing_render_head_extras()` (или deprecated-stub)
- `includes/admin-pages.php` — заменить «Head & SEO» на «Снипеты» в dashboard `<ul>`
- Дока: CLAUDE.md и docs/SETUP.md — переписать раздел про head/seo на «Снипеты»

### 5.3 Удалённые

- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-head-seo.php`

## 6. Тесты

PHP CLI с wp-bootstrap.php mock:

- `tests/test_snippets_renderer.php`
  - T1: глобальные head-снипеты отсортированы по priority
  - T2: локальный снипет рендерится только если `get_queried_object_id()` ∈ target_post_ids
  - T3: disabled снипет не рендерится
  - T4: пустой код не выводит обёртку
  - T5: позиции изолированы (head не лезет в body_open)
  - T6: локальные приоритетней глобальных при той же position (выводятся после)
  - T7: `landing_snippets_sanitize_code()` сохраняет script/meta/link/iframe-теги
  - T8: `landing_snippets_sanitize_code()` фильтрует `<form>` (не в allow-list)
  - T9: target_post_ids saved/loaded как массив int

Mock'и в `wp-bootstrap.php` — добавить:
- `register_post_type`, `wp_insert_post`, `get_posts`, `get_post_meta`, `update_post_meta`, `wp_kses`, `get_queried_object_id`, `do_action('wp_body_open')`.

## 7. Live smoke на ailexi.ru

1. Re-deploy mu-plugin: `bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a`
2. Открыть `http://ailexi.ru/wp-admin/admin.php?page=landing-config-snippets`
3. Добавить «Y.Metrika test» — position=head, scope=global, code=полный snippet из ya.ru
4. Сохранить.
5. `curl -s http://ailexi.ru/ | grep -c "mc.yandex.ru/metrika"` → 1+
6. Добавить «Schema.org Home» — position=head, scope=local, target=Home page
7. Открыть Home → snippet в исходниках; открыть другую страницу → нет snippet'а.
8. Disable snippet → проверить что исчез.

## 8. Out of scope (для следующих фаз)

- Network defaults / per-site inheritance — пока каждый subsite сам по себе (как сейчас в B17 запрошено отдельно).
- Snippet templates library (preset «Yandex.Metrika», пользователь только вводит counter ID) — отдельный B17/B18-related вопрос.
- A/B-сегментация snippet'ов (показывать разные снипеты разным юзерам) — отдельный feature.
- Import/export snippets (JSON dump) — отдельный feature.
- Snippet versioning beyond WP-revisions — отдельный feature.

## 9. Risks

| Risk | Mitigation |
|---|---|
| `wp_kses` со script позволяет XSS если admin компрометирован | capability `manage_options` — единственная защита; документировано в SETUP.md |
| post_meta `_lp_snippet_target_post_ids` (массив) перформанс при тысячах snippet'ов | для MVP — линейный foreach. При >100 snippet'ов добавить cache via `wp_cache_get` |
| Body_open hook не во всех темах (старые темы могут не вызывать `wp_body_open()`) | Документировать; на современных темах OK |
| CodeMirror отсутствует в core WP? | использовать `wp_enqueue_code_editor()` — это core с WP 4.9+ |

## 10. Migration / cleanup

- Удалить старые опции, если есть (на ailexi.ru их нет, но скрипт безопасен):
  ```php
  foreach (['ga4_id','yandex_metrika_id','fb_pixel_id','tiktok_pixel_id',
            'gsc_verification','yandex_webmaster_id','og_default_image',
            'og_default_title','og_default_description','fonts_google_url',
            'raw_html_head'] as $k) {
      delete_option('landing_' . $k);
  }
  ```
  Этот код запускается **один раз** при первой активации snippets manager (через флаг `landing_snippets_migration_done` в sitemeta).

## 11. Готовность к плану

После одобрения этой спеки — пишу `docs/superpowers/plans/2026-05-19-s2a2-snippets-manager.md` с разбивкой на ~6-8 tasks с TDD, потом subagent-driven impl.

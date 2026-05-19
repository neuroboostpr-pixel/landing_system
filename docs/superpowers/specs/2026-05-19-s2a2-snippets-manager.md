# S2-A.2: Snippets manager (replaces Head & SEO)

> Status: ready for plan
> Branch: `worktree-s2a2-snippets-manager`
> Spec author: Claude (S2-A live UX testing на ailexi.ru показал, что 11 фиксированных полей Head & SEO слишком жёсткие; пользователи копируют готовые snippet'ы целиком, и не могут добавить произвольный счётчик/виджет/JSON-LD/chat-widget. Решение — заменить весь экран на универсальный snippets manager.)

## 1. Цель

Дать маркетологу/клиенту через wp-admin вставлять **произвольное количество HTML-snippet'ов** в `<head>`, начало `<body>` или footer любой страницы. Снипеты:

- **Глобальные** (на весь subsite) или **локальные** (на конкретные Page/Post).
- Локальные имеют приоритет (выводятся ПОСЛЕ глобальных в той же позиции → каскадно перебивают).
- Включаются/выключаются галочкой без удаления.
- Поддерживают любой HTML: `<script>`, `<meta>`, `<link>`, `<style>`, `<noscript>`, `<iframe>`, `<div>` (любые виджеты, schema.org JSON-LD, font preload, chat-виджеты, Tag Manager и т.д.).

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

### 3.2 Renderer

Три hook'а в `helpers.php` (или новый `includes/snippets.php`):

```php
add_action('wp_head',       'landing_snippets_render_head',       5);
add_action('wp_body_open',  'landing_snippets_render_body_open',  5);
add_action('wp_footer',     'landing_snippets_render_body_close', 99);

function landing_snippets_render_head() {
    landing_snippets_render('head');
}
// аналогично для body_open / body_close
```

Логика `landing_snippets_render($position)`:

1. Глобальные снипеты (`scope=global`, `enabled=true`, `position=$position`) — отсортированы по `priority ASC`.
2. Локальные снипеты (`scope=local`, `enabled=true`, `position=$position`, `target_post_ids` содержит `get_queried_object_id()`).
3. Вывод: для каждого — оборачивается комментариями `<!-- lp_snippet:<id> "<title>" -->` для дебага, затем echo `code` (уже прошедший wp_kses при save).

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

#### 3.4.1 Список (Лендинг → Снипеты)

WP_List_Table-style страница: `admin.php?page=landing-config-snippets`

Колонки:

| Title | Position | Scope | Enabled | Updated | Actions |
|---|---|---|---|---|---|
| GA4 main | head | global | ✅ | 2026-05-19 | Edit / Delete |
| GTM noscript | body_open | global | ✅ | 2026-05-19 | Edit / Delete |
| Schema.org HomePage | head | local (3 pages) | ✅ | 2026-05-19 | Edit / Delete |
| JivoSite chat | body_close | global | ❌ | 2026-05-19 | Edit / Delete |

Кнопка `Add new` сверху → форма создания.

#### 3.4.2 Форма создания/редактирования

`admin.php?page=landing-config-snippets&action=edit&id=<N>`

Поля:

- **Title** (text, required) — для админки
- **Position** (radio): `head` / `body_open` / `body_close`
- **Scope** (radio): `global (all pages)` / `local (selected pages)`
- **Target pages** (multi-select, visible when scope=local) — список Page+Post с поиском
- **Enabled** (checkbox, default true)
- **Priority** (number, default 10) — для порядка вывода
- **Code** (textarea, monospace, ~15 rows, syntax-highlight через CodeMirror если доступен)
- **Save** / **Cancel** / **Delete (if editing)**

#### 3.4.3 Meta-box в редакторе Page/Post

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

- `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php` — CPT registration + renderer (3 hook'а)
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-snippets.php` — list + edit page + meta-box

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

# S2-A.2 Snippets Manager — Implementation Plan (rescoped)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Spec is authoritative: [../specs/2026-05-19-s2a2-snippets-manager.md](../specs/2026-05-19-s2a2-snippets-manager.md). Read it before each task.

**Goal:** Universal HTML snippets manager (CPT `lp_snippet`) — заменяет старый Head & SEO. Поддерживает **two-level storage**: network snippets (CPT на blog_id=1, виден всем subsites) + site snippets (CPT на текущем subsite). Override через `_lp_snippet_name` meta.

**Architecture:** Spec §3.

**Tech Stack:** PHP 8.3, WP 6.9 Multisite, WP CPT + post_meta, `wp_kses` allow-list, WP_List_Table-style админка. Тесты — PHP CLI с расширенным `wp-bootstrap.php` mock.

---

## Pre-requisites (done)

- Task 1 (`06a5b6b`) — удалён admin-head-seo + landing_render_head_extras
- Task 2 (`57d80bf`) — wp-bootstrap.php mock расширен для CPT/post_meta/wp_kses

---

## Task 3: snippets.php — CPT + sanitize + CRUD + storage layer (TDD)

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/snippets.php`
- Create: `skills/wp-landing-config/tests/test_snippets_helpers.php`
- Modify: `landing-config.php` — добавить `require_once .../snippets.php`

**Что внутри snippets.php:**

```php
namespace LandingConfig\Snippets;

const POST_TYPE = 'lp_snippet';
const VALID_POSITIONS = ['head', 'body_open', 'body_close'];
const VALID_SCOPES = ['global', 'local'];
const NETWORK_BLOG_ID = 1;  // master blog where network snippets live

const ALLOWED_HTML = [...]; // spec §3.3 — script/meta/link/style/noscript/iframe/div/span/img/a/p/br

// CPT registration on init (per-blog).
add_action('init', __NAMESPACE__ . '\\register', 5);
function register(): void { register_post_type(POST_TYPE, [...spec §3.1...]); }

function sanitize_code(string $code): string;     // wp_kses($code, ALLOWED_HTML)

// CRUD — все принимают флаг $is_network=false по умолчанию.
// При $is_network=true: switch_to_blog(NETWORK_BLOG_ID) → операция → restore.
function save_snippet(array $args, bool $is_network = false): int;
function get_snippet(int $id, bool $is_network = false): ?array;
function delete_snippet(int $id, bool $is_network = false): bool;
function list_snippets(array $filter = [], bool $is_network = false): array;

// Удобные обёртки для clarity:
function list_site_snippets(array $filter = []): array  { return list_snippets($filter, false); }
function list_network_snippets(array $filter = []): array { return list_snippets($filter, true); }
```

**Возвращаемый формат `get_snippet` / item в `list_snippets`:**

```php
[
  'id' => int,
  'title' => string,
  'name' => string,           // machine-id, '' если не задан
  'code' => string,           // sanitized HTML
  'position' => 'head'|'body_open'|'body_close',
  'scope' => 'global'|'local',
  'target_post_ids' => int[],
  'enabled' => bool,
  'priority' => int,
  'is_network' => bool,       // прочитан из meta _lp_snippet_is_network
]
```

**Filter ключи для list_snippets:** `position`, `scope`, `enabled`, `name`.

**Tests (TDD, ~12 assertions):**
- sanitize: script/meta/link/iframe сохранены; form/onclick вырезаны
- save round-trip: title/name/position/scope/priority/enabled/target_post_ids/is_network
- update path: `id` в `$args` → wp_update_post
- defaults: position='head', scope='global', enabled=true, priority=10, target_post_ids=[]
- invalid position fallback к 'head'
- list filter by position и by name
- delete удаляет post + meta
- **network path**: save с `is_network=true` → switch_to_blog mock зафиксировал id=1; list_network_snippets возвращает только is_network=true
- **list_site_snippets** не возвращает network entries (на том же blog мог бы быть случайный is_network=true post; фильтр исключает)

**Mock update (если нужно):** в `wp-bootstrap.php` `switch_to_blog($id)` уже есть из Task 3 S2-A. Убедиться что `_mock_posts` per-blog не разделяются — для тестов это OK (все на одном виртуальном blog).

**Commit:**
```
feat(wp-landing-config): snippets.php — CPT + CRUD with network/site dual storage
```

---

## Task 4: snippets.php renderer — network+site cascade (TDD)

**Files:** modify `snippets.php` (append), create `test_snippets_renderer.php`

**Что добавить в snippets.php:**

```php
add_action('wp_head',      __NAMESPACE__ . '\\render_head',       5);
add_action('wp_body_open', __NAMESPACE__ . '\\render_body_open',  5);
add_action('wp_footer',    __NAMESPACE__ . '\\render_body_close', 99);

function render_head(): void       { render('head'); }
function render_body_open(): void  { render('body_open'); }
function render_body_close(): void { render('body_close'); }

function render(string $position): void {
    if (!in_array($position, VALID_POSITIONS, true)) return;

    $site = list_site_snippets(['position' => $position, 'enabled' => true]);

    // Page-scope filter: keep global + (local with current page in targets)
    $current = get_queried_object_id();
    $site = array_values(array_filter($site, function ($s) use ($current) {
        if ($s['scope'] === 'global') return true;
        return in_array($current, $s['target_post_ids'], true);
    }));

    // Names of site snippets → for network-override
    $site_names = [];
    foreach ($site as $s) { if ($s['name'] !== '') $site_names[] = $s['name']; }

    $network = list_network_snippets(['position' => $position, 'enabled' => true]);
    $network = array_values(array_filter($network, function ($s) use ($site_names) {
        return $s['name'] === '' || !in_array($s['name'], $site_names, true);
    }));

    $all = array_merge($network, $site);
    usort($all, fn($a, $b) => $a['priority'] - $b['priority']);

    foreach ($all as $s) {
        $tag = $s['is_network'] ? 'network' : 'site';
        printf("\n<!-- lp_snippet:%d \"%s\" [%s] -->\n", $s['id'], $s['title'], $tag);
        echo $s['code'];
        printf("\n<!-- /lp_snippet:%d -->\n", $s['id']);
    }
}
```

**Tests (~10 assertions):**
- T1: render('head') outputs sorted by priority ASC (mix of network+site)
- T2: position isolation — body_open snippet не лезет в head
- T3: disabled snippet не выводится
- T4: local snippet only on target_post_ids match
- T5: **network snippet** виден на subsite (даже когда `set_mock_queried_object_id` != blog 1)
- T6: **override**: site snippet с `name='ga4'` → network с тем же name скипается; без `name` → оба выводятся
- T7: site без `name` + network с `name='gtm'` → оба выводятся (no collision)
- T8: debug-comment включает [network] или [site] tag
- T9: invalid position → empty (no fatal)
- T10: priority sort работает кросс-source (network priority=5 идёт раньше site priority=10)

**Commit:**
```
feat(wp-landing-config): snippets renderer with network+site cascade
```

---

## Task 5: admin-snippets.php — site admin UI (subsite Лендинг → Снипеты)

**Files:** create `includes/admin-snippets.php`, modify `landing-config.php`

**Структура (spec §3.4.1, 3.4.3):**

- `add_submenu_page('landing-config', 'Снипеты', ...)` после CTA, перед Интеграции (правка `landing-config.php` — добавить require после `admin-cta.php`)
- `dispatch()` switch: action=list|new|edit|save|delete|override
- `render_list()`:
  - Table A (Site snippets) — owns: Title/Name/Position/Scope/Enabled/Priority + Edit/Delete
  - Table B (Inherited from network) — read-only: Name/Title/Position/Status (`Active inherited` или `Overridden by site "<name>"`) + кнопка «Override» (action=override&network_id=N → клонирует в site CPT, открывает edit)
- `render_edit_form()` — title/name/position/scope/target_pages/enabled/priority/code (spec §3.4.3)
- `handle_save()` — `save_snippet($args, false)` → redirect
- `handle_delete()` — nonced
- `handle_override()` — `get_snippet($network_id, true)` → копирует в site через `save_snippet($payload, false)` → redirect к edit

**Тестов нет** (admin UI, manual smoke на Beget в Task 6).

**Commit:**
```
feat(wp-landing-config): admin-snippets.php — site admin (list + inherited + override)
```

---

## Task 5b: admin-snippets-network.php — network admin UI

**Files:** create `includes/admin-snippets-network.php`, modify `landing-config.php`

**Структура (spec §3.4.2):**

- `add_action('network_admin_menu', ...)` добавляет submenu под parent `landing-config-network` (зарегистрирован в admin-pages.php)
- `dispatch()` — list|new|edit|save|delete
- `render_list()` — таблица: Name/Title/Position/Enabled/Priority/Overridden by/Actions
  - «Overridden by» = scan всех subsites через `get_sites()` + `switch_to_blog` + `list_site_snippets(['name' => $n])` — собрать subsite hosts где override есть. Это N+1 запрос но N мал (≤10 сайтов в типичной сети).
- `render_edit_form()` — те же поля что site, **без** scope/target_pages (всегда global). Поле `name` подсвечено как «важное — машина-id».
- `handle_save()` — `save_snippet($args, true)`
- `handle_delete()` — `delete_snippet($id, true)`
- Capability: `manage_network_options`

**Также в admin-pages.php обновить dashboard description** «Лендинг (сеть)»: упомянуть что есть «Снипеты» на network admin.

**Commit:**
```
feat(wp-landing-config): admin-snippets-network.php — super-admin UI for shared snippets
```

---

## Task 6: live smoke + docs

**Steps:**

1. `bash skills/wp-landing-config/scripts/install-mu-plugin.sh /tmp/test-s2a`
2. Browser smoke:
   - subsite admin `http://ailexi.ru/wp-admin/admin.php?page=landing-config-snippets` — пустой список
   - network admin `http://ailexi.ru/wp-admin/network/admin.php?page=landing-config-network-snippets` — пустой
   - Создать на network: Title=«Y.Metrika», Name=`metrika`, position=head, code=полный snippet с ya.ru. Save.
   - На обоих subsites (ailexi.ru и russian.ailexi.ru): `curl -s http://<host>/ | grep -c "mc.yandex.ru/metrika"` → ≥1
   - На subsite admin (ailexi.ru): создать site snippet с name=`metrika` (другой counter id). Save.
   - `curl -s http://ailexi.ru/` → должен показать site version (network skipped).
   - `curl -s http://russian.ailexi.ru/` → network version (override не применился).
3. Update CLAUDE.md / docs/SETUP.md / docs/beget-cookbook.md — раздел Snippets manager + примечание о network/site cascade.

**Commit:**
```
docs(s2a2): snippets manager + network/site cascade live-validated
```

---

## Self-Review

**Spec coverage:** все §3 секции (storage / renderer / sanitize / admin UI / network) → Tasks 3-5b.

**Deferred:** spec §3.4.4 meta-box в Page/Post editor — отдельный спринт.

**Risks:**
- wp-bootstrap.php mock не разделяет _mock_posts per-blog — Task 3 тестам это OK (всё на одном виртуальном blog с переключением `_mock_current_blog_id`), но если потребуется проверять что post реально создаётся на blog 1 а не на текущем — нужен mock update.
- `wp_body_open()` hook может не вызываться в старых темах — задокументировать в SETUP.md.

**Execution:** subagent-driven, по 1 задаче на subagent. Spec-review + code-quality review после каждой.

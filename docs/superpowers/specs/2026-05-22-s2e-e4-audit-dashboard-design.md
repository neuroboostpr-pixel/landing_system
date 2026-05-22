# S2-E.4 — Audit Dashboard + Head & SEO Settings — Design

**Status:** approved (interactive brainstorm 2026-05-22).
**Phase:** E4 (продолжение S2-E.1, реализующее AI checks + admin UI; auto-fix через deep-links)
**Spec reference:** [S2-E spec §3.7 + §13](2026-05-15-s2e-seo-tech-audit-design.md)
**Related:** [B2 Cookie-banner Library](2026-05-22-b2-cookie-banner-library-design.md) (architectural pattern reuse), [head-seo.php injector merged dcefe95](../../../skills/wp-landing-config/mu-plugin/landing-config/includes/head-seo.php)

## Goal

Дать маркетологу в `Network admin → Лендинг`:

1. **Меню «Аудит»** с табами категорий (Обзор / HTML / Network / Schema / AI) — запуск аудита кнопкой, просмотр failures, deep-link на правильное место правки. Multisite-aware (селектор сегмента `all` / root / per-subsite).
2. **Меню «Head & SEO»** — settings page (description / OG image / OG type / Twitter card) с live preview OG-карточки и SERP-сниппета.
3. **Расширение Python skill** `seo-tech-audit` — 3 AI checks (llms.txt / schema.org / no-JS render), флаги `--hosts-file` и `--with-fix-hints` для интеграции с PHP-стороной.

## Non-goals

- Auto-fix кнопки (только deep-links). Auto-fix через wp_options — может быть S2-E.4.1.
- Cron / scheduled audits — только manual launch.
- History snapshots — wp_sitemeta хранит latest run only.
- Page-level SEO overrides — только site-wide (`landing_seo_*` options).
- Image generation для OG — только wp.media picker existing files.
- 3-й preview «raw `<head>` source viewer» — отложен.

## Architecture

### Python skill (расширение `seo-tech-audit`)

```
skills/seo-tech-audit/scripts/
├── runners/
│   ├── ai_readiness.py        # NEW: 3 checks (AI1/AI2/AI3)
│   └── ...                    # existing
├── lib/
│   ├── fix_actions.py         # NEW: CHECK_ID → fix metadata catalog (46 entries)
│   └── ...                    # existing
└── run-audit.py               # MODIFIED: --hosts-file, --with-fix-hints

skills/seo-tech-audit/config/
└── quality-thresholds.yaml    # MODIFIED: +AI1/AI2/AI3

skills/seo-tech-audit/tests/
├── test_ai_readiness.py       # NEW: 6 unit
├── test_fix_actions.py        # NEW: 4 unit (one per category)
└── fixtures/
    ├── good-llms.txt          # NEW
    ├── good-schema.html       # NEW (has Organization JSON-LD)
    └── no-js-empty.html       # NEW
```

**AI1 — llms.txt validation:**
- HTTP GET `/llms.txt`
- Pass if: 200 OK AND содержит хотя бы одну строку формата `# <title>` (H1) AND хотя бы одну `[link](url)` markdown ссылку
- Минимальная валидация по [llmstxt.org spec](https://llmstxt.org)
- Soft check (hard=false в thresholds)

**AI2 — Schema.org Organization/Product/FAQ:**
- Парсит весь HTML, ищет все `<script type="application/ld+json">`
- Pass if: содержит хотя бы один JSON-LD блок с `@type` ∈ `{Organization, LocalBusiness, Product, FAQPage}`
- Soft check

**AI3 — no-JS render:**
- HTTP GET с `User-Agent` обычным (без JS execution)
- Pass if: `<body>` содержит ≥1KB текста (без учёта `<script>` / `<style>` контента), либо есть `<noscript>` fallback с контентом
- Soft check — некоторые SPA правомерно render-blank без JS

**fix_actions.py catalog:**
```python
# Pure data — no logic. PHP-сторона читает через json.dumps в --with-fix-hints.
CATALOG = {
    # HTML checks → routes inside wp-admin
    "H6": {"label": "Заполнить Description", "type": "admin_page",
           "page": "landing-config-head-seo"},
    "H8": {"label": "Открыть редактор главной", "type": "post_edit",
           "use_homepage_id": True},
    "H10": {"label": "Открыть Settings → General", "type": "raw_url",
            "url": "options-general.php#blogtimezone"},  # WP_Settings has no anchor for site_language but close
    # ... 25 HTML mappings
    # Network
    "N8": {"label": "Открыть Settings → Reading (Search engine visibility)",
           "type": "raw_url", "url": "options-reading.php"},
    "N9": {"label": "Sitemap создаётся WordPress автоматически (/wp-sitemap.xml). "
                    "Если 404 — проверь permalinks.", "type": "raw_url",
           "url": "options-permalink.php"},
    # ... 13 Network mappings
    # Schema
    "S1": {"label": "Заполнить OG-теги", "type": "admin_page",
           "page": "landing-config-head-seo"},
    "S5": {"label": "Установить Site Icon в Customizer", "type": "raw_url",
           "url": "customize.php?autofocus[control]=site_icon"},
    # ... 5 Schema mappings
    # AI
    "AI1": {"label": "Создать llms.txt", "type": "raw_url",
            "url": "admin.php?page=landing-config-head-seo#llms-txt"},
    # AI2/AI3 — Schema and no-JS — only suggestion text, no action button
    "AI2": {"label": "Добавить JSON-LD Organization в functions.php темы",
            "type": "suggestion"},
    "AI3": {"label": "Сайт render-blank без JS — see https://web.dev/rendering-on-the-web/",
            "type": "suggestion"},
}
```

Type semantics:
- `admin_page` → URL = `network/admin.php?page=<page>` (или `admin.php?page=<page>` если per-blog)
- `post_edit` + `use_homepage_id: true` → URL = `post.php?post=<show_on_front_page_id>&action=edit`
- `raw_url` → URL = `admin_url(<url>)` (PHP-сторона добавляет admin_root)
- `suggestion` → нет кнопки, только description-плашка

PHP-функция `build_deep_link_url($check_id, $blog_id, $admin_root)` парсит каталог и возвращает `{label, url, type}`.

### PHP mu-plugin module (новый)

```
mu-plugin/landing-config/includes/seo-audit/
├── admin-network.php       # Network → Лендинг → Аудит main router
├── audit-runner.php        # shell_exec + cache management
├── deep-links.php          # build_deep_link_url() — читает JSON-каталог
├── fix-actions.json        # copy of fix_actions.py CATALOG (build-step: python генерит)
└── tabs/
    ├── overview.php        # segments × categories matrix
    ├── html.php
    ├── network.php
    ├── schema.php
    └── ai_readiness.php

mu-plugin/landing-config/includes/
└── head-seo-admin.php      # Settings page + OG card + SERP snippet preview

mu-plugin/landing-config/assets/seo-audit/
├── admin.css               # tabs styling, failures table, segment selector
├── preview.js              # head-seo live preview updater
└── preview.css             # OG card + SERP snippet styling
```

### Меню структура

```
Лендинг (Network admin)
  ├── CTA                       (existing)
  ├── Интеграции                (existing)
  ├── Snippets                  (existing)
  ├── Cookie-banner             (existing)
  ├── ── separator ──
  ├── Аудит                     ← НОВОЕ (parent menu, default → tab=overview)
  ├── Head & SEO                ← НОВОЕ
  └── Lead Statuses             (existing)
```

«Аудит» — единая menu page, табы внутри страницы через query-param `?tab=overview|html|network|schema|ai_readiness`.

Site admin (subsite) добавляет read-only страницы:
- `Лендинг → SEO Audit (read-only)` — deep-link на network с `&segment=<current_blog_id>`
- `Лендинг → Head & SEO (read-only)` — то же

### Аудит запуск flow

**Multisite (segment=all):**
1. `get_sites(['fields' => 'ids'])` → URLs
2. Запись в `/tmp/lp-audit-<rand>.txt`
3. `shell_exec("python3 .../run-audit.py --hosts-file /tmp/lp-audit-<rand>.txt --json --with-fix-hints --out /tmp/lp-audit-<rand>/")`
4. Парс JSON → per-site results
5. Сохранить в `wp_sitemeta::landing_seo_audit_aggregate` + `landing_seo_audit_<blog_id>` (по одному на каждый сайт)
6. Очистить tmp
7. Redirect на `?tab=overview&segment=all&audited=1`

**Single-segment (segment=N):**
- `shell_exec("python3 .../run-audit.py --url https://<host>/ --json --with-fix-hints --out /tmp/.../")`
- Сохранить только `landing_seo_audit_<N>`
- Redirect на текущий tab с `audited=1`

**Тайм-аут:** PHP `set_time_limit(180)`. UI показывает loading spinner на 60-120 сек.

### Head & SEO settings + Preview

Settings page `landing-config-head-seo` с layout 2-column:

```
┌─────────────────────────────────┬──────────────────────────────┐
│  Левая колонка — форма          │  Правая колонка — preview    │
├─────────────────────────────────┼──────────────────────────────┤
│  Сегмент: [Network ▼]           │                              │
│                                 │  ┌──── OG-карточка ────┐   │
│  Description: [textarea]        │  │ [og:image preview]  │   │
│  (char counter ≥70)             │  │                     │   │
│                                 │  ├─────────────────────┤   │
│  OG Image: [Choose…] [preview]  │  │ example.com         │   │
│                                 │  │ Title from input    │   │
│  OG Type: [website ▼]           │  │ Description first   │   │
│                                 │  │   90 chars...       │   │
│  Twitter Card: [summary_large ▼]│  └─────────────────────┘   │
│                                 │                              │
│  llms.txt content:              │  ┌──── SERP snippet ───┐   │
│  [textarea (markdown)]          │  │ example.com › path  │   │
│                                 │  │ Title (blue)        │   │
│  [Save]                         │  │ Description (gray)  │   │
│                                 │  └─────────────────────┘   │
└─────────────────────────────────┴──────────────────────────────┘
```

**Preview JS:**
- `assets/seo-audit/preview.js` слушает `input` event на формy
- Обновляет `.lp-preview-og-title`, `.lp-preview-og-desc`, `.lp-preview-og-image`, `.lp-preview-serp-*` в DOM
- При смене OG Image picker — обновляет thumbnail в OG-карточке
- Стили `.lp-preview-og-card` фиксированы, не зависят от темы

**OG-карточка стилизация** — visual mockup в стиле Facebook/Telegram:
- Border 1px, border-radius 4px
- Image area 480×252 (соотношение 1200:630)
- Под image: домен (gray, uppercase, 12px), title (16px bold), description (14px gray, max 2 lines)

**SERP snippet стилизация** — visual mockup в стиле Google:
- Breadcrumb (зелёный, 12px): `example.com › path`
- Title (синий #1a0dab, 20px, underlined on hover)
- Description (серый #4d5156, 14px, line-clamp 2)

### Cascade для Head & SEO

Тот же паттерн S2-A.3 (network default + per-site override) что Cookie-banner:
- Записи живут в **NETWORK_BLOG_ID = 1** через `switch_to_blog(1)`
- `landing_seo_description` и пр. — wp_options в blog=1 (network default)
- Если segment=N — override в blog=N → wp_options в blog=N
- Resolver: site override → network default → пустая строка
- `head-seo.php` injector (уже существует) переделать на cascade-aware read

### Кэш audit-результатов

`wp_sitemeta::landing_seo_audit_<blog_id>` — JSON с full audit-report (single host).
`wp_sitemeta::landing_seo_audit_aggregate` — JSON с aggregate (multisite). Содержит `sites: [...]`.
`wp_sitemeta::landing_seo_audit_<blog_id>_ts` — Unix timestamp последнего прогона.

Admin показывает timestamp «Последний прогон: 2 часа назад» + кнопку «Перезапустить».

### Stage-11 gate (carry-over from S2-E.1)

Существующий `seo_audit_pass` в `config/stage-gates.yaml::10_qa` остаётся без изменений. Его invocation (CLI `--project`) теперь возвращает aggregate `passed` (все hard ≥ all hosts).

## Data Model

### wp_options (per blog, used by head-seo-admin)

| Key | Type | Default | Source |
|---|---|---|---|
| `landing_seo_description` | string | `''` | network blog=1 + per-site override |
| `landing_seo_og_image` | string (URL) | `''` | same |
| `landing_seo_og_type` | string | `'website'` | same |
| `landing_seo_twitter_card` | string | `'summary_large_image'` | same |
| `landing_seo_llms_txt` | text | `''` (если пусто — `/llms.txt` не отдаётся) | same |

### wp_sitemeta (network-wide cache)

| Key | Type | Description |
|---|---|---|
| `landing_seo_audit_<N>` | JSON | Last per-site audit report |
| `landing_seo_audit_aggregate` | JSON | Last multisite aggregate |
| `landing_seo_audit_<N>_ts` | int | Unix ts |

### fix-actions.json (build artifact)

Auto-generated по `fix_actions.py::CATALOG` при stage-08 build шаге или при первой загрузке mu-plugin. PHP читает через `json_decode`.

## llms.txt rewrite rule

Если `landing_seo_llms_txt` непуст — mu-plugin регистрирует `add_rewrite_rule('^llms\\.txt$', 'index.php?lp_llms_txt=1', 'top')` + `template_redirect` handler который выдаёт content из option с `Content-Type: text/markdown`.

## Error handling

| Условие | Поведение |
|---|---|
| `shell_exec` отключён в php.ini | Admin показывает «Audit недоступен — нужен shell_exec в php.ini». CLI прогон через wp-cli возможен. |
| `python3` не найден | Tries `python` fallback. Если нет — ошибка с инструкцией установить. |
| Audit прогон >180 сек | timeout → admin показывает «Прогон превысил 3 мин, попробуй per-segment». |
| `/tmp` недоступно | Используется `sys_get_temp_dir()`. |
| JSON parse fail (rare — Python вернул не-JSON) | Показать stderr stdout, suggestion run from CLI. |
| Preview JS не загрузился | Form работает, только preview не рендерится — graceful degradation. |
| OG image URL невалидный | Preview показывает placeholder «нет изображения». |

## Testing

### Python unit
- `test_ai_readiness.py` — 6 tests (AI1 pass/fail/missing, AI2 with-org/without/invalid-json, AI3 sufficient/blank/noscript-fallback)
- `test_fix_actions.py` — 4 tests (one per category)
- Existing tests pass без regression

### Python integration
- `test_run_audit_integration.py` extended: `--hosts-file` mode + `--with-fix-hints` enriches results

### PHP integration (mocked shell_exec)
- `test_audit_runner.php` — 3 tests: success, timeout, python-not-found
- `test_deep_links.php` — 4 tests (one per category, verify URL building)
- `test_head_seo_admin_save.php` — 2 tests (network save, site override)
- `test_head_seo_cascade.php` — verify head-seo.php injector reads cascade correctly

### Manual UI QA
- Network admin Аудит menu → каждый таб открывается
- Кнопка «Запустить» работает, показывает результаты в течение 120 сек
- Каждый failure имеет работающую deep-link кнопку (клик → нужная админ-страница открыта)
- Head & SEO form save → reload → значения сохранены
- Preview обновляется на input (без сохранения)

## Acceptance

- [ ] Network admin: `Лендинг → Аудит` menu + 5 табов работает
- [ ] Селектор сегмента: all/0/N — корректно показывает данные
- [ ] Кнопка «Запустить» в multisite-режиме обходит все subsites
- [ ] Per-segment failure list содержит deep-link для каждой ошибки
- [ ] Network admin: `Лендинг → Head & SEO` menu работает
- [ ] Cascade Head & SEO: network default + per-site override корректно
- [ ] Preview OG-карточки + SERP-сниппета обновляется live на input
- [ ] Save Head & SEO → значения попадают в правильный blog (NETWORK_BLOG_ID для segment=0)
- [ ] Python skill: `--hosts-file` + `--with-fix-hints` работают, тесты зелёные
- [ ] AI1/AI2/AI3 добавлены, 6 unit-тестов
- [ ] dubai-avto-liza: запустить через admin (network + per-segment), увидеть failures с работающими deep-links
- [ ] Stage-11 gate `seo_audit_pass` всё ещё работает (regression)

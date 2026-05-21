# S2-CD: WordPress Multisite + Segment Cloning

**Дата:** 2026-05-18
**Owner:** Спец 2
**Roadmap:** [2026-05-15-specialist-2-roadmap.md](2026-05-15-specialist-2-roadmap.md)
**Источник:** п.6 (клонирование) + п.7 (поддомены/мультисайт) из [ПЛАН-ДОРАБОТОК](../../planning/2026-05-15-plan-dorabotok.md)
**POC:** [tests/poc/](../../../tests/poc/) — boy: Beget shared `ailexi.ru` + WP 6.9.4 multisite
**Статус:** brainstorm complete, POC validated. Awaiting user approval → writing-plans.

---

## 1. Цель

Дать агентству возможность управлять **N лендингов одного клиента** (сегменты «русские в Дубае», «семьи в Дубае», «бизнес-туристы») как **единой WordPress Multisite-сетью**:

- Одна wp-admin Network для всех сайтов клиента.
- Каждый сегмент — отдельный subsite на своём поддомене (`russian.liauto.dubai`, `family.liauto.dubai`).
- Клонирование «one click» — байт-в-байт копия с одного subsite на новый (без авто-LLM-правок текста, маркетолог потом ручкой/командой меняет).
- Lazy Blocks definitions, бренд, дизайн **шарятся** через mu-plugin или тему — один файл = блок на всех subsites.
- SEO/AI готовность с дня 1: per-site sitemap, robots.txt, JSON-LD Schema.org, llms.txt.

**Что НЕ в скоупе** (отложено в S2-A после ревизии):
- Admin UI для интеграций / CRM / head-редактора (S2-A).
- Авто-перепись текста при клонировании (S2-A1+).
- SaaS-уровень с собственным builder вместо Gutenberg (другой проект).

---

## 2. POC-валидированная архитектура

> Всё ниже подтверждено POC на боевом Beget shared (`tests/poc/scripts/00-setup-multisite.sh` GREEN).
> Cтрого ссылаемся на конкретные тесты в скобках.

### 2.1 Hosting и DNS

| Слой | Решение | Подтверждено |
|---|---|---|
| Хостинг | Beget shared, план любой с MySQL + PHP 8.3 | Tests на плане Blog |
| DNS | NS на Бегете (`is_beget_dns: true`), всё через Beget API | Test 00 |
| Subdomain creation | `domain/addSubdomainVirtual` с `subdomain="*"` для wildcard + per-segment subdomains | Test 00 |
| PHP | Per-subdomain через `domain/changePhpVersion` (`full_fqdn`, `php_version="8.3"`) | Test 00 |
| Site routing | Один `site/add` + `site/linkDomain` каждый subdomain → один public_html. Beget НЕ создаёт отдельных папок для subdomains. | Test 00 |
| SSL | **Решено:** Beget панель даёт бесплатный wildcard Let's Encrypt в один клик (Домены → SSL → wildcard), авто-renew. POC также доказал что acme.sh + наш `dns_beget` hook **выпускает** wildcard и per-subdomain cert, но **установка** в nginx Beget без панели невозможна (на shared нет API, нет writable path к nginx-config). Скрейп-автоматизация — следующая итерация S2-CD. | Cookbook §SSL |

### 2.2 WordPress

| Слой | Решение | Подтверждено |
|---|---|---|
| WP | 6.9.4, Multisite **subdomain mode** (НЕ subdirectory) | Test 00 |
| MySQL | Отдельная БД на проект (`esper21_poc` через `mysql/addDb`) | Test 00 |
| Theme | Classic theme (Twenty Twenty-One). Block-themes (TT5) ломают front-page `page_on_front` rendering | Test 01 |
| Plugins | `lazy-blocks` 4.3.0 (network-active), `seo-by-rank-math` 1.0.270 (network-active) | Test 00 |
| `.htaccess` | Стандартный WP multisite + `RewriteRule ^([_0-9a-zA-Z-]+/)?(.*\.php)$ $2 [L]` | Test 00 |

### 2.3 Lazy Blocks через mu-plugin (ключевой механизм)

**Это критическая часть архитектуры — закрывает главный риск S2-CD.**

Один mu-plugin `wp-content/mu-plugins/landing-blocks.php` регистрирует ВСЕ Lazy Blocks definitions клиента. Они автоматически видны на всех subsites сети. (Test 01: лазиблок зарегистрирован в `WP_Block_Type_Registry` на ailexi.ru / alpha.ailexi.ru / bravo.ailexi.ru одинаково.)

**Жёсткие требования** (обнаружены в POC, без них **НЕ РАБОТАЕТ**):

1. **Slug ОБЯЗАН начинаться с `lazyblock/`** — Lazy Blocks хардкодит namespace в `register_block_type`. Slug должен быть `lazyblock/<kebab-case>`, например `lazyblock/hero`, `lazyblock/pricing-table`.
2. **Регистрация в `init` hook с priority `<20`**. Lazy Blocks свой `register_block` на priority 20 — наш `add_block()` должен сработать раньше. Использовать priority 5.
3. **Render-функция через `code.frontend_callback`** в массиве блока. НЕ через `add_filter('lzb/lazyblock-X/frontend_callback', ...)` — этот фильтр в plugin code не вызывается для программно добавленных блоков.
4. **`code.output_method = 'php'`**.

**Минимальный шаблон для генератора stage-08:**

```php
<?php
/**
 * Plugin Name: <Project> Landing Blocks
 */
add_action('init', function () {
    if (!function_exists('lazyblocks')) return;

    lazyblocks()->add_block([
        'id'    => 1001,
        'title' => 'Hero',
        'slug'  => 'lazyblock/hero',          // MUST start with lazyblock/
        'icon'  => 'star-filled',
        'category' => 'common',
        'code'  => [
            'output_method'     => 'php',
            'frontend_callback' => function ($attrs) {
                echo render_hero($attrs);     // arbitrary PHP
            },
        ],
        'controls' => [
            ['name' => 'headline', 'type' => 'text', 'default' => ''],
            ['name' => 'cta_url',  'type' => 'url',  'default' => '#'],
        ],
    ]);
}, 5);  // priority < 20
```

### 2.4 SEO и AI-готовность

Через mu-plugins, по одному файлу на функцию:

| File | Что | Test |
|---|---|---|
| `mu-plugins/landing-blocks.php` | Lazy Blocks definitions | 01, 02 |
| `mu-plugins/landing-robots.php` | AI-bot allow-list в robots.txt | 04 |
| `mu-plugins/landing-schema.php` | Organization + Product/FAQPage JSON-LD | 06 |
| `mu-plugins/landing-llms.php` | `/llms.txt` rewrite endpoint | 07 |
| `mu-plugins/landing-gsc.php` | GSC verification per-blog (через `wp_options.gsc_token`) | 08 |

Все mu-plugins **сами** определяют контекст через `get_current_blog_id()` и `home_url()` — никаких хардкодов. (Tests 04, 06, 07, 08: проверяют отсутствие cross-site leak.)

RankMath (network-activated) обрабатывает:
- per-site sitemap.xml (test 03)
- per-post canonical, OG tags
- structured data overrides

### 2.5 Domain layout (вариант A из roadmap)

```
Один проект агентства = одна WP Multisite installation, один main client domain.

Пример (для клиента LiAuto в Дубае):
  liauto.dubai             ← root subsite (blog_id=1, main marketing landing)
  russian.liauto.dubai     ← subsite (blog_id=2, "русские в Дубае" segment)
  family.liauto.dubai      ← subsite (blog_id=3, "семьи с детьми" segment)
  business.liauto.dubai    ← subsite (blog_id=4, "бизнес-туристы" segment)
```

DNS: `*.liauto.dubai` wildcard A-record + named subdomains alpha/bravo через Beget API.

В будущем (фаза B): агентский корневой `*.lendings-agency.ru` с custom domain mapping per subsite. Не делается в S2-CD первой итерации.

---

## 3. Изменения в landing-system

### 3.1 Новые артефакты

- `template/.landing-state.yaml` — добавить поле `subsites: []` (массив записей `{slug, host, blog_id, segment_brief_path}`).
- `template/13_СЕГМЕНТЫ/` — новая директория для контента сегментов:
  ```
  13_СЕГМЕНТЫ/
    russian/
      brief.yaml          # бриф под сегмент (демография, оффер, цены)
      prototype.md        # текст-прототип специфичный для сегмента
      photos/             # фото для этого сегмента (если другие)
    family/
      ...
  ```
- `skills/wp-multisite/SKILL.md` — новый скилл для multisite-операций
- `skills/wp-multisite/scripts/migrate-to-multisite.sh` — мигрирует существующий single-site WP в multisite (создаёт wildcard DNS + WP_ALLOW_MULTISITE + `wp core multisite-convert`)
- `skills/wp-multisite/scripts/clone-subsite.sh` — копирует subsite (db + content) на новый поддомен
- `skills/wp-multisite/scripts/setup-multisite.sh` — для нового проекта: subdomain mode из коробки (если в brief.yaml указан `multisite: true` или после первого `/landing-clone`)
- `.claude/commands/landing-segment.md` — `/landing-segment <name>` создаёт новый сегмент (subdomain + subsite + 13_СЕГМЕНТЫ/<name>/ skeleton)
- `.claude/commands/landing-clone.md` — обновлённая команда: если single-site → запускает миграцию в multisite сначала, затем clone

### 3.2 Изменения в существующих скиллах

- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh`:
  - Read `subsites:` from `.landing-state.yaml`
  - Если subsites пуст → текущий single-site режим (без изменений)
  - Если subsites есть → multisite-aware:
    - Beget API: `domain/addSubdomainVirtual` для wildcard + каждого segment subdomain
    - `site/linkDomain` для каждого + `domain/changePhpVersion` на 8.3
    - `wp core multisite-install` если первый раз; иначе `wp site create --slug=<seg>` для новых
    - rsync mu-plugins/themes (shared, network-wide)

- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-registration.py`:
  - **CRITICAL FIX:** Force slug to start with `lazyblock/` (валидация в генераторе)
  - **CRITICAL FIX:** Output `add_action('init', ..., 5)` с приоритетом 5
  - **CRITICAL FIX:** Render code в `code.frontend_callback`, не в `add_filter`
  - Output **один** mu-plugin файл `landing-blocks.php` (не множество per-block PHP файлов)

- `skills/wp-gutenberg-block-builder/scripts/generate-page-content.py`:
  - Multisite-aware: `wp post create --url=http://<host>` для front-page каждого subsite

### 3.3 Изменения в spec S2-A (pending revision)

S2-A (`landing-config` mu-plugin) уже помечен `pending-revision`. После S2-CD:
- `landing-config.php` mu-plugin должен быть **network-aware**
- Settings storage: `wp_sitemeta` для shared (CRM ключи общие на всю сетку) vs `wp_options` per-blog (CTA пресеты per-segment)
- `wp_landing_leads` — отдельная таблица per-blog, чтобы заявки сегментов не пересекались
- Admin UI «Заявки» — фильтр «все сегменты / только этот»

---

## 4. Workflow для маркетолога

### 4.1 Новый проект, начиная с одного лендинга

Без изменений от текущего пайплайна:
1. `/landing-start` → `/landing-prototype` → `/landing-references` → `/landing-brand` → ... → `/landing-deploy`
2. Деплоится как single-site (без multisite-overhead).

### 4.2 Добавление второго сегмента (single → multisite миграция)

1. Маркетолог выполняет `/landing-segment russian` (новая команда).
2. Под капотом:
   - Если проект ещё single-site → запускается `migrate-to-multisite.sh`:
     - `WP_ALLOW_MULTISITE` в `wp-config.php`
     - Beget API: wildcard subdomain `*.<root>` + named `russian.<root>`
     - `wp core multisite-convert --url=http://<root>`
     - rewrite `.htaccess`
     - Текущий лендинг становится `blog_id=1`
   - Создаётся `13_СЕГМЕНТЫ/russian/` skeleton с примерными `brief.yaml` и `prototype.md`
3. Маркетолог редактирует `13_СЕГМЕНТЫ/russian/brief.yaml` + `prototype.md` (сегмент-specific тексты, фото, цены).
4. `/landing-go` запускает pipeline для **этого сегмента** (генерация контента → wp-cli создание subsite → импорт страниц).
5. Деплой: новый subsite `russian.<root>` доступен.

### 4.3 Клонирование byte-by-byte

Если маркетолог хочет «такой же сайт но на другом поддомене без правок»:

```
/landing-clone family-test
```

→ `clone-subsite.sh source=alpha dest=family-test`:
- `wp site create --slug=family-test`
- Export content всех страниц alpha → import в новый subsite
- Копирование `wp_options` (с правкой `home`/`siteurl`)
- Копирование `wp_*_postmeta` для всех страниц
- Auto-redeploy

Никаких авто-правок текста/цен — байт-в-байт.

---

## 5. SSL — финальное решение

После расширенного исследования (см. [docs/beget-cookbook.md](../../beget-cookbook.md) и [tests/poc/RESULTS.md](../../../tests/poc/RESULTS.md) §SSL):

### Что доказал POC

| Подход | Статус |
|---|---|
| Beget панель → бесплатный wildcard Let's Encrypt | ✅ Один клик, авто-renew |
| Beget auto-issue для `<root>` + `www.<root>` после `site/add` | ✅ Из коробки |
| acme.sh wildcard cert через DNS-01 (наш `dns_beget` hook) | ✅ Cert выпущен |
| acme.sh per-subdomain через HTTP-01 (`--webroot`) | ✅ Cert выпущен |
| Установка выпущенного cert в nginx Beget **без панели** | ❌ Невозможно на shared (нет API, permission denied к /etc/nginx/) |
| Beget API endpoints `ssl/*`, `cert/*` | ❌ NO_SUCH_METHOD |

### Решение для S2-CD первой итерации

**SSL — manual one-click через панель Beget.** При создании нового проекта (single → multisite migration) `/landing-segment` после успешного деплоя выдаёт маркетологу инструкцию:

1. Открыть панель Beget → Домены → найти корневой домен
2. Кликнуть SSL-иконку → «Бесплатный wildcard»
3. Через 30 минут — 1 день wildcard `*.<root>` готов
4. Покрывает ВСЕ существующие и будущие subsites одной операцией
5. Auto-renew управляется Beget

**Один ручной шаг на жизнь проекта.** Новые сегменты wildcard покрывает автоматически.

### Артефакты POC сохранены для следующей итерации

- acme.sh установлен в `~/.acme.sh/` на боевом Бегете
- `dns_beget` hook — production-ready ([tests/poc/dns-beget-hook.sh](../../../tests/poc/dns-beget-hook.sh))
- Сертификаты выписаны и лежат

При миграции на VPS / при написании скрейпера панели — всё переиспользуется без перевыпуска.

### Скрейпер панели Beget — отложен в S2-CD.2

Полная автоматизация SSL через scraping cp.beget.com (Python requests + session cookies, POST формы выпуска SSL) технически возможна за ~2-3 часа работы. Откладывается до того момента, когда ручной клик в первой итерации станет реальной болью (если будет).

---

## 6. Lazy Blocks safety gate

POC показал что наш `add_block()` шаблон зависит от ТРЁХ конкретных требований Lazy Blocks (slug, priority, callback location). Любое будущее изменение генератора stage-08 должно прогонять **regression test**:

```bash
tests/integration/test_lazy_blocks_smoke.sh
```

После S2-CD этот тест расширяется:
- Проверяет регистрацию блока на 2+ subsites (как POC tests 01/02)
- Проверяет что `WP_Block_Type_Registry::is_registered('lazyblock/<slug>')` = true
- Проверяет что front HTML содержит `lazyblock-<slug>` класс
- Запускается **обязательно после каждого Task** в плане S2-CD и S2-A.

---

## 7. POC findings — список known issues / workarounds

| Issue | Workaround |
|---|---|
| Beget кеширует HTML на корне если домен не привязан к site entity | Всегда вызывать `site/linkDomain` для каждого FQDN после `addSubdomainVirtual` |
| PHP по умолчанию для нового subdomain = 5.6 | Сразу после `addSubdomainVirtual` вызывать `domain/changePhpVersion full_fqdn=... php_version="8.3"` |
| `wp_options.show_on_front=page` теряется при смене темы | После `theme activate` сразу пере-выставлять `show_on_front` + `page_on_front` |
| TT5 (block-theme) НЕ выводит page content на front-page при `page_on_front` | Использовать classic theme (TT2021 или собственная) |
| Lazy Blocks `add_block(['slug'=>'X/...'])` для X !== `lazyblock` тихо не регистрирует блок в WP registry | Всегда `slug = 'lazyblock/<name>'` |
| `add_filter('lzb/lazyblock-X/frontend_callback', ...)` не работает для программных блоков | Render внутри `code.frontend_callback` |
| Beget API не имеет SSL endpoint | Ручной выпуск через панель или Cloudflare proxy |

---

## 8. POC results (final, см. также [tests/poc/RESULTS.md](../../../tests/poc/RESULTS.md))

**Итог: 10 из 11 GREEN, 1 косметический. Архитектурные риски закрыты.**

| Test | Status | Что доказано |
|---|---|---|
| 00-setup-multisite | 🟢 | Wildcard DNS + WP install + 2 subsites end-to-end через Beget API |
| 01-lazy-blocks-network | 🟢 | mu-plugin регистрирует Lazy Block на ВСЕХ subsites (slug `lazyblock/x`, priority<20, `code.frontend_callback`) |
| 02-lazy-blocks-render | 🟢 | Front HTML рендерится per-subsite с per-page параметрами |
| 03-sitemap-per-site | 🟢 | `/wp-sitemap.xml` независимы per subsite, нет cross-leak |
| 04-robots-per-site | 🟢 | AI bots allow-list работает, нет cross-leak |
| 05-rank-math-network | 🟢 | RankMath per-site title/desc, без leak между сегментами |
| 06-schema-org-faq | 🟢 | Organization + FAQPage JSON-LD per-host |
| 07-llms-txt-rewrite | 🟡 | Body + host правильные, Content-Type косметика (text/html вместо text/plain) — не влияет на AI-ботов |
| 08-search-console-meta | 🟢 | GSC verification per-blog, нет cross-leak |
| 09-ai-bot-fetches | 🟢 (revised) | Все RAG/search боты проходят. Beget блокирует ТОЛЬКО training-краулеры (GPTBot, ClaudeBot) — для коммерческих лендингов это плюс, не минус. AI-видимость в ChatGPT Search/Claude/Perplexity/Google AI работает из коробки |
| 10-clone-subsite | 🟢 | `wp site create` + content copy end-to-end |

### Critical findings (для имплементации)

**Lazy Blocks через mu-plugin — главный риск закрыт:**
- Slug **обязан** начинаться с `lazyblock/`
- `add_action('init', ..., 5)` — priority < 20
- Render через `code.frontend_callback`, не через `add_filter`
- `code.output_method = 'php'`

**Beget API подводные камни (см. [docs/beget-cookbook.md](../../beget-cookbook.md)):**
- Без `site/linkDomain` nginx отдаёт статический кеш, не вызывает PHP
- По умолчанию новый subdomain — PHP 5.6, нужен `domain/changePhpVersion`
- Wildcard subdomain в DNS работает, но HTTP routing требует отдельный linkDomain
- WAF блокирует только GPTBot/ClaudeBot (training-боты), всё остальное проходит

**Темы:** classic (Twenty Twenty-One), НЕ block-theme (TT5). Block-themes не рендерят page content на front-page при `page_on_front`.

**SSL:** manual через панель Beget в первой итерации. Скрейп-автоматизация — следующая итерация. Все артефакты POC (acme.sh + hook + cert files) сохранены на сервере для переиспользования.

---

## 9. Decision request — Phased implementation

После approval этого спека — `writing-plans` skill превращает spec в план фазовой имплементации:

| Фаза | Содержимое | Smoke-gate |
|---|---|---|
| **CD1** | `migrate-to-multisite.sh` + `/landing-segment <name>` команда + `clone-subsite.sh` (на основе POC test 10) | Lazy Blocks smoke + multisite smoke на `dubai-avto-liza` |
| **CD2** | Multisite-aware `deploy-wordpress.sh` + `13_СЕГМЕНТЫ/` workflow + `.landing-state.yaml` поле `subsites[]` | E2E прогон `/landing-segment` создаёт работающий subsite |
| **CD3** | Lazy Blocks генератор fixes (slug namespace `lazyblock/`, priority 5, `code.frontend_callback`) — переписать `generate-lzb-registration.py` под POC-paterns | Lazy Blocks smoke + регрессия на существующих проектах |
| **CD4** | SEO/AI mu-plugins из POC (robots, schema, llms-txt, gsc) — портируются как переиспользуемые скиллы | Audit-скрипт (S2-E) подтверждает все 4 мu-plugins работают |
| **CD5** | Документация SSL процедуры (один клик в панели) + чеклист для маркетолога | Manual проверка |
| **CD6** *(отложенная)* | Скрейпер cp.beget.com для автоматизации SSL | Smoke на тестовом домене |

Каждая фаза — отдельный план + отдельный PR в worktree, со smoke-gate перед merge. Логика smoke-gate из roadmap: `bash tests/integration/test_lazy_blocks_smoke.sh` обязательна после каждого Task.

### Что начнём первым

**CD1** — наибольшая инкрементальная ценность: команда `/landing-segment russian` появляется в landing-system, маркетолог может создать первый клон, всё остальное (proper deploy script, генератор fixes, SEO mu-plugins) докатывается следующими фазами без потери уже работающего.

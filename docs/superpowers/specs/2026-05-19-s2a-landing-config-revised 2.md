# S2-A: Pre-deploy & Admin Config — REVISED для multisite

**Дата:** 2026-05-19
**Owner:** Спец 2
**Заменяет:** [2026-05-15-s2a-pre-deploy-admin-config-design.md](2026-05-15-s2a-pre-deploy-admin-config-design.md) (pending-revision)
**Опирается на:** S2-CD CD1 (multisite + segments) — смерджено в main 2026-05-19
**Источник:** [docs/planning/2026-05-15-plan-dorabotok.md](../../planning/2026-05-15-plan-dorabotok.md), пункты 1-4 части «Специалист 2».
**Статус:** ready for writing-plans (все архитектурные риски разрешены или подтверждены POC).

---

## 1. Цель (без изменений)

Дать маркетологу и клиенту возможность настраивать всю «runtime»-часть лендинга (интеграции с CRM, маршрутизация заявок, CTA-кнопки, head/SEO) **в стандартной wp-admin без кода**.

Заявки никогда не теряются — даже без настроенной CRM пишутся в БД и шлются на email админа. Все CTA-кнопки на сайте берут таргет из единых пресетов — смена WhatsApp-номера = одна правка, а не 15.

---

## 2. Архитектура (revised для multisite)

### 2.1 Размещение mu-plugin

Must-use plugin `landing-config/` создаётся **разработчиками** (в этом проекте) и попадает в репо как **полностью готовый PHP-код** — не генерируется на stage-08 из шаблонов.

Расположение в репо: `skills/wp-landing-config/mu-plugin/landing-config/` (готовый код, не Jinja-шаблоны).
Расположение на сервере: `<BEGET_PATH>/wp-content/mu-plugins/landing-config/landing-config.php` + дополнительные файлы.

**Почему так** (изменено от исходной спеки):
- Исходный план был генерировать mu-plugin на stage-08 из Jinja-шаблонов через `generate-mu-plugin.py`. Это overkill — mu-plugin не имеет per-project переменных (всё runtime-конфигурируется через wp-admin).
- Простой PHP-код в репо + копирование деплоем. Меньше движущихся частей, проще тестировать.

### 2.2 Network vs per-site хранилище

Multisite (validated в S2-CD CD1) → используем оба уровня хранилища:

| Что | Где | Почему |
|---|---|---|
| **Общие** для всей сети: дефолтные CRM-ключи, default WhatsApp-номер агентства | `wp_sitemeta` (network options) | Маркетолог настраивает один раз на network admin, применяется ко всем segments |
| **Per-site override:** API-ключи клиента, его телефон/email | `wp_options` (per-blog) | Каждый клиент может переопределить для своего сегмента |
| **Заявки (leads)** | `wp_<blog_id>_landing_leads` (per-blog таблица) | Заявки разных сегментов не пересекаются. Главный сайт сети тоже имеет свою таблицу. |
| **Лог доставок** | `wp_<blog_id>_landing_lead_log` | per-blog для аудита |

Helper: `landing_config_get($key, $blog_id = null)` — читает per-site override, fallback на network default.

### 2.3 Admin pages

**Главное admin-меню** «Лендинг» с 5 sub-страницами. Доступно **в каждом subsite** через wp-admin **и** на уровне network admin (для шаблонов).

| Страница | Subsite | Network |
|---|---|---|
| Setup wizard (one-time) | ✓ показывается при первом заходе | — |
| Интеграции (CRM + аналитика + мессенджеры) | ✓ per-site override | ✓ network defaults |
| Заявки (БД + экспорт CSV + filter «все сегменты / только этот») | ✓ только свои | ✓ объединённый просмотр + фильтр по blog_id |
| CTA-кнопки (5 пресетов) | ✓ per-site override | ✓ network defaults |
| Head & SEO (поля + raw-textarea) | ✓ per-site | — (специфика для сегмента) |

### 2.4 REST endpoint для заявок

`/wp-json/landing/v1/lead` — один endpoint, **multisite-aware**: автоматически определяет текущий subsite через `get_current_blog_id()`, пишет в правильную per-blog таблицу.

### 2.5 Шифрование API-ключей

API-ключи (AmoCRM token, Bitrix24 webhook, HubSpot key) шифруются AES-256-CBC с ключом из `wp_salt('secure_auth')` перед записью в options. Открытым текстом в БД не лежат.

В UI: input type=password + кнопка «Reveal» с подтверждением пароля админа.

---

## 3. Компоненты (revised)

### 3.1 Новый скилл `wp-landing-config`

`skills/wp-landing-config/`:
- `SKILL.md` — описание скилла, точка входа
- `mu-plugin/landing-config/landing-config.php` — основной plugin file (bootstrap + activation hook)
- `mu-plugin/landing-config/includes/db.php` — создание таблиц + миграции
- `mu-plugin/landing-config/includes/admin-pages.php` — регистрация admin menu + sub-pages
- `mu-plugin/landing-config/includes/admin-integrations.php` — страница «Интеграции»
- `mu-plugin/landing-config/includes/admin-leads.php` — страница «Заявки»
- `mu-plugin/landing-config/includes/admin-cta.php` — страница «CTA-кнопки»
- `mu-plugin/landing-config/includes/admin-head-seo.php` — страница «Head & SEO»
- `mu-plugin/landing-config/includes/rest-lead.php` — REST endpoint `/landing/v1/lead`
- `mu-plugin/landing-config/includes/encryption.php` — encrypt/decrypt helpers
- `mu-plugin/landing-config/includes/helpers.php` — `landing_get_cta()`, `landing_render_head_extras()`, `landing_config_get()`
- `mu-plugin/landing-config/adapters/AdapterInterface.php` — интерфейс CRM-адаптера
- `mu-plugin/landing-config/adapters/{AmoCRM,Bitrix24,HubSpot,Telegram,WhatsApp,Email}.php` — 6 адаптеров
- `mu-plugin/landing-config/assets/admin.css` — стили админ-страниц (vanilla, без сборки)
- `mu-plugin/landing-config/assets/admin.js` — vanilla JS для «Test connection» + masked inputs
- `mu-plugin/landing-config/uninstall.php` — drop tables + options при удалении

**Скилл-скрипты:**
- `scripts/install-mu-plugin.sh` — копирует `mu-plugin/landing-config/` в `<BEGET_PATH>/wp-content/mu-plugins/landing-config/` через rsync
- `scripts/test-mu-plugin.sh` — runtime тесты на боевом WP (создание формы → проверка записи в БД → проверка email-fallback)
- `tests/test_install_mu_plugin.bats` — bats для install-скрипта
- `tests/test_helpers.php` — PHPUnit для helpers (если PHPUnit доступен в env), иначе доп. bats с инструкцией

**Slash-команда:**
- `.claude/commands/landing-admin-install.md` — `/landing-admin-install` — копирует mu-plugin в текущий multisite проект и активирует

### 3.2 Изменения существующих файлов

- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — после деплоя темы запускать `install-mu-plugin.sh` чтобы mu-plugin копировался автоматически
- `skills/wp-multisite/scripts/landing-segment.sh` — добавить вызов `landing_config_get_or_set_defaults($blog_id)` после создания subsite (заполнит дефолты пресетов + перенесёт network defaults)
- `CLAUDE.md` — раздел про landing-config plugin

### 3.3 Шаблон проекта (template/)

Без изменений — конфигурации plugin'а **не в файлах проекта**, а в БД.

---

## 4. Workflow для маркетолога/клиента

### 4.1 Установка mu-plugin (один раз на проект)

После CD1 у проекта уже multisite. Маркетолог запускает:
```
/landing-admin-install
```

Что происходит:
1. Скрипт копирует `skills/wp-landing-config/mu-plugin/landing-config/` в `<BEGET_PATH>/wp-content/mu-plugins/`
2. mu-plugin авто-активируется (это особенность mu-plugins WP — не нужен `wp plugin activate`)
3. Activation hook создаёт таблицы `wp_landing_leads` + `wp_landing_lead_log` в каждом subsite через `dbDelta()`
4. Появляется меню «Лендинг» в wp-admin каждого subsite

### 4.2 Настройка интеграций (клиент в своей админке)

1. Клиент заходит в `russian.liauto.dubai/wp-admin/`
2. Видит меню «Лендинг» → «Интеграции»
3. Вкладки:
   - **Аналитика:** GA4 ID, Yandex.Metrika ID, FB Pixel, TikTok Pixel
   - **CRM:** выбор + API-ключ + URL (AmoCRM/Bitrix24/HubSpot)
   - **Мессенджеры:** Telegram bot token + chat_id, WhatsApp Business API
   - **Email:** SMTP настройки для autoresponder
4. У каждого поля кнопка **«Test connection»** — делает тестовый запрос → green/red
5. Сохраняет — данные шифруются и записываются в `wp_options`

### 4.3 Заявки

1. Клиент или менеджер → «Лендинг» → «Заявки»
2. Видит **список заявок** из БД с фильтрами (дата, статус доставки в CRM, segment)
3. Каждая заявка: name, phone, email, message, UTM-метки, IP, дата, какие adapter'ы успешно отправили
4. **«Retry now»** кнопка для упавших доставок
5. **«Экспорт CSV»** — выгрузка всех или выбранных
6. На network admin — **сводный просмотр** заявок со всех сегментов с filter по blog_id

### 4.4 CTA-кнопки

1. «Лендинг» → «CTA-кнопки»
2. 5 пресетов: `primary` (форма-модалка), `whatsapp`, `phone`, `form_modal`, `learn_more`
3. Для каждого: тип + параметры (URL, телефон, текст шаблона WA-сообщения)
4. Все кнопки в шаблонах темы через `landing_get_cta('primary', $url_override)` получают URL из пресета
5. Сменить WhatsApp-номер = одна правка, обновятся все 15 кнопок на сайте

### 4.5 Head & SEO

1. «Лендинг» → «Head & SEO»
2. Структурированные поля: GSC verification, Yandex Webmaster verification, OG default image/title/desc, favicon upload (Media Library), Google Fonts URL
3. Дополнительный «Custom HTML in `<head>`» textarea — для случаев когда поле не подходит (Hotjar, custom JS, etc.). Прогоняется через `wp_kses` whitelist для безопасности.

---

## 5. Error handling и безопасность

### 5.1 Заявки никогда не теряются

```
POST /wp-json/landing/v1/lead
  ↓
1. validate (honeypot + required fields)
2. INSERT INTO wp_<blog_id>_landing_leads (ALWAYS)
3. wp_mail(admin_email) (best effort, не блокирует)
4. foreach $enabled_adapter:
     try { $adapter->send($lead); log success }
     catch { log error, schedule wp_cron retry }
5. return 200 with lead_id
```

Если CRM упала, заявка **уже в БД** + email админу.

### 5.2 Async retry упавших доставок

`wp_schedule_single_event($timestamp, 'landing_retry_delivery', [$lead_id, $adapter])` — 3 попытки с backoff (1m, 5m, 30m). После — manual «Retry now» в админке.

### 5.3 Шифрование API-ключей

- Encrypt: `openssl_encrypt($value, 'aes-256-cbc', wp_salt('secure_auth'), 0, $iv)`
- Decrypt при чтении в адаптере
- Хранится `base64(iv) + ':' + base64(ciphertext)`

### 5.4 wp_kses whitelist для raw HTML в head

```php
$allowed_html = [
    'script' => ['src', 'async', 'defer'],
    'meta'   => ['name', 'content', 'http-equiv'],
    'link'   => ['rel', 'href', 'type'],
    'style'  => [],
    'noscript' => [],
];
echo wp_kses($raw_html, $allowed_html);
```

Inline `<script>` без src — пропускается с warning в админке (защита от XSS).

### 5.5 Capability checks

- `manage_network_options` — для network admin страниц
- `manage_options` — для per-site страниц
- Editor может просматривать заявки + экспортировать CSV, но не править интеграции

### 5.6 Rate limit

REST `/lead` endpoint: max 10 заявок с одного IP в час (через `wp_transient`). Превышение → 429.

---

## 6. Фазы имплементации (5 фаз)

Делаем последовательно. Каждая = свой PR (рекомендация) или серия коммитов в одном PR.

### Фаза A1 — Фундамент + REST endpoint + БД

- mu-plugin scaffolding (landing-config.php, includes/db.php, uninstall.php)
- Activation hook: `dbDelta()` создаёт `wp_<blog_id>_landing_leads` + `wp_<blog_id>_landing_lead_log` в каждом subsite
- REST endpoint `/wp-json/landing/v1/lead` с валидацией (nonce, honeypot, required fields)
- Email-fallback через `wp_mail`
- `install-mu-plugin.sh` (rsync на Beget)
- Bats тесты для install + smoke на ailexi.ru

### Фаза A2 — Admin страница «Заявки»

- Регистрация admin menu «Лендинг» + sub-page «Заявки»
- WP_List_Table с фильтрами и сортировкой
- Экспорт CSV
- Network admin: сводный просмотр со всех blog_id с filter
- bats + manual smoke

### Фаза A3 — CTA-пресеты + helper

- Admin страница «CTA-кнопки» с 5 пресетами
- Helper `landing_get_cta($preset, $url_override)` для использования в темах
- `wp_options` storage + network defaults через `wp_sitemeta`
- Документация для разработчиков темы как использовать helper
- bats

### Фаза A4 — Head & SEO админка

- Admin страница «Head & SEO»
- Структурированные поля (GA4, Y.Metrika, FB Pixel, TikTok, GSC, Y.Webmaster, OG, favicon, fonts)
- Raw HTML textarea с wp_kses
- `landing_render_head_extras()` helper — вызывается на `wp_head` hook
- bats + manual smoke (зайти на сайт через curl, проверить что Y.Metrika код в head)

### Фаза A5 — Интеграции: 6 адаптеров + Test-connection + шифрование + async-retry

- `AdapterInterface` + 6 адаптеров (AmoCRM, Bitrix24, HubSpot, Telegram, WhatsApp, Email)
- Admin страница «Интеграции» с per-adapter настройками
- Encryption helpers (encrypt/decrypt при сохранении/чтении)
- Кнопка «Test connection» для каждого adapter — AJAX endpoint
- `wp_schedule_single_event` для async retry упавших доставок
- bats для encryption + manual smoke для каждого adapter

---

## 7. Validated dependencies (из CD1 POC)

- WordPress Multisite (subdomain mode) — работает на Beget shared, см. tests/poc/RESULTS.md
- PHP 8.3 на Beget — настроен через `domain/changePhpVersion` (часть `landing-segment.sh`)
- Beget shared позволяет mu-plugins (всегда активны, не требуют activate)
- `wp_remote_post` для CRM endpoint'ов — стандартный WP API, работает out-of-the-box
- `wp_schedule_single_event` — стандартный WP-cron, работает (хотя на Beget shared cron триггерится через web requests, не через системный cron — может быть задержка до первого визита)

## 8. Известные ограничения

- **WP-cron на Beget shared** триггерится только при HTTP-запросах. Если сайт без посетителей, async retry может задержаться. Mitigation: для критичных сегментов настраивать external cron (uptime monitor caller, например).
- **Email-fallback** требует настроенного SMTP. Без него `wp_mail` использует PHP `mail()` который на Beget может попасть в спам. Рекомендация в документации: настроить SMTP сразу.
- **6 адаптеров** покрывают самые частые CRM. Для редких (Salesforce, Pipedrive) нужно реализовать новый класс — это ~50 строк PHP по шаблону интерфейса.

---

## 9. Decision request

После approval этой revised-spec → запускаем `writing-plans` для большого плана со всеми 5 фазами (~25-30 tasks).

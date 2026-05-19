# Beget Hosting Cookbook

> Validated рабочие рецепты для Beget shared hosting. Каждый рецепт **проверен на боевом аккаунте `esper21`** (домен `ailexi.ru`). Источники проверки указаны.
>
> Файл живёт чтобы не переоткрывать одно и то же при каждой итерации. Добавляйте сюда новые находки сразу.

**Дата последнего обновления:** 2026-05-18

---

## API endpoint и аутентификация

- URL: `https://api.beget.com/api/<category>/<method>`
- Auth: `login=<account>` + `passwd=<API_PASSWORD>` (НЕ основной пароль аккаунта — отдельный API password из раздела «Управление аккаунтом → API»)
- Все параметры передаются через `--data-urlencode` POST
- JSON payload в `input_data={...}`, формат — `input_format=json`, `output_format=json`

**Тест валидности кред:**
```bash
curl -s -X POST "https://api.beget.com/api/user/getAccountInfo" \
  --data-urlencode "login=$BEGET_LOGIN" \
  --data-urlencode "passwd=$BEGET_PASSWORD" \
  --data-urlencode "input_format=json" \
  --data-urlencode "output_format=json"
```

**Структура успешного ответа:**
```json
{"status":"success","answer":{"status":"success","result": <данные>}}
```
Оба `status` должны быть `success`. Внутренний может быть `error` с `errors[]` массивом.

---

## Что Beget API УМЕЕТ (validated)

### Domain management
- `domain/getList` — все домены аккаунта
- `domain/getSubdomainList` — все поддомены
- `domain/addSubdomainVirtual` — создать поддомен. **Принимает `*` для wildcard** и **`_acme-challenge` для DNS-01 challenge** (underscore prefix OK).
- `domain/deleteSubdomain` — удалить поддомен
- `domain/getPhpVersion` — текущий PHP для FQDN (`{"full_fqdn":"alpha.ailexi.ru"}`)
- `domain/changePhpVersion` — сменить PHP (`{"full_fqdn":"...", "php_version":"8.3"}`). **Поддерживаемые версии:** "5.2", "5.3", "5.6", "7.0"-"7.4", "8.0"-"8.5". **Также триггерит rebuild nginx config** — полезно после link/unlink.

### DNS management
- `dns/getData` — получить DNS-записи для FQDN. **Если FQDN не существует**, возвращает inner status `error` + `Failed to get DNS records`.
- `dns/changeRecords` — **полная замена** всех записей данного типа на FQDN. Не append, не merge — заменяет.
  - Payload: `{"fqdn":"...","records":{"TXT":[{"priority":10,"value":"..."}], "A":[...]}}`
  - Каждая запись имеет `priority` и `value` (для TXT и A) или `value` (для CNAME) или `exchange`+`preference` (для MX).
  - **Чтобы добавить запись:** GET текущие → append → POST полный объект.

### MySQL
- `mysql/getList` — список баз с accesses (без паролей)
- `mysql/addDb` — `{"suffix":"poc","password":"..."}` → создаёт `<login>_<suffix>` + localhost access
- `mysql/dropDb` — `{"suffix":"poc"}`
- `mysql/changeAccessPassword` — `{"suffix":"poc","access":"localhost","password":"..."}`

### Sites
- `site/getList` — список «сайт-сущностей» с привязанными доменами
- `site/add` — `{"name":"ailexi.ru"}` → создаёт сайт-сущность с public_html
- `site/linkDomain` — `{"domain_id":12513532,"site_id":9192816}` — линкует FQDN к public_html
- `site/unlinkDomain` — `{"domain_id":12513532}`

---

## Что Beget API НЕ УМЕЕТ

- **SSL-методы.** Нет endpoint для выпуска/установки/удаления сертификатов. Альтернативы:
  - Wildcard через панель (Домены → SSL иконка) — бесплатно, авто-обновление.
  - acme.sh + кастомный DNS hook (см. ниже) — полная автоматизация без панели.
- **MySQL `getAccessList`** — нет (только `getList` с accesses-объектом без паролей).

---

## Подводные камни Beget shared (validated)

### 1. Нет site/linkDomain → nginx отдаёт статический cache HTML вместо PHP

**Симптом:** на корне домена возвращается старый HTML, `index.php` отдаёт 404. Хеши Last-Modified старые.

**Причина:** домен в `domain/getList` есть, но не привязан к «сайт-сущности» в `site/getList`. nginx у Бегета в этом случае работает в режиме «парковки» — отдаёт прежний контент.

**Решение:** `site/add` + `site/linkDomain` для всех FQDN (включая wildcard `*.<root>`). Дополнительно `domain/changePhpVersion` триггерит nginx-reload — конфиг применяется за ~60 секунд.

### 2. По умолчанию PHP 5.6 на новом subdomain

**Симптом:** новый поддомен после `addSubdomainVirtual` отдаёт HTTP 500 на WordPress.

**Причина:** Beget назначает дефолтный PHP 5.6 для cgi.

**Решение:** сразу после `addSubdomainVirtual` вызвать `domain/changePhpVersion full_fqdn=... php_version="8.3"`. Применяется за ~60 секунд.

### 3. Wildcard subdomain в DNS работает, но HTTP-routing нужен отдельно

**Симптом:** `random-name.ailexi.ru` резолвится в DNS (wildcard работает), но nginx не знает что с ним делать.

**Решение:** `site/linkDomain` для wildcard subdomain ID (тот что вернул `addSubdomainVirtual` с `subdomain="*"`).

### 4. WAF блокирует ТОЛЬКО training-боты OpenAI/Anthropic (GPTBot, ClaudeBot)

**Что блокируется (HTTP 503):**
- `GPTBot` — training crawler OpenAI
- `ClaudeBot` — training crawler Anthropic

**Что НЕ блокируется (HTTP 200):**
- `ChatGPT-User`, `OAI-SearchBot` — live ChatGPT search/RAG
- `Claude-User`, `Claude-SearchBot` — live Claude search
- `PerplexityBot`, `Google-Extended`, `Yandex-Neuro`, `CCBot`, `Bytespider`, `FacebookBot` — всё ОК

**Вывод:** для AI-видимости в ChatGPT Search / Claude / Perplexity / Google AI **специальные настройки не нужны**, всё работает из коробки. Блокировка training-краулеров — фактически защита контента от обучения чужих моделей, **для коммерческих лендингов это плюс, не минус**.

### 5. SSL дефолтный сертификат — общий `CN=beget.com`

**Симптом:** браузер показывает «Not secure» на `https://<домен>.ru/`, потому что сертификат выписан на `beget.com`, а не на твой домен.

**Решение:** выпустить Let's Encrypt (через панель или acme.sh — см. ниже).

### 6. WordPress siteurl=https на домене без SSL = не зайти в админку

**Симптом:** wp-login.php или wp-admin/ редиректят на сломанный HTTPS, браузер показывает «Не удаётся подключиться». Это происходит на тех. поддоменах вида `<login>.beget.tech` (на них SSL не выдаётся) или на новых проектах до заказа SSL.

**Диагностика:**
```bash
wp option get siteurl   # https://... ?
wp option get home      # https://... ?
curl -sI https://<host>  # SSL handshake fails?
```

**Решение** — если SSL ещё не настроен, переключить на HTTP:
```bash
wp option update siteurl 'http://<host>/<path>'
wp option update home 'http://<host>/<path>'
```

**Профилактика на новом проекте:** не ставить `siteurl=https://` пока SSL не настроен **и не проверен** через curl. Stage-08 генератор должен выставлять `http://` по умолчанию, апгрейдить на `https://` только после успешного выпуска SSL.

---

## Wildcard SSL: два рабочих способа

### Способ A — встроенный в панель Beget (manual, recommended for non-CI use)

1. Панель Beget → раздел «Домены»
2. Найти корневой домен → иконка SSL
3. Заказать бесплатный wildcard Let's Encrypt
4. Через 30 минут — 1 день выпускается
5. **Авто-обновление** Beget делает сам

Минус: ручной шаг. Плюс: zero-maintenance.

### Способ B — acme.sh + custom Beget DNS hook (full automation)

**Установка acme.sh на Beget shared:**
```bash
ssh esper21@esper21.beget.tech '
  cd ~ && rm -rf .acme.sh acme-tmp && mkdir acme-tmp && cd acme-tmp
  curl -sL https://github.com/acmesh-official/acme.sh/archive/master.tar.gz | tar xz
  cd acme.sh-master
  ./acme.sh --install --home ~/.acme.sh --accountemail YOUR@email --force
'
```

Примечания:
- Cron нет на shared Бегете → ставим renewal через **панель Beget → Cron**, команда: `cd ~/.acme.sh && ./acme.sh --cron --home ~/.acme.sh > /dev/null`, расписание: ежедневно в 03:00.
- `sed: preserving permissions` warning при установке — не критично, всё работает.

**Регистрация Let's Encrypt аккаунта:**
```bash
ssh ... 'cd ~/.acme.sh && ./acme.sh --register-account -m YOUR@email --server letsencrypt'
```

**DNS hook `~/.acme.sh/dnsapi/dns_beget.sh`:** см. [tests/poc/dns-beget-hook.sh](../tests/poc/dns-beget-hook.sh) (production-ready версия).

Hook требует:
- `BEGET_Login`, `BEGET_Password` env vars
- Хардкод mapping `root_domain → domain_id` (`_beget_root_domain_id()` function). Получить ID через `domain/getList` один раз.

**Выпуск wildcard:**
```bash
ssh ... 'cd ~/.acme.sh && \
  BEGET_Login="<login>" BEGET_Password="<api_pass>" \
  ./acme.sh --issue --dns dns_beget \
    -d ailexi.ru -d "*.ailexi.ru" \
    --server letsencrypt --dnssleep 30'
```

**Установка cert на сервер (для подмены Beget-дефолта на наш wildcard) — TBD.**
Это последний нерешённый шаг для способа B: Beget не имеет API endpoint чтобы загрузить кастомный сертификат. Возможные пути:
- Загрузить через панель вручную → теряем автоматизацию.
- Использовать `~/.acme.sh/<domain>/fullchain.cer` в nginx-конфиге сервера — но shared nginx не позволяет править свой vhost.
- ⚠️ **Возможно способ B работает только до выпуска cert, без установки.** Тогда практическая ценность только в proof-of-concept / для миграции на VPS позже.

---

## Domain IDs (текущий аккаунт esper21)

| FQDN | ID |
|---|---|
| ailexi.ru | 12513532 |
| ailexi.store | 12513533 |
| ailexi.online | 13568994 |
| esper21.beget.tech | 12513573 |

Получено через `domain/getList`. Обновлять при добавлении новых.

## Subdomain IDs

Динамически растут. Получать через `domain/getSubdomainList`.

---

## SSH + wp-cli

- Host: `<login>.beget.tech`, port 22
- Login = account login (esper21)
- Auth: SSH-ключ через панель «Доступы → SSH»
- HOME: `/home/<first-letter>/<login>` (например `/home/e/esper21`)
- wp-cli: **НЕ использовать `/usr/local/bin/wp`** — этот wrapper запускает PHP 7.4 по дефолту. Использовать:
  ```
  /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar <args>
  ```
- PHP бинарники: `/usr/local/bin/php{5.2,5.3,5.6,7.0-7.4,8.0-8.5}` (PHP 8.3 — рекомендуемый для современного WP)

---

## WordPress Multisite на Beget shared (validated)

**Setup recipe (full end-to-end automation):**

1. Wildcard DNS: `addSubdomainVirtual subdomain="*"` для root domain
2. Создание per-segment subdomains: `addSubdomainVirtual subdomain="<seg>"` (опционально — wildcard покрывает любые)
3. `site/add name="<root>"` → получить `site_id`
4. `site/linkDomain` для каждого FQDN (root, `*`, и каждый named subdomain)
5. `domain/changePhpVersion php_version="8.3"` для каждого FQDN
6. `mysql/addDb suffix="..."` + `changeAccessPassword`
7. `wp core download` + `wp config create` + `wp config set WP_ALLOW_MULTISITE true`
8. `wp core multisite-install --url=http://<root> --admin_user=... --subdomains`
9. Записать `.htaccess` (см. tests/poc/scripts/00-setup-multisite.sh phase 4)
10. `wp plugin install lazy-blocks seo-by-rank-math --activate-network`
11. `wp theme install <theme>` + `wp theme enable <theme> --network` + `wp theme activate <theme>` (для каждого subsite)
12. `wp site create --slug=<seg>` для каждого сегмента

**Тема:** использовать **classic** (Twenty Twenty-One), а не block-theme (TT5). Block-themes не выводят page content на front-page при `page_on_front`.

---

## Lazy Blocks на multisite (КРИТИЧНО)

mu-plugin `wp-content/mu-plugins/landing-blocks.php` — один файл, регистрирует ВСЕ блоки на network-уровне.

**Жёсткие требования (без них тихо НЕ работает):**
1. Slug **обязан** начинаться с `lazyblock/` — Lazy Blocks хардкодит namespace в `register_block_type`.
2. `add_action('init', ..., 5)` — priority **меньше 20** (Lazy Blocks свой `register_block` на priority 20).
3. Render-функция передаётся через **`code.frontend_callback`** в массиве блока, а не через `add_filter('lzb/...')`.
4. `code.output_method = 'php'`.

**Минимальный рабочий код:**
```php
<?php
/** Plugin Name: Landing Blocks */
add_action('init', function () {
    if (!function_exists('lazyblocks')) return;
    lazyblocks()->add_block([
        'id'    => 1001,
        'title' => 'Hero',
        'slug'  => 'lazyblock/hero',          // MUST start with lazyblock/
        'category' => 'common',
        'code'  => [
            'output_method'     => 'php',
            'frontend_callback' => function ($attrs) {
                echo '<section>'. esc_html($attrs['headline']) .'</section>';
            },
        ],
        'controls' => [
            ['name' => 'headline', 'type' => 'text', 'default' => ''],
        ],
    ]);
}, 5);
```

**Validated на POC:** test 01 + test 02 GREEN (блок зарегистрирован на 3 subsites одновременно и рендерится с per-page параметрами).

---

## POC Artifacts (сохранены на Beget после POC)

- WP Multisite на `ailexi.ru` (admin: `admin` / `PocAdmin2026Aa1!`)
- Subsites: alpha, bravo, clone (.ailexi.ru)
- DB `esper21_poc`
- 5 mu-plugins в `wp-content/mu-plugins/` (poc-block, poc-robots, poc-schema, poc-llms, poc-gsc)
- Backup старого ailexi.ru WP в `~/poc-backup/`
- acme.sh установлен в `~/.acme.sh/` (account Let's Encrypt зарегистрирован, hook dns_beget.sh установлен, wildcard cert TBD)

---

## TODO / нерешённое

1. **Cert deployment** через acme.sh: как загрузить выписанный `.crt`+`.key` на Бегет shared без панели? Возможно нужен подход «использовать панель для финальной установки» или «переходить на VPS».
2. Cron для `acme.sh --cron` через панель Bagets → задокументировать процедуру.

---

## SSL: расширенный отчёт (validated 2026-05-18)

### Что работает по выпуску сертификатов

| Подход | Статус | Команда |
|---|---|---|
| Beget auto-issue для `<root>` + `www.<root>` | ✅ Из коробки после `site/add` + `site/linkDomain` | Никакая |
| acme.sh wildcard cert через DNS-01 | ✅ Через наш `dns_beget` hook | `./acme.sh --issue --dns dns_beget -d <root> -d "*.<root>"` |
| acme.sh per-subdomain cert через HTTP-01 | ✅ Через `--webroot` (`.well-known/acme-challenge/` доступно) | `./acme.sh --issue --webroot ~/<root>/public_html -d <sub>.<root>` |
| acme.sh per-subdomain cert через DNS-01 | ❌ **НЕ работает** — TXT на `_acme-challenge.<sub>.<root>` Бегет не пропагирует в публичный DNS | — |
| Beget auto-issue для subdomains | ❌ Не выпускает после `addSubdomainVirtual` + `linkDomain` | — |

### Что НЕ работает по установке сертификатов

| Подход | Статус |
|---|---|
| API `ssl/*`, `cert/*` endpoints | ❌ NO_SUCH_METHOD |
| Положить cert в `~/.ssl/`, `~/ssl/` и nginx подхватит | ❌ Эти папки не сканируются |
| Edit `/etc/nginx/*` configs | ❌ Permission denied (root only) |
| Использовать выпущенный нами cert вне панели | ❌ Невозможно на shared |

**Вывод по SSL без панели:**
1. Выпустить wildcard или per-subdomain cert через acme.sh — ОК, работает.
2. Установить cert в nginx Бегета без панели — **невозможно на shared**.
3. Реальные варианты для прода:
   - **Лучше:** один раз заказать wildcard через панель Бегета (бесплатно, авто-renew) — закрывает все subdomains.
   - **Альтернатива:** скрейпинг web-панели Бегета (Python requests + session cookie) для автоматизированной установки cert. Не реализовано.
   - **Иначе:** VPS вместо shared, где nginx-config доступен → выпуск + установка через acme.sh end-to-end.

### Артефакты на сервере после POC

- `~/.acme.sh/` — установлен acme.sh, Let's Encrypt account зарегистрирован
- `~/.acme.sh/dnsapi/dns_beget.sh` — наш hook (production-ready)
- `~/.acme.sh/ailexi.ru_ecc/` — wildcard cert `*.ailexi.ru + ailexi.ru` (валидный, но не установлен в nginx)
- `~/.acme.sh/alpha.ailexi.ru_ecc/` — single cert `alpha.ailexi.ru` (тоже не установлен)
- Beget сам отдаёт Let's Encrypt cert для `ailexi.ru` (он его auto-выпустил), но subdomains — без SSL

## S2-A landing-config — установка и проверка (2026-05-19)

### Установка mu-plugin

```bash
bash skills/wp-landing-config/scripts/install-mu-plugin.sh <project-dir>
```

Что делает:
- rsync `mu-plugin/landing-config/` → `<BEGET_PATH>/wp-content/mu-plugins/landing-config/`
- триггерит миграцию БД через `wp-cli --network option get siteurl` (init-хук создаёт таблицы во всех subsite)

### Smoke REST endpoint

```bash
bash skills/wp-landing-config/scripts/test-smoke-rest.sh <project-dir>
```

Читает `audience_segments` из `.landing-state.yaml`, POSTит SmokeTest lead
на каждый subsite, ожидает HTTP 200.

### Pitfall: PHP CLI на Beget

Wp-cli shim `/usr/local/bin/wp` использует PHP 7.4. Для PHP 8.3:
```
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar
```

### Артефакты на WP

- `wp_<bid>_landing_leads` — заявки (per-blog)
- `wp_<bid>_landing_lead_log` — лог CRM-доставок (per-blog)
- `wp_options::landing_*` — per-site настройки (CTA, head/SEO, integrations)
- `wp_options::landing_integration_<adapter>_<field>` — креды адаптера (password-поля зашифрованы AES-256-GCM)
- `wp_sitemeta::landing_defaults_*` — network defaults
- `wp_sitemeta::landing_config_db_version` — версия схемы

### Phase A1-A5 ready for merge

Implemented:
- A1: каркас, БД, REST, email-fallback, rate-limit, honeypot
- A2: admin-leads (per-site + network aggregate)
- A3: CTA presets + landing_get_cta() helper
- A4: head & SEO admin + landing_render_head_extras()
- A5: 6 adapters (Email/Telegram/WhatsApp/AmoCRM/Bitrix24/HubSpot) +
       admin-integrations с AJAX Test connection + async retry

Live E2E smoke на ailexi.ru запланирован после merge.

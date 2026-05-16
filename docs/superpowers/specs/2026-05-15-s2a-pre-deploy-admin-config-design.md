# S2-A: Pre-deploy & Admin Config (mu-plugin `landing-config`)

**Дата:** 2026-05-15
**Owner:** Спец 2
**Roadmap:** [2026-05-15-specialist-2-roadmap.md](2026-05-15-specialist-2-roadmap.md)
**Источник:** [docs/planning/2026-05-15-plan-dorabotok.md](../../planning/2026-05-15-plan-dorabotok.md), пункты 1-4 части «Специалист 2».
**Статус:** brainstorm complete, **PENDING REVISION** под multisite-aware (см. [roadmap](2026-05-15-specialist-2-roadmap.md) — S2-CD делается первым). Ревизия после approval S2-CD spec.

**Что требует ревизии после S2-CD:**
- mu-plugin → network-activated; `wp_options` → `wp_sitemeta` для общих ключей, per-site override для специфичных.
- `wp_landing_leads` — per-site таблица (одна на blog_id), чтобы заявки сегментов не пересекались.
- Admin UI «Заявки» — фильтр «все сайты сетки / только этот».
- CTA пресеты, head/SEO — network defaults + per-site override.
- Test-connection и async-retry — учитывать что разные сайты сетки могут иметь разные API-ключи.

---

## 1. Цель

Дать маркетологу и клиенту возможность настраивать всю «runtime»-часть лендинга (интеграции с CRM, маршрутизация заявок, CTA-кнопки, head/SEO) **в стандартной wp-admin без кода**. Заявки никогда не теряются — даже без настроенной CRM пишутся в БД и шлются на email админа. Все CTA-кнопки на сайте берут таргет из единых пресетов — смена WhatsApp-номера = одна правка, а не 15.

## 2. Архитектура

Must-use plugin `landing-config.php`, генерируется на stage-08 в `08_КОД/wp-theme/mu-plugins/landing-config/` новым скиллом `wp-landing-config` и копируется деплоем в `/wp-content/mu-plugins/`. Плагин не зависит от темы (можно отключить тему — заявки всё равно собираются) и не зависит от Lazy Blocks плагина (но интегрируется с ним через PHP-helper `landing_get_cta()` в `block.php` шаблонах).

**Принципы:**
- Никаких внешних SDK — все интеграции через `wp_remote_post()` к публичным HTTPS endpoint-ам CRM.
- API-ключи в `wp_options` шифруются AES-256-CBC с ключом из `wp_salt('secure_auth')`.
- Каждый адаптер — отдельный PHP-класс, реализующий интерфейс `LandingConfig\Adapter\AdapterInterface`. Новый CRM = новый класс, без правки ядра.
- Settings API + Native admin pages (без React/Vue).
- Custom table `wp_landing_leads` создаётся activation-hook'ом через `dbDelta()`. Версия схемы в опции `landing_db_version`.

**Главное admin-меню** «Лендинг» с 5 sub-страницами:
1. Setup wizard (показывается one-time при первом входе)
2. Интеграции (CRM + мессенджеры + аналитика)
3. Заявки (просмотр БД-таблицы + экспорт CSV + настройка маршрутизации)
4. CTA-кнопки (5 пресетов + дефолтное поведение)
5. Head & SEO (структурированные поля + raw-textarea)

## 3. Компоненты

### 3.1 Новые файлы в landing_system

**Скилл-генератор:**
- `skills/wp-landing-config/SKILL.md`
- `skills/wp-landing-config/scripts/generate-mu-plugin.py` — читает `08_КОД/landing-config.yaml` (опциональный авторский шаблон) + `block-spec.yaml` для CTA-слотов → рендерит Jinja-шаблоны.
- `skills/wp-landing-config/scripts/lib/config_loader.py` — валидация YAML через jsonschema.
- `skills/wp-landing-config/templates/plugin-main.php.j2` — bootstrap + activation hook.
- `skills/wp-landing-config/templates/admin-{integrations,leads,cta,head-seo,wizard}.php.j2`
- `skills/wp-landing-config/templates/rest-lead.php.j2` — REST endpoint.
- `skills/wp-landing-config/templates/adapters/{amocrm,bitrix24,hubspot,telegram,whatsapp,email}.php.j2`
- `skills/wp-landing-config/templates/helpers.php.j2` — `landing_get_cta()`, `landing_render_head_extras()`, encryption helpers.
- `skills/wp-landing-config/templates/assets/admin.css`, `admin.js` (vanilla JS).
- `skills/wp-landing-config/tests/test_generate_mu_plugin.py`
- `skills/wp-landing-config/tests/test_config_loader.py`
- `skills/wp-landing-config/tests/fixtures/landing-config.minimal.yaml`
- `skills/wp-landing-config/tests/fixtures/landing-config.invalid.yaml`

**Шаблон проекта:**
- `template/08_КОД/landing-config.example.yaml` — аннотированный пример авторского конфига (дефолты пресетов, какие интеграции включить в UI).

**Тесты-гейты (общие для всех под-проектов Спеца 2):**
- `tests/integration/test_lazy_blocks_smoke.sh` — переиспользуемый smoke-gate.
- `tests/integration/test_mu_plugin_smoke.sh` — поднимает wp-env, активирует mu-plugin, дёргает REST, проверяет таблицу.
- `tests/integration/test_cta_routing.sh` — рендерит страницу с блоком, проверяет href в HTML соответствует пресету.

**Документация и команды:**
- `docs/standards/wp-admin-config-checklist.md` — ручной чеклист для маркетолога после деплоя.
- `.claude/commands/landing-admin-setup.md` *(опциональный slash для повторной генерации только mu-plugin без полного rebuild)*.

### 3.2 Изменяемые файлы

- `skills/wp-gutenberg-block-builder/scripts/generate-lzb-templates.py` — добавить вызов `<?php echo landing_get_cta($cta_slot, $url_override); ?>` в `<a>` шаблоны кнопок, когда блок объявил `cta_slot` в `block-spec.yaml`.
- `docs/superpowers/specs/2026-05-13-block-spec-format.md` — добавить поле `cta_slot` (string, optional, enum из `landing-config.yaml::cta_presets.keys()`) в схему control'ов типа `link`.
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — копировать `mu-plugins/landing-config/` в `/wp-content/mu-plugins/` через rsync. Никакой `wp plugin activate` (mu-plugins всегда активны). Smoke после деплоя: `wp eval "echo class_exists('LandingConfig\\Plugin');"` → 1.
- `agents/wp-builder.md` — упомянуть новый скилл `wp-landing-config`.
- `agents/integrations-engineer.md` — переориентировать: теперь отвечает за заполнение `landing-config.yaml` на этапе stack/build, а не за runtime-настройки.
- `CLAUDE.md` — добавить раздел про mu-plugin `landing-config` в секцию «Quality Standards».
- `docs/SETUP.md` — добавить «Что клиент настраивает в админке после деплоя».

### 3.3 Удаляемые / deprecated

Нет — S2-A добавляет, ничего не удаляет.

## 4. CTA-пресеты — схема

`landing-config.example.yaml` поставляется со следующими дефолтами:

```yaml
version: 1
cta_presets:
  primary:
    type: scroll          # scroll | whatsapp | tel | mailto | modal | anchor | url
    target: "#contact-form"
    label_default: "Оставить заявку"
  whatsapp:
    type: whatsapp
    phone: ""             # client fills in admin
    message_template: "Здравствуйте! Интересует {block_context}"
    label_default: "Написать в WhatsApp"
  phone:
    type: tel
    phone: ""
    label_default: "Позвонить"
  form_modal:
    type: modal
    form_id: "main"
    label_default: "Получить предложение"
  learn_more:
    type: anchor
    target: ""            # filled per-block via override
    label_default: "Подробнее"

integrations_enabled:     # какие табы показывать в admin UI
  - amocrm
  - bitrix24
  - hubspot
  - telegram
  - whatsapp
  - email

head_defaults:
  ga4_id: ""
  yandex_metrika_id: ""
  fb_pixel_id: ""
  tiktok_pixel_id: ""
  gsc_verification: ""
  og_default_image: ""    # filled from brand-kit
```

В Lazy Blocks `block-spec.yaml` control'ы типа `link` расширяются:

```yaml
controls:
  - name: cta_button
    type: link
    cta_slot: primary           # NEW — ссылка на пресет
    allow_url_override: true    # NEW — можно ли в редакторе ввести свой URL вместо пресета
```

## 5. Data flow

### 5.1 Build-time (stage-08)

```
07_ПРОТОТИП/prototype.yaml ─┐
                            ├─► block-spec.yaml ──► generate-lzb-* ──► theme/blocks/*/block.php
                            │                                            (использует landing_get_cta())
landing-config.example      │
landing-config.yaml ────────┴─► generate-mu-plugin ──► theme/mu-plugins/landing-config/
```

### 5.2 Deploy-time (stage-09)

```
deploy-wordpress.sh:
  rsync theme/ → server
  rsync mu-plugins/ → /wp-content/mu-plugins/         ← новое
  wp plugin install lazy-blocks --activate            ← из миграции stage-08
  wp media import …
  wp post create (front-page)
  # mu-plugin активируется автоматически
  # activation hook создаёт wp_landing_leads через dbDelta()
  smoke checks (см. §7)
```

### 5.3 Runtime — submit формы

```
форма (frontend JS) ──POST── /wp-json/landing/v1/lead
                              {name, phone, message, source_block, utm_*}
   ↓
LeadController::handle()
   1. nonce + validate (honeypot, обязательные поля)
   2. INSERT INTO wp_landing_leads (всегда)
   3. wp_mail(admin_email, ...) (всегда, отключаемо галочкой)
   4. foreach enabled_adapter in [amocrm, bitrix24, hubspot, telegram, whatsapp]:
        try { $adapter->send($lead); log success }
        catch (e) {
          log error в wp_landing_lead_log;
          wp_schedule_single_event(now + 60s, 'landing_retry_delivery', [lead_id, adapter, attempt=1])
        }
   5. return {ok: true, lead_id: N}
   ↓
форма показывает success-message (из настроек CTA)
```

### 5.4 Runtime — async retry

`landing_retry_delivery` cron hook:
- attempts: 1 → +60s, 2 → +300s, 3 → +1800s
- после 3 — final fail, в `wp_landing_lead_log` статус `failed_permanent`, в админке red-dot badge на «Заявки».
- Кнопка «Retry now» в UI.

### 5.5 Runtime — клик CTA-кнопки

```
block.php рендерит:
  <a href="<?= esc_url(landing_get_cta('whatsapp', $override_url, ['model' => $post->title])) ?>" ...>
       ↓
landing_get_cta($slot, $override, $context):
   1. Если $override и control allows_override → вернуть $override.
   2. Прочитать wp_options['landing_cta_presets'][$slot].
   3. По type сформировать URL:
        whatsapp → "https://wa.me/{phone}?text=" + urlencode(template с подстановкой $context)
        tel      → "tel:{phone}"
        modal    → "#" + data-modal="$form_id"  (admin.js перехватывает onclick)
        scroll   → "#contact-form"
        anchor   → $target
        url      → $target as-is
        mailto   → "mailto:{email}?subject=..."
   4. Если preset не настроен → fallback на 'scroll' с #contact-form + log warning.
```

### 5.6 Runtime — head

```
wp_head action (priority 5):
  landing_render_head_extras()
    ├─ inline GA4 (если ID настроен)
    ├─ inline Yandex.Metrika
    ├─ <meta property="og:..."> из настроек или дефолтов
    ├─ <link rel="icon"> на favicon из Media Library
    ├─ <link rel="stylesheet" href="<google_fonts_url>">
    └─ wp_kses($raw_head_html, $head_whitelist)  ← раздел «Прочий HTML»
```

`$head_whitelist`: tags `meta`, `link`, `script[src,async,defer,type]`, `style`, `noscript`; attrs специфичные для аналитики/верификации. Inline `<script>` без `src` пропускаются с warning в админке (защита от XSS через клиент-редактор).

### 5.7 Хранение

| Опция | Содержимое |
|---|---|
| `wp_options.landing_integrations` | JSON с API-ключами (шифруется) и тогглами адаптеров |
| `wp_options.landing_cta_presets` | JSON с 5 пресетами (любое количество, дефолт = 5) |
| `wp_options.landing_head_seo` | JSON со структурированными полями + raw |
| `wp_options.landing_routing` | JSON: какие адаптеры активны, autoresponder template, основной канал |
| `wp_options.landing_errors` | Ring buffer 50 записей последних runtime-ошибок |
| `wp_options.landing_db_version` | string, schema version для миграций |
| `wp_landing_leads` (custom table) | id, created_at, name, phone, email, message, source_block, utm_*, processed_status |
| `wp_landing_lead_log` (custom table) | id, lead_id, adapter, attempt, status, response, created_at |

## 6. Error handling

**Build-time:**
- `generate-mu-plugin.py` валидирует `landing-config.yaml` через jsonschema. Fast-fail с указанием поля. Без файла — генерим из `landing-config.example.yaml`, warning в лог.
- После генерации запускается `php -l` на каждом сгенерированном `.php` файле. Любой syntax error = exit 1.

**Deploy-time:**
- rsync mu-plugins падает → весь deploy откатывается (rollback в `wp-cli-deployer`).
- Activation hook защищён `IF NOT EXISTS` + `dbDelta()`. Миграция через switch по `landing_db_version`.
- Smoke (см. §7) — если красный, deploy помечается `failed`, требуется ручное вмешательство.

**Runtime — REST `/lead`:**
- Nonce fail → 403 + log (вероятный бот).
- Validate fail (honeypot заполнен, обязательные поля пусты) → 400, форма показывает inline error.
- DB INSERT fail → 500 + ring-buffer log. Форма показывает «временная ошибка, позвоните +X» (телефон из настроек).
- `wp_mail` fail → log, **не блокирует** ответ (заявка уже в БД).
- Adapter sync fail → log + schedule retry (см. §5.4). Юзеру отвечаем 200 (с точки зрения юзера — заявка принята).

**Runtime — CTA helper:**
- Пресет не существует → возвращает `#` с `data-cta-error="preset_X_missing"` для дебага в DevTools, визуально кнопка ведёт в null. Log в `landing_errors`.
- WhatsApp без phone → fallback на scroll-to-form.

**Admin UI:**
- Каждое поле API-ключа имеет кнопку «Test connection» → adapter делает dummy-call (например, GET `/api/v4/account` для AmoCRM) → green check / red X с текстом ошибки. **Закрывает требование п.1 ПЛАН-ДОРАБОТОК** («тестовый запрос — проверяет работает ли»).
- Sanitize callback на каждое поле.
- Capability check: только `manage_options` (admin) видит весь UI; роль `editor` видит только «Заявки» (просмотр + экспорт).

## 7. Testing strategy

### 7.1 Unit (pytest)
- `tests/test_generate_mu_plugin.py` — генератор пишет валидный PHP (`php -l` зелёный), все опции Settings API регистрируются, REST route регистрируется.
- `tests/test_config_loader.py` — валидация `landing-config.yaml` через jsonschema (минимальный YAML; невалидный; missing fields).

### 7.2 PHP unit (phpunit, минимум)
- Adapter classes — мок `wp_remote_post()`, проверка формата body для каждой CRM.
- `landing_get_cta()` — таблица параметров → ожидаемые URL.
- Encryption helpers — round-trip (encrypt → decrypt = original).

### 7.3 Integration (bats + wp-env)

**`tests/integration/test_lazy_blocks_smoke.sh`** — обязательный gate, переиспользуется всеми под-проектами Спеца 2. Проверяет:
1. Генераторы stage-08 отрабатывают на фикстуре без ошибок.
2. `wp-env start` поднимает WP с темой + Lazy Blocks плагином.
3. `wp post create` для front-page возвращает ID.
4. `curl /` → HTTP 200.
5. HTML содержит ≥1 класс `lazyblock-`.
6. PHP error.log пустой за последние 30 секунд.
7. `wp eval "echo function_exists('landing_get_cta');"` → 1 (после внедрения S2-A).
8. `wp db query "DESCRIBE wp_landing_leads"` → схема есть.

Принимает `--project <slug>` (default `dubai-avto-liza`).

**`tests/integration/test_mu_plugin_smoke.sh`**:
1. `wp-env start` с темой и mu-plugin.
2. `wp option update landing_integrations '{}'`.
3. `curl -X POST /wp-json/landing/v1/lead -d {name,phone}` → 200, `lead_id` в ответе.
4. `wp db query "SELECT COUNT(*) FROM wp_landing_leads"` → ≥1.
5. `wp eval "echo class_exists('LandingConfig\\Plugin');"` → 1.

**`tests/integration/test_cta_routing.sh`**:
1. Создать страницу с блоком `cta_button` (`cta_slot: whatsapp`).
2. Настроить `wp_options.landing_cta_presets.whatsapp.phone = +971500000000`.
3. `curl /test-page` → HTML содержит `href="https://wa.me/971500000000?text=..."`.

### 7.4 E2E ручной чеклист

`docs/standards/wp-admin-config-checklist.md`:
- После деплоя зайти в админку → Setup wizard.
- Подключить Telegram → нажать «Test connection» → green.
- Сделать тестовую заявку с фронта → проверить:
  - письмо пришло на admin_email
  - запись в «Заявки» появилась
  - сообщение пришло в Telegram
- Сменить WhatsApp-номер в CTA-пресете → проверить что все кнопки на сайте обновились.

### 7.5 Regression gates в плане работ

Каждый Task в плане заканчивается:
```
- [ ] Run: bash tests/integration/test_lazy_blocks_smoke.sh
- [ ] Run: bash tests/integration/test_mu_plugin_smoke.sh
- [ ] Оба exit 0 — иначе Task не completed
```

Это формализованное выполнение требования из CLAUDE.md «После каждой доработки — гонять авто-проверку чтобы старое не сломалось» и явного user-requirement «добавь проверку работы lazy blocks после каждого этапа доработок».

## 8. Безопасность

- API-ключи: AES-256-CBC + ключ из `wp_salt('secure_auth')`. В UI показываются как `••••••••` с кнопкой «Reveal» (требует подтверждения пароля).
- REST endpoint защищён nonce-ом для авторизованных юзеров и honeypot-полем для анонимных.
- Rate-limit: max 10 заявок/IP/час (transient API). Превышение → 429.
- raw_head_html прогоняется через `wp_kses` whitelist.
- CSRF: nonce на все admin-формы.
- Capability checks: только `manage_options` редактирует интеграции/head.

## 9. Out of scope

- Multisite-aware режим (см. S2-D).
- Полноценный CRM-UI (lead pipeline, assigned-to, status workflow) — `wp_landing_leads` это **журнал**, не замена CRM.
- A/B testing форм — отдельный под-проект.
- SMS-уведомления — добавим адаптер позже, не P0.
- Telegram bot 2-way (отвечать клиенту из админки) — только отправка из лендинга в чат менеджера.

## 10. Open questions для имплементации

- Какой Telegram-API использовать: Bot API (требует bot token) или раздачу через `t.me/share/url=...` (без API)? **Предложение:** Bot API, удобнее для клиента.
- WhatsApp: Business API (платный, требует Meta-аккаунт) или клик-ту-чат через `wa.me/{phone}` (бесплатно, но без подтверждения доставки)? **Предложение:** для CTA-кнопок — `wa.me`; для «получить уведомление о заявке менеджеру» — Bot API через посредника (например, Twilio) — отложим до P1.
- Хранить ли API-ключи в `wp_options` или в `wp-config.php` (более безопасно но требует SSH)? **Предложение:** опционально — UI показывает «настроить в wp-config» для параноидальных клиентов, иначе хранит зашифрованно в БД.

Эти три вопроса решаются на этапе писания плана (writing-plans skill).

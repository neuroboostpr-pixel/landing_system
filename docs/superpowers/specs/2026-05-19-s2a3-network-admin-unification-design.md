# S2-A.3 — Network-Admin Unification (CTA + Integrations + Snippets cascade)

**Дата:** 2026-05-19
**Owner:** Спец 2
**Roadmap:** [2026-05-15-specialist-2-roadmap.md](2026-05-15-specialist-2-roadmap.md) §S2-A
**Предшественники:** [S2-A](2026-05-19-s2a-landing-config-revised.md), [S2-A.2](2026-05-19-s2a2-snippets-manager.md)
**Статус:** brainstorm complete, awaiting user review → writing-plans.

---

## 1. Цель

Свести все настройки лендинг-системы (CTA-кнопки, Интеграции, Снипеты, Заявки) в **одну точку — Network admin** мультисайта, с per-сегментным override через единый паттерн cascade «network default → site override».

Маркетолог-агент работает из network admin (super-admin), не переключается между поддоменами. Read-only-проекция на subsite остаётся для контекста («что вижу — то и применяется к этому сайту»).

### Что закрывает

- **R4 из текущего бэклога:** маркетолог жалуется «карточки в одной админке, CTA в другой» → одна.
- **Архитектурный долг S2-A:** CTA и Integrations сейчас site-only, не имеют network-уровня. Унифицируется паттерн со Snippets (S2-A.2).
- **B17/B18 предусловие:** будущая CTA-Library (CPT с превью + usage map) сядет на готовую CPT-инфраструктуру S2-A.3.

### Что НЕ в скоупе

- Custom-statuses workflow для заявок — это **B19**, отдельный спек.
- CTA-Library с произвольным числом кнопок и Lazy-Blocks-meta — это **B17**, отдельный спек.
- Snippet-parser для счётчиков (auto-detect ID из вставленного snippet) — это **B18**, отдельный спек.
- Live testing 5 не-Email адаптеров — **B20**, отдельный спек (нужны test-credentials).
- Внешний UI вне wp-admin (SaaS-уровень) — отложено.

---

## 2. UX-обзор

```
Network admin → Лендинг
  ├ Лендинг             (dashboard как сейчас, R2)
  ├ Заявки (все сегменты)  (как сейчас, S2-A.1)
  ├ CTA-кнопки          (новое, с селектором сегмента)
  ├ Интеграции           (новое, с селектором сегмента)
  └ Снипеты              (как сейчас + добавляется селектор сегмента)
```

**Селектор сегмента** — общий компонент в верхней части каждой управляющей страницы:

```
[ Сегмент: ▼ (network default) ────────────────── ] [Применить]
            ├ (network default — общие для всех сегментов)
            ├ ailexi.ru          (главный сайт сети ★)
            ├ russian.ailexi.ru
            └ family.ailexi.ru
```

URL-параметр `?segment=<blog_id|0>`, где `0` означает «network default». Состояние селектора сохраняется в URL — копируемая ссылка ведёт ровно туда.

### CTA-кнопки

- Селектор сегмента сверху.
- При `segment=0` (network) — таблица 5 пресетов (`primary`, `whatsapp`, `phone`, `form_modal`, `learn_more`), редактирование всех полей напрямую.
- При `segment=N` (subsite) — те же 5 пресетов, но каждый показан с badge:
  - `Inherited from network` (read-only превью значений) + кнопка [Override для этого сегмента]
  - `Site override` — поля редактируемые + кнопка [Удалить override → вернуться к network default]
- Override-toggle on/off включает/выключает per-preset запись для сегмента. Сам preset_name (`primary`, `whatsapp`, ...) остаётся одинаковым на всех уровнях — это **machine-id**, как `name` в Snippets.

### Интеграции

- Селектор сегмента сверху.
- 6 карточек: Email / Telegram / WhatsApp / AmoCRM / Bitrix24 / HubSpot.
- При `segment=0` — каждая карточка раскрывается в форму настроек как сейчас.
- При `segment=N` — большой toggle в шапке карточки **«Использовать свой <AdapterName> для этого сегмента»**:
  - off (default) — отображение network-настроек read-only с маскированными credentials (`token: •••• ****`) + текст «Заявки этого сегмента уйдут в <network adapter summary>».
  - on — раскрывается полная форма для site-override; снизу пометка «При снятии галочки сегмент вернётся к network-настройкам».

### Снипеты

Текущая структура (S2-A.2) уже cascade-aware. Добавляется только **селектор сегмента сверху унифицированно** + перенос страницы в подпункты единой `Лендинг`:

- Network admin → Лендинг → Снипеты — единая страница.
- При `segment=0` — список network snippets, добавление/редактирование/удаление, столбец «Overridden by» как сейчас (имена сабсайтов).
- При `segment=N` — список site snippets конкретного blog_id + раздел «Inherited from network» с кнопкой [Override] на каждом.

### Site admin (read-only mode)

На каждом `<segment>.ailexi.ru/wp-admin` пункт «Лендинг» остаётся, но:

- Те же 4 раздела (Заявки / CTA / Интеграции / Снипеты).
- **Заявки** — read-write как сейчас (заявки именно этого сегмента, экспорт CSV доступен — это нужно clientside admin, не super-admin work).
- **CTA / Интеграции / Снипеты** — read-only:
  - Все формы и checkboxes имеют `disabled` атрибут
  - Submit-кнопки скрыты
  - Badge «Inherited from network» / «Site override (managed by super-admin)»
  - Server-side guard в save-handlers — если запрос пришёл не из network-admin контекста, отбиваем 403
  - Краткая инструкция «Эти настройки управляются из network admin → Лендинг → ... → [link]»

---

## 3. Архитектура данных

Используем единый паттерн **CPT с meta**, как уже сделано для Snippets (S2-A.2). Хранение per-blog с явным `is_network` flag, и для network — CPT на blog_id = `NETWORK_BLOG_ID` (== `get_main_site_id()`, обычно `1`).

### 3.1 CPT `lp_cta` (новый)

| post_meta key | Type | Меaning |
|---|---|---|
| `_lp_cta_preset_name`     | string | `primary`/`whatsapp`/`phone`/`form_modal`/`learn_more` (machine-id, как `name` в Snippets) |
| `_lp_cta_type`            | string | `scroll`/`whatsapp`/`tel`/`mailto`/`modal`/`anchor`/`url` |
| `_lp_cta_label`           | string | Текст по умолчанию на кнопке |
| `_lp_cta_target`          | string | URL / якорь / номер телефона |
| `_lp_cta_phone`           | string | Спец-поле для tel/whatsapp |
| `_lp_cta_form_id`         | string | Спец-поле для modal |
| `_lp_cta_message_template`| string | Спец-поле для WhatsApp |
| `_lp_cta_is_network`      | '0'/'1'| Признак: network-уровень или site-override |

CPT: `public=false`, `show_ui=false`, `show_in_rest=false`, `supports=['title']`. Capabilities — те же plural-primitives как `lp_snippet` после фикса R3.

### 3.2 CPT `lp_integration` (новый)

| post_meta key | Type | Meaning |
|---|---|---|
| `_lp_int_adapter_name` | string | `email`/`telegram`/`whatsapp`/`amocrm`/`bitrix24`/`hubspot` (machine-id) |
| `_lp_int_enabled`      | '0'/'1'| Адаптер включён |
| `_lp_int_settings`     | array (serialized) | Все остальные поля адаптера, **encrypted-fields зашифрованы через `LandingConfig\Encryption\encrypt`** |
| `_lp_int_is_network`   | '0'/'1'| Признак |

`_lp_int_settings` — `wp_kses`-санитайзированный массив (структура задаётся каждым `AdapterInterface::field_definitions()`). Encrypted поля помечены `'encrypt' => true` в схеме адаптера и шифруются перед `update_post_meta`. Текущая шифрация AES-256-GCM из S2-A остаётся.

### 3.3 Snippets (no schema change)

CPT `lp_snippet` уже корректно устроен (S2-A.2). Меняется только UI-обёртка (добавление селектора сегмента в admin-snippets) и снимаются дублирующиеся подпункты с subsite-admin.

### 3.4 Резолвер cascade (новый, общий)

`includes/cascade.php` — единый helper:

```php
namespace LandingConfig\Cascade;

/** Для одного adapter/preset_name вернуть финальную запись с указанием, откуда. */
function resolve_for_blog(string $cpt, string $name_meta_key, string $name, int $blog_id): ?array;

/** Список всех элементов CPT для сегмента (network defaults + site overrides по имени). */
function list_for_blog(string $cpt, string $name_meta_key, int $blog_id): array;

/** Есть ли site override данного name для blog_id? */
function has_site_override(string $cpt, string $name_meta_key, string $name, int $blog_id): bool;
```

Логика:
1. Возьми все site-snapshots (`is_network=0`) для `blog_id` — каждый сводный по `name`.
2. Возьми все network-snapshots (`is_network=1`) с blog_id=1.
3. Для каждого `name` — site побеждает network. Без `name` (как у безымянных snippets) — site и network считаются независимыми, оба применяются.

Этот же резолвер используется в:
- `landing_get_cta($preset_name)` — берёт current_blog_id, резолвит CTA-CPT
- `LandingConfig\Adapters\<X>Adapter::settings()` — берёт current_blog_id, резолвит integration-CPT
- `LandingConfig\Snippets\render($position)` — уже использует свою специализированную логику (никаких изменений)

### 3.5 Encryption-pass-through при override

При site-override для AmoCRM/Bitrix24/HubSpot/Telegram/WhatsApp credentials шифруются тем же ключом что и network. `WP_LANDING_CONFIG_KEY` (master key из S2-A) — общий для сети, не per-blog. Это упрощает super-admin migration данных, не теряет на безопасности (credentials и так доступны super-admin'у).

---

## 4. Миграция существующих данных

Один раз при первом запуске после деплоя S2-A.3:

1. **CTA**: `wp_1_options.landing_cta_presets` (5 пресетов на blog_id=1, формат S2-A) → создать 5 CPT `lp_cta` записей с `is_network=1` на blog_id=1.
2. **Integrations**: `wp_<N>_options.landing_integration_<adapter>` для всех blog_id и всех адаптеров → создать CPT `lp_integration` записи:
   - blog_id=1 (главный сайт) → `is_network=1`
   - blog_id>1 (сегменты) → `is_network=0` (site-level override на этом сегменте)
3. После успешной миграции — `update_site_option('landing_config_migration_s2a3', '1')`. Старые `wp_options` записи **не удаляем** — оставляем как backup (читаются только если CPT-запись отсутствует, fallback).
4. После 2-3 недель боевой эксплуатации без жалоб — отдельный коммит удаляет fallback.

Скрипт миграции — `includes/migrate-to-s2a3.php`, идемпотентен (проверяет marker option).

---

## 5. Структура файлов

```
mu-plugin/landing-config/
  landing-config.php                   (порядок require обновлён)
  includes/
    cascade.php                        НОВЫЙ — общий резолвер
    cta.php                            НОВЫЙ — CPT lp_cta + CRUD + helper landing_get_cta()
    integrations.php                   НОВЫЙ — CPT lp_integration + CRUD + AdapterInterface::settings() refactor
    migrate-to-s2a3.php                НОВЫЙ — одноразовая миграция данных
    admin-pages.php                    (оставляем dashboard + network_dashboard как сейчас)
    admin-cta.php                      РЕРАЙТ — теперь network_admin_menu + segment selector
    admin-integrations.php             РЕРАЙТ — то же
    admin-snippets.php                 РЕРАЙТ — селектор сегмента, объединение с network admin
    admin-snippets-network.php         УДАЛЯЕМ (мерджим в admin-snippets.php)
    admin-leads-network.php            (как сейчас)
    admin-leads.php                    (как сейчас)
    admin-cta-readonly.php             НОВЫЙ — read-only UI на subsite
    admin-integrations-readonly.php    НОВЫЙ — read-only UI на subsite
    admin-snippets-readonly.php        НОВЫЙ — read-only UI на subsite
    snippets.php                       (как есть после R3 фикса)
    helpers.php
    db.php
    encryption.php
    rest-lead.php
  adapters/
    AdapterInterface.php               РАСШИРЕН — добавить static field_definitions()
    EmailAdapter.php                   (читать settings() через cascade)
    TelegramAdapter.php                (то же)
    WhatsAppAdapter.php                (то же)
    AmoCRMAdapter.php                  (то же)
    Bitrix24Adapter.php                (то же)
    HubSpotAdapter.php                 (то же)
```

### Компонент: SegmentSelector (re-usable)

`includes/cascade.php::render_segment_selector(string $page_slug, int $current_segment): void`:

```html
<div class="lp-segment-selector">
  <form method="get" style="display:inline;">
    <input type="hidden" name="page" value="<?= esc_attr($page_slug) ?>">
    <label>Сегмент:
      <select name="segment" onchange="this.form.submit()">
        <option value="0">— общие (network default)</option>
        <option value="1">ailexi.ru ★</option>
        <option value="2">russian.ailexi.ru</option>
      </select>
    </label>
  </form>
</div>
```

GET-запрос вместо AJAX-у — copy-paste-friendly URL, отсутствие JS-runtime-baggage.

---

## 6. Меню — итоговая структура

### Network admin (super-admin only)

```
Лендинг (top-level)
├ Лендинг (dashboard, R2-карточки)
├ Заявки (все сегменты)              — admin-leads-network.php
├ CTA-кнопки                         — admin-cta.php (новый рерайт)
├ Интеграции                         — admin-integrations.php (новый рерайт)
└ Снипеты                            — admin-snippets.php (рерайт + merge с _network.php)
```

### Site admin (обычный admin сегмента)

```
Лендинг (top-level)
├ Заявки                              — admin-leads.php (read-write, как сейчас)
├ CTA-кнопки [просмотр]              — admin-cta-readonly.php
├ Интеграции [просмотр]               — admin-integrations-readonly.php
└ Снипеты [просмотр]                  — admin-snippets-readonly.php
```

---

## 7. Helper API — обратная совместимость

### landing_get_cta(string $preset_name, string $url_override = null, array $context = []): array

Поведение: **не меняется** для внешних потребителей (тем). Внутри теперь:

```php
function landing_get_cta(string $preset_name, ?string $url_override = null, array $context = []): array {
    $blog_id = \get_current_blog_id();
    $resolved = \LandingConfig\Cascade\resolve_for_blog(
        'lp_cta', '_lp_cta_preset_name', $preset_name, $blog_id
    );
    if (!$resolved) {
        // Fallback на S2-A wp_options до завершения миграции
        $resolved = _legacy_get_cta_from_options($preset_name);
    }
    // ... шаблонизация message_template с $context ...
    return $resolved;
}
```

### landing_render_head_extras() (deprecated S2-A.2)

Уже удалено в S2-A.2 (Head & SEO заменён на Snippets). Подтверждения не требует.

### landing_config_get(string $key, $default = null)

Поведение: **не меняется**. Внутренне читает через cascade, но интерфейс прежний.

---

## 8. Безопасность

### Server-side guards на subsite

В каждом `admin-*-readonly.php` все save-action endpoints отвечают 403:

```php
function reject_save_on_subsite(): void {
    if (!is_network_admin()) {
        wp_die('Эти настройки управляются super-admin\'ом из network admin.', 403);
    }
}
```

Подтверждение через двойной guard:
1. UI: `disabled` атрибуты на полях.
2. Server: проверка `is_network_admin()` в save-handlers (даже если кто-то форму распарсит и сделает POST вручную).

### Маскирование credentials в read-only view

На subsite в Интеграции read-only mode credentials отображаются как `••••••••${last_4}` (последние 4 символа для распознавания). Полные значения видны **только** в network admin при разворачивании `<details>` блока.

### Capability checks

- Network страницы: `manage_network_options`.
- Site read-only страницы: `manage_options` (sub-admin сегмента или super-admin).
- В обоих случаях — двойная проверка в menu hook + render callback (как сейчас).

---

## 9. Тесты

### Unit (PHP)

1. **`cascade.php::resolve_for_blog`** — таблица сценариев:
   - Только network: должен вернуть network.
   - Только site: должен вернуть site.
   - Оба: site побеждает.
   - Ни одного: `null`.
   - С пустым `name` (для snippets-style): network и site сосуществуют, не override.
2. **`landing_get_cta` cascade integration**:
   - На blog_id=1 без override: вернёт network preset.
   - На blog_id=2 с site-override (например, `whatsapp`): вернёт site.
   - На blog_id=2 без site-override (`primary`): вернёт network.
   - Fallback на legacy `wp_options` когда CPT пуст (для backward-compat в переходный период).
3. **AdapterInterface::settings() refactor** — для каждого из 6 адаптеров: тот же набор полей возвращается через cascade resolver.
4. **Encryption round-trip cross-cascade**: encrypted поле в network → site override → read back на site должен decrypt чисто.
5. **Миграция**: фикстура wp_options с CTA + integrations → run migrate → CPT записи созданы корректно → marker option = '1' → второй прогон no-op.

### Integration (bats / wp-cli live)

1. **Server-side guard**: POST с subsite-admin URL'а на save endpoint → 403. POST из network admin → 200.
2. **Read-only view rendering**: на subsite видны badge'и `inherited` / `override`, формы disabled, submit-кнопки отсутствуют (DOM grep).
3. **Network-admin segment selector**: GET с `?segment=0` показывает network, `?segment=2` показывает override view для blog_id=2.
4. **Full smoke (`scripts/install-mu-plugin.sh` + UI walkthrough)** на ailexi.ru — должен пройти без regression в R1/R2/R3.

### Regression

После каждой фазы — прогон `tests/test_*.php` + `tests/integration/test_lazy_blocks_smoke.sh` на ailexi.ru.

---

## 10. Фазы имплементации

| Фаза | Содержимое | Деливерится отдельным коммитом |
|---|---|---|
| **A3.1** | `cascade.php` resolver + unit-тесты; `cta.php` CPT + helper `landing_get_cta` через cascade; миграция S2-A wp_options → CPT для CTA | да |
| **A3.2** | `integrations.php` CPT + AdapterInterface refactor; миграция wp_options → CPT для 6 адаптеров; encryption round-trip tests | да |
| **A3.3** | `admin-cta.php` (network admin рерайт + segment selector); `admin-cta-readonly.php` (subsite view); server-side save guard | да |
| **A3.4** | `admin-integrations.php` (network admin рерайт + segment selector + override toggle на адаптер); `admin-integrations-readonly.php` | да |
| **A3.5** | `admin-snippets.php` (merge с `admin-snippets-network.php` + segment selector); `admin-snippets-readonly.php`; удаление `admin-snippets-network.php` | да |
| **A3.6** | Remove R1 diagnostic logger; final smoke на ailexi.ru; doc update | да |

Каждая фаза самодостаточна — между фазами система работает (например, после A3.1 CTA через cascade работает, а Integrations ещё на старой схеме).

---

## 11. Известные ограничения / откладываемое

- **B17 CTA-Library** (произвольное число CTA с превью + usage map): требует чтобы CTA было CPT — S2-A.3 даёт фундамент, но B17 — отдельный спек.
- **B18 snippet-parser**: требует чтобы settings parsing был на UI-форме — S2-A.3 даёт сайт settings forms, но добавление intelligent parsing — отдельный спек.
- **B19 Lead status workflow**: ортогональная фича, не требует S2-A.3 — может идти параллельно или после.
- **R5 wildcard SSL**: ручной шаг в Beget панели, не блокер.
- **Multi-CTA per preset_name на одном сегменте**: явно НЕ поддерживается. 5 пресетов на blog_id, один preset_name = одна запись. Хочешь больше кнопок — это B17.

---

## 12. Open questions (для review)

1. **Migration safety net**: оставлять ли legacy fallback навсегда или удалить через 2-3 недели? Рекомендую — удалить через 2-3 недели, очистить debt.
2. **Site admin role для read-only**: должна ли `editor` роль видеть read-only view, или только `administrator`? Текущая позиция: только `administrator` (capability `manage_options`).
3. **Selector at top vs sticky sidebar**: селектор сегмента в шапке страницы (форма) или sticky-блок над таблицей? Рекомендую — обычный inline-блок над таблицей (минимум CSS, copy-paste-friendly URL).

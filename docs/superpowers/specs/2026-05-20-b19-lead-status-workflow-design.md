# B19 — Lead Status Workflow (MVP)

**Дата:** 2026-05-20
**Скоуп:** S2-A.4 (продолжение S2-A.3)
**Зависимости:** S2-A.3 Network-Admin Unification (готов)
**Trello / backlog:** [docs/BACKLOG.md#B19](../BACKLOG.md)

## 1. Контекст и проблема

В таблице `wp_<bid>_landing_leads` уже существует колонка `processed_status VARCHAR(32) NOT NULL DEFAULT 'pending'` с индексом, но в админке «Заявки» (`admin-leads.php`) нет ни одного элемента UI для смены статуса. Маркетолог видит список входящих заявок, но не может пометить заявку как «обработана», «в работе», «закрыта успешно». На multisite с десятками заявок в неделю это критичная функциональная дыра.

Эта работа добавляет редактируемый словарь статусов, карточку заявки с историей изменений, и расширения списка заявок (табы-фильтры, колонка статуса, bulk-actions). CRM-синхронизация (двусторонняя — статус из CRM в админку и из админки в CRM) явно вынесена за скоуп MVP — она требует расширения `AdapterInterface::update_status()` и тестов с реальными credentials всех 5 адаптеров, что превращает задачу в отдельный трек размера S2-A.3.

## 2. Дизайн в одной фразе

Четвёртая ось каскада S2-A.3 (после CTA, Integrations, Snippets): `lp_lead_status` CPT с network→site override; карточка заявки с timeline истории и модальным окном смены статуса; subsubsub-табы и bulk-action в существующем списке заявок.

## 3. Архитектура данных

### 3.1 Vocabulary статусов — CPT `lp_lead_status`

Регистрируется по той же схеме что `lp_cta`, `lp_integration`, `lp_snippet`: private (show_ui/show_in_menu false), capability_type=post с map_meta_cap=true, capabilities edit/edit_others/publish/delete → `manage_options`.

Поля статуса (хранятся в post_meta):
- `_lp_status_slug` — машинное имя (a-z0-9_-, primary identifier, used in URLs и `landing_leads.processed_status`)
- `_lp_status_label` — отображаемое название («Новая», «В работе», ...)
- `_lp_status_color` — hex-цвет бейджа (#RRGGBB)
- `_lp_status_order` — int для сортировки (по умолчанию 10, 20, 30, ...)
- `_lp_is_network` — bool, признак network-default vs site-override (как в других CPT)

Cascade-поведение: переиспользуется `LandingConfig\Cascade\resolve_for_blog/list_for_blog/has_site_override` с параметрами `POST_TYPE='lp_lead_status'`, `NAME_META='_lp_status_slug'`, `NETWORK_META='_lp_is_network'`. Сегмент может либо добавить свой статус с уникальным slug, либо переопределить network-default по совпадающему slug.

Функции в namespace `LandingConfig\LeadStatuses`:
```php
save_lead_status(array $args, bool $is_network, int $blog_id, int $post_id = 0): int
get_lead_status(int $id): ?array
list_lead_statuses(int $blog_id): array  // отсортировано по order asc
resolve_lead_status(string $slug, int $blog_id): ?array
delete_lead_status(int $id): bool
has_override(string $slug, int $blog_id): bool
```

### 3.2 Таблица истории — `wp_<bid>_landing_lead_status_log`

Per-blog таблица, создаётся в `db.php::install_schema()` через `dbDelta` (idempotent применение).

```sql
CREATE TABLE wp_<bid>_landing_lead_status_log (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    lead_id BIGINT(20) UNSIGNED NOT NULL,
    user_id BIGINT(20) UNSIGNED NULL,
    from_status VARCHAR(64) NULL,
    to_status VARCHAR(64) NOT NULL,
    comment TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY lead_id (lead_id),
    KEY created_at (created_at)
) <charset>;
```

`user_id` nullable — позволит позже добавить системные изменения (например, миграция или CRM-webhook). `from_status` nullable — первая запись «создана» имеет from=NULL. `comment` nullable — для bulk-action с пустым комментарием и для будущих системных изменений.

Helper-функции в namespace `LandingConfig\LeadStatusLog`:
```php
log_status_change(int $lead_id, ?string $from, string $to, ?int $user_id, ?string $comment): int
get_status_history(int $lead_id): array  // отсортировано created_at desc
```

`log_status_change` валидирует, что `$to` существует в vocab текущего blog (через `resolve_lead_status`), иначе возвращает 0 и пишет error_log без записи в БД. Это второй слой защиты после whitelist-валидации в admin-post handler.

### 3.3 Связь с landing_leads

Колонка `processed_status VARCHAR(32)` остаётся как есть. После каждой смены статуса:
1. Запись в `landing_lead_status_log` через `log_status_change()`
2. `UPDATE landing_leads SET processed_status = ? WHERE id = ?`

Обе операции в одной транзакции (`$wpdb->query('START TRANSACTION')` + COMMIT/ROLLBACK). Если транзакция падает в bulk-action, ROLLBACK откатывает только текущую итерацию, цикл продолжается на следующей заявке.

## 4. Архитектура UI

### 4.1 Network admin: редактор словаря статусов

Slug `landing-config-network-lead-statuses` под parent `landing-config-network`, cap `manage_network_options`. Файл `includes/admin-lead-statuses.php`, namespace `LandingConfig\Admin\LeadStatuses`. Шаблон точно как `admin-cta.php`:

- Селектор сегмента сверху (`render_selector` из `segment-selector.php`)
- При segment=0 — список network-default статусов, форма add/edit (поля slug/label/color/order), кнопка Delete
- При segment=N>0 — список эффективных статусов с бейджами INHERITED (синий) / SITE OVERRIDE (жёлтый), для inherited — кнопка «Override для этого сегмента», для override — кнопка «Удалить override»
- Все form actions → `\network_admin_url('admin-post.php')` (lesson из S2-A.3)
- Два admin_post hooks: `landing_lead_status_save` и `landing_lead_status_delete_override`

### 4.2 Subsite read-only: просмотр эффективных статусов

Slug `landing-config-lead-statuses` под parent `landing-config`, cap `manage_options`. Файл `includes/admin-lead-statuses-readonly.php`, namespace `LandingConfig\Admin\LeadStatusesReadOnly`. Таблица всех эффективных статусов для текущего blog_id с колонками slug/label/color/order/source (inherited/site override) + deep-link на network editor c корректным `&segment=<current_blog_id>`.

### 4.3 Карточка заявки

Slug `landing-config-lead-detail`, под parent `landing-config`, cap `manage_options`. Файл `includes/admin-lead-detail.php`, namespace `LandingConfig\Admin\LeadDetail`. Параметр `?id=N` — id заявки в текущем blog.

Структура страницы:
1. **Заголовок** — «Заявка #N» + большой бейдж текущего статуса (label, color из vocab)
2. **Данные заявки** — таблица с полями: created_at, name, phone, email, message, source_block, utm_*, ip, user_agent. Read-only.
3. **Кнопка «Сменить статус»** — открывает модальное окно
4. **Timeline** — список истории из `get_status_history($lead_id)`: «<user_name> сменил <from_label> → <to_label> <timestamp>. Комментарий: <comment>». Бейджи from/to цветные.

Модальное окно (через WP-Thickbox или native `<dialog>` — выбор в плане): `<select>` со всеми статусами из vocab, `<textarea>` для комментария, кнопка Save. Submit идёт в `admin-post.php?action=landing_lead_change_status`. Nonce-name: `landing_lead_change_status_<lead_id>`.

Admin-post handler `handle_change_status()`:
1. cap check `manage_options`
2. nonce check
3. sanitize `lead_id` (int), `to_status` (sanitize_key), `comment` (sanitize_textarea_field, может быть пустым)
4. whitelist: `resolve_lead_status($to_status, get_current_blog_id())` — если null, wp_die 400
5. fetch current status из `landing_leads.processed_status` (для `from_status`)
6. transaction: log_status_change + UPDATE landing_leads
7. redirect назад на карточку с `?saved=1`

### 4.4 Расширения списка заявок (admin-leads.php)

Модифицируем существующий `render_page()`:

**Сверху** — subsubsub-табы. Один SQL запрос:
```sql
SELECT processed_status, COUNT(*) FROM landing_leads GROUP BY processed_status
```
Из vocab (list_lead_statuses) строим вкладки в порядке `order`. Первая вкладка «Все (N_total)», далее по vocab «<label> (N)». Активная вкладка определяется по `?status=<slug>`. При status=all (default) — выбираются все строки.

**Колонка «Статус»** — между «Email» и «Сообщение». Для каждой строки берём `resolve_lead_status($r['processed_status'], $blog_id)` и рендерим бейдж с label+color. Если статус не найден в vocab (например, после удаления статуса из vocab, но в leads ещё есть старое значение) — серый бейдж с raw slug и иконкой warning.

**Колонка checkbox** — крайняя левая, name=`lead_ids[]`, value=`$r['id']`. Заголовок таблицы — checkbox «выбрать все».

**Колонка «Имя» становится ссылкой** — на `?page=landing-config-lead-detail&id=N`.

**Над таблицей — bulk-action UI**:
```html
<form method="post" action="network_admin_url('admin-post.php')">
  <select name="bulk_action">
    <option value="">— Действие —</option>
    <option value="change_status">Изменить статус</option>
  </select>
  <button type="submit" class="button">Применить</button>
</form>
```

Когда выбрано change_status и кликнули Apply — открывается modal с form-checkboxes пробрасываемыми в hidden inputs, select из vocab и textarea для общего комментария. Submit → `admin-post.php?action=landing_leads_bulk_status`.

**Bulk handler `handle_bulk_status()`**:
1. cap check + nonce check
2. sanitize `lead_ids` (array of int), `to_status` (sanitize_key), `comment` (sanitize_textarea_field)
3. whitelist: resolve_lead_status($to_status, $blog_id) — если null, wp_die
4. fetch current user_id через `get_current_user_id()`
5. цикл по lead_ids: транзакция (log + UPDATE) для каждой
6. redirect на список с `?bulk_updated=<count>`

### 4.5 Seed дефолтных статусов

При первом запуске на свежей установке vocab пустой → табы и dropdown в карточке будут пустые → UX broken. Поэтому в `migrate-to-s2a3.php::maybe_run()` добавляется вызов `seed_default_lead_statuses($main_id)` который идемпотентно создаёт 5 статусов в network:

| slug | label | color | order |
|---|---|---|---|
| pending | Новая | #2271b1 | 10 |
| in_progress | В работе | #dba617 | 20 |
| won | Закрыта успешно | #00a32a | 30 |
| lost | Отказ | #d63638 | 40 |
| spam | Спам | #646970 | 50 |

Идемпотентность: если `list_lead_statuses($main_id)` непустой — функция выходит без действий. Маркер тот же `landing_config_migration_s2a3_cta` (расширяется охват, не плодим новый).

Маркетолог может удалить, переименовать, добавить любые статусы — seed не воссоздаст их повторно. Если все статусы удалены, маркетолог увидит пустой список — это его явное решение.

## 5. Файлы

### Создаются
- `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-statuses.php` — CPT + CRUD
- `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-status-log.php` — таблица helpers
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses.php` — network admin UI
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-statuses-readonly.php` — subsite readonly
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php` — карточка заявки
- `skills/wp-landing-config/tests/test_lead_statuses.php` — unit-тесты CPT
- `skills/wp-landing-config/tests/test_lead_status_log.php` — unit-тесты таблицы

### Модифицируются
- `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` — добавить CREATE TABLE для status_log в install_schema()
- `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` — табы, колонка статуса, checkbox, link на карточку, bulk-action UI + handler
- `skills/wp-landing-config/mu-plugin/landing-config/includes/migrate-to-s2a3.php` — добавить seed_default_lead_statuses, вызвать в maybe_run
- `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` — require'ы новых файлов
- `skills/wp-landing-config/tests/integration/test_s2a3_smoke.sh` — проверка lp_lead_status CPT + новые admin URLs
- `CLAUDE.md` — секция про S2-A.4 после S2-A.3

## 6. Безопасность

- Все state-changing actions через `admin_post_*` hooks (никогда не на GET от пользователя)
- Цепочка в каждом handler: capability check → nonce check → sanitize → whitelist валидация → запись
- Whitelist всех принимаемых slug'ов через `resolve_lead_status()` (vocab — единственный источник истины)
- Все echo пользовательских данных через `esc_html`/`esc_attr`/`esc_url`
- SQL — только prepared statements через `$wpdb->prepare()`
- Bulk-action: транзакция per-lead, ROLLBACK при падении одной не блокирует следующие
- comment поле через `sanitize_textarea_field` (strip tags), при выводе — `esc_html` с nl2br

## 7. Тестирование

### 7.1 Unit-тесты (PHP, моки в tests/fixtures/wp-bootstrap.php)

**test_lead_statuses.php** (~12 ассертов):
- T1: save_lead_status round-trip (slug/label/color/order сохраняются, get возвращает корректно)
- T2: resolve_lead_status network → site cascade (network default + site override по слugу — site выигрывает)
- T3: list_lead_statuses сортирует по order asc
- T4: has_override корректно
- T5: delete_lead_status удаляет
- T6: whitelist валидации в save (некорректный slug → 0)
- T7: update path (post_id передан → wp_update_post, не дубль)

**test_lead_status_log.php** (~10 ассертов):
- T1: log_status_change round-trip (запись создаётся, get_status_history возвращает)
- T2: get_status_history сортирует created_at desc
- T3: log_status_change с from=NULL (первая запись) работает
- T4: log_status_change с invalid to_status (не в vocab) — возвращает 0, в БД нет записи
- T5: log_status_change с пустым comment — сохраняет NULL
- T6: log_status_change с user_id=NULL (системное изменение) — сохраняет NULL

### 7.2 Regression

Полный прогон `tests/test_*.php`. Ожидаем: только pre-existing openssl-failures (5 в test_encryption, 2 в test_integrations, 2 в test_adapter_settings_cascade). Никаких новых падений.

### 7.3 Live smoke

Расширение `tests/integration/test_s2a3_smoke.sh`:
- T7: lp_lead_status CPT registered (count >= 5 после seed-миграции)
- T8: HTTP 200/302 на network admin URL landing-config-network-lead-statuses
- T9: HTTP 200/302 на subsite URL landing-config-lead-statuses
- T10: HTTP 200/302 на subsite URL landing-config-lead-detail?id=1 (если хотя бы одна заявка есть)

### 7.4 UI-тесты

Отложены до боевого сайта (ailexi.ru не используется для ручного UI-тестирования по решению пользователя 2026-05-20). На ailexi.ru проверяем только livenes — что страницы регистрируются и не падают с фаталами.

## 8. Скоуп: что НЕ делаем

Явно вне scope, чтобы не было плавающих границ:

- **CRM sync** (двусторонняя). Требует AdapterInterface::update_status() для каждого из 5 адаптеров + webhook handlers + тесты с real credentials. Отдельный трек.
- **Кастомные статусы на уровне заявки** (не из vocab). Только vocab-defined slug'и.
- **Transitions/FSM** («из won нельзя в pending»). Любой статус доступен любой заявке.
- **Уведомления при смене статуса** (email, slack, Telegram).
- **Назначение ответственного на заявку** (assignee).
- **Per-user permissions** на конкретные переходы.
- **AJAX inline-смена статуса в списке** (только через карточку заявки). Если окажется нужным — отдельная фаза после получения фидбэка.

## 9. Зависимости

- S2-A.3 Network-Admin Unification — готов и в main (после мерджа этой ветки). Используется: cascade resolver, segment selector, миграционный фреймворк, шаблоны admin pages, шаблоны readonly pages.
- Существующая таблица `landing_leads` с колонкой `processed_status` — не меняется.
- Существующий `admin-leads.php` — расширяется (не переписывается).

## 10. План фаз

1. **B19.1** — lp_lead_status CPT (lead-statuses.php) + unit-тесты
2. **B19.2** — landing_lead_status_log таблица + helpers + unit-тесты
3. **B19.3** — Network admin lead-statuses UI + readonly (admin-lead-statuses.php + readonly)
4. **B19.4** — расширения admin-leads.php: табы + колонка статуса + checkbox + ссылка
5. **B19.5** — карточка заявки + модальное окно смены + handler
6. **B19.6** — bulk-action UI + handler с транзакциями
7. **B19.7** — seed-миграция + smoke + docs

Каждая фаза: TDD (RED+GREEN+commit), две стадии code review (spec compliance + code quality), фиксы. После B19.3, B19.5, B19.7 — deploy на ailexi.ru с livenes-проверкой.

## 11. Ссылки

- Backlog: [docs/BACKLOG.md#B19](../BACKLOG.md)
- Зависимость: [docs/superpowers/specs/2026-05-19-s2a3-network-admin-unification-design.md](2026-05-19-s2a3-network-admin-unification-design.md)
- Базовый S2-A: [docs/superpowers/specs/2026-05-19-s2a-landing-config-revised.md](2026-05-19-s2a-landing-config-revised.md)

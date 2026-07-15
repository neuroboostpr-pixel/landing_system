# HybridAutos Lead Backend Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сохранять каждую дошедшую до WordPress заявку до внешних отправок, ставить Email, Telegram, Roistat и CRM в надёжную очередь и давать администратору понятный след для восстановления контакта.

**Architecture:** REST-эндпоинт сначала пишет аудит, затем атомарно сохраняет заявку вместе со снимком плана доставки и создаёт по одной задаче на каждую включённую интеграцию. Фоновый worker (обработчик очереди) берёт задачи через условное обновление в базе, вызывает строго указанную интеграцию и записывает подтверждённый, повторяемый, окончательный или неопределённый результат. Сверка очереди восстанавливает пропущенные задачи только для новых заявок после `cutover_lead_id`; старые заявки никогда не рассылаются автоматически.

**Tech Stack:** PHP 8.1+, WordPress MU-plugin и REST API, MySQL/MariaDB через `$wpdb` и `dbDelta`, WP-Cron плюс системный cron Beget, самостоятельные PHP CLI mock-тесты без внешних библиотек.

## Global Constraints

- Перед production-деплоем обязателен свежий полный backup файлов и базы, SHA-256 manifest и успешная репетиция восстановления на непроизводственной копии.
- GitHub хранит только код; `wp-config.php`, пароли, токены, дампы, логи, uploads и контакты клиентов в Git не попадают.
- До production должны быть опубликованы и сверены remote SHA веток `backup/hybridautos-prod-before-reliability-2026-07-15` и `fix/lead-reliability-observability`, а отдельный private repository `hybridautos-ae` должен содержать актуальную тему и release manifest.
- Все изменения базы только additive: не переименовывать и не удалять столбцы; каждый новый обязательный столбец имеет безопасное значение по умолчанию; старый PHP-код продолжает работать после миграции.
- `DB_VERSION` повышается ровно до `1.1.0`.
- `submission_id` хранится как nullable `CHAR(36)` с уникальным индексом; старый запрос без UUID получает UUID на сервере.
- Активный вызов и блокировка reCAPTCHA удаляются; административные настройки могут временно оставаться, но REST не требует токен и не вызывает Google.
- Контакт считается принятым только после числового `lead_id`; сбой создания очереди после сохранения контакта не превращает ответ в ошибку.
- В `delivery_plan` нет токенов, паролей и URL с секретным ключом: только integration ID, label, adapter type и HMAC-SHA-256 configuration hash.
- Один ряд `landing_lead_log` описывает одну попытку; максимум пять попыток на запланированный канал.
- Автоповтор разрешён только при доказанном отказе до доставки или HTTP 429. Timeout, ошибка чтения, HTTP 5xx и потерянный ответ дают `unknown` без автоматического повтора.
- Состояния очереди строго ограничены: `pending`, `sending`, `success`, `accepted`, `retry_wait`, `failed_permanent`, `unknown`.
- Задержки попыток: первая немедленно, затем `+1 minute`, `+5 minutes`, `+30 minutes`, `+2 hours`; lock lease равен `300` секундам.
- Telegram успешен только при HTTP 200 и JSON `ok=true`, с сохранением `message_id`.
- Roistat успешен при документированном JSON success или точном plain-text `Lead was successfully created`; в payload передаётся `site_lead_id`.
- Email получает `accepted` только когда `wp_mail()` вернул `true`; это не обещание попадания во входящие.
- Worker всегда загружает точный `integration_id`; выбор первой интеграции данного типа запрещён.
- Старые синхронные `send_admin_email()` и `dispatch_all_integrations()` удаляются. Письма отправляет только включённая Email-интеграция, сейчас это `elapova00@gmail.com`.
- Логи скрывают секреты и ограничивают body до 2000 символов.
- Системный cron Beget запускает worker каждую минуту; heartbeat `landing_delivery_last_worker_run` обновляется на каждом запуске.
- Этот план закрывает server-side сохранение, доставку, админку и cron. Browser form lifecycle, CTA registry, first-touch attribution в JavaScript и GTM/Yandex/Google Ads выполняются отдельным планом и остаются обязательным вторым gate перед включением рекламы.

---

## File Structure

| Путь | Ответственность |
|---|---|
| `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php` | Схема `1.1.0`, безопасная additive-миграция, индексы, фиксация `cutover_lead_id`. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php` | Снимок плана доставки, безопасный config hash, постановка и сверка задач, чтение истории, ручной retry. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php` | Atomic claim, lock lease, вызов адаптера, классификация результата, расписание повторов, heartbeat и cron hooks. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php` | Ранний аудит, consent, UUID/idempotency, атомарное сохранение заявки, быстрый ответ после постановки в очередь. |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php` | Единый контракт результата и явная передача настроек выбранной интеграции. |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/DeliveryResponse.php` | Единая безопасная классификация HTTP/WP errors и точный result shape. |
| `skills/wp-landing-config/mu-plugin/landing-config/adapters/{Email,Telegram,Roistat,WhatsApp,AmoCRM,Bitrix24,HubSpot}Adapter.php` | Отправка с точными settings и provider-specific доказательством успеха. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php` | Проверка соединения именно для выбранной integration record. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php` | История каналов и безопасная ручная повторная отправка. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php` | Сводка доставки, состояние heartbeat, корректное удаление связанных delivery rows. |
| `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-audit.php` | Двухшаговое восстановление audit row с явным подтверждением текущего плана доставки. |
| `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php` | Порядок загрузки адаптеров, delivery-модулей, REST и admin-файлов. |
| `skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php` | Управляемая память базы, HTTP, mail, cron и времени для PHP mock-тестов. |
| `skills/wp-landing-config/tests/test_lead_delivery_schema.php` | Контроль additive schema, индексов, preflight и cutover. |
| `skills/wp-landing-config/tests/test_lead_delivery_plan.php` | Снимок плана, скрытие секретов, одна задача на интеграцию, reconciliation. |
| `skills/wp-landing-config/tests/test_adapter_delivery_results.php` | Exact settings и правила Email/Telegram/Roistat/HTTP. |
| `skills/wp-landing-config/tests/test_lead_delivery_worker.php` | Atomic claim, concurrency, retry, timeout, stale lock, config change, heartbeat. |
| `skills/wp-landing-config/tests/test_rest_lead_reliability.php` | Сохранение до доставки, UUID duplicate/conflict, consent, audit и полный attribution. |
| `skills/wp-landing-config/tests/test_lead_delivery_admin.php` | Политика ручного retry и подтверждённое восстановление из audit. |

## Stable Interfaces

Эти имена и типы фиксированы для всех задач плана:

```php
namespace LandingConfig\LeadDelivery;

const CUTOVER_OPTION = 'landing_delivery_cutover_lead_id';
const MAX_ATTEMPTS = 5;
const LOCK_LEASE_SECONDS = 300;
const RETRY_DELAYS = [1 => 0, 2 => 60, 3 => 300, 4 => 1800, 5 => 7200];

function configuration_hash(string $adapter, array $settings): string;
function build_delivery_plan(int $blog_id, ?array $integration_ids = null): array;
function encode_delivery_plan(array $plan): string;
function decode_delivery_plan(?string $json): array;
function enqueue_missing_jobs(int $lead_id, array $plan, ?string $now = null): int;
function reconcile_missing_jobs(int $limit = 100, ?string $now = null): int;
function get_delivery_history(int $lead_id): array;
function get_delivery_summary(array $lead_ids): array;
function manual_retry(
    int $lead_id,
    int $source_attempt_id,
    int $target_integration_id,
    bool $confirm_unknown,
    bool $confirm_current_configuration,
    ?string $now = null
): array;

namespace LandingConfig\LeadDeliveryWorker;

const CRON_HOOK = 'landing_delivery_worker';
const HEARTBEAT_OPTION = 'landing_delivery_last_worker_run';

function claim_due_attempt(?string $now = null): ?array;
function process_attempt(array $attempt, ?string $now = null): string;
function mark_stale_sending_unknown(?string $now = null): int;
function run_worker(int $limit = 20, ?string $now = null): array;
function register_cron(): void;
function run_scheduled_worker(): void;

namespace LandingConfig\Adapters;

interface AdapterInterface {
    public static function name(): string;
    public static function label(): string;
    public static function field_defs(): array;
    public static function field_definitions(): array;
    public static function settings(): array;
    public function send(array $lead, ?array $settings = null): array;
    public function test_connection(?array $settings = null): array;
}
```

Каждый `send()` возвращает один контракт:

```php
[
    'status'        => 'success|accepted|retry_wait|failed_permanent|unknown',
    'response_code' => null,
    'response_body' => '',
    'provider_id'   => null,
    'error'         => null,
    'retry_after'   => null,
]
```

`response_code` имеет тип `?int`, `provider_id` и `error` — `?string`, `retry_after` — `?int`. Адаптер не возвращает `pending` или `sending`: эти состояния принадлежат очереди.

### Task 1: PHP Reliability Test Harness

**Files:**
- Create: `skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php`
- Create: `skills/wp-landing-config/tests/test_lead_reliability_fixture.php`
- Modify: `skills/wp-landing-config/tests/fixtures/wp-bootstrap.php`

**Interfaces:**
- Consumes: существующие WordPress mocks из `wp-bootstrap.php`.
- Produces: `LeadReliabilityWpdb`, `lr_reset_state(): void`, `lr_rows(string $table): array`, `lr_queue_row($row): void`, `lr_queue_results(array $rows): void`, `lr_queue_query_count(int $count): void`, `lr_set_http($response): void`, `lr_set_mail_result(bool $result): void`, `lr_set_now(string $mysql): void`.

- [ ] **Step 1: Write the fixture contract test**

Создать самостоятельный CLI-тест, который проверяет память четырёх таблиц, уникальный UUID, уникальную delivery attempt, управляемый HTTP и atomic query result:

```php
<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';

$failures = 0;
$assert = static function (bool $condition, string $message) use (&$failures): void {
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

lr_reset_state();
global $wpdb;
$leads = $wpdb->get_blog_prefix() . 'landing_leads';
$log = $wpdb->get_blog_prefix() . 'landing_lead_log';

$assert($wpdb->insert($leads, ['submission_id' => '11111111-1111-4111-8111-111111111111']) === 1, 'first UUID inserts');
$assert($wpdb->insert($leads, ['submission_id' => '11111111-1111-4111-8111-111111111111']) === false, 'duplicate UUID is rejected');
$assert(str_contains($wpdb->last_error, 'submission_id'), 'duplicate names submission_id');

$attempt = ['lead_id' => 1, 'adapter' => 'email', 'integration_id' => 7, 'attempt' => 1];
$assert($wpdb->insert($log, $attempt) === 1, 'first delivery attempt inserts');
$assert($wpdb->insert($log, $attempt) === false, 'duplicate delivery attempt is rejected');

lr_queue_query_count(1);
$assert($wpdb->query('UPDATE wp_landing_lead_log SET status=\'sending\' WHERE id=1') === 1, 'claim reports one changed row');
lr_queue_query_count(0);
$assert($wpdb->query('UPDATE wp_landing_lead_log SET status=\'sending\' WHERE id=1') === 0, 'second claim loses race');

lr_set_http(['response' => ['code' => 503], 'body' => 'busy', 'headers' => []]);
$http = wp_remote_post('https://provider.invalid', []);
$assert(wp_remote_retrieve_response_code($http) === 503, 'HTTP response is controllable');

echo $failures === 0 ? "PASS: lead reliability fixture\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
```

- [ ] **Step 2: Run the contract test and confirm the missing fixture**

Run: `php skills/wp-landing-config/tests/test_lead_reliability_fixture.php`

Expected: exit code `255` and an error containing `Failed opening required` for `lead-reliability-bootstrap.php`.

- [ ] **Step 3: Implement the isolated reliability fixture**

Создать fixture, который не меняет поведение старых тестов. Его database mock хранит строки по имени таблицы и намеренно моделирует только SQL-поверхность, используемую delivery-модулями:

```php
<?php
require_once __DIR__ . '/wp-bootstrap.php';

if (!defined('MINUTE_IN_SECONDS')) { define('MINUTE_IN_SECONDS', 60); }
if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }

final class LeadReliabilityWpdb extends MockWpdbInsert {
    public array $tables = [];
    public array $row_queue = [];
    public array $results_queue = [];
    public array $query_count_queue = [];
    public array $query_log = [];
    public string $last_error = '';
    public int $rows_affected = 0;
    private int $next_id = 1;

    public function insert($table, $data, $formats = null) {
        $this->last_error = '';
        $rows = $this->tables[$table] ?? [];
        if (str_ends_with($table, 'landing_leads') && !empty($data['submission_id'])) {
            foreach ($rows as $row) {
                if (($row['submission_id'] ?? null) === $data['submission_id']) {
                    $this->last_error = 'Duplicate entry for submission_id';
                    return false;
                }
            }
        }
        if (str_ends_with($table, 'landing_lead_log')) {
            foreach ($rows as $row) {
                $same = (int)($row['lead_id'] ?? 0) === (int)($data['lead_id'] ?? 0)
                    && (string)($row['adapter'] ?? '') === (string)($data['adapter'] ?? '')
                    && (int)($row['integration_id'] ?? 0) === (int)($data['integration_id'] ?? 0)
                    && (int)($row['attempt'] ?? 0) === (int)($data['attempt'] ?? 0);
                if ($same) {
                    $this->last_error = 'Duplicate entry for delivery_attempt';
                    return false;
                }
            }
        }
        $id = isset($data['id']) ? (int)$data['id'] : $this->next_id++;
        $row = ['id' => $id] + $data;
        $this->tables[$table][] = $row;
        $this->insert_id = $id;
        $this->rows_affected = 1;
        return 1;
    }

    public function update($table, $data, $where, $formats = null, $where_formats = null) {
        $changed = 0;
        foreach ($this->tables[$table] ?? [] as $index => $row) {
            $matches = true;
            foreach ($where as $key => $value) {
                if (($row[$key] ?? null) != $value) { $matches = false; break; }
            }
            if ($matches) {
                $this->tables[$table][$index] = array_merge($row, $data);
                $changed++;
            }
        }
        $this->rows_affected = $changed;
        return $changed;
    }

    public function delete($table, $where, $where_format = null) {
        $before = count($this->tables[$table] ?? []);
        $this->tables[$table] = array_values(array_filter(
            $this->tables[$table] ?? [],
            static function (array $row) use ($where): bool {
                foreach ($where as $key => $value) {
                    if (($row[$key] ?? null) != $value) { return true; }
                }
                return false;
            }
        ));
        $this->rows_affected = $before - count($this->tables[$table]);
        return $this->rows_affected;
    }

    public function get_row($sql, $output = OBJECT) {
        $row = array_shift($this->row_queue);
        if ($row === null) { return null; }
        return $output === ARRAY_A ? (array)$row : (object)$row;
    }

    public function get_results($sql, $output = OBJECT) {
        $rows = array_shift($this->results_queue) ?? [];
        return $output === ARRAY_A ? array_map('get_object_vars', array_map(static fn($r) => (object)$r, $rows)) : array_map(static fn($r) => (object)$r, $rows);
    }

    public function get_var($sql) {
        $row = array_shift($this->row_queue);
        if (is_array($row)) { return reset($row); }
        if (is_object($row)) { $values = get_object_vars($row); return reset($values); }
        return $row;
    }

    public function query($sql) {
        $this->query_log[] = (string)$sql;
        $count = array_shift($this->query_count_queue) ?? 0;
        $this->rows_affected = (int)$count;
        return (int)$count;
    }
}

function lr_reset_state(): void {
    $GLOBALS['wpdb'] = new LeadReliabilityWpdb();
    $GLOBALS['_mock_options'] = [];
    $GLOBALS['_mock_site_meta'] = [];
    $GLOBALS['_mock_dbdelta_calls'] = [];
    $GLOBALS['_mock_inserted_leads'] = [];
    $GLOBALS['_mock_mail_sent'] = [];
    $GLOBALS['_mock_transients'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    $GLOBALS['_lr_http'] = ['response' => ['code' => 200], 'body' => '{"ok":true}', 'headers' => []];
    $GLOBALS['_lr_http_requests'] = [];
    $GLOBALS['_lr_mail_result'] = true;
    $GLOBALS['_lr_now'] = '2026-07-15 12:00:00';
    $GLOBALS['_lr_next_scheduled'] = [];
    $GLOBALS['_lr_uuid_counter'] = 0;
    $GLOBALS['_mock_posts'] = [];
    $GLOBALS['_mock_post_meta'] = [];
    $GLOBALS['_mock_next_post_id'] = 1;
}

function lr_rows(string $table): array { return $GLOBALS['wpdb']->tables[$table] ?? []; }
function lr_queue_row($row): void { $GLOBALS['wpdb']->row_queue[] = $row; }
function lr_queue_results(array $rows): void { $GLOBALS['wpdb']->results_queue[] = $rows; }
function lr_queue_query_count(int $count): void { $GLOBALS['wpdb']->query_count_queue[] = $count; }
function lr_set_http($response): void { $GLOBALS['_lr_http'] = $response; }
function lr_set_mail_result(bool $result): void { $GLOBALS['_lr_mail_result'] = $result; }
function lr_set_now(string $mysql): void { $GLOBALS['_lr_now'] = $mysql; }

function wp_generate_uuid4() {
    $GLOBALS['_lr_uuid_counter']++;
    return 'aaaaaaaa-aaaa-4aaa-8aaa-' . str_pad((string)$GLOBALS['_lr_uuid_counter'], 12, '0', STR_PAD_LEFT);
}
function wp_is_uuid($uuid, $version = null) { return preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i', (string)$uuid) === 1; }
function wp_next_scheduled($hook) { return $GLOBALS['_lr_next_scheduled'][$hook] ?? false; }
function wp_schedule_event($timestamp, $recurrence, $hook, $args = [], $wp_error = false) { $GLOBALS['_lr_next_scheduled'][$hook] = $timestamp; return true; }
function wp_clear_scheduled_hook($hook) { unset($GLOBALS['_lr_next_scheduled'][$hook]); return 1; }
function wp_remote_retrieve_header($response, $header) { return $response['headers'][strtolower($header)] ?? $response['headers'][$header] ?? ''; }
function get_home_url() { return 'https://hybridautos.test'; }
function is_email($value) { return filter_var($value, FILTER_VALIDATE_EMAIL) !== false; }

lr_reset_state();
```

В reliability fixture нельзя повторно объявить уже существующие global functions. Поэтому в `wp-bootstrap.php` сделать четыре обратно совместимых изменения и добавить минимальный `WP_Error` mock:

```php
function wp_mail($to, $subject, $body, $headers = []) {
    $GLOBALS['_mock_mail_sent'][] = compact('to', 'subject', 'body');
    return array_key_exists('_lr_mail_result', $GLOBALS) ? (bool)$GLOBALS['_lr_mail_result'] : true;
}

function wp_remote_post($url, $args) {
    if (array_key_exists('_lr_http', $GLOBALS)) {
        $GLOBALS['_lr_http_requests'][] = compact('url', 'args');
        return $GLOBALS['_lr_http'];
    }
    return ['response' => ['code' => 200], 'body' => '{"ok":true}'];
}

function current_time($fmt, $gmt = false) {
    if (array_key_exists('_lr_now', $GLOBALS)) { return $GLOBALS['_lr_now']; }
    return date('Y-m-d H:i:s');
}

if (!class_exists('WP_Error')) {
    class WP_Error {
        private string $code;
        private string $message;
        public function __construct(string $code = '', string $message = '') { $this->code = $code; $this->message = $message; }
        public function get_error_code(): string { return $this->code; }
        public function get_error_message(): string { return $this->message; }
    }
}
function is_wp_error($value) { return $value instanceof WP_Error; }

function add_option($key, $value = '', $deprecated = '', $autoload = 'yes') {
    $bid = get_current_blog_id();
    if (array_key_exists($key, $GLOBALS['_mock_options'][$bid] ?? [])) { return false; }
    $GLOBALS['_mock_options'][$bid][$key] = $value;
    return true;
}
```

Это тестовая инфраструктура; production behavior не меняется. Старые tests по-прежнему получают текущую системную дату, успешный mail и HTTP 200, пока reliability fixture не установит `_lr_*` globals.

- [ ] **Step 4: Run fixture and all pre-existing PHP tests**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_reliability_fixture.php
for test in skills/wp-landing-config/tests/test_*.php; do php "$test"; done
```

Expected: fixture печатает `PASS: lead reliability fixture`; каждый существующий файл завершается с exit code `0`, итог shell command имеет exit code `0`.

- [ ] **Step 5: Commit the test infrastructure**

```bash
git add skills/wp-landing-config/tests/fixtures/wp-bootstrap.php \
  skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php \
  skills/wp-landing-config/tests/test_lead_reliability_fixture.php
git commit -m "test: add lead reliability PHP harness"
```

### Task 2: Additive Database 1.1.0 and Cutover Boundary

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`
- Create: `skills/wp-landing-config/tests/test_lead_delivery_schema.php`
- Test: `skills/wp-landing-config/tests/test_db_schema.php`

**Interfaces:**
- Consumes: `$wpdb`, `dbDelta()`, per-blog WordPress options.
- Produces: `LandingConfig\DB\DB_VERSION === '1.1.0'`, `LandingConfig\DB\initialize_delivery_cutover_for_current_blog(): int`, `LandingConfig\DB\verify_delivery_schema_for_current_blog(): bool`, additive columns and exact indexes.

- [ ] **Step 1: Write the failing schema and cutover tests**

В новом тесте вызвать `create_tables_for_current_blog()` и проверить literal schema fragments, затем смоделировать старый сайт с максимальным lead ID `73`:

```php
<?php
require __DIR__ . '/fixtures/lead-reliability-bootstrap.php';
require __DIR__ . '/../mu-plugin/landing-config/includes/db.php';

use const LandingConfig\DB\DB_VERSION;
use function LandingConfig\DB\create_tables_for_current_blog;
use function LandingConfig\DB\initialize_delivery_cutover_for_current_blog;

$failures = 0;
$assert = static function (bool $ok, string $message) use (&$failures): void {
    if (!$ok) { $failures++; fwrite(STDERR, "FAIL: {$message}\n"); }
};

lr_reset_state();
create_tables_for_current_blog();
$sql = implode("\n", $GLOBALS['_mock_dbdelta_calls']);

$assert(DB_VERSION === '1.1.0', 'database version is 1.1.0');
$assert(str_contains($sql, 'submission_id CHAR(36) NULL'), 'nullable UUID exists');
$assert(str_contains($sql, 'UNIQUE KEY submission_id (submission_id)'), 'UUID unique index exists');
$assert(str_contains($sql, 'delivery_plan LONGTEXT NULL'), 'delivery plan exists');
$assert(str_contains($sql, 'UNIQUE KEY delivery_attempt (lead_id, adapter, integration_id, attempt)'), 'attempt unique index exists');
$assert(str_contains($sql, 'KEY status_next_attempt (status, next_attempt_at)'), 'due lookup index exists');

foreach ([
    'landing_url', 'submit_url', 'landing_referrer',
    'gclid', 'gbraid', 'wbraid', 'yclid', 'fbclid', 'msclkid',
    'ym_client_id', 'roistat_visit', 'form_id', 'brand', 'model',
    'cta_key', 'cta_label', 'cta_placement'
] as $column) {
    $assert(substr_count($sql, $column . ' ') >= 2, "{$column} exists in leads and audit");
}

lr_queue_row(['max_id' => 73]);
$cutover = initialize_delivery_cutover_for_current_blog();
$assert($cutover === 74, 'cutover starts after historical lead');
$assert((int)get_option('landing_delivery_cutover_lead_id') === 74, 'cutover is persisted per blog');

lr_queue_row(['max_id' => 999]);
$assert(initialize_delivery_cutover_for_current_blog() === 74, 'cutover never moves on later deploy');

echo $failures === 0 ? "PASS: delivery schema 1.1.0\n" : "FAILURES: {$failures}\n";
exit($failures === 0 ? 0 : 1);
```

Добавить отдельный assertion, что старый insert, содержащий только `lead_id`, `adapter`, `attempt`, `status`, остаётся допустимым благодаря defaults новых log-полей.

- [ ] **Step 2: Run the schema test and confirm the old version fails**

Run: `php skills/wp-landing-config/tests/test_lead_delivery_schema.php`

Expected: non-zero exit and failures `database version is 1.1.0`, `nullable UUID exists`, `attempt unique index exists`.

- [ ] **Step 3: Implement the exact additive schema**

В `db.php` изменить version и добавить в `landing_leads`:

```php
const DB_VERSION = '1.1.0';

// Inside CREATE TABLE landing_leads, before PRIMARY KEY:
submission_id CHAR(36) NULL,
contact_fingerprint CHAR(64) NOT NULL DEFAULT '',
delivery_plan LONGTEXT NULL,
landing_url TEXT NULL,
submit_url TEXT NULL,
landing_referrer TEXT NULL,
gclid VARCHAR(191) NOT NULL DEFAULT '',
gbraid VARCHAR(191) NOT NULL DEFAULT '',
wbraid VARCHAR(191) NOT NULL DEFAULT '',
yclid VARCHAR(191) NOT NULL DEFAULT '',
fbclid VARCHAR(191) NOT NULL DEFAULT '',
msclkid VARCHAR(191) NOT NULL DEFAULT '',
ym_client_id VARCHAR(191) NOT NULL DEFAULT '',
form_id VARCHAR(191) NOT NULL DEFAULT '',
brand VARCHAR(191) NOT NULL DEFAULT '',
model VARCHAR(191) NOT NULL DEFAULT '',
cta_key VARCHAR(191) NOT NULL DEFAULT '',
cta_label VARCHAR(191) NOT NULL DEFAULT '',
cta_placement VARCHAR(191) NOT NULL DEFAULT '',
PRIMARY KEY (id),
UNIQUE KEY submission_id (submission_id),
KEY created_at (created_at),
KEY processed_status (processed_status)
```

`roistat_visit` уже есть и не дублируется. В `landing_lead_audit` добавить `submission_id`, `contact_fingerprint`, все недостающие UTM (`utm_term`, `utm_content`) и тот же полный набор attribution; все новые text/varchar поля nullable или имеют `DEFAULT ''`.

Полностью заменить definition `landing_lead_log` на additive-compatible definition:

```php
$log_sql = "CREATE TABLE $log (
    id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    lead_id BIGINT(20) UNSIGNED NOT NULL,
    adapter VARCHAR(64) NOT NULL DEFAULT '',
    integration_id BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
    integration_label VARCHAR(191) NOT NULL DEFAULT '',
    config_hash CHAR(64) NOT NULL DEFAULT '',
    idempotency_key VARCHAR(191) NOT NULL DEFAULT '',
    attempt INT(11) NOT NULL DEFAULT 1,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    response_code INT(11) NULL,
    response_body TEXT NULL,
    error_text VARCHAR(500) NULL,
    next_attempt_at DATETIME NULL,
    locked_at DATETIME NULL,
    lock_token CHAR(36) NULL,
    finished_at DATETIME NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    provider_id VARCHAR(191) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY delivery_attempt (lead_id, adapter, integration_id, attempt),
    KEY lead_id (lead_id),
    KEY status_next_attempt (status, next_attempt_at)
) $charset;";
```

- [ ] **Step 4: Add preflight, verification, and immutable cutover**

До `dbDelta($log_sql)` на upgrade проверить старые rows:

```php
function assert_delivery_log_can_be_indexed(): void {
    global $wpdb;
    $table = get_lead_log_table_name();
    $exists = $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $table));
    if ($exists !== $table) { return; }
    $has_integration_id = $wpdb->get_var("SHOW COLUMNS FROM {$table} LIKE 'integration_id'") !== null;
    $group = $has_integration_id
        ? 'lead_id, adapter, integration_id, attempt'
        : 'lead_id, adapter, attempt';
    $duplicate = $wpdb->get_row(
        "SELECT {$group}, COUNT(*) AS row_count
         FROM {$table}
         GROUP BY {$group}
         HAVING COUNT(*) > 1
         LIMIT 1",
        ARRAY_A
    );
    if ($duplicate) {
        throw new \RuntimeException('landing_lead_log contains duplicate legacy attempts; migration 1.1.0 stopped before unique index');
    }
}

function initialize_delivery_cutover_for_current_blog(): int {
    $saved = get_option('landing_delivery_cutover_lead_id', false);
    if ($saved !== false) { return (int)$saved; }
    global $wpdb;
    $max = (int)$wpdb->get_var('SELECT MAX(id) AS max_id FROM ' . get_leads_table_name());
    $cutover = $max + 1;
    add_option('landing_delivery_cutover_lead_id', $cutover, '', 'no');
    return (int)get_option('landing_delivery_cutover_lead_id', $cutover);
}

function verify_delivery_schema_for_current_blog(): bool {
    global $wpdb;
    $lead_columns = array_column(
        $wpdb->get_results('SHOW COLUMNS FROM ' . get_leads_table_name(), ARRAY_A),
        'Field'
    );
    $log_columns = array_column(
        $wpdb->get_results('SHOW COLUMNS FROM ' . get_lead_log_table_name(), ARRAY_A),
        'Field'
    );
    foreach (['submission_id', 'delivery_plan'] as $column) {
        if (!in_array($column, $lead_columns, true)) { return false; }
    }
    foreach (['integration_id', 'next_attempt_at', 'locked_at', 'provider_id'] as $column) {
        if (!in_array($column, $log_columns, true)) { return false; }
    }

    $index_rows = $wpdb->get_results('SHOW INDEX FROM ' . get_lead_log_table_name(), ARRAY_A);
    $indexes = [];
    foreach ($index_rows as $row) {
        $name = (string)$row['Key_name'];
        $indexes[$name]['non_unique'] = (int)$row['Non_unique'];
        $indexes[$name]['columns'][(int)$row['Seq_in_index']] = (string)$row['Column_name'];
    }
    foreach ($indexes as &$index) {
        ksort($index['columns']);
        $index['columns'] = array_values($index['columns']);
    }
    unset($index);

    return ($indexes['delivery_attempt']['non_unique'] ?? 1) === 0
        && ($indexes['delivery_attempt']['columns'] ?? []) === ['lead_id', 'adapter', 'integration_id', 'attempt']
        && ($indexes['status_next_attempt']['columns'] ?? []) === ['status', 'next_attempt_at'];
}
```

`maybe_install_or_migrate()` обновляет network option `landing_config_db_version` только после успешного preflight, четырёх `dbDelta`, schema verification и `initialize_delivery_cutover_for_current_blog()` на каждом blog.

Добавить test cases: preflight duplicate бросает `RuntimeException`; verification false не обновляет DB version; multisite сохраняет отдельный cutover на каждом blog.

- [ ] **Step 5: Run schema and legacy tests**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_schema.php
php skills/wp-landing-config/tests/test_db_schema.php
php skills/wp-landing-config/tests/test_rest_lead.php
```

Expected: все три команды завершаются с exit code `0`; новый тест печатает `PASS: delivery schema 1.1.0`.

- [ ] **Step 6: Inspect generated SQL for forbidden destructive changes**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_schema.php
rg -n "DROP (COLUMN|TABLE)|RENAME (COLUMN|TABLE)|ALTER .* NOT NULL" skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
```

Expected: PHP test passes; `rg` prints no matches and exits `1`.

- [ ] **Step 7: Commit the database migration**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/db.php \
  skills/wp-landing-config/tests/test_lead_delivery_schema.php
git commit -m "feat: add lead delivery schema 1.1.0"
```

### Task 3: Immutable Delivery Plan and Durable First Attempts

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php`
- Create: `skills/wp-landing-config/tests/test_lead_delivery_plan.php`
- Read: `skills/wp-landing-config/mu-plugin/landing-config/includes/integrations.php`
- Read: `skills/wp-landing-config/mu-plugin/landing-config/includes/db.php`

**Interfaces:**
- Consumes: `LandingConfig\Integrations\list_integrations(int): array`, `LandingConfig\Integrations\get_integration(int): ?array`, DB table-name helpers and `CUTOVER_OPTION`.
- Produces: all `LandingConfig\LeadDelivery` interfaces listed in Stable Interfaces except `manual_retry()`, which Task 7 completes.

- [ ] **Step 1: Write failing plan, secrecy, enqueue, and reconciliation tests**

Создать две enabled Email integrations с разными IDs/settings и одну disabled Telegram integration. Проверить exact IDs, stable ordering, absence of secrets and one first attempt per enabled integration:

```php
$plan = LandingConfig\LeadDelivery\build_delivery_plan(1);
$assert(array_column($plan, 'integration_id') === [11, 12], 'plan contains exact enabled IDs in ascending order');
$assert(array_column($plan, 'adapter') === ['email', 'email'], 'two integrations of one type remain distinct');
$json = LandingConfig\LeadDelivery\encode_delivery_plan($plan);
$assert(!str_contains($json, 'mail-secret-one'), 'plan hides first secret');
$assert(!str_contains($json, 'mail-secret-two'), 'plan hides second secret');
$assert(preg_match('/^[0-9a-f]{64}$/', $plan[0]['config_hash']) === 1, 'plan stores safe hash');

$created = LandingConfig\LeadDelivery\enqueue_missing_jobs(75, $plan, '2026-07-15 12:00:00');
$assert($created === 2, 'one first attempt per plan entry');
$assert(LandingConfig\LeadDelivery\enqueue_missing_jobs(75, $plan, '2026-07-15 12:00:00') === 0, 'enqueue is idempotent');

$rows = lr_rows('wp_landing_lead_log');
$assert(array_column($rows, 'integration_id') === [11, 12], 'queue preserves exact IDs');
$assert(array_column($rows, 'attempt') === [1, 1], 'first attempts are numbered one');
$assert(array_column($rows, 'status') === ['pending', 'pending'], 'first attempts are immediately due');
```

Добавить reconciliation cases:

1. lead `74` при cutover `75` не получает задач;
2. lead `75` с сохранённым plan и без jobs получает недостающие jobs;
3. lead `76` с одной существующей job получает только вторую;
4. invalid/empty saved plan ничего не создаёт;
5. reconciliation использует JSON из lead, а не список интеграций, активный сегодня.

- [ ] **Step 2: Run and confirm module is absent**

Run: `php skills/wp-landing-config/tests/test_lead_delivery_plan.php`

Expected: non-zero exit with `Failed opening required` for `includes/lead-delivery.php` or `Call to undefined function LandingConfig\LeadDelivery\build_delivery_plan()`.

- [ ] **Step 3: Implement safe plan hashing and deterministic plan building**

В новом файле определить constants и pure helpers:

```php
<?php
namespace LandingConfig\LeadDelivery;

if (!defined('ABSPATH')) { exit; }

const CUTOVER_OPTION = 'landing_delivery_cutover_lead_id';
const MAX_ATTEMPTS = 5;
const LOCK_LEASE_SECONDS = 300;
const RETRY_DELAYS = [1 => 0, 2 => 60, 3 => 300, 4 => 1800, 5 => 7200];

function normalize_for_hash(array $value): array {
    ksort($value, SORT_STRING);
    foreach ($value as $key => $item) {
        if (is_array($item)) { $value[$key] = normalize_for_hash($item); }
    }
    return $value;
}

function configuration_hash(string $adapter, array $settings): string {
    $material = wp_json_encode([
        'adapter' => sanitize_key($adapter),
        'settings' => normalize_for_hash($settings),
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    return hash_hmac('sha256', (string)$material, wp_salt('secure_auth'));
}

function build_delivery_plan(int $blog_id, ?array $integration_ids = null): array {
    $allowed = $integration_ids === null ? null : array_values(array_unique(array_map('intval', $integration_ids)));
    $plan = [];
    foreach (\LandingConfig\Integrations\list_integrations($blog_id) as $integration) {
        $id = (int)$integration['id'];
        if (empty($integration['enabled'])) { continue; }
        if ($allowed !== null && !in_array($id, $allowed, true)) { continue; }
        $adapter = sanitize_key((string)$integration['adapter_type']);
        $plan[] = [
            'integration_id' => $id,
            'integration_label' => sanitize_text_field((string)$integration['label']),
            'adapter' => $adapter,
            'config_hash' => configuration_hash($adapter, (array)$integration['settings']),
        ];
    }
    usort($plan, static fn(array $a, array $b): int => $a['integration_id'] <=> $b['integration_id']);
    return $plan;
}

function encode_delivery_plan(array $plan): string {
    return (string)wp_json_encode(array_values($plan), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
}

function decode_delivery_plan(?string $json): array {
    $decoded = json_decode((string)$json, true);
    if (!is_array($decoded)) { return []; }
    $plan = [];
    foreach ($decoded as $entry) {
        if (!is_array($entry)) { return []; }
        $id = (int)($entry['integration_id'] ?? 0);
        $adapter = sanitize_key((string)($entry['adapter'] ?? ''));
        $hash = strtolower((string)($entry['config_hash'] ?? ''));
        if ($id <= 0 || $adapter === '' || preg_match('/^[0-9a-f]{64}$/', $hash) !== 1) { return []; }
        $plan[] = [
            'integration_id' => $id,
            'integration_label' => sanitize_text_field((string)($entry['integration_label'] ?? '')),
            'adapter' => $adapter,
            'config_hash' => $hash,
        ];
    }
    return $plan;
}
```

HMAC позволяет сравнить настройки, не сохраняя расшифрованные secrets и не раскрывая их через обычный SHA dictionary check.

- [ ] **Step 4: Implement idempotent first-attempt enqueue**

`enqueue_missing_jobs()` для каждой plan entry делает insert attempt `1`; duplicate unique key считается уже существующей задачей, прочая DB error записывается через `error_log()` без plan/settings:

```php
function delivery_idempotency_key(int $lead_id, int $integration_id): string {
    return sprintf('site-lead:%d:%d:%d', get_current_blog_id(), $lead_id, $integration_id);
}

function enqueue_missing_jobs(int $lead_id, array $plan, ?string $now = null): int {
    global $wpdb;
    $table = \LandingConfig\DB\get_lead_log_table_name();
    $now = $now ?: current_time('mysql', true);
    $created = 0;
    foreach ($plan as $entry) {
        $row = [
            'lead_id' => $lead_id,
            'adapter' => $entry['adapter'],
            'integration_id' => (int)$entry['integration_id'],
            'integration_label' => $entry['integration_label'],
            'config_hash' => $entry['config_hash'],
            'idempotency_key' => delivery_idempotency_key($lead_id, (int)$entry['integration_id']),
            'attempt' => 1,
            'status' => 'pending',
            'next_attempt_at' => $now,
            'updated_at' => $now,
        ];
        $inserted = $wpdb->insert($table, $row);
        if ($inserted === 1) { $created++; continue; }
        if (stripos((string)$wpdb->last_error, 'duplicate') !== false) { continue; }
        error_log('[landing-config] delivery enqueue failed for lead ' . $lead_id . ' integration ' . (int)$entry['integration_id']);
    }
    return $created;
}
```

- [ ] **Step 5: Implement cutover-limited reconciliation and read helpers**

`reconcile_missing_jobs()` выбирает до `$limit` leads с `id >= get_option(CUTOVER_OPTION)` и непустым `delivery_plan`, декодирует только сохранённый plan и вызывает `enqueue_missing_jobs()`. Запрос не соединяется с текущим integration post type. `get_delivery_history()` сортирует `attempt ASC, id ASC`; `get_delivery_summary()` одним query возвращает latest terminal status каждого exact `(lead_id, adapter, integration_id)` и маркирует lead ниже cutover как `legacy/untracked`.

Ключевой reconciliation query:

```php
$sql = $wpdb->prepare(
    "SELECT id, delivery_plan
     FROM " . \LandingConfig\DB\get_leads_table_name() . "
     WHERE id >= %d AND delivery_plan IS NOT NULL AND delivery_plan <> ''
     ORDER BY id ASC
     LIMIT %d",
    (int)get_option(CUTOVER_OPTION, PHP_INT_MAX),
    max(1, $limit)
);
```

Добавить test, где current integrations уже изменены, а сохранённый plan содержит старые IDs; reconciliation создаёт только старые IDs.

- [ ] **Step 6: Run plan tests and secret scan**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_plan.php
rg -n "bot_token|access_token|webhook_url|password" skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php
```

Expected: PHP prints `PASS: delivery plan and reconciliation`; `rg` prints no matches and exits `1`.

- [ ] **Step 7: Commit the durable plan layer**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php \
  skills/wp-landing-config/tests/test_lead_delivery_plan.php
git commit -m "feat: persist immutable lead delivery plans"
```

### Task 4: Exact Integration Settings and Provider-Proven Results

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/adapters/DeliveryResponse.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/RoistatAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/AmoCRMAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/Bitrix24Adapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/adapters/HubSpotAdapter.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`
- Create: `skills/wp-landing-config/tests/test_adapter_delivery_results.php`
- Test: `skills/wp-landing-config/tests/test_adapter_settings_cascade.php`

**Interfaces:**
- Consumes: exact decrypted settings returned by `LandingConfig\Integrations\get_integration(int)`.
- Produces: `DeliveryResponse::result()`, `DeliveryResponse::wp_error()`, `DeliveryResponse::http_failure()`, adapter `send(array $lead, ?array $settings = null): array`, adapter `test_connection(?array $settings = null): array`.

- [ ] **Step 1: Write failing exact-settings tests**

Создать две Email integration records и доказать, что explicit settings побеждают первую интеграцию и legacy options:

```php
$adapter = new LandingConfig\Adapters\EmailAdapter();
lr_set_mail_result(true);
$result = $adapter->send(
    ['id' => 91, 'name' => 'Ad Lead', 'phone' => '+971500000001', 'email' => 'buyer@example.com',
     'message' => '', 'source_block' => '', 'utm_source' => 'google', 'utm_medium' => 'cpc',
     'utm_campaign' => 'dubai', 'utm_term' => 'hybrid', 'utm_content' => 'ad-1',
     'landing_url' => 'https://hybridautos.ae/', 'submit_url' => 'https://hybridautos.ae/zeekr/',
     'form_id' => 'zeekr-main', 'brand' => 'Zeekr', 'model' => 'Zeekr 001',
     'cta_key' => 'model-card', 'cta_label' => 'Get offer', 'cta_placement' => 'hero',
     'created_at' => '2026-07-15 12:00:00'],
    ['to' => 'elapova00@gmail.com', 'subject' => 'Новая заявка HybridAutos']
);
$mail = end($GLOBALS['_mock_mail_sent']);
$assert($mail['to'] === 'elapova00@gmail.com', 'exact Email integration is used');
$assert($result['status'] === 'accepted', 'wp_mail true means accepted');
$assert(str_contains($mail['body'], 'utm_source: google'), 'full attribution is visible to sales');
```

Добавить cases:

- explicit empty settings дают `failed_permanent`, а не fallback к первой integration;
- `wp_mail(false)` даёт `retry_wait` и не даёт `accepted`;
- Telegram HTTP 200 + `{"ok":true,"result":{"message_id":456}}` даёт `success` и provider ID `456`;
- Telegram HTTP 200 + `{"ok":false,"error_code":400}` даёт `failed_permanent`;
- Telegram 429 + `parameters.retry_after=90` даёт `retry_wait`, `retry_after=90`;
- Telegram HTTP 200 с malformed body даёт `unknown`;
- Roistat JSON `{"status":"ok"}` и exact plain text `Lead was successfully created` дают `success`;
- Roistat отправляет `site_lead_id` из lead payload;
- cURL error 6 и 7 дают `retry_wait`; cURL error 28 даёт `unknown`;
- любой HTTP 5xx даёт `unknown`; HTTP 401 даёт `failed_permanent`.

- [ ] **Step 2: Run and confirm the interface mismatch**

Run: `php skills/wp-landing-config/tests/test_adapter_delivery_results.php`

Expected: non-zero exit with `Too many arguments to function LandingConfig\Adapters\EmailAdapter::send()` or missing `DeliveryResponse`.

- [ ] **Step 3: Implement the normalized response helper**

Создать `DeliveryResponse.php`:

```php
<?php
namespace LandingConfig\Adapters;

if (!defined('ABSPATH')) { exit; }

final class DeliveryResponse {
    private const STATUSES = ['success', 'accepted', 'retry_wait', 'failed_permanent', 'unknown'];

    public static function result(
        string $status,
        ?int $response_code = null,
        string $response_body = '',
        ?string $provider_id = null,
        ?string $error = null,
        ?int $retry_after = null
    ): array {
        if (!in_array($status, self::STATUSES, true)) {
            throw new \InvalidArgumentException('Unsupported delivery status: ' . $status);
        }
        return [
            'status' => $status,
            'response_code' => $response_code,
            'response_body' => $response_body,
            'provider_id' => $provider_id,
            'error' => $error,
            'retry_after' => $retry_after,
        ];
    }

    public static function wp_error($error): array {
        $message = method_exists($error, 'get_error_message') ? (string)$error->get_error_message() : 'HTTP transport error';
        if (str_contains($message, 'cURL error 6') || str_contains($message, 'cURL error 7')) {
            return self::result('retry_wait', null, '', null, $message);
        }
        return self::result('unknown', null, '', null, $message);
    }

    public static function http_failure(int $code, string $body, ?int $retry_after = null): array {
        if ($code === 429) {
            return self::result('retry_wait', $code, $body, null, 'HTTP 429', max(1, (int)$retry_after));
        }
        if ($code >= 400 && $code < 500) {
            return self::result('failed_permanent', $code, $body, null, 'HTTP ' . $code);
        }
        return self::result('unknown', $code, $body, null, 'HTTP ' . $code);
    }

    public static function retry_after($response): ?int {
        $value = wp_remote_retrieve_header($response, 'retry-after');
        if (is_numeric($value)) { return max(1, (int)$value); }
        return null;
    }
}
```

- [ ] **Step 4: Change the adapter interface without losing direct-call compatibility**

В `AdapterInterface.php` использовать exact signatures:

```php
public function send(array $lead, ?array $settings = null): array;
public function test_connection(?array $settings = null): array;
```

Во всех семи adapters начало обоих методов строится одинаково по смыслу:

```php
$explicit = $settings !== null;
$s = $settings ?? static::settings();
```

Если `$explicit === true`, отсутствующий field считается configuration error и никогда не читается из `landing_config_get()` или `resolve_integration()`. Legacy fallback разрешён только когда caller передал `null`.

В `admin-integrations.php` заменить вызов на exact selected integration:

```php
$result = $adapter->test_connection((array)$integration['settings']);
```

- [ ] **Step 5: Implement Email, Telegram, and Roistat proof rules**

Email завершает `send()` так:

```php
$sent = \wp_mail($to, $subject, $body);
return $sent
    ? DeliveryResponse::result('accepted', null, 'wp_mail returned true')
    : DeliveryResponse::result('retry_wait', null, '', null, 'wp_mail returned false');
```

Email и Telegram body включают `landing_url`, `submit_url`, `landing_referrer`, пять UTM, шесть ad click IDs, `ym_client_id`, `roistat_visit`, `form_id`, `brand`, `model`, `cta_key`, `cta_label`, `cta_placement`; пустые поля пропускаются. Ни один field не добавляется в URL запроса.

Telegram normalization:

```php
if (\is_wp_error($resp)) { return DeliveryResponse::wp_error($resp); }
$code = \wp_remote_retrieve_response_code($resp);
$raw = \wp_remote_retrieve_body($resp);
$body = json_decode($raw, true);
if ($code === 200 && is_array($body) && ($body['ok'] ?? false) === true) {
    return DeliveryResponse::result('success', 200, $raw, (string)($body['result']['message_id'] ?? ''));
}
if (($body['error_code'] ?? $code) === 429) {
    return DeliveryResponse::result(
        'retry_wait',
        429,
        $raw,
        null,
        (string)($body['description'] ?? 'Telegram rate limit'),
        max(1, (int)($body['parameters']['retry_after'] ?? DeliveryResponse::retry_after($resp) ?? 60))
    );
}
if ($code >= 400 || (is_array($body) && ($body['ok'] ?? null) === false)) {
    return DeliveryResponse::http_failure((int)($body['error_code'] ?? $code ?: 400), $raw);
}
return DeliveryResponse::result('unknown', $code, $raw, null, 'Telegram response not confirmed');
```

Roistat payload добавляет top-level `site_lead_id => (string)$lead['site_lead_id']`. В `fields` добавить exact attribution map, удалив только пустые значения:

```php
$payload['fields'] = array_filter([
    'site' => $site_url,
    'source' => $lead['source_block'] ?? 'site',
    'landing_url' => $lead['landing_url'] ?? '',
    'submit_url' => $lead['submit_url'] ?? '',
    'landing_referrer' => $lead['landing_referrer'] ?? '',
    'utm_source' => $lead['utm_source'] ?? '',
    'utm_medium' => $lead['utm_medium'] ?? '',
    'utm_campaign' => $lead['utm_campaign'] ?? '',
    'utm_term' => $lead['utm_term'] ?? '',
    'utm_content' => $lead['utm_content'] ?? '',
    'gclid' => $lead['gclid'] ?? '',
    'gbraid' => $lead['gbraid'] ?? '',
    'wbraid' => $lead['wbraid'] ?? '',
    'yclid' => $lead['yclid'] ?? '',
    'fbclid' => $lead['fbclid'] ?? '',
    'msclkid' => $lead['msclkid'] ?? '',
    'ym_client_id' => $lead['ym_client_id'] ?? '',
    'form_id' => $lead['form_id'] ?? '',
    'brand' => $lead['brand'] ?? '',
    'model' => $lead['model'] ?? '',
    'cta_key' => $lead['cta_key'] ?? '',
    'cta_label' => $lead['cta_label'] ?? '',
    'cta_placement' => $lead['cta_placement'] ?? '',
], static fn($value): bool => $value !== '');
```

Его success check:

```php
$json = json_decode($body, true);
$json_ok = is_array($json) && (($json['status'] ?? '') === 'ok' || ($json['success'] ?? false) === true);
$plain_ok = trim($body) === 'Lead was successfully created';
if ($code >= 200 && $code < 300 && ($json_ok || $plain_ok)) {
    $provider_id = is_array($json) ? (string)($json['id'] ?? $json['lead_id'] ?? '') : null;
    return DeliveryResponse::result('success', $code, $body, $provider_id ?: null);
}
return DeliveryResponse::http_failure($code, $body, DeliveryResponse::retry_after($resp));
```

Malformed 2xx и 5xx проходят отдельной веткой `unknown`, а не `failed_permanent`.

- [ ] **Step 6: Normalize the four dormant CRM adapters**

WhatsApp, AmoCRM, Bitrix24 и HubSpot принимают exact settings и считают success только по provider ID:

| Adapter | Provider proof | `provider_id` |
|---|---|---|
| WhatsApp | HTTP 2xx и непустой `messages[0].id` | `messages[0].id` |
| AmoCRM | HTTP 2xx и непустой `_embedded.leads[0].id` | `_embedded.leads[0].id` |
| Bitrix24 | HTTP 2xx и непустой `result` | `result` |
| HubSpot | HTTP 2xx и непустой `id` | `id` |

Для каждого adapter exact final pattern:

```php
if (\is_wp_error($resp)) { return DeliveryResponse::wp_error($resp); }
$code = \wp_remote_retrieve_response_code($resp);
$raw = \wp_remote_retrieve_body($resp);
$json = json_decode($raw, true);
$provider_id = is_array($json) ? (string)($json['id'] ?? '') : '';
if ($code >= 200 && $code < 300 && $provider_id !== '') {
    return DeliveryResponse::result('success', $code, $raw, $provider_id);
}
if ($code >= 200 && $code < 300) {
    return DeliveryResponse::result('unknown', $code, $raw, null, 'Provider success was not confirmed');
}
return DeliveryResponse::http_failure($code, $raw, DeliveryResponse::retry_after($resp));
```

В WhatsApp/AmoCRM/Bitrix24 заменить только выражение извлечения ID по таблице выше; это четыре полных provider-specific expressions, а не общий 2xx guess.

- [ ] **Step 7: Load the helper before adapters and run all adapter tests**

В `landing-config.php` загрузить `adapters/DeliveryResponse.php` непосредственно перед `AdapterInterface.php`.

Run:

```bash
php skills/wp-landing-config/tests/test_adapter_delivery_results.php
php skills/wp-landing-config/tests/test_adapter_settings_cascade.php
php skills/wp-landing-config/tests/test_integrations.php
```

Expected: все команды exit `0`; новый test prints `PASS: exact adapter delivery results`; mail recipient assertion показывает `elapova00@gmail.com`.

- [ ] **Step 8: Commit exact adapter behavior**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/adapters/DeliveryResponse.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/AdapterInterface.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/EmailAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/TelegramAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/RoistatAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/WhatsAppAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/AmoCRMAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/Bitrix24Adapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/adapters/HubSpotAdapter.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/admin-integrations.php \
  skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
  skills/wp-landing-config/tests/test_adapter_delivery_results.php
git commit -m "feat: use exact integration settings for lead delivery"
```

### Task 5: Atomic Worker, Safe Retries, Reconciliation, and Heartbeat

**Files:**
- Create: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php`
- Create: `skills/wp-landing-config/tests/test_lead_delivery_worker.php`

**Interfaces:**
- Consumes: `LeadDelivery` constants/helpers, `Integrations\get_integration(int)`, adapter result contract.
- Produces: all `LandingConfig\LeadDeliveryWorker` interfaces listed above; `LeadDelivery\redact_log_text(string): string`.

- [ ] **Step 1: Write failing claim and two-worker tests**

Test one due row selected by both workers. Queue database results so worker A conditional UPDATE changes one row and worker B changes zero; assert only worker A receives the attempt:

```php
lr_queue_row(['id' => 301]);
lr_queue_query_count(1);
lr_queue_row([
    'id' => 301, 'lead_id' => 75, 'adapter' => 'email', 'integration_id' => 11,
    'integration_label' => 'Elapova', 'config_hash' => str_repeat('a', 64),
    'idempotency_key' => 'site-lead:1:75:11', 'attempt' => 1,
    'status' => 'sending', 'lock_token' => 'aaaaaaaa-aaaa-4aaa-8aaa-000000000001'
]);
$a = LandingConfig\LeadDeliveryWorker\claim_due_attempt('2026-07-15 12:00:00');

lr_queue_row(['id' => 301]);
lr_queue_query_count(0);
$b = LandingConfig\LeadDeliveryWorker\claim_due_attempt('2026-07-15 12:00:00');

$assert((int)$a['id'] === 301, 'winner receives claimed row');
$assert($b === null, 'loser does not send duplicate');
```

Проверить SQL, переданный в mock, либо сохранить его в fixture как `query_log`: он содержит `status IN ('pending','retry_wait')`, `finished_at IS NULL`, due time, selected `id`, old status и `locked_at` lease condition.

- [ ] **Step 2: Write failing result-policy tests**

Добавить cases:

- Email `accepted` is terminal and never selected again;
- Telegram/Roistat `success` stores provider ID and is terminal;
- first safe failure finishes attempt 1 as `retry_wait` and inserts attempt 2 due `12:01:00`;
- attempt 2 safe failure inserts attempt 3 due `+5 minutes`;
- provider 429 with `retry_after=600` schedules later of normal delay and 600 seconds;
- timeout and HTTP 503 finish as `unknown` with no next row;
- attempt 5 safe failure becomes `failed_permanent` with `retry_limit_exhausted`;
- config hash mismatch becomes `failed_permanent/config_changed` without HTTP or mail call;
- missing/disabled integration becomes `failed_permanent/integration_missing_or_disabled`;
- stale `sending` older than 300 seconds becomes `unknown`, not `pending`;
- simulated crash after provider success leaves `sending`, and stale recovery changes it to `unknown`;
- response redaction removes `token`, `key`, `secret`, `Authorization: Bearer` and truncates to 2000 characters;
- `run_worker()` updates heartbeat even when queue is empty;
- reconciliation runs before claim and restores one missing job from the saved plan.

- [ ] **Step 3: Run and confirm worker functions are absent**

Run: `php skills/wp-landing-config/tests/test_lead_delivery_worker.php`

Expected: non-zero exit with missing `lead-delivery-worker.php` or undefined `claim_due_attempt()`.

- [ ] **Step 4: Implement secret-safe logging**

Добавить в `lead-delivery.php`:

```php
function redact_log_text(string $value): string {
    $value = preg_replace('/([?&](?:token|key|secret|access_token|bot_token)=)[^&\s]+/i', '$1[redacted]', $value);
    $value = preg_replace('/(Authorization\s*:\s*Bearer\s+)[^\s]+/i', '$1[redacted]', (string)$value);
    $value = preg_replace('/("(?:token|key|secret|access_token|bot_token)"\s*:\s*")[^"]+/i', '$1[redacted]', (string)$value);
    return mb_substr((string)$value, 0, 2000);
}
```

Worker хранит только результат этой функции в `response_body` и первые 500 символов redacted error в `error_text`.

- [ ] **Step 5: Implement atomic conditional claim**

Создать worker file. Candidate selection и claim:

```php
function claim_due_attempt(?string $now = null): ?array {
    global $wpdb;
    $table = \LandingConfig\DB\get_lead_log_table_name();
    $now = $now ?: current_time('mysql', true);
    $lease_before = gmdate('Y-m-d H:i:s', strtotime($now . ' UTC') - \LandingConfig\LeadDelivery\LOCK_LEASE_SECONDS);

    for ($try = 0; $try < 3; $try++) {
        $candidate = $wpdb->get_row($wpdb->prepare(
            "SELECT id, status FROM {$table}
             WHERE status IN ('pending','retry_wait')
               AND finished_at IS NULL
               AND next_attempt_at <= %s
               AND (locked_at IS NULL OR locked_at < %s)
             ORDER BY next_attempt_at ASC, id ASC
             LIMIT 1",
            $now,
            $lease_before
        ), ARRAY_A);
        if (!$candidate) { return null; }

        $token = wp_generate_uuid4();
        $changed = $wpdb->query($wpdb->prepare(
            "UPDATE {$table}
             SET status='sending', locked_at=%s, lock_token=%s, updated_at=%s
             WHERE id=%d AND status=%s AND finished_at IS NULL
               AND (locked_at IS NULL OR locked_at < %s)",
            $now,
            $token,
            $now,
            (int)$candidate['id'],
            (string)$candidate['status'],
            $lease_before
        ));
        if ($changed !== 1) { continue; }
        return $wpdb->get_row($wpdb->prepare(
            "SELECT * FROM {$table} WHERE id=%d AND lock_token=%s",
            (int)$candidate['id'],
            $token
        ), ARRAY_A) ?: null;
    }
    return null;
}
```

Worker никогда не вызывает adapter, если `$changed !== 1`.

- [ ] **Step 6: Implement exact integration resolution and processing**

`process_attempt()` загружает lead по `lead_id`, exact integration по `integration_id`, проверяет enabled/type/hash, добавляет `$lead['site_lead_id'] = $attempt['idempotency_key']`, создаёт adapter по фиксированной map и вызывает:

```php
$result = $adapter->send($lead, (array)$integration['settings']);
```

Map exact:

```php
[
    'email' => \LandingConfig\Adapters\EmailAdapter::class,
    'telegram' => \LandingConfig\Adapters\TelegramAdapter::class,
    'whatsapp' => \LandingConfig\Adapters\WhatsAppAdapter::class,
    'amocrm' => \LandingConfig\Adapters\AmoCRMAdapter::class,
    'bitrix24' => \LandingConfig\Adapters\Bitrix24Adapter::class,
    'hubspot' => \LandingConfig\Adapters\HubSpotAdapter::class,
    'roistat' => \LandingConfig\Adapters\RoistatAdapter::class,
]
```

Missing lead, unknown adapter, deleted/disabled integration, adapter mismatch и config hash mismatch завершают текущую row как `failed_permanent`; для hash mismatch exact `error_text` начинается `config_changed:`.

- [ ] **Step 7: Implement one-row-per-attempt retry history**

Для `success`, `accepted`, `failed_permanent`, `unknown` worker ставит `finished_at=$now`, очищает lock и не создаёт row. Для `retry_wait`:

1. current attempted row получает `status='retry_wait'`, `finished_at=$now`, redacted result и `next_attempt_at=$due`;
2. если current attempt меньше 5, вставляется новая row с `attempt+1`, `status='retry_wait'`, `finished_at=NULL`, `next_attempt_at=$due`;
3. worker claims только `retry_wait` rows с `finished_at IS NULL`;
4. если current attempt равен 5, current status меняется на `failed_permanent`, а error получает prefix `retry_limit_exhausted:`.

Due calculation:

```php
$next_attempt = (int)$attempt['attempt'] + 1;
$normal_delay = \LandingConfig\LeadDelivery\RETRY_DELAYS[$next_attempt];
$provider_delay = max(0, (int)($result['retry_after'] ?? 0));
$delay = max($normal_delay, $provider_delay);
$due = gmdate('Y-m-d H:i:s', strtotime($now . ' UTC') + $delay);
```

Insert копирует exact adapter, integration ID/label, config hash и idempotency key; unique constraint превращает повторный scheduler call в no-op.

- [ ] **Step 8: Implement stale locks, reconciliation, worker loop, and heartbeat**

`mark_stale_sending_unknown()` одним conditional UPDATE меняет `sending` с `locked_at < now-300s` на `unknown`, ставит `finished_at`, очищает lock token и пишет `worker_lock_expired_delivery_may_have_succeeded`.

`run_worker()` exact order:

```php
function run_worker(int $limit = 20, ?string $now = null): array {
    $now = $now ?: current_time('mysql', true);
    update_option(HEARTBEAT_OPTION, $now, false);
    $summary = ['reconciled' => 0, 'stale_unknown' => 0, 'claimed' => 0,
        'success' => 0, 'accepted' => 0, 'retry_wait' => 0,
        'failed_permanent' => 0, 'unknown' => 0];
    $summary['stale_unknown'] = mark_stale_sending_unknown($now);
    $summary['reconciled'] = \LandingConfig\LeadDelivery\reconcile_missing_jobs(100, $now);
    for ($i = 0; $i < max(0, $limit); $i++) {
        $attempt = claim_due_attempt($now);
        if ($attempt === null) { break; }
        $summary['claimed']++;
        $status = process_attempt($attempt, $now);
        $summary[$status]++;
    }
    return $summary;
}
```

Каждый adapter call оборачивается `try/catch (\Throwable $e)`: exception после начала send становится `unknown`, потому что внешняя система могла принять данные.

- [ ] **Step 9: Run worker tests twice to catch state leakage**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_worker.php
php skills/wp-landing-config/tests/test_lead_delivery_worker.php
```

Expected: оба запуска печатают `PASS: atomic lead delivery worker` и exit `0`; assertion mail/HTTP call count остаётся `1` в two-worker case.

- [ ] **Step 10: Commit the worker**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php \
  skills/wp-landing-config/tests/test_lead_delivery_worker.php
git commit -m "feat: add atomic lead delivery worker"
```

### Task 6: Idempotent REST Save-Before-Send Endpoint

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php`
- Create: `skills/wp-landing-config/tests/test_rest_lead_reliability.php`
- Modify: `skills/wp-landing-config/tests/test_rest_lead.php`

**Interfaces:**
- Consumes: `build_delivery_plan()`, `encode_delivery_plan()`, `decode_delivery_plan()`, `enqueue_missing_jobs()` and new DB columns.
- Produces: `sanitize_lead_payload(array,string): array`, `contact_fingerprint(string,string): string`, `resolve_submission_id(array): array`, `insert_or_resolve_lead(array): array`, REST response `{ok:true,lead_id:int,delivery_status:'queued'}`.

- [ ] **Step 1: Write failing save-before-send and attribution tests**

Test request contains consent, one exact UUID, phone, Email and every attribution field. Configure all adapters to fail, call `handle_lead()`, and assert:

```php
$response = LandingConfig\REST\handle_lead(new WP_REST_Request($params));
$data = $response->get_data();
$assert($response->get_status() === 200, 'adapter failure does not lose saved lead');
$assert($data['ok'] === true && is_int($data['lead_id']) && $data['lead_id'] > 0, 'positive lead id confirms save');
$assert($data['delivery_status'] === 'queued', 'delivery is asynchronous');
$assert(count(lr_rows('wp_landing_leads')) === 1, 'contact is durable before worker');
$assert(count(lr_rows('wp_landing_lead_log')) === 3, 'one job for Email, Telegram and Roistat');
$assert(count($GLOBALS['_mock_mail_sent']) === 0, 'REST does not synchronously mail');
$assert(count($GLOBALS['_lr_http_requests'] ?? []) === 0, 'REST does not synchronously call providers');
```

For each of these exact fields assert the saved lead and audit row carry its sanitized value:

```php
[
    'landing_url', 'submit_url', 'landing_referrer',
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'gclid', 'gbraid', 'wbraid', 'yclid', 'fbclid', 'msclkid',
    'ym_client_id', 'roistat_visit', 'form_id', 'brand', 'model',
    'cta_key', 'cta_label', 'cta_placement'
]
```

- [ ] **Step 2: Write failing idempotency, race, consent, and reCAPTCHA-removal tests**

Добавить exact cases:

1. повторный POST с UUID и тем же normalized phone/email возвращает исходный `lead_id`, оставляет один lead и два audit rows;
2. unique insert race: pre-check не находит lead, insert получает duplicate, re-read находит исходный lead — результат всё равно duplicate success;
3. тот же UUID с другим phone или email возвращает HTTP `409`, error `submission_conflict`, один lead и два recoverable audit rows;
4. missing UUID получает valid server UUID и сохраняется;
5. malformed UUID возвращает `400 invalid_submission_id` после audit insert;
6. отсутствующий/ложный `pd_consent` возвращает `400 pd_consent_required` и audit `blocked_by=pd_consent`;
7. `recaptcha_token=''`, старый `recaptcha_token='cached-token'` и `lp_recaptcha_enabled=1` никогда не вызывают HTTP и не блокируют;
8. queue insert failure после lead insert сохраняет HTTP 200; saved plan позволяет reconciliation создать rows позже;
9. generic lead insert error возвращает 500 и audit `blocked_by=db_error`;
10. duplicate request does not fire `landing_config_lead_received` twice.

- [ ] **Step 3: Run and confirm current synchronous behavior fails**

Run: `php skills/wp-landing-config/tests/test_rest_lead_reliability.php`

Expected: non-zero exit; failures mention missing `delivery_status`, synchronous mail/HTTP calls, missing consent rejection, and duplicate UUID behavior.

- [ ] **Step 4: Implement bounded sanitization and early audit**

Определить field limits и helpers:

```php
const TEXT_LIMITS = [
    'name' => 191, 'phone' => 64, 'email' => 191, 'message' => 2000, 'source_block' => 191,
    'utm_source' => 191, 'utm_medium' => 191, 'utm_campaign' => 191, 'utm_term' => 191, 'utm_content' => 191,
    'gclid' => 191, 'gbraid' => 191, 'wbraid' => 191, 'yclid' => 191, 'fbclid' => 191, 'msclkid' => 191,
    'ym_client_id' => 191, 'roistat_visit' => 64, 'form_id' => 191, 'brand' => 191, 'model' => 191,
    'cta_key' => 191, 'cta_label' => 191, 'cta_placement' => 191,
];
const URL_FIELDS = ['landing_url', 'submit_url', 'landing_referrer'];

function bounded_text($value, int $limit): string {
    return mb_substr(sanitize_text_field(wp_unslash((string)$value)), 0, $limit);
}

function contact_fingerprint(string $phone, string $email): string {
    $normalized_phone = preg_replace('/\D+/', '', $phone);
    $normalized_email = strtolower(trim($email));
    return hash('sha256', $normalized_phone . '|' . $normalized_email);
}
```

`sanitize_lead_payload()` applies `esc_url_raw()` plus 2048-character limit to URLs, `sanitize_email()` to Email, `sanitize_textarea_field()` to message, and bounded text to other keys. Audit insert runs immediately after `submission_id` normalization and before honeypot, consent, contact or rate-limit decisions.

После audit exact validation order сохраняется: invalid UUID, honeypot, explicit consent, at least one phone/Email, per-IP rate limit, затем atomic insert. Каждый reject вызывает `audit_log_block()` с code `invalid_submission_id`, `honeypot`, `pd_consent`, `validation` или `rate_limit`; существующий rate-limit test остаётся зелёным.

- [ ] **Step 5: Remove active reCAPTCHA and restore explicit consent**

Удалить `verify_recaptcha()` и весь блок, вызывающий Google/threshold. `recaptcha_score` при новом insert всегда `null`; audit может оставить `recaptcha_token_present` только как compatibility evidence, не выполняя token.

Consent exact rule:

```php
$consent = strtolower((string)($params['pd_consent'] ?? ''));
if (!in_array($consent, ['1', 'on', 'yes', 'true'], true)) {
    audit_log_block($audit_id, 'pd_consent', 'explicit consent missing');
    return new \WP_REST_Response(['ok' => false, 'error' => 'pd_consent_required'], 400);
}
```

Business result: reCAPTCHA code cannot silently reject a real ad lead; legal consent remains explicit and unchecked by default on the browser side.

- [ ] **Step 6: Implement UUID normalization and atomic duplicate resolution**

`resolve_submission_id()` returns `['ok'=>true,'submission_id'=><uuid>]` for valid/missing IDs and `['ok'=>false,'submission_id'=><sanitized>]` for malformed input. `insert_or_resolve_lead()`:

```php
function insert_or_resolve_lead(array $data): array {
    global $wpdb;
    $table = \LandingConfig\DB\get_leads_table_name();
    $existing = $wpdb->get_row($wpdb->prepare(
        "SELECT id, contact_fingerprint, delivery_plan FROM {$table} WHERE submission_id=%s LIMIT 1",
        $data['submission_id']
    ), ARRAY_A);
    if ($existing) {
        return hash_equals((string)$existing['contact_fingerprint'], (string)$data['contact_fingerprint'])
            ? ['status' => 'duplicate', 'lead_id' => (int)$existing['id'], 'delivery_plan' => (string)$existing['delivery_plan']]
            : ['status' => 'conflict', 'lead_id' => (int)$existing['id'], 'delivery_plan' => (string)$existing['delivery_plan']];
    }

    $inserted = $wpdb->insert($table, $data);
    if ($inserted === 1) {
        return ['status' => 'created', 'lead_id' => (int)$wpdb->insert_id, 'delivery_plan' => (string)$data['delivery_plan']];
    }
    if (stripos((string)$wpdb->last_error, 'duplicate') !== false) {
        $existing = $wpdb->get_row($wpdb->prepare(
            "SELECT id, contact_fingerprint, delivery_plan FROM {$table} WHERE submission_id=%s LIMIT 1",
            $data['submission_id']
        ), ARRAY_A);
        if ($existing) {
            return hash_equals((string)$existing['contact_fingerprint'], (string)$data['contact_fingerprint'])
                ? ['status' => 'duplicate', 'lead_id' => (int)$existing['id'], 'delivery_plan' => (string)$existing['delivery_plan']]
                : ['status' => 'conflict', 'lead_id' => (int)$existing['id'], 'delivery_plan' => (string)$existing['delivery_plan']];
        }
    }
    return ['status' => 'error', 'lead_id' => 0, 'delivery_plan' => ''];
}
```

`409` detail в audit содержит только `existing_lead_id=<number>` и никогда не копирует чужие contact values в response.

- [ ] **Step 7: Save plan and enqueue without synchronous delivery**

Перед insert:

```php
$plan = \LandingConfig\LeadDelivery\build_delivery_plan(get_current_blog_id());
$data['delivery_plan'] = \LandingConfig\LeadDelivery\encode_delivery_plan($plan);
```

После created/duplicate:

```php
$saved_plan = \LandingConfig\LeadDelivery\decode_delivery_plan($result['delivery_plan']);
\LandingConfig\LeadDelivery\enqueue_missing_jobs($result['lead_id'], $saved_plan, current_time('mysql', true));
audit_log_success($audit_id, $result['lead_id']);
if ($result['status'] === 'created') {
    do_action('landing_config_lead_received', $result['lead_id'], $data);
}
return new \WP_REST_Response([
    'ok' => true,
    'lead_id' => (int)$result['lead_id'],
    'delivery_status' => 'queued',
], 200);
```

Удалить целиком `dispatch_all_integrations()`, `_tg_escape_markdown()`, `_send_telegram()` и `send_admin_email()` из REST file. Очередь является единственным delivery path.

- [ ] **Step 8: Run REST reliability and backward-compatibility tests**

Run:

```bash
php skills/wp-landing-config/tests/test_rest_lead_reliability.php
php skills/wp-landing-config/tests/test_rest_lead.php
rg -n "verify_recaptcha|send_admin_email|dispatch_all_integrations|_send_telegram" skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php
```

Expected: both PHP files exit `0`; new test prints `PASS: idempotent save-before-send REST`; `rg` prints no matches and exits `1`.

- [ ] **Step 9: Commit REST reliability**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/rest-lead.php \
  skills/wp-landing-config/tests/test_rest_lead.php \
  skills/wp-landing-config/tests/test_rest_lead_reliability.php
git commit -m "fix: save leads before external delivery"
```

### Task 7: Administrator Visibility, Controlled Retry, and Audit Recovery

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-audit.php`
- Create: `skills/wp-landing-config/tests/test_lead_delivery_admin.php`
- Test: `skills/wp-landing-config/tests/test_lead_detail_validation.php`

**Interfaces:**
- Consumes: delivery history, exact current integrations, REST insert helper, saved plan.
- Produces: `LeadDelivery\manual_retry(...)`, `LeadDelivery\plan_confirmation_hash(array): string`, `LandingConfig\Admin\LeadAudit\promote_selected_rows(array $audit_ids, bool $confirmed, string $posted_plan_hash): array`, POST action `landing_lead_delivery_retry`, two-step audit promotion and status/heartbeat presentation.

- [ ] **Step 1: Write failing retry-policy tests as an exact case table**

В `test_lead_delivery_admin.php` прогнать этот data table через `manual_retry()`:

```php
$cases = [
    ['source' => 'success',          'confirm_unknown' => false, 'same_hash' => true,  'active_exists' => false, 'attempt' => 1, 'expected' => 'already_delivered'],
    ['source' => 'accepted',         'confirm_unknown' => false, 'same_hash' => true,  'active_exists' => false, 'attempt' => 1, 'expected' => 'already_delivered'],
    ['source' => 'unknown',          'confirm_unknown' => false, 'same_hash' => true,  'active_exists' => false, 'attempt' => 1, 'expected' => 'duplicate_risk_confirmation_required'],
    ['source' => 'unknown',          'confirm_unknown' => true,  'same_hash' => true,  'active_exists' => false, 'attempt' => 1, 'expected' => 'queued'],
    ['source' => 'failed_permanent', 'confirm_unknown' => false, 'same_hash' => false, 'active_exists' => false, 'attempt' => 1, 'expected' => 'configuration_confirmation_required'],
    ['source' => 'failed_permanent', 'confirm_unknown' => false, 'same_hash' => false, 'active_exists' => false, 'attempt' => 1, 'expected' => 'queued'],
    ['source' => 'failed_permanent', 'confirm_unknown' => false, 'same_hash' => true,  'active_exists' => true,  'attempt' => 1, 'expected' => 'active_attempt_exists'],
    ['source' => 'failed_permanent', 'confirm_unknown' => false, 'same_hash' => true,  'active_exists' => false, 'attempt' => 5, 'expected' => 'attempt_limit_reached'],
];
```

Для row с changed hash второй case передаёт `confirm_current_configuration=true`; первый — false. Assert queued row хранит target integration ID, current label/hash, next attempt number и `pending`, но исходный JSON plan в lead не изменяется.

Добавить rebind case: exhausted integration ID `11` разрешает explicit target ID `21` с attempt `1` только после configuration confirmation. Это сохраняет лимит пяти попыток на один planned channel.

- [ ] **Step 2: Write failing audit confirmation and UI-state tests**

Test exact behavior:

```php
$plan = LandingConfig\LeadDelivery\build_delivery_plan(1);
$hash = LandingConfig\LeadDelivery\plan_confirmation_hash($plan);
$assert(strlen($hash) === 64, 'confirmation hash is stable HMAC');
$assert(!str_contains(json_encode($plan), 'secret'), 'confirmation never contains secret settings');

$without_checkbox = LandingConfig\Admin\LeadAudit\promote_selected_rows([501], false, $hash);
$assert($without_checkbox['error'] === 'delivery_plan_confirmation_required', 'silent promotion is blocked');

$changed_hash = LandingConfig\Admin\LeadAudit\promote_selected_rows([501], true, str_repeat('0', 64));
$assert($changed_hash['error'] === 'delivery_plan_changed', 'stale confirmation is blocked');

$promoted = LandingConfig\Admin\LeadAudit\promote_selected_rows([501], true, $hash);
$assert($promoted['promoted'] === 1, 'confirmed audit row becomes a lead');
$assert(count(lr_rows('wp_landing_lead_log')) === count($plan), 'promotion creates the confirmed jobs');
```

Add render assertions with output buffering: lead detail contains labels `Email`, `Telegram`, `Roistat`, `accepted`, `unknown`, provider ID and warning text `Повтор может создать дубль`; list page contains heartbeat warning when timestamp is older than five minutes and red failed count.

- [ ] **Step 3: Run and confirm retry/recovery functions are absent**

Run: `php skills/wp-landing-config/tests/test_lead_delivery_admin.php`

Expected: non-zero exit with undefined `manual_retry()` or `promote_selected_rows()`.

- [ ] **Step 4: Implement manual retry with hard safety gates**

`manual_retry()` exact decision order:

```php
if (in_array($source['status'], ['success', 'accepted'], true)) {
    return ['ok' => false, 'error' => 'already_delivered'];
}
if (!in_array($source['status'], ['retry_wait', 'failed_permanent', 'unknown'], true) || empty($source['finished_at'])) {
    return ['ok' => false, 'error' => 'active_attempt_exists'];
}
if ($source['status'] === 'unknown' && !$confirm_unknown) {
    return ['ok' => false, 'error' => 'duplicate_risk_confirmation_required'];
}
if ($active_attempt_exists) {
    return ['ok' => false, 'error' => 'active_attempt_exists'];
}
if (!$target || empty($target['enabled'])) {
    return ['ok' => false, 'error' => 'target_integration_missing_or_disabled'];
}
$target_hash = configuration_hash((string)$target['adapter_type'], (array)$target['settings']);
$configuration_changed = (int)$target['id'] !== (int)$source['integration_id']
    || !hash_equals((string)$source['config_hash'], $target_hash);
if ($configuration_changed && !$confirm_current_configuration) {
    return ['ok' => false, 'error' => 'configuration_confirmation_required'];
}
```

Затем query получает `MAX(attempt)` для target `(lead_id, adapter, integration_id)`. При значении 5 возвращается `attempt_limit_reached`; новый integration ID начинает с attempt 1. Insert использует current target label/hash, исходный lead ID, новый idempotency key `site-lead:<blog>:<lead>:<target-integration>`, status `pending`, due now. Success result: `['ok'=>true,'error'=>null,'status'=>'queued','attempt_id'=><int>]`.

`plan_confirmation_hash()`:

```php
function plan_confirmation_hash(array $plan): string {
    return hash_hmac('sha256', encode_delivery_plan($plan), wp_salt('nonce'));
}
```

- [ ] **Step 5: Add delivery history and safe retry form to lead detail**

Register:

```php
\add_action('admin_post_landing_lead_delivery_retry', __NAMESPACE__ . '\handle_delivery_retry');
```

History table columns are exact: `Канал`, `Integration ID`, `Попытка`, `Статус`, `Начало`, `Завершение`, `Provider ID`, `HTTP`, `Ошибка`, `Действие`. Badge colors: green `success`, blue `accepted`, amber `pending/retry_wait/sending`, red `failed_permanent`, violet `unknown`.

Retry form appears only for finished `retry_wait`, `failed_permanent`, `unknown`. It carries nonce `landing_lead_delivery_retry_<attempt_id>`, source attempt ID, lead ID and selected target integration ID. Unknown requires an unchecked checkbox:

```html
<label><input type="checkbox" name="confirm_unknown" value="1" required> Повтор может создать дубль во внешней системе; я проверил канал и принимаю риск.</label>
```

Changed/deleted configuration requires a current enabled integration selector and another unchecked checkbox:

```html
<label><input type="checkbox" name="confirm_current_configuration" value="1" required> Отправить через выбранную текущую конфигурацию.</label>
```

Handler проверяет `manage_options`, nonce, целочисленные IDs, вызывает `manual_retry()` и возвращает на detail URL с `delivery_retry=queued` либо safe error code. Ни response body, ни secret не попадают в query string.

- [ ] **Step 6: Add list summary, heartbeat, and complete deletion**

`admin-leads.php` получает summaries одним grouped query через `get_delivery_summary(array_column($rows, 'id'))`. Добавить колонку `Доставка`:

- `Email: accepted`, `Telegram: success`, `Roistat: unknown` показываются отдельными badges;
- lead ниже cutover показывает `legacy/untracked`;
- отсутствие jobs у lead после cutover показывает red `queue_missing`;
- failed/unknown count виден без открытия detail.

Heartbeat banner logic:

```php
$heartbeat = (string)get_option(\LandingConfig\LeadDeliveryWorker\HEARTBEAT_OPTION, '');
$age = $heartbeat === '' ? PHP_INT_MAX : time() - strtotime($heartbeat . ' UTC');
$heartbeat_level = $age <= 120 ? 'success' : ($age <= 300 ? 'warning' : 'error');
```

Messages: `Worker работает`, `Worker задерживается`, `Worker не запускался более 5 минут`. На `error` объяснить: контакт уже сохранён, но внешние уведомления задерживаются.

В bulk и single delete transaction добавить перед удалением lead:

```php
$delivery_table = \LandingConfig\DB\get_lead_log_table_name();
$del_delivery = $wpdb->delete($delivery_table, ['lead_id' => $lead_id], ['%d']);
if ($del_delivery === false) { throw new \RuntimeException('delivery log delete failed: ' . $wpdb->last_error); }
```

Audit rows не удаляются этой кнопкой: они остаются отдельным журналом и управляются site privacy retention process.

- [ ] **Step 7: Replace direct audit promotion with two-step confirmation**

Первый POST больше не inserts leads. Он строит current enabled plan, показывает integration ID, label, adapter и configuration hash prefix (первые 12 hex), но не settings, и отправляет второй POST с:

```html
<input type="hidden" name="action" value="landing_audit_bulk_promote">
<input type="hidden" name="promotion_stage" value="confirm">
<input type="hidden" name="plan_hash" value="<escaped 64-char HMAC>">
<label><input type="checkbox" name="confirm_delivery_plan" value="1" required> Я подтверждаю перечисленные каналы доставки.</label>
```

Second POST rebuilds current plan. `hash_equals(plan_confirmation_hash($current_plan), sanitize_text_field($_POST['plan_hash']))` must pass. Each row with no lead ID receives a server UUID, fingerprint, all attribution columns, saved confirmed plan; `insert_or_resolve_lead()`, audit update and `enqueue_missing_jobs()` run. If plan changed between screens, no rows are promoted and confirmation is rendered again with notice `Список интеграций изменился; проверьте его заново.`

Вынести mutation в testable function с exact guard:

```php
function promote_selected_rows(array $audit_ids, bool $confirmed, string $posted_plan_hash): array {
    $plan = \LandingConfig\LeadDelivery\build_delivery_plan(get_current_blog_id());
    if (!$confirmed) {
        return ['promoted' => 0, 'skipped' => 0, 'error' => 'delivery_plan_confirmation_required'];
    }
    $current_hash = \LandingConfig\LeadDelivery\plan_confirmation_hash($plan);
    if (!preg_match('/^[0-9a-f]{64}$/', $posted_plan_hash) || !hash_equals($current_hash, $posted_plan_hash)) {
        return ['promoted' => 0, 'skipped' => 0, 'error' => 'delivery_plan_changed'];
    }
    return promote_rows_with_confirmed_plan(array_values(array_unique(array_map('intval', $audit_ids))), $plan);
}
```

`promote_rows_with_confirmed_plan()` reads each audit row by ID, skips an existing `lead_id`, copies the exact lead/audit attribution fields defined in Task 6, generates UUID and fingerprint, persists `encode_delivery_plan($plan)`, then enqueues only this `$plan`. It returns exact shape `['promoted'=><int>,'skipped'=><int>,'error'=>null]`.

- [ ] **Step 8: Run admin tests and ensure no unsafe retry action exists**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_admin.php
php skills/wp-landing-config/tests/test_lead_detail_validation.php
rg -n "status.*(success|accepted).*landing_lead_delivery_retry" skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php
```

Expected: both PHP tests exit `0`; new test prints `PASS: lead delivery admin safety`; the final `rg` prints no match because terminal delivered rows render no retry form.

- [ ] **Step 9: Commit administrator recovery tools**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-detail.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/admin-leads.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/admin-lead-audit.php \
  skills/wp-landing-config/tests/test_lead_delivery_admin.php
git commit -m "feat: expose recoverable lead delivery history"
```

### Task 8: Plugin Load Order, Minute Cron, and Full Automated Quality Gate

**Files:**
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/landing-config.php`
- Modify: `skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php`
- Modify: `skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php`
- Modify: `skills/wp-landing-config/tests/test_lead_delivery_worker.php`
- Test: every file matching `skills/wp-landing-config/tests/test_*.php`

**Interfaces:**
- Consumes: adapters, delivery plan, worker, REST and admin modules.
- Produces: recurrence `landing_every_minute`, event `landing_delivery_worker`, one-minute heartbeat and deterministic dependency order.

- [ ] **Step 1: Add failing cron registration assertions**

Extend worker test:

```php
lr_reset_state();
LandingConfig\LeadDeliveryWorker\register_cron();
$assert(wp_next_scheduled('landing_delivery_worker') !== false, 'worker event is scheduled');
$first = wp_next_scheduled('landing_delivery_worker');
LandingConfig\LeadDeliveryWorker\register_cron();
$assert(wp_next_scheduled('landing_delivery_worker') === $first, 'registration is idempotent');

$schedules = LandingConfig\LeadDeliveryWorker\cron_schedules([]);
$assert($schedules['landing_every_minute']['interval'] === 60, 'custom recurrence is one minute');

LandingConfig\LeadDeliveryWorker\run_scheduled_worker();
$assert(get_option('landing_delivery_last_worker_run') === '2026-07-15 12:00:00', 'scheduled run records heartbeat');
```

Add a load-order smoke test that requires `landing-config.php` and asserts classes/functions for all seven adapters, LeadDelivery, Worker and REST are defined without fatal error.

- [ ] **Step 2: Run and confirm cron functions are missing**

Run: `php skills/wp-landing-config/tests/test_lead_delivery_worker.php`

Expected: non-zero exit with undefined `register_cron()` or `cron_schedules()`.

- [ ] **Step 3: Register one-minute WP-Cron acceleration**

In worker file:

```php
function cron_schedules(array $schedules): array {
    $schedules['landing_every_minute'] = [
        'interval' => 60,
        'display' => 'Landing delivery every minute',
    ];
    return $schedules;
}

function register_cron(): void {
    if (!wp_next_scheduled(CRON_HOOK)) {
        wp_schedule_event(time() + 10, 'landing_every_minute', CRON_HOOK);
    }
}

function run_scheduled_worker(): void {
    run_worker(20);
}

add_filter('cron_schedules', __NAMESPACE__ . '\\cron_schedules');
add_action('init', __NAMESPACE__ . '\\register_cron', 20);
add_action(CRON_HOOK, __NAMESPACE__ . '\\run_scheduled_worker');
```

WP-Cron remains an accelerator; Task 9 installs independent Beget system cron, so delivery does not depend on visitors.

- [ ] **Step 4: Make plugin dependency order explicit**

In `landing-config.php`, load in this exact relative order:

```php
require_once LANDING_CONFIG_DIR . '/includes/integrations.php';
require_once LANDING_CONFIG_DIR . '/adapters/DeliveryResponse.php';
require_once LANDING_CONFIG_DIR . '/adapters/AdapterInterface.php';
require_once LANDING_CONFIG_DIR . '/adapters/EmailAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/TelegramAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/WhatsAppAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/AmoCRMAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/Bitrix24Adapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/HubSpotAdapter.php';
require_once LANDING_CONFIG_DIR . '/adapters/RoistatAdapter.php';
require_once LANDING_CONFIG_DIR . '/includes/lead-delivery.php';
require_once LANDING_CONFIG_DIR . '/includes/lead-delivery-worker.php';
require_once LANDING_CONFIG_DIR . '/includes/rest-lead.php';
```

Remove the previous duplicate adapter and REST `require_once` lines. Admin files load only after this block, ensuring detail/audit handlers can call delivery functions.

- [ ] **Step 5: Run syntax check and every PHP mock test**

Run:

```bash
find skills/wp-landing-config/mu-plugin/landing-config -name '*.php' -print0 | xargs -0 -n1 php -l
set -e
for test in skills/wp-landing-config/tests/test_*.php; do php "$test"; done
```

Expected: every syntax line ends `No syntax errors detected`; every test exits `0`; no shell output contains `FAIL` or `Fatal error`.

- [ ] **Step 6: Run focused reliability suite in risk order**

Run:

```bash
php skills/wp-landing-config/tests/test_lead_delivery_schema.php
php skills/wp-landing-config/tests/test_lead_delivery_plan.php
php skills/wp-landing-config/tests/test_adapter_delivery_results.php
php skills/wp-landing-config/tests/test_lead_delivery_worker.php
php skills/wp-landing-config/tests/test_rest_lead_reliability.php
php skills/wp-landing-config/tests/test_lead_delivery_admin.php
```

Expected exact PASS labels, in order:

```text
PASS: delivery schema 1.1.0
PASS: delivery plan and reconciliation
PASS: exact adapter delivery results
PASS: atomic lead delivery worker
PASS: idempotent save-before-send REST
PASS: lead delivery admin safety
```

- [ ] **Step 7: Run static safety scans**

Run:

```bash
rg -n "verify_recaptcha|send_admin_email|dispatch_all_integrations|_send_telegram" skills/wp-landing-config/mu-plugin/landing-config
rg -n -- "->send\(\$lead\)" skills/wp-landing-config/mu-plugin/landing-config
rg -n "DROP (COLUMN|TABLE)|RENAME (COLUMN|TABLE)" skills/wp-landing-config/mu-plugin/landing-config/includes/db.php
git diff --check
```

Expected: first three `rg` commands print no matches and exit `1`; `git diff --check` exits `0` with no output.

- [ ] **Step 8: Commit the wiring and cron hooks**

```bash
git add skills/wp-landing-config/mu-plugin/landing-config/landing-config.php \
  skills/wp-landing-config/mu-plugin/landing-config/includes/lead-delivery-worker.php \
  skills/wp-landing-config/tests/fixtures/lead-reliability-bootstrap.php \
  skills/wp-landing-config/tests/test_lead_delivery_worker.php
git commit -m "feat: schedule reliable lead delivery every minute"
```

### Task 9: Backup, Staging Migration, Controlled Cutover, and Production Evidence

**Files:**
- Create during release outside Git: immutable backup directory under the hosting account home.
- Create during release outside Git: database dump, file archive and SHA-256 manifest.
- Do not modify source files in this task.

**Interfaces:**
- Consumes: tested commits from Tasks 1–8, Beget SSH shell already positioned at the WordPress root, WP-CLI, `/usr/local/bin/php8.3`, `/usr/local/bin/wp-cli.phar`.
- Produces: verified recovery point, staging restore evidence, cron line, migration proof, real lead IDs and per-channel delivery evidence.

- [ ] **Step 1: Verify clean source scope and remote backup commits before touching production**

Run in each local repository:

```bash
git status --short
git fetch origin
git rev-parse backup/hybridautos-prod-before-reliability-2026-07-15
git rev-parse origin/backup/hybridautos-prod-before-reliability-2026-07-15
git rev-parse fix/lead-reliability-observability
git rev-parse origin/fix/lead-reliability-observability
```

Expected: `git status --short` is empty for release-owned files; each local/remote pair prints the same 40-character SHA. Repeat equivalent SHA comparison in private `hybridautos-ae`; its release commit contains the active custom theme and manifest.

- [ ] **Step 2: Create a fresh full production recovery point**

From the production WordPress root over Beget SSH:

```bash
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$HOME/hybridautos-release-$STAMP"
mkdir -m 700 "$BACKUP_DIR"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db export "$BACKUP_DIR/database.sql"
SITE_ROOT="$(pwd)"
SITE_NAME="$(basename "$SITE_ROOT")"
SITE_PARENT="$(dirname "$SITE_ROOT")"
tar -C "$SITE_PARENT" -czf "$BACKUP_DIR/site-files.tgz" "$SITE_NAME"
(cd "$BACKUP_DIR" && sha256sum database.sql site-files.tgz > SHA256SUMS)
chmod 600 "$BACKUP_DIR/database.sql" "$BACKUP_DIR/site-files.tgz" "$BACKUP_DIR/SHA256SUMS"
ln -sfn "$BACKUP_DIR" "$HOME/hybridautos-previous-release"
printf '%s\n' "$BACKUP_DIR"
(cd "$BACKUP_DIR" && sha256sum -c SHA256SUMS)
```

Expected: WP-CLI prints `Success: Exported to`; final line prints one new backup directory; `sha256sum -c "$BACKUP_DIR/SHA256SUMS"` prints `database.sql: OK` and `site-files.tgz: OK`.

Проверить `tar -tzf "$BACKUP_DIR/site-files.tgz" | sed -n '1,20p'`: archive содержит WordPress root, core, `wp-content`, `wp-config.php` и `.htaccess`. Production deployment остаётся заблокирован, если это не полный site archive и одновременно нет свежего полного Beget snapshot.

- [ ] **Step 3: Rehearse restore on a non-production clone**

In the already-created staging clone root, first prove that it is not production, then restore both files and database into a new rehearsal directory that uses the staging database credentials:

```bash
set -euo pipefail
BACKUP_DIR="$(readlink -f "$HOME/hybridautos-previous-release")"
STAGING_SOURCE_ROOT="$(pwd)"
STAGING_HOME="$(/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get home)"
test "$STAGING_HOME" != 'https://hybridautos.ae'
RESTORE_ROOT="$HOME/hybridautos-restore-rehearsal-20260715"
test ! -e "$RESTORE_ROOT"
mkdir -m 700 "$RESTORE_ROOT"
tar -xzf "$BACKUP_DIR/site-files.tgz" -C "$RESTORE_ROOT" --strip-components=1
cp "$STAGING_SOURCE_ROOT/wp-config.php" "$RESTORE_ROOT/wp-config.php"
cd "$RESTORE_ROOT"
(cd "$BACKUP_DIR" && sha256sum -c SHA256SUMS)
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db import "$BACKUP_DIR/database.sql"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar search-replace 'https://hybridautos.ae' "$STAGING_HOME" --all-tables-with-prefix --skip-columns=guid
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option update home "$STAGING_HOME"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option update siteurl "$STAGING_HOME"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar core verify-checksums
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get home
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db check
```

Expected: two checksum `OK` lines, restored `wp-admin`, `wp-includes`, `wp-content`, `wp-config.php`, `Success: Imported from`, WordPress core checksum success, the same non-production `$STAGING_HOME`, and every database table reports `OK`. Point the existing staging vhost temporarily to `$RESTORE_ROOT` or use its Beget clone mapping, then open staging admin and one public page; verify login, one historical lead and active theme. Record timestamp, staging URL, dump checksum and screenshot in the release record. Do not continue if either pre-import or post-import home is `https://hybridautos.ae`.

- [ ] **Step 4: Test migration 1.1.0 and old-code compatibility on staging**

Deploy the new MU-plugin only to staging, then run:

```bash
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar eval '\LandingConfig\DB\maybe_install_or_migrate(); echo \LandingConfig\DB\DB_VERSION, PHP_EOL;'
PREFIX="$(/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db prefix)"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query "SHOW INDEX FROM ${PREFIX}landing_leads WHERE Key_name='submission_id'; SHOW INDEX FROM ${PREFIX}landing_lead_log WHERE Key_name IN ('delivery_attempt','status_next_attempt');"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get landing_delivery_cutover_lead_id
```

Expected: first command prints `1.1.0`; indexes list `submission_id`, `delivery_attempt`, `status_next_attempt`; cutover equals historical `MAX(landing_leads.id)+1` at migration time.

Temporarily run the previous plugin archive against the migrated staging DB and submit an old-format request with no UUID:

```bash
curl -sS -X POST "$(/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get home)/?rest_route=/landing/v1/lead" \
  --data-urlencode 'name=Old format control' \
  --data-urlencode 'phone=+971500000099' \
  --data-urlencode 'pd_consent=1'
```

Expected: HTTP response contains `"ok":true` and a positive `lead_id`; no SQL unknown-column/default error appears in PHP log. Restore the new plugin before continuing.

- [ ] **Step 5: Verify staging queue, retries, stale lock, and two-worker concurrency**

Create one staging lead with new UUID and ad-like attribution. Force only its first Email attempt to return false in the same WP-CLI process, creating attempt 2:

```bash
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar eval '
add_filter("pre_wp_mail", static fn() => false);
$r=\LandingConfig\LeadDeliveryWorker\run_worker(20);
echo wp_json_encode($r), PHP_EOL;
'
```

Expected: summary contains `"retry_wait":1`; delivery table shows finished attempt 1 and unfinished attempt 2 due one minute later. After at least one cron minute, attempt 2 becomes `accepted` and the due queue is empty.

Create a second staging lead, then launch two processes simultaneously:

```bash
printf '1\n2\n' | xargs -P2 -I{} /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar eval '\LandingConfig\LeadDeliveryWorker\run_worker(1);'
```

Expected: exact `(lead_id, adapter, integration_id, attempt)` count is `1`; provider evidence shows one external message for that attempt. Manually age one controlled `sending` test row beyond five minutes and run worker; expected final state is `unknown`, never `pending`.

- [ ] **Step 6: Deploy backward-compatible backend to production with an allow-list**

Upload new files to temporary paths, verify their SHA-256 against the release manifest, then replace only these targets: `landing-config.php`, `includes/db.php`, `includes/rest-lead.php`, `includes/lead-delivery.php`, `includes/lead-delivery-worker.php`, three admin lead files, `includes/admin-integrations.php`, `adapters/DeliveryResponse.php`, `adapters/AdapterInterface.php` and seven adapter files. Never delete the live MU-plugin directory and never use site-wide `--delete`.

Run production migration and health checks:

```bash
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar eval '\LandingConfig\DB\maybe_install_or_migrate(); echo \LandingConfig\DB\DB_VERSION, PHP_EOL;'
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar cron event list --fields=hook,next_run_gmt,recurrence | grep landing_delivery_worker
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get landing_delivery_cutover_lead_id
```

Expected: `1.1.0`, one scheduled `landing_delivery_worker` with recurrence `landing_every_minute`, and a positive immutable cutover.

- [ ] **Step 7: Install and verify independent Beget system cron**

While still in production WordPress root:

```bash
set -euo pipefail
WP_ROOT="$(pwd)"
CRON_LINE="* * * * * cd $WP_ROOT && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar cron event run landing_delivery_worker --due-now --quiet"
CRON_TMP="$(mktemp)"
{ crontab -l 2>/dev/null || true; } | awk '$0 !~ /landing_delivery_worker/' > "$CRON_TMP"
printf '%s\n' "$CRON_LINE" >> "$CRON_TMP"
crontab "$CRON_TMP"
rm -f "$CRON_TMP"
crontab -l | grep 'landing_delivery_worker'
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar cron event run landing_delivery_worker --due-now
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar option get landing_delivery_last_worker_run
```

Expected: exactly one cron line beginning `* * * * *`; manual run prints `Success: Executed the cron event`; heartbeat is current UTC MySQL time. After two minutes, admin heartbeat remains green without a public site visit.

- [ ] **Step 8: Run old-format and new-format production control submissions**

Old cached-client control:

```bash
curl -sS -X POST 'https://hybridautos.ae/?rest_route=/landing/v1/lead' \
  --data-urlencode 'name=Production old format control' \
  --data-urlencode 'phone=+971500000097' \
  --data-urlencode 'pd_consent=1'
```

New client control:

```bash
UUID="$(/usr/local/bin/php8.3 -r 'echo sprintf("%04x%04x-%04x-4%03x-%04x-%04x%04x%04x", random_int(0,65535),random_int(0,65535),random_int(0,65535),random_int(0,4095),random_int(0,16383)|0x8000,random_int(0,65535),random_int(0,65535),random_int(0,65535));')"
curl -sS -X POST 'https://hybridautos.ae/wp-json/landing/v1/lead' \
  --data-urlencode "submission_id=$UUID" \
  --data-urlencode 'name=Production ad-like control' \
  --data-urlencode 'phone=+971500000098' \
  --data-urlencode 'pd_consent=1' \
  --data-urlencode 'landing_url=https://hybridautos.ae/?utm_source=google&utm_medium=cpc&utm_campaign=reliability-control&gclid=test-control' \
  --data-urlencode 'submit_url=https://hybridautos.ae/zeekr/' \
  --data-urlencode 'utm_source=google' \
  --data-urlencode 'utm_medium=cpc' \
  --data-urlencode 'utm_campaign=reliability-control' \
  --data-urlencode 'gclid=test-control' \
  --data-urlencode 'form_id=release-control' \
  --data-urlencode 'brand=Zeekr' \
  --data-urlencode 'model=Zeekr 001' \
  --data-urlencode 'cta_key=release-control' \
  --data-urlencode 'cta_label=Release control' \
  --data-urlencode 'cta_placement=server-check'
```

Expected: each response is exact shape `{"ok":true,"lead_id":<positive integer>,"delivery_status":"queued"}`. Repeat the new request with the same UUID and contact: same `lead_id`, no second lead. Repeat with same UUID and different phone: HTTP `409`, `submission_conflict`, second audit row retained.

- [ ] **Step 9: Verify production contact and delivery evidence**

For each control `lead_id`, verify in WordPress admin and SQL:

```bash
PREFIX="$(/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db prefix)"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query "SELECT id,submission_id,phone,utm_source,utm_medium,utm_campaign,gclid,form_id,brand,model,cta_key FROM ${PREFIX}landing_leads ORDER BY id DESC LIMIT 2;"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query "SELECT lead_id,adapter,integration_id,attempt,status,provider_id,error_text FROM ${PREFIX}landing_lead_log ORDER BY id DESC LIMIT 20;"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar db query "SELECT COUNT(*) AS due_count FROM ${PREFIX}landing_lead_log WHERE status IN ('pending','retry_wait') AND finished_at IS NULL AND next_attempt_at <= UTC_TIMESTAMP();"
```

Expected business evidence:

- contact and complete ad attribution are visible even before notifications;
- Email exact recipient is `elapova00@gmail.com` and status is `accepted`, followed by manual inbox confirmation;
- Telegram is `success` with non-empty `message_id` provider ID;
- Roistat is `success` by JSON/plain-text proof and CRM confirms `site_lead_id`;
- due count becomes `0`; no `sending` lock remains older than five minutes;
- old WordPress admin Email fallback sends nothing; only one Email delivery row exists.

- [ ] **Step 10: Record rollback commands before reopening traffic**

Keep the exact previous plugin archive and manifest path in the release record. Rollback sequence:

```bash
CRON_TMP="$(mktemp)"
{ crontab -l 2>/dev/null || true; } | awk '$0 !~ /landing_delivery_worker/' > "$CRON_TMP"
crontab "$CRON_TMP"
rm -f "$CRON_TMP"
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar eval '\LandingConfig\LeadDeliveryWorker\mark_stale_sending_unknown();'
PREVIOUS_RELEASE_DIR="$(readlink -f "$HOME/hybridautos-previous-release")"
(cd "$PREVIOUS_RELEASE_DIR" && sha256sum -c SHA256SUMS)
ROLLBACK_ROOT="$(mktemp -d)"
tar -xzf "$PREVIOUS_RELEASE_DIR/site-files.tgz" -C "$ROLLBACK_ROOT" --strip-components=1
/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar cache flush
```

Copy the exact allow-listed plugin files named in Step 6 from `$ROLLBACK_ROOT` into the live root with `install -m 0644`; do not copy the whole archive over production and do not use `--delete`. Leave additive DB columns in place. Before any full database restore, export an emergency current dump and preserve/merge `landing_leads`, `landing_lead_audit`, `landing_lead_log`, `landing_lead_status_log`, integration posts/postmeta, and relevant `lp_*`/`landing_*` options. Never reset an ambiguous `sending` row to `pending`.

Expected: rollback rehearsal on staging restores previous code, old-format POST still saves, new columns remain harmless, and no queue worker runs afterward.

- [ ] **Step 11: Enforce the two release gates**

Mark **contact preservation ready** only after Steps 1–10 have stored evidence. Do not mark **advertising analytics ready** from this backend plan. Paid traffic remains off until the separate browser/CTA/attribution/GTM plan proves all six page families, removes the URL-contains-`thank-you` conversion trigger, publishes GTM/Yandex/Google Ads changes and confirms one `lead_success` only after positive numeric `lead_id`.

## Final Self-Review Checklist

- [ ] Every POST that reaches WordPress produces an audit row before validation.
- [ ] Every accepted contact is in `landing_leads` before any Email/Telegram/Roistat/CRM call.
- [ ] Duplicate UUID returns the original lead; conflicting contact gets 409 and remains in audit.
- [ ] reCAPTCHA makes no browser/server execution or blocking decision.
- [ ] Saved plan contains exact IDs/labels/types/HMAC hashes and no secrets.
- [ ] Queue has one first attempt per saved plan entry and reconciliation never uses today’s integration list for an old lead.
- [ ] Historical leads below cutover remain `legacy/untracked` and are not sent.
- [ ] Worker claim requires exactly one conditional UPDATE; stale send becomes `unknown`.
- [ ] Retry delays, five-attempt cap and provider-specific success rules match the design.
- [ ] Email goes only through enabled integration `elapova00@gmail.com`; no admin-address duplicate path remains.
- [ ] Admin shows status/error/provider evidence and blocks unsafe retry by default.
- [ ] Audit promotion requires a current plan HMAC plus explicit unchecked confirmation.
- [ ] System cron and heartbeat work without visitors.
- [ ] Fresh backup, restore rehearsal, GitHub SHA checks and allow-list rollback pass before production.
- [ ] Backend completion is not reported as paid-traffic readiness until the separate browser/analytics gate passes.

## Execution Handoff

Implement Tasks 1–8 with `superpowers:subagent-driven-development`, one fresh implementation agent and one spec/code review gate per task. Run Task 9 only with production authorization and after the owner confirms the fresh backup/restore evidence; production commands change customer-facing systems and therefore are not part of unattended code execution.

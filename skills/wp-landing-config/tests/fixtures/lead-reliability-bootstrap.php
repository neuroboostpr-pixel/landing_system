<?php
require_once __DIR__ . '/wp-bootstrap.php';

if (!defined('MINUTE_IN_SECONDS')) { define('MINUTE_IN_SECONDS', 60); }
if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }

final class LeadReliabilityWpdb extends MockWpdbInsert {
    public array $tables = [];
    public array $results_queue = [];
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
        if (stripos((string) $sql, 'GET_LOCK(') !== false) {
            $this->query_log[] = (string) $sql;
            return !empty($GLOBALS['_lr_force_lock_failure']) ? 0 : 1;
        }
        if (stripos((string) $sql, 'RELEASE_LOCK(') !== false) {
            $this->query_log[] = (string) $sql;
            return 1;
        }
        $row = array_shift($this->row_queue);
        if (is_array($row)) { return reset($row); }
        if (is_object($row)) { $values = get_object_vars($row); return reset($values); }
        return $row;
    }

    public function query($sql) {
        $this->query_log[] = (string)$sql;
        if (preg_match('/INSERT\s+INTO\s+`?([^`\s]+landing_monitor_alerts)`?\s*\(([^)]+)\)\s*VALUES\s*\((.*?)\)\s*ON\s+DUPLICATE/s', (string)$sql, $m)) {
            $table = $m[1];
            $columns = array_map(static fn($v) => trim($v, " `\t\r\n"), explode(',', $m[2]));
            $values = str_getcsv($m[3], ',', "'", '\\');
            $row = [];
            foreach ($columns as $index => $column) {
                $value = trim((string)($values[$index] ?? ''));
                if (strcasecmp($value, 'NULL') === 0) { $value = null; }
                elseif (in_array($column, ['lead_id','integration_id','fingerprint_scope','provider_response_code','occurrence_count','send_attempts'], true)) {
                    $value = (int)$value;
                }
                $row[$column] = $value;
            }
            foreach ($this->tables[$table] ?? [] as $index => $existing) {
                if (($existing['fingerprint'] ?? '') !== ($row['fingerprint'] ?? '')) { continue; }
                $this->tables[$table][$index]['occurrence_count'] = (int)($existing['occurrence_count'] ?? 1) + 1;
                foreach (['last_seen_at','safe_status','safe_category','provider_response_code'] as $field) {
                    $this->tables[$table][$index][$field] = $row[$field] ?? null;
                }
                if (($row['resolution'] ?? '') !== '') {
                    $this->tables[$table][$index]['resolution'] = $row['resolution'];
                    $this->tables[$table][$index]['resolved_at'] = $row['resolved_at'] ?? null;
                }
                $this->insert_id = (int)($existing['id'] ?? 0);
                $this->rows_affected = 2;
                return 2;
            }
            $id = $this->next_id++;
            $row = ['id' => $id] + $row;
            $this->tables[$table][] = $row;
            $this->insert_id = $id;
            $this->rows_affected = 1;
            return 1;
        }
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
    $GLOBALS['_mock_transient_ttls'] = [];
    $GLOBALS['_mock_actions_fired'] = [];
    $GLOBALS['_lr_http'] = ['response' => ['code' => 200], 'body' => '{"ok":true}', 'headers' => []];
    $GLOBALS['_lr_http_requests'] = [];
    unset($GLOBALS['_lr_before_http']);
    $GLOBALS['_lr_mail_result'] = true;
    $GLOBALS['_lr_now'] = '2026-07-15 12:00:00';
    $GLOBALS['_lr_next_scheduled'] = [];
    $GLOBALS['_lr_scheduled_single'] = [];
    $GLOBALS['_lr_spawn_cron_calls'] = [];
    $GLOBALS['_lr_uuid_counter'] = 0;
    $GLOBALS['_lr_force_lock_failure'] = false;
    $GLOBALS['_lr_logged_in'] = false;
    $GLOBALS['_lr_capabilities'] = [];
    $GLOBALS['_lr_valid_nonces'] = [];
    $GLOBALS['_lr_current_user_id'] = 0;
    $GLOBALS['_lr_nonce_actions'] = [];
    $GLOBALS['_lr_redirects'] = [];
    $GLOBALS['_lr_nocache_headers'] = false;
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
function wp_schedule_single_event($timestamp, $hook, $args = [], $wp_error = false) {
    $GLOBALS['_lr_next_scheduled'][$hook] = $timestamp;
    $GLOBALS['_lr_scheduled_single'][] = ['timestamp' => (int)$timestamp, 'hook' => (string)$hook, 'args' => $args];
    return true;
}
function spawn_cron($gmt_time = 0) { $GLOBALS['_lr_spawn_cron_calls'][] = $gmt_time; return true; }
function wp_clear_scheduled_hook($hook) { unset($GLOBALS['_lr_next_scheduled'][$hook]); return 1; }
function wp_remote_retrieve_header($response, $header) { return $response['headers'][strtolower($header)] ?? $response['headers'][$header] ?? ''; }
function get_home_url() { return 'https://hybridautos.test'; }
function is_email($value) { return filter_var($value, FILTER_VALIDATE_EMAIL) !== false; }

lr_reset_state();

<?php
require_once __DIR__ . '/wp-bootstrap.php';

if (!defined('MINUTE_IN_SECONDS')) { define('MINUTE_IN_SECONDS', 60); }
if (!defined('OBJECT')) { define('OBJECT', 'OBJECT'); }

final class LeadReliabilityWpdb extends MockWpdbInsert {
    public array $tables = [];
    public array $results_queue = [];
    public array $col_queue = [];
    private int $next_id = 1;

    public function insert($table, $data, $formats = null) {
        $this->last_query = 'INSERT INTO `' . (string)$table . '`';
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
        $sql = (string)$sql;
        if (!empty($GLOBALS['_lr_execute_monitor_claim_sql'])
            && preg_match('/SELECT\s+\*\s+FROM\s+`?([^`\s]+landing_monitor_alerts)`?.*LIMIT\s+1/is', $sql, $match)) {
            $this->query_log[] = $sql;
            $rows = $this->tables[$match[1]] ?? [];
            preg_match("/telegram_status\s+IN\s+\(([^)]+)\)/i", $sql, $status_match);
            $statuses = isset($status_match[1])
                ? array_map(static fn(string $status): string => trim($status, " '\""), explode(',', $status_match[1]))
                : [];
            preg_match("/incident_kind\s*<>\s*'([^']+)'/i", $sql, $kind_match);
            $excluded_kind = (string)($kind_match[1] ?? '');
            preg_match("/due_at\s*<=\s*'([^']+)'/i", $sql, $due_match);
            $due_cutoff = (string)($due_match[1] ?? '');
            preg_match('/send_attempts\s*<\s*(\d+)/i', $sql, $attempt_match);
            $attempt_limit = isset($attempt_match[1]) ? (int)$attempt_match[1] : PHP_INT_MAX;
            $requires_unresolved = stripos($sql, 'resolved_at IS NULL') !== false;
            $rows = array_values(array_filter($rows, static function (array $row) use (
                $statuses, $excluded_kind, $due_cutoff, $attempt_limit, $requires_unresolved
            ): bool {
                if ($statuses !== [] && !in_array((string)($row['telegram_status'] ?? ''), $statuses, true)) {
                    return false;
                }
                if ($excluded_kind !== '' && (string)($row['incident_kind'] ?? '') === $excluded_kind) {
                    return false;
                }
                if ($requires_unresolved && !empty($row['resolved_at'])) { return false; }
                if ($due_cutoff !== '' && (string)($row['due_at'] ?? '') > $due_cutoff) { return false; }
                return (int)($row['send_attempts'] ?? 0) < $attempt_limit;
            }));
            usort($rows, static fn(array $left, array $right): int =>
                strcmp((string)($left['due_at'] ?? ''), (string)($right['due_at'] ?? ''))
                ?: (int)($left['id'] ?? 0) <=> (int)($right['id'] ?? 0));
            $row = $rows[0] ?? null;
            if (!is_array($row)) { return null; }
            return $output === ARRAY_A ? $row : (object)$row;
        }
        $row = array_shift($this->row_queue);
        if ($row === null) { return null; }
        $row = (array)$row;
        if (preg_match('/^SELECT\s+(.+?)\s+FROM\s+`?[^`\s]*landing_leads`?\s+WHERE\s+submission_id=/i', (string)$sql, $match)) {
            $selected = array_map(
                static fn(string $field): string => trim($field, " `\t\n\r\0\x0B"),
                explode(',', $match[1])
            );
            $row = array_intersect_key($row, array_fill_keys($selected, true));
        }
        return $output === ARRAY_A ? $row : (object)$row;
    }

    public function get_results($sql, $output = OBJECT) {
        $sql = (string)$sql;
        $this->query_log[] = $sql;
        if (str_contains($sql, '/* landing_delivery_catalog */')) {
            $rows = $this->integration_catalog_rows();
            return $output === ARRAY_A ? $rows : array_map(static fn($row) => (object)$row, $rows);
        }
        if (str_contains($sql, '/* landing_delivery_integration */')) {
            preg_match('/WHERE p\.ID=(\d+)/', $sql, $match);
            $rows = $this->integration_catalog_rows((int)($match[1] ?? 0));
            return $output === ARRAY_A ? $rows : array_map(static fn($row) => (object)$row, $rows);
        }
        if (str_contains($sql, 'SELECT integration_id,adapter FROM')
            && preg_match('/WHERE lead_id=(\d+)/', $sql, $match)) {
            $lead_id = (int)$match[1];
            $rows = array_values(array_filter(
                $this->tables[\LandingConfig\DB\get_lead_log_table_name()] ?? [],
                static fn(array $row): bool => (int)($row['lead_id'] ?? 0) === $lead_id
                    && (int)($row['attempt'] ?? 0) === 1
            ));
            $rows = array_map(static fn(array $row): array => [
                'integration_id' => $row['integration_id'] ?? 0,
                'adapter' => $row['adapter'] ?? '',
            ], $rows);
            return $output === ARRAY_A ? $rows : array_map(static fn($row) => (object)$row, $rows);
        }
        $rows = array_shift($this->results_queue) ?? [];
        return $output === ARRAY_A ? array_map('get_object_vars', array_map(static fn($r) => (object)$r, $rows)) : array_map(static fn($r) => (object)$r, $rows);
    }

    private function integration_catalog_rows(?int $only_id = null): array {
        $rows = [];
        foreach ($GLOBALS['_mock_posts'] ?? [] as $id => $post) {
            $post = is_object($post) ? get_object_vars($post) : (array)$post;
            if ($only_id !== null && (int)$id !== $only_id) { continue; }
            if (($post['post_type'] ?? '') !== 'lp_integration' || ($post['post_status'] ?? '') !== 'publish') { continue; }
            if (isset($post['_mock_blog_id']) && (int)$post['_mock_blog_id'] !== get_current_blog_id()) { continue; }
            $meta = $GLOBALS['_mock_post_meta'][$id] ?? [];
            $rows[] = [
                'ID' => (int)$id,
                'post_title' => (string)($post['post_title'] ?? ''),
                'post_type' => (string)($post['post_type'] ?? ''),
                'post_status' => (string)($post['post_status'] ?? ''),
                'adapter_type' => $meta['_lp_int_adapter_type'] ?? '',
                'legacy_adapter_type' => $meta['_lp_int_adapter_name'] ?? '',
                'label' => $meta['_lp_int_label'] ?? '',
                'description' => $meta['_lp_int_description'] ?? '',
                'settings' => $meta['_lp_int_settings'] ?? [],
                'encrypted_fields' => $meta['_lp_int_encrypted_fields'] ?? [],
                'is_network' => $meta['_lp_int_is_network'] ?? '0',
                'enabled' => $meta['_lp_int_enabled'] ?? '0',
            ];
        }
        usort($rows, static fn(array $left, array $right): int => (int)$left['ID'] <=> (int)$right['ID']);
        return $rows;
    }

    public function get_col($sql) {
        $this->query_log[] = (string)$sql;
        return array_shift($this->col_queue) ?? [];
    }

    public function get_var($sql) {
        if (stripos((string) $sql, 'GET_LOCK(') !== false) {
            $this->query_log[] = (string) $sql;
            $pattern = (string)($GLOBALS['_lr_force_lock_failure_pattern'] ?? '');
            $forced = !empty($GLOBALS['_lr_force_lock_failure'])
                && ($pattern === '' || str_contains((string)$sql, $pattern));
            return $forced ? 0 : 1;
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
        if (preg_match(
            '/DELETE\s+FROM\s+`?([^`\s]+landing_monitor_alerts)`?\s+WHERE.*LIMIT\s+1000/is',
            (string)$sql,
            $match
        )) {
            preg_match_all(
                "/'(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})'/",
                (string)$sql,
                $date_matches
            );
            $dates = $date_matches[1] ?? [];
            $cutoff_30 = (string)($dates[0] ?? '');
            $cutoff_90 = (string)($dates[2] ?? '');
            preg_match("/telegram_status\s+NOT\s+IN\s+\(([^)]+)\)/i", (string)$sql, $protected_match);
            $protected_statuses = isset($protected_match[1])
                ? array_map(static fn(string $status): string => trim($status, " '\""), explode(',', $protected_match[1]))
                : [];
            preg_match(
                "/telegram_status='suppressed'\s+AND\s+last_seen_at\s*(<=|>=|<|>)\s*'([^']+)'/i",
                (string)$sql,
                $suppressed_match
            );
            $suppressed_operator = (string)($suppressed_match[1] ?? '');
            $suppressed_cutoff = (string)($suppressed_match[2] ?? '');
            $resolved_excludes_suppressed = preg_match(
                "/telegram_status\s*<>\s*'suppressed'\s+AND\s+resolved_at\s+IS\s+NOT\s+NULL/i",
                (string)$sql
            ) === 1;
            $table = $match[1];
            $deleted = 0;
            $remaining = [];
            foreach ($this->tables[$table] ?? [] as $row) {
                $status = (string)($row['telegram_status'] ?? '');
                $resolved_at = (string)($row['resolved_at'] ?? '');
                $sent_at = (string)($row['sent_at'] ?? '');
                $last_seen_at = (string)($row['last_seen_at'] ?? '');
                $last_response_at = (string)($row['last_response_at'] ?? '');
                $terminal_time = $last_response_at !== '' ? $last_response_at : $last_seen_at;
                $protected = in_array($status, $protected_statuses, true);
                $resolved_expired = $resolved_at !== '' && $resolved_at < $cutoff_30
                    && (!$resolved_excludes_suppressed || $status !== 'suppressed');
                $suppressed_expired = $status === 'suppressed' && $suppressed_cutoff !== '' && match ($suppressed_operator) {
                    '<' => $last_seen_at < $suppressed_cutoff,
                    '<=' => $last_seen_at <= $suppressed_cutoff,
                    '>' => $last_seen_at > $suppressed_cutoff,
                    '>=' => $last_seen_at >= $suppressed_cutoff,
                    default => false,
                };
                $expired = !$protected && (
                    $resolved_expired
                    || ($status === 'sent' && $sent_at !== '' && $sent_at < $cutoff_30)
                    || (in_array($status, ['unknown','failed'], true) && $terminal_time < $cutoff_90)
                    || $suppressed_expired
                );
                if ($expired && $deleted < 1000) {
                    $deleted++;
                    continue;
                }
                $remaining[] = $row;
            }
            $this->tables[$table] = $remaining;
            $this->rows_affected = $deleted;
            return $deleted;
        }
        if (preg_match(
            "/UPDATE\\s+`?([^`\\s]+landing_monitor_alerts)`?\\s+SET\\s+telegram_status='suppressed',"
            . ".*WHERE\\s+.*LIMIT\\s+(\\d+)/is",
            (string)$sql,
            $match
        )) {
            $table = $match[1];
            $limit = max(1, (int)$match[2]);
            preg_match("/telegram_status\s+IN\s+\(([^)]+)\)/i", (string)$sql, $status_match);
            $statuses = isset($status_match[1])
                ? array_map(static fn(string $status): string => trim($status, " '\""), explode(',', $status_match[1]))
                : [];
            preg_match("/incident_kind\\s*=\\s*'([^']+)'/i", (string)$sql, $kind_match);
            $required_kind = (string)($kind_match[1] ?? '');
            $changed = 0;
            foreach ($this->tables[$table] ?? [] as $index => $row) {
                if ($changed >= $limit) { break; }
                if (($required_kind !== '' && ($row['incident_kind'] ?? '') !== $required_kind)
                    || !in_array(($row['telegram_status'] ?? ''), $statuses, true)) {
                    continue;
                }
                $this->tables[$table][$index]['telegram_status'] = 'suppressed';
                $this->tables[$table][$index]['locked_at'] = null;
                $this->tables[$table][$index]['lock_token'] = null;
                $changed++;
            }
            $this->rows_affected = $changed;
            return $changed;
        }
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
                $normalization_suffix =
                    "telegram_status=IF(VALUES(telegram_status)='suppressed','suppressed',telegram_status),"
                    . "locked_at=IF(VALUES(telegram_status)='suppressed',NULL,locked_at),"
                    . "lock_token=IF(VALUES(telegram_status)='suppressed',NULL,lock_token)";
                $normalizes_suppressed = str_ends_with((string)$sql, $normalization_suffix);
                if (($row['telegram_status'] ?? '') === 'suppressed' && $normalizes_suppressed) {
                    $this->tables[$table][$index]['telegram_status'] = 'suppressed';
                    $this->tables[$table][$index]['locked_at'] = null;
                    $this->tables[$table][$index]['lock_token'] = null;
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
    $GLOBALS['_landing_config_schema_runtime_verified'] = true;
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
    $GLOBALS['_lr_force_lock_failure_pattern'] = '';
    $GLOBALS['_lr_execute_monitor_claim_sql'] = false;
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

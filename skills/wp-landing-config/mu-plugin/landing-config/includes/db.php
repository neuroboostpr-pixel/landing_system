<?php
namespace LandingConfig\DB;

if (!defined('ABSPATH')) { exit; }

const DB_VERSION = '1.3.0';
const DB_VERSION_OPTION = 'landing_config_db_version';
const SCHEMA_VERIFIED_OPTION = 'landing_config_schema_verified_version';
const SCHEMA_RECHECK_AFTER_OPTION = 'landing_config_schema_recheck_after';
const SCHEMA_RECHECK_SECONDS = 3600;
const DELIVERY_ROLLOUT_BOUNDARY_OPTION = 'landing_delivery_async_boundary';
const DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION = 'landing_delivery_async_min_lead_id';
const SCHEMA_RUNTIME_REQUEST_STATE_KEY = '_landing_config_schema_runtime_verified';

function set_schema_runtime_verified_for_request(?bool $verified): void {
    if ($verified === null) {
        unset($GLOBALS[SCHEMA_RUNTIME_REQUEST_STATE_KEY]);
        return;
    }
    $GLOBALS[SCHEMA_RUNTIME_REQUEST_STATE_KEY] = $verified;
}

function schema_runtime_is_verified(): bool {
    if (array_key_exists(SCHEMA_RUNTIME_REQUEST_STATE_KEY, $GLOBALS)) {
        return $GLOBALS[SCHEMA_RUNTIME_REQUEST_STATE_KEY] === true;
    }
    return (string)get_site_option(DB_VERSION_OPTION, '') === DB_VERSION
        && (string)get_site_option(SCHEMA_VERIFIED_OPTION, '') === DB_VERSION;
}

/** @return array{current:string,verified:string,recheck_after:int}|null */
function read_schema_runtime_state_from_database(): ?array {
    global $wpdb;
    $keys = [DB_VERSION_OPTION, SCHEMA_VERIFIED_OPTION, SCHEMA_RECHECK_AFTER_OPTION];

    if (is_multisite()) {
        $table = str_replace('`', '', (string)($wpdb->sitemeta ?? (($wpdb->base_prefix ?? 'wp_') . 'sitemeta')));
        $network_id = function_exists('get_current_network_id')
            ? (int)get_current_network_id()
            : max(1, (int)($wpdb->siteid ?? 1));
        $sql = $wpdb->prepare(
            "SELECT meta_key AS option_key,meta_value AS option_value "
            . "/* landing_schema_runtime_state */ FROM `{$table}` "
            . 'WHERE site_id=%d AND meta_key IN (%s,%s,%s)',
            $network_id,
            ...$keys
        );
    } else {
        $table = str_replace('`', '', (string)($wpdb->options ?? (($wpdb->prefix ?? 'wp_') . 'options')));
        $sql = $wpdb->prepare(
            "SELECT option_name AS option_key,option_value AS option_value "
            . "/* landing_schema_runtime_state */ FROM `{$table}` "
            . 'WHERE option_name IN (%s,%s,%s)',
            ...$keys
        );
    }

    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $rows = $wpdb->get_results($sql, ARRAY_A);
    if (!is_array($rows) || (string)($wpdb->last_error ?? '') !== '') { return null; }

    $values = [];
    foreach ($rows as $row) {
        $key = (string)($row['option_key'] ?? '');
        if (!in_array($key, $keys, true) || array_key_exists($key, $values)) { return null; }
        $value = $row['option_value'] ?? '';
        $values[$key] = function_exists('maybe_unserialize') ? maybe_unserialize($value) : $value;
    }
    return [
        'current' => (string)($values[DB_VERSION_OPTION] ?? ''),
        'verified' => (string)($values[SCHEMA_VERIFIED_OPTION] ?? ''),
        'recheck_after' => is_numeric($values[SCHEMA_RECHECK_AFTER_OPTION] ?? null)
            ? (int)$values[SCHEMA_RECHECK_AFTER_OPTION]
            : 0,
    ];
}

function clear_schema_runtime_option_cache(): void {
    if (!function_exists('wp_cache_delete')) { return; }
    $keys = [DB_VERSION_OPTION, SCHEMA_VERIFIED_OPTION, SCHEMA_RECHECK_AFTER_OPTION];
    if (is_multisite()) {
        global $wpdb;
        $network_id = function_exists('get_current_network_id')
            ? (int)get_current_network_id()
            : max(1, (int)($wpdb->siteid ?? 1));
        foreach ($keys as $key) {
            wp_cache_delete($network_id . ':' . $key, 'site-options');
        }
        return;
    }

    // A single-site option can be served from either its individual key or
    // the bulk autoload/notoptions maps, so invalidate all three paths.
    wp_cache_delete('alloptions', 'options');
    wp_cache_delete('notoptions', 'options');
    foreach ($keys as $key) { wp_cache_delete($key, 'options'); }
}

function valid_mysql_utc_timestamp(string $value): bool {
    if (preg_match('/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/', $value) !== 1) { return false; }
    $parsed = \DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new \DateTimeZone('UTC'));
    return $parsed instanceof \DateTimeImmutable && $parsed->format('Y-m-d H:i:s') === $value;
}

/**
 * Mark the first instant at which exact per-integration reservations can be
 * created. Historical rows receive integration_id=0 during dbDelta, so the
 * marker must exist before the new REST intake can save its first lead.
 */
function ensure_delivery_rollout_boundary_for_current_blog(): string {
    $existing = (string)get_option(DELIVERY_ROLLOUT_BOUNDARY_OPTION, '');
    if (valid_mysql_utc_timestamp($existing)) { return $existing; }

    $boundary = function_exists('current_time')
        ? (string)current_time('mysql', true)
        : gmdate('Y-m-d H:i:s');
    if (!valid_mysql_utc_timestamp($boundary)) { $boundary = gmdate('Y-m-d H:i:s'); }

    if (add_option(DELIVERY_ROLLOUT_BOUNDARY_OPTION, $boundary, '', false)) { return $boundary; }
    // Another request may have won the atomic add. Preserve its earlier
    // boundary; replace only a malformed internal value, which remains safe
    // because "now" cannot include historical leads.
    $concurrent = (string)get_option(DELIVERY_ROLLOUT_BOUNDARY_OPTION, '');
    if (valid_mysql_utc_timestamp($concurrent)) { return $concurrent; }
    update_option(DELIVERY_ROLLOUT_BOUNDARY_OPTION, $boundary);
    return $boundary;
}

/**
 * Timestamps from the legacy site were stored in WordPress local time while
 * the worker uses UTC. An immutable id cutover is therefore the authoritative
 * guard that prevents any historical lead from being replayed after rollout.
 */
function ensure_delivery_rollout_min_lead_id_for_current_blog(): int {
    $existing = (int)get_option(DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION, 0);
    if ($existing > 0) { return $existing; }

    global $wpdb;
    $table = str_replace('`', '', get_leads_table_name());
    // A missing table is the legitimate first-install case, while a failed
    // metadata query is not proof that the site is empty. Prove which case we
    // have before attempting MAX(id), otherwise a new install can never create
    // its tables and a database outage could replay historical leads.
    if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
    $found_table = $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $table));
    if ((string)($wpdb->last_error ?? '') !== '') {
        error_log('[landing-config] delivery_cutover_table_probe_failed');
        return 0;
    }

    if ($found_table === null || $found_table === false || $found_table === '') {
        $maximum = 0;
    } elseif ((string)$found_table !== $table) {
        error_log('[landing-config] delivery_cutover_table_probe_mismatch');
        return 0;
    } else {
        // WPDB reports query failures via null/last_error rather than
        // exceptions. Never turn an unreadable existing table into a
        // permanent cutover of 1.
        if (isset($wpdb->last_error)) { $wpdb->last_error = ''; }
        $maximum_raw = $wpdb->get_var("SELECT COALESCE(MAX(id),0) FROM `{$table}`");
        if (($maximum_raw === null || $maximum_raw === false || !is_numeric($maximum_raw))
            || (string)($wpdb->last_error ?? '') !== '') {
            error_log('[landing-config] delivery_cutover_read_failed');
            return 0;
        }
        $maximum = (int)$maximum_raw;
    }
    if ($maximum < 0) {
        error_log('[landing-config] delivery_cutover_read_failed');
        return 0;
    }
    $minimum = max(1, $maximum + 1);
    if (add_option(DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION, (string)$minimum, '', false)) {
        return $minimum;
    }
    $concurrent = (int)get_option(DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION, 0);
    if ($concurrent > 0) { return $concurrent; }
    return update_option(DELIVERY_ROLLOUT_MIN_LEAD_ID_OPTION, (string)$minimum) ? $minimum : 0;
}

function ensure_delivery_rollout_boundaries(): bool {
    if (!is_multisite()) {
        return ensure_delivery_rollout_boundary_for_current_blog() !== ''
            && ensure_delivery_rollout_min_lead_id_for_current_blog() > 0;
    }
    $ok = true;
    foreach (get_sites(['number' => 0]) as $site) {
        switch_to_blog((int)$site->blog_id);
        try {
            $ok = ensure_delivery_rollout_boundary_for_current_blog() !== ''
                && ensure_delivery_rollout_min_lead_id_for_current_blog() > 0
                && $ok;
        }
        finally { restore_current_blog(); }
    }
    return $ok;
}

function get_leads_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_leads';
}

function get_lead_log_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_lead_log';
}

function get_lead_audit_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_lead_audit';
}

function get_form_events_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_form_events';
}

function get_lead_status_log_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_lead_status_log';
}

function get_monitor_alerts_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_monitor_alerts';
}

function schema_migration_lock_name(): string {
    global $wpdb;
    $scope = (string)($wpdb->base_prefix ?? $wpdb->prefix ?? 'wp_');
    if (defined('DB_NAME')) { $scope .= ':' . (string)DB_NAME; }
    return 'landing_schema_' . substr(hash('sha256', $scope), 0, 40);
}

function acquire_schema_migration_lock(): bool {
    global $wpdb;
    $name = schema_migration_lock_name();
    $result = $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)', $name));
    return (string)$result === '1';
}

function release_schema_migration_lock(): void {
    global $wpdb;
    $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', schema_migration_lock_name()));
}

/**
 * Install schema on first run; let dbDelta handle additive column diffs on
 * version bumps. Data migrations (e.g. backfill on schema change) require
 * explicit branches on $current — not currently needed.
 */
function maybe_install_or_migrate(): void {
    set_schema_runtime_verified_for_request(null);
    // This intentionally runs even when the schema version is already current:
    // a partially completed rollout must fail closed rather than replay legacy
    // leads whose migrated delivery rows have integration_id=0.
    if (!ensure_delivery_rollout_boundaries()) {
        error_log('[landing-config] delivery_cutover_marker_failed');
        return;
    }
    $current = get_site_option(DB_VERSION_OPTION, '');
    $verified = (string)get_site_option(SCHEMA_VERIFIED_OPTION, '');
    $recheck_after = (int)get_site_option(SCHEMA_RECHECK_AFTER_OPTION, 0);
    if ($current === DB_VERSION && $verified === DB_VERSION && $recheck_after > time()) {
        set_schema_runtime_verified_for_request(true);
        return;
    }

    // Only one PHP request may perform the expensive live-schema audit or
    // migration. Other visitors keep using the last verified release instead
    // of multiplying metadata queries at the hourly boundary.
    if (!acquire_schema_migration_lock()) { return; }
    try {

    // The values read before GET_LOCK may be stale: another request can finish
    // the migration while this contender is waiting for the lock. Re-read the
    // exact markers while we own it, otherwise the contender repeats all DDL
    // and needlessly extends the fail-closed intake window.
    $locked_state = read_schema_runtime_state_from_database();
    if ($locked_state === null) {
        set_schema_runtime_verified_for_request(false);
        error_log('[landing-config] schema_runtime_state_read_failed');
        return;
    }
    clear_schema_runtime_option_cache();
    $current = $locked_state['current'];
    $verified = $locked_state['verified'];
    $recheck_after = $locked_state['recheck_after'];
    set_schema_runtime_verified_for_request(
        $current === DB_VERSION && $verified === DB_VERSION
    );
    if ($current === DB_VERSION && $verified === DB_VERSION && $recheck_after > time()) {
        return;
    }

    // A controlled hourly recheck catches later schema drift without adding
    // dozens of SHOW metadata queries to every paid-traffic request.
    if ($current === DB_VERSION && schemas_are_ready()) {
        update_site_option(SCHEMA_VERIFIED_OPTION, DB_VERSION);
        update_site_option(SCHEMA_RECHECK_AFTER_OPTION, time() + SCHEMA_RECHECK_SECONDS);
        set_schema_runtime_verified_for_request(true);
        return;
    }
    set_schema_runtime_verified_for_request(false);
    update_site_option(SCHEMA_VERIFIED_OPTION, '');
    update_site_option(SCHEMA_RECHECK_AFTER_OPTION, 0);

    $ok = true;
    // Tables are per-blog (not network-wide) so each audience segment owns its leads — required for data-isolation between subsites.
    if (is_multisite()) {
        // 'number' => 0 means "no limit" in WP_Site_Query.
        $sites = get_sites(['number' => 0]);
        foreach ($sites as $site) {
            switch_to_blog((int)$site->blog_id);
            try {
                create_tables_for_current_blog();
            } catch (\Throwable $e) {
                $ok = false;
            } finally {
                restore_current_blog();
            }
        }
    } else {
        try {
            create_tables_for_current_blog();
        } catch (\Throwable $e) {
            $ok = false;
        }
    }

    if ($ok && schemas_are_ready()) {
        update_site_option(DB_VERSION_OPTION, DB_VERSION);
        update_site_option(SCHEMA_VERIFIED_OPTION, DB_VERSION);
        update_site_option(SCHEMA_RECHECK_AFTER_OPTION, time() + SCHEMA_RECHECK_SECONDS);
        set_schema_runtime_verified_for_request(true);
    } else {
        error_log('[landing-config] schema_migration_failed');
    }
    } finally {
        release_schema_migration_lock();
    }
}

function schemas_are_ready(): bool {
    if (!is_multisite()) { return schema_is_ready_for_current_blog(); }
    $ready = true;
    foreach (get_sites(['number' => 0]) as $site) {
        switch_to_blog((int)$site->blog_id);
        try { $ready = schema_is_ready_for_current_blog() && $ready; }
        finally { restore_current_blog(); }
    }
    return $ready;
}

/**
 * These historical marker functions remain part of the bootstrap contract for
 * older installs. The current schema migration already owns every referenced
 * column/table under one named lock, so marker helpers must never invoke
 * dbDelta independently. They acknowledge completion only after the exact
 * current schema has been verified.
 */
function record_legacy_migration_marker(string $marker): void {
    if (get_site_option($marker) || !schema_runtime_is_verified()) { return; }
    update_site_option($marker, true);
}

function maybe_migrate_b1_pd_consent(): void {
    record_legacy_migration_marker('landing_config_migration_b1_pd_consent');
}

function maybe_migrate_roistat_visit(): void {
    record_legacy_migration_marker('landing_config_migration_roistat_visit');
}

function maybe_migrate_recaptcha_score(): void {
    record_legacy_migration_marker('landing_config_migration_recaptcha_score');
}

function maybe_migrate_lead_audit(): void {
    record_legacy_migration_marker('landing_config_migration_lead_audit');
}

function create_tables_for_current_blog(): void {
    global $wpdb;
    $charset = $wpdb->get_charset_collate();
    $leads = get_leads_table_name();
    $log = get_lead_log_table_name();
    $status_log = get_lead_status_log_table_name();
    $audit = get_lead_audit_table_name();
    $form_events = get_form_events_table_name();
    $alerts = get_monitor_alerts_table_name();

    $leads_sql = "CREATE TABLE $leads (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        submission_id CHAR(36) NULL,
        name VARCHAR(191) NOT NULL DEFAULT '',
        phone VARCHAR(64) NOT NULL DEFAULT '',
        email VARCHAR(191) NOT NULL DEFAULT '',
        message TEXT NULL,
        source_block TEXT NOT NULL,
        utm_source VARCHAR(191) NOT NULL DEFAULT '',
        utm_medium VARCHAR(191) NOT NULL DEFAULT '',
        utm_campaign VARCHAR(191) NOT NULL DEFAULT '',
        utm_term VARCHAR(191) NOT NULL DEFAULT '',
        utm_content VARCHAR(191) NOT NULL DEFAULT '',
        roistat_visit VARCHAR(64) NOT NULL DEFAULT '',
        ip VARCHAR(45) NOT NULL DEFAULT '',
        user_agent TEXT NULL,
        delivery_targets TEXT NULL,
        delivery_reservations_ready TINYINT(1) NOT NULL DEFAULT 0,
        audit_origin_id BIGINT(20) UNSIGNED NULL,
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        pd_consent_granted_at DATETIME NULL,
        recaptcha_score DECIMAL(3,2) NULL,
        PRIMARY KEY (id),
        KEY submission_id (submission_id),
        KEY created_at (created_at),
        KEY delivery_reconcile (delivery_reservations_ready,id),
        UNIQUE KEY audit_origin (audit_origin_id),
        KEY processed_status (processed_status)
    ) $charset;";

    $log_sql = "CREATE TABLE $log (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        lead_id BIGINT(20) UNSIGNED NOT NULL,
        adapter VARCHAR(64) NOT NULL,
        integration_id BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
        attempt INT(11) NOT NULL DEFAULT 1,
        status VARCHAR(32) NOT NULL DEFAULT 'queued',
        response_code INT(11) NULL,
        response_body TEXT NULL,
        error_text VARCHAR(500) NULL,
        next_attempt_at DATETIME NULL,
        locked_at DATETIME NULL,
        finished_at DATETIME NULL,
        provider_id BIGINT(20) UNSIGNED NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY lead_id (lead_id),
        KEY delivery_queue (status,next_attempt_at),
        KEY lead_integration (lead_id,integration_id),
        KEY status_adapter (status, adapter)
    ) $charset;";

    $status_log_sql = "CREATE TABLE $status_log (
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
    ) $charset;";

    $audit_sql = "CREATE TABLE $audit (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        submission_id CHAR(36) NULL,
        ip VARCHAR(45) NOT NULL DEFAULT '',
        user_agent TEXT NULL,
        name VARCHAR(191) NOT NULL DEFAULT '',
        phone VARCHAR(64) NOT NULL DEFAULT '',
        email VARCHAR(191) NOT NULL DEFAULT '',
        message TEXT NULL,
        source_block TEXT NOT NULL,
        utm_source VARCHAR(191) NOT NULL DEFAULT '',
        utm_medium VARCHAR(191) NOT NULL DEFAULT '',
        utm_campaign VARCHAR(191) NOT NULL DEFAULT '',
        utm_term VARCHAR(191) NOT NULL DEFAULT '',
        utm_content VARCHAR(191) NOT NULL DEFAULT '',
        roistat_visit VARCHAR(64) NOT NULL DEFAULT '',
        pd_consent VARCHAR(8) NOT NULL DEFAULT '',
        recaptcha_token_present TINYINT(1) NOT NULL DEFAULT 0,
        blocked_by VARCHAR(64) NULL COMMENT 'NULL=ok, иначе: honeypot|rate_limit|pd_consent|recaptcha_failed|validation|db_error',
        block_detail VARCHAR(255) NULL,
        lead_id BIGINT(20) UNSIGNED NULL COMMENT 'id в landing_leads если заявка сохранена',
        PRIMARY KEY (id),
        KEY submission_id (submission_id),
        KEY created_at (created_at),
        KEY blocked_by (blocked_by),
        KEY lead_id (lead_id)
    ) $charset;";

    // Deliberately contains only anonymous workflow metadata. Contact fields,
    // raw network identifiers, referrers and full URLs do not belong here.
    $form_events_sql = "CREATE TABLE $form_events (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        submission_id CHAR(36) NOT NULL,
        event_sequence SMALLINT UNSIGNED NULL,
        event_name VARCHAR(32) NOT NULL,
        event_detail VARCHAR(32) NOT NULL DEFAULT '',
        form_id VARCHAR(100) NOT NULL DEFAULT '',
        brand VARCHAR(100) NOT NULL DEFAULT '',
        cta_key VARCHAR(100) NOT NULL DEFAULT '',
        page_path VARCHAR(255) NOT NULL DEFAULT '',
        utm_source VARCHAR(191) NOT NULL DEFAULT '',
        utm_medium VARCHAR(191) NOT NULL DEFAULT '',
        utm_campaign VARCHAR(191) NOT NULL DEFAULT '',
        PRIMARY KEY (id),
        KEY submission_id (submission_id),
        KEY submission_sequence (submission_id,event_sequence),
        KEY event_name (event_name),
        KEY created_at (created_at)
    ) $charset;";

    $alerts_sql = "CREATE TABLE $alerts (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        fingerprint CHAR(64) NOT NULL,
        incident_kind VARCHAR(32) NOT NULL,
        severity VARCHAR(16) NOT NULL,
        submission_id CHAR(36) NULL,
        lead_id BIGINT(20) UNSIGNED NULL,
        integration_id BIGINT(20) UNSIGNED NULL,
        fingerprint_scope BIGINT(20) UNSIGNED NOT NULL DEFAULT 0,
        adapter VARCHAR(64) NOT NULL DEFAULT '',
        safe_status VARCHAR(32) NOT NULL DEFAULT '',
        safe_category VARCHAR(64) NOT NULL DEFAULT '',
        provider_response_code SMALLINT UNSIGNED NULL,
        occurrence_count INT UNSIGNED NOT NULL DEFAULT 1,
        first_seen_at DATETIME NOT NULL,
        last_seen_at DATETIME NOT NULL,
        due_at DATETIME NOT NULL,
        locked_at DATETIME NULL,
        lock_token CHAR(36) NULL,
        sent_at DATETIME NULL,
        resolved_at DATETIME NULL,
        resolution VARCHAR(32) NOT NULL DEFAULT '',
        telegram_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        send_attempts SMALLINT UNSIGNED NOT NULL DEFAULT 0,
        last_response_at DATETIME NULL,
        telegram_response_code SMALLINT UNSIGNED NULL,
        telegram_message_id BIGINT(20) UNSIGNED NULL,
        PRIMARY KEY (id),
        UNIQUE KEY fingerprint (fingerprint),
        KEY queue_due (telegram_status,resolved_at,due_at),
        KEY submission_id (submission_id),
        KEY lead_integration (lead_id,integration_id)
    ) $charset;";

    if (!function_exists('dbDelta')) {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    }
    dbDelta($leads_sql);
    dbDelta($log_sql);
    dbDelta($status_log_sql);
    dbDelta($audit_sql);
    dbDelta($form_events_sql);
    dbDelta($alerts_sql);
    if (!ensure_delivery_reservation_index($log) || !schema_is_ready_for_current_blog()) {
        throw new \RuntimeException('landing_config_schema_incomplete');
    }
}

/** Exact type/null/default/extra contract for every runtime column. */
function schema_column_contract_for_current_blog(): array {
    $leads = str_replace('`', '', get_leads_table_name());
    $audit = str_replace('`', '', get_lead_audit_table_name());
    $log = str_replace('`', '', get_lead_log_table_name());
    $status_log = str_replace('`', '', get_lead_status_log_table_name());
    $form_events = str_replace('`', '', get_form_events_table_name());
    $alerts = str_replace('`', '', get_monitor_alerts_table_name());
    $column = static fn(string $type, bool $nullable, $default = null): array =>
        ['type' => $type, 'nullable' => $nullable, 'default' => $default, 'extra' => ''];
    $created = static fn(): array => [
        'type' => 'datetime', 'nullable' => false,
        'default_pattern' => '/^current_timestamp(?:\(\))?$/i',
        'extra' => '',
    ];
    $id = static fn(): array => [
        'type' => 'bigint unsigned', 'nullable' => false,
        'default' => null, 'extra' => 'auto_increment',
    ];

    return [
        $leads => [
            'id' => $id(), 'created_at' => $created(),
            'submission_id' => $column('char(36)', true),
            'name' => $column('varchar(191)', false, ''),
            'phone' => $column('varchar(64)', false, ''),
            'email' => $column('varchar(191)', false, ''),
            'message' => $column('text', true),
            'source_block' => $column('text', false),
            'utm_source' => $column('varchar(191)', false, ''),
            'utm_medium' => $column('varchar(191)', false, ''),
            'utm_campaign' => $column('varchar(191)', false, ''),
            'utm_term' => $column('varchar(191)', false, ''),
            'utm_content' => $column('varchar(191)', false, ''),
            'roistat_visit' => $column('varchar(64)', false, ''),
            'ip' => $column('varchar(45)', false, ''),
            'user_agent' => $column('text', true),
            'delivery_targets' => $column('text', true),
            'delivery_reservations_ready' => $column('tinyint', false, '0'),
            'audit_origin_id' => $column('bigint unsigned', true),
            'processed_status' => $column('varchar(32)', false, 'pending'),
            'pd_consent_granted_at' => $column('datetime', true),
            'recaptcha_score' => $column('decimal(3,2)', true),
        ],
        $log => [
            'id' => $id(), 'lead_id' => $column('bigint unsigned', false),
            'adapter' => $column('varchar(64)', false),
            'integration_id' => $column('bigint unsigned', false, '0'),
            'attempt' => $column('int', false, '1'),
            'status' => $column('varchar(32)', false, 'queued'),
            'response_code' => $column('int', true),
            'response_body' => $column('text', true),
            'error_text' => $column('varchar(500)', true),
            'next_attempt_at' => $column('datetime', true),
            'locked_at' => $column('datetime', true),
            'finished_at' => $column('datetime', true),
            'provider_id' => $column('bigint unsigned', true),
            'created_at' => $created(),
        ],
        $status_log => [
            'id' => $id(), 'lead_id' => $column('bigint unsigned', false),
            'user_id' => $column('bigint unsigned', true),
            'from_status' => $column('varchar(64)', true),
            'to_status' => $column('varchar(64)', false),
            'comment' => $column('text', true), 'created_at' => $created(),
        ],
        $audit => [
            'id' => $id(), 'created_at' => $created(),
            'submission_id' => $column('char(36)', true),
            'ip' => $column('varchar(45)', false, ''),
            'user_agent' => $column('text', true),
            'name' => $column('varchar(191)', false, ''),
            'phone' => $column('varchar(64)', false, ''),
            'email' => $column('varchar(191)', false, ''),
            'message' => $column('text', true),
            'source_block' => $column('text', false),
            'utm_source' => $column('varchar(191)', false, ''),
            'utm_medium' => $column('varchar(191)', false, ''),
            'utm_campaign' => $column('varchar(191)', false, ''),
            'utm_term' => $column('varchar(191)', false, ''),
            'utm_content' => $column('varchar(191)', false, ''),
            'roistat_visit' => $column('varchar(64)', false, ''),
            'pd_consent' => $column('varchar(8)', false, ''),
            'recaptcha_token_present' => $column('tinyint', false, '0'),
            'blocked_by' => $column('varchar(64)', true),
            'block_detail' => $column('varchar(255)', true),
            'lead_id' => $column('bigint unsigned', true),
        ],
        $form_events => [
            'id' => $id(), 'created_at' => $created(),
            'submission_id' => $column('char(36)', false),
            'event_sequence' => $column('smallint unsigned', true),
            'event_name' => $column('varchar(32)', false),
            'event_detail' => $column('varchar(32)', false, ''),
            'form_id' => $column('varchar(100)', false, ''),
            'brand' => $column('varchar(100)', false, ''),
            'cta_key' => $column('varchar(100)', false, ''),
            'page_path' => $column('varchar(255)', false, ''),
            'utm_source' => $column('varchar(191)', false, ''),
            'utm_medium' => $column('varchar(191)', false, ''),
            'utm_campaign' => $column('varchar(191)', false, ''),
        ],
        $alerts => [
            'id' => $id(), 'fingerprint' => $column('char(64)', false),
            'incident_kind' => $column('varchar(32)', false),
            'severity' => $column('varchar(16)', false),
            'submission_id' => $column('char(36)', true),
            'lead_id' => $column('bigint unsigned', true),
            'integration_id' => $column('bigint unsigned', true),
            'fingerprint_scope' => $column('bigint unsigned', false, '0'),
            'adapter' => $column('varchar(64)', false, ''),
            'safe_status' => $column('varchar(32)', false, ''),
            'safe_category' => $column('varchar(64)', false, ''),
            'provider_response_code' => $column('smallint unsigned', true),
            'occurrence_count' => $column('int unsigned', false, '1'),
            'first_seen_at' => $column('datetime', false),
            'last_seen_at' => $column('datetime', false),
            'due_at' => $column('datetime', false),
            'locked_at' => $column('datetime', true),
            'lock_token' => $column('char(36)', true),
            'sent_at' => $column('datetime', true),
            'resolved_at' => $column('datetime', true),
            'resolution' => $column('varchar(32)', false, ''),
            'telegram_status' => $column('varchar(32)', false, 'pending'),
            'send_attempts' => $column('smallint unsigned', false, '0'),
            'last_response_at' => $column('datetime', true),
            'telegram_response_code' => $column('smallint unsigned', true),
            'telegram_message_id' => $column('bigint unsigned', true),
        ],
    ];
}

/** Gate the version marker on the complete live table and index contract. */
function schema_is_ready_for_current_blog(): bool {
    global $wpdb;
    $leads = str_replace('`', '', get_leads_table_name());
    $audit = str_replace('`', '', get_lead_audit_table_name());
    $log = str_replace('`', '', get_lead_log_table_name());
    $status_log = str_replace('`', '', get_lead_status_log_table_name());
    $form_events = str_replace('`', '', get_form_events_table_name());
    $alerts = str_replace('`', '', get_monitor_alerts_table_name());

    $required_columns = schema_column_contract_for_current_blog();
    foreach (array_keys($required_columns) as $required_table) {
        $found = $wpdb->get_var("SHOW TABLES LIKE '{$required_table}'");
        if ((string)$found !== $required_table && (string)$found !== 'present') { return false; }
    }

    foreach ($required_columns as $table => $columns) {
        foreach ($columns as $required_column => $definition) {
            $column = $wpdb->get_row("SHOW COLUMNS FROM `{$table}` LIKE '{$required_column}'", ARRAY_A);
            if (!is_array($column) || (string)($column['Field'] ?? '') !== $required_column) { return false; }
            if (!column_definition_matches($column, $definition)) {
                return false;
            }
        }
    }

    $required_indexes = [
        $leads => [
            'PRIMARY' => [true, ['id']], 'submission_id' => [false, ['submission_id']],
            'created_at' => [false, ['created_at']],
            'delivery_reconcile' => [false, ['delivery_reservations_ready','id']],
            'audit_origin' => [true, ['audit_origin_id']],
            'processed_status' => [false, ['processed_status']],
        ],
        $log => [
            'PRIMARY' => [true, ['id']], 'lead_id' => [false, ['lead_id']],
            'delivery_queue' => [false, ['status','next_attempt_at']],
            'lead_integration' => [false, ['lead_id','integration_id']],
            'status_adapter' => [false, ['status','adapter']],
            'delivery_attempt' => [true, ['lead_id','integration_id','attempt']],
        ],
        $status_log => [
            'PRIMARY' => [true, ['id']], 'lead_id' => [false, ['lead_id']],
            'created_at' => [false, ['created_at']],
        ],
        $audit => [
            'PRIMARY' => [true, ['id']], 'submission_id' => [false, ['submission_id']],
            'created_at' => [false, ['created_at']], 'blocked_by' => [false, ['blocked_by']],
            'lead_id' => [false, ['lead_id']],
        ],
        $form_events => [
            'PRIMARY' => [true, ['id']], 'submission_id' => [false, ['submission_id']],
            'submission_sequence' => [false, ['submission_id','event_sequence']],
            'event_name' => [false, ['event_name']], 'created_at' => [false, ['created_at']],
        ],
        $alerts => [
            'PRIMARY' => [true, ['id']], 'fingerprint' => [true, ['fingerprint']],
            'queue_due' => [false, ['telegram_status','resolved_at','due_at']],
            'submission_id' => [false, ['submission_id']],
            'lead_integration' => [false, ['lead_id','integration_id']],
        ],
    ];
    foreach ($required_indexes as $table => $indexes) {
        foreach ($indexes as $name => [$unique, $columns]) {
            $rows = $wpdb->get_results(
                "SHOW INDEX FROM `{$table}` WHERE Key_name='{$name}'", ARRAY_A
            );
            if (!index_definition_is_exact($rows, $columns, $unique)) { return false; }
        }
    }
    return true;
}

function column_definition_matches(array $column, array $contract): bool {
    $type = normalize_mysql_column_type((string)($column['Type'] ?? ''));
    if ($type !== normalize_mysql_column_type((string)($contract['type'] ?? ''))) { return false; }
    $nullable = strtoupper((string)($column['Null'] ?? '')) === 'YES';
    if ($nullable !== (bool)($contract['nullable'] ?? false)) { return false; }
    if (array_key_exists('default_pattern', $contract)) {
        if (!array_key_exists('Default', $column)
            || preg_match((string)$contract['default_pattern'], (string)$column['Default']) !== 1) {
            return false;
        }
    } elseif (array_key_exists('default', $contract)) {
        if (!array_key_exists('Default', $column)) { return false; }
        $expected = $contract['default'];
        $actual = $column['Default'];
        if ($expected === null ? $actual !== null : (string)$actual !== (string)$expected) { return false; }
    }
    if (array_key_exists('extra', $contract)) {
        $extra = strtolower(trim((string)($column['Extra'] ?? '')));
        $tokens = array_values(array_filter(preg_split('/\s+/', $extra) ?: [],
            static fn(string $token): bool => $token !== '' && $token !== 'default_generated'));
        sort($tokens, SORT_STRING);
        $expected_tokens = array_values(array_filter(preg_split('/\s+/', strtolower((string)$contract['extra'])) ?: []));
        sort($expected_tokens, SORT_STRING);
        if ($tokens !== $expected_tokens) { return false; }
    }
    return true;
}

function normalize_mysql_column_type(string $type): string {
    $type = strtolower(trim(preg_replace('/\s+/', ' ', $type) ?? $type));
    return preg_replace('/\b(tinyint|smallint|mediumint|int|integer|bigint)\(\d+\)/', '$1', $type) ?? $type;
}

function index_definition_is_exact($indexes, array $expected_columns, bool $unique): bool {
    if (!is_array($indexes) || count($indexes) !== count($expected_columns)) { return false; }
    usort($indexes, static fn(array $left, array $right): int =>
        (int)($left['Seq_in_index'] ?? 0) <=> (int)($right['Seq_in_index'] ?? 0));
    $columns = [];
    $expected_non_unique = $unique ? 0 : 1;
    foreach ($indexes as $row) {
        if ((int)($row['Non_unique'] ?? -1) !== $expected_non_unique) { return false; }
        if (($row['Sub_part'] ?? null) !== null) { return false; }
        $columns[] = strtolower((string)($row['Column_name'] ?? ''));
    }
    return $columns === array_map('strtolower', $expected_columns);
}

function delivery_reservation_index_is_exact($indexes): bool {
    return index_definition_is_exact($indexes, ['lead_id','integration_id','attempt'], true);
}

/**
 * Preserve duplicate historical adapter-only rows before adding the exact
 * per-integration reservation key used by the asynchronous worker.
 */
function ensure_delivery_reservation_index(string $log_table): bool {
    global $wpdb;
    $safe_table = str_replace('`', '', $log_table);
    if ($wpdb->query("UPDATE `{$safe_table}` SET attempt=id WHERE integration_id=0 AND attempt=1") === false) {
        return false;
    }
    $indexes = $wpdb->get_results("SHOW INDEX FROM `{$safe_table}` WHERE Key_name='delivery_attempt'", ARRAY_A);
    if (delivery_reservation_index_is_exact($indexes)) { return true; }
    if (!empty($indexes)
        && $wpdb->query("ALTER TABLE `{$safe_table}` DROP INDEX delivery_attempt") === false) {
        return false;
    }
    if ($wpdb->query("ALTER TABLE `{$safe_table}` ADD UNIQUE KEY delivery_attempt (lead_id,integration_id,attempt)") === false) {
        return false;
    }
    return delivery_reservation_index_is_exact($wpdb->get_results(
        "SHOW INDEX FROM `{$safe_table}` WHERE Key_name='delivery_attempt'", ARRAY_A
    ));
}

<?php
namespace LandingConfig\DB;

if (!defined('ABSPATH')) { exit; }

const DB_VERSION = '1.1.0';
const DB_VERSION_OPTION = 'landing_config_db_version';
const DELIVERY_ROLLOUT_BOUNDARY_OPTION = 'landing_delivery_async_boundary';

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

function ensure_delivery_rollout_boundaries(): void {
    if (!is_multisite()) {
        ensure_delivery_rollout_boundary_for_current_blog();
        return;
    }
    foreach (get_sites(['number' => 0]) as $site) {
        switch_to_blog((int)$site->blog_id);
        try { ensure_delivery_rollout_boundary_for_current_blog(); }
        finally { restore_current_blog(); }
    }
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

/**
 * Install schema on first run; let dbDelta handle additive column diffs on
 * version bumps. Data migrations (e.g. backfill on schema change) require
 * explicit branches on $current — not currently needed.
 */
function maybe_install_or_migrate(): void {
    // This intentionally runs even when the schema version is already current:
    // a partially completed rollout must fail closed rather than replay legacy
    // leads whose migrated delivery rows have integration_id=0.
    ensure_delivery_rollout_boundaries();
    $current = get_site_option(DB_VERSION_OPTION, '');
    if ($current === DB_VERSION) {
        return;
    }

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

    if ($ok) {
        update_site_option(DB_VERSION_OPTION, DB_VERSION);
    }
}

/**
 * One-time migration: add pd_consent_granted_at column to existing installs.
 * Runs dbDelta for all blogs so the column is backfilled on sites that already
 * passed the DB_VERSION check before this column was introduced (B1 cookie-banner).
 * Marker: landing_config_migration_b1_pd_consent
 */
function maybe_migrate_b1_pd_consent(): void {
    if (get_site_option('landing_config_migration_b1_pd_consent')) {
        return;
    }

    $ok = true;
    if (is_multisite()) {
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

    if ($ok) {
        update_site_option('landing_config_migration_b1_pd_consent', true);
    }
}

/**
 * One-time migration: add roistat_visit column to existing installs.
 * Marker: landing_config_migration_roistat_visit
 */
function maybe_migrate_roistat_visit(): void {
    if (get_site_option('landing_config_migration_roistat_visit')) {
        return;
    }

    $ok = true;
    if (is_multisite()) {
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

    if ($ok) {
        update_site_option('landing_config_migration_roistat_visit', true);
    }
}

/**
 * One-time migration: add recaptcha_score column to existing installs.
 * Marker: landing_config_migration_recaptcha_score
 */
function maybe_migrate_recaptcha_score(): void {
    if (get_site_option('landing_config_migration_recaptcha_score')) {
        return;
    }

    $ok = true;
    if (is_multisite()) {
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

    if ($ok) {
        update_site_option('landing_config_migration_recaptcha_score', true);
    }
}

/**
 * One-time migration: create landing_lead_audit table on existing installs.
 * Marker: landing_config_migration_lead_audit
 */
function maybe_migrate_lead_audit(): void {
    if (get_site_option('landing_config_migration_lead_audit')) {
        return;
    }

    $ok = true;
    if (is_multisite()) {
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

    if ($ok) {
        update_site_option('landing_config_migration_lead_audit', true);
    }
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
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        pd_consent_granted_at DATETIME NULL,
        recaptcha_score DECIMAL(3,2) NULL,
        PRIMARY KEY (id),
        KEY submission_id (submission_id),
        KEY created_at (created_at),
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
    ensure_delivery_reservation_index($log);
}

/**
 * Preserve duplicate historical adapter-only rows before adding the exact
 * per-integration reservation key used by the asynchronous worker.
 */
function ensure_delivery_reservation_index(string $log_table): void {
    global $wpdb;
    $safe_table = str_replace('`', '', $log_table);
    $wpdb->query("UPDATE `{$safe_table}` SET attempt=id WHERE integration_id=0 AND attempt=1");
    $indexes = $wpdb->get_results("SHOW INDEX FROM `{$safe_table}` WHERE Key_name='delivery_attempt'", ARRAY_A);
    if (empty($indexes)) {
        $wpdb->query("ALTER TABLE `{$safe_table}` ADD UNIQUE KEY delivery_attempt (lead_id,integration_id,attempt)");
    }
}

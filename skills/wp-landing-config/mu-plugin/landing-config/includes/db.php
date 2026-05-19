<?php
namespace LandingConfig\DB;

if (!defined('ABSPATH')) { exit; }

const DB_VERSION = '1.0.0';
const DB_VERSION_OPTION = 'landing_config_db_version';

function get_leads_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_leads';
}

function get_lead_log_table_name(): string {
    global $wpdb;
    return $wpdb->get_blog_prefix() . 'landing_lead_log';
}

function maybe_install_or_migrate(): void {
    $current = get_site_option(DB_VERSION_OPTION, '');
    if ($current === DB_VERSION) {
        return;
    }

    // Per-blog tables: switch to each blog, create tables, restore.
    if (function_exists('get_sites') && is_multisite()) {
        $sites = get_sites(['number' => 999]);
        foreach ($sites as $site) {
            switch_to_blog((int)$site->blog_id);
            create_tables_for_current_blog();
            restore_current_blog();
        }
    } else {
        create_tables_for_current_blog();
    }

    update_site_option(DB_VERSION_OPTION, DB_VERSION);
}

function create_tables_for_current_blog(): void {
    global $wpdb;
    $charset = $wpdb->get_charset_collate();
    $leads = get_leads_table_name();
    $log = get_lead_log_table_name();

    $leads_sql = "CREATE TABLE $leads (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        name VARCHAR(191) NOT NULL DEFAULT '',
        phone VARCHAR(64) NOT NULL DEFAULT '',
        email VARCHAR(191) NOT NULL DEFAULT '',
        message TEXT NULL,
        source_block VARCHAR(191) NOT NULL DEFAULT '',
        utm_source VARCHAR(191) NOT NULL DEFAULT '',
        utm_medium VARCHAR(191) NOT NULL DEFAULT '',
        utm_campaign VARCHAR(191) NOT NULL DEFAULT '',
        utm_term VARCHAR(191) NOT NULL DEFAULT '',
        utm_content VARCHAR(191) NOT NULL DEFAULT '',
        ip VARCHAR(45) NOT NULL DEFAULT '',
        user_agent VARCHAR(500) NOT NULL DEFAULT '',
        processed_status VARCHAR(32) NOT NULL DEFAULT 'pending',
        PRIMARY KEY (id),
        KEY created_at (created_at),
        KEY processed_status (processed_status)
    ) $charset;";

    $log_sql = "CREATE TABLE $log (
        id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
        lead_id BIGINT(20) UNSIGNED NOT NULL,
        adapter VARCHAR(64) NOT NULL,
        attempt INT(11) NOT NULL DEFAULT 1,
        status VARCHAR(32) NOT NULL DEFAULT 'pending',
        response_code INT(11) NULL,
        response_body TEXT NULL,
        error_text VARCHAR(500) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        KEY lead_id (lead_id),
        KEY status_adapter (status, adapter)
    ) $charset;";

    if (!function_exists('dbDelta')) {
        require_once ABSPATH . 'wp-admin/includes/upgrade.php';
    }
    dbDelta($leads_sql);
    dbDelta($log_sql);
}

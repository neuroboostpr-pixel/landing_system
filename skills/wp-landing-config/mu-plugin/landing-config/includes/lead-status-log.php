<?php
namespace LandingConfig\LeadStatusLog;

if (!defined('ABSPATH')) { exit; }

use function LandingConfig\DB\get_lead_status_log_table_name;
use function LandingConfig\LeadStatuses\resolve_lead_status;

/**
 * Записать изменение статуса в лог.
 * Возвращает id новой записи или 0 если to_status не валиден (нет в vocab).
 */
function log_status_change(int $lead_id, ?string $from_status, string $to_status, ?int $user_id, ?string $comment): int {
    global $wpdb;

    // Whitelist: to_status должен существовать в vocab текущего blog
    $vocab_match = resolve_lead_status($to_status, \get_current_blog_id());
    if ($vocab_match === null) {
        \error_log("[landing-config] log_status_change: invalid to_status='{$to_status}' for lead_id={$lead_id}");
        return 0;
    }

    $table = get_lead_status_log_table_name();
    $comment_value = ($comment === null || $comment === '') ? null : $comment;

    $data = [
        'lead_id'     => $lead_id,
        'user_id'     => $user_id,
        'from_status' => $from_status,
        'to_status'   => $to_status,
        'comment'     => $comment_value,
    ];

    // Drop $format arg: WP_DB->insert auto-detects formats, и null значения
    // в $data корректно конвертируются в SQL NULL. Передача null внутри
    // $format массива — некорректное использование WP API (sprintf падает).
    $wpdb->insert($table, $data);
    return (int) $wpdb->insert_id;
}

/** Получить историю изменений статуса заявки, отсортирована created_at desc. */
function get_status_history(int $lead_id): array {
    global $wpdb;
    $table = get_lead_status_log_table_name();
    $rows = $wpdb->get_results(
        $wpdb->prepare("SELECT * FROM `$table` WHERE lead_id = %d ORDER BY created_at DESC, id DESC", $lead_id),
        ARRAY_A
    );
    return is_array($rows) ? $rows : [];
}

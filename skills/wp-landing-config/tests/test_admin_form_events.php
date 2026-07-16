<?php
$file = __DIR__ . '/../mu-plugin/landing-config/includes/admin-form-events.php';
if (!is_file($file)) {
    fwrite(STDERR, "FAIL: admin-form-events.php is missing\n");
    exit(1);
}

$source = file_get_contents($file);
$failures = 0;
$tests = 0;
$assert = static function (bool $condition, string $message) use (&$failures, &$tests): void {
    $tests++;
    if (!$condition) {
        $failures++;
        fwrite(STDERR, "FAIL: {$message}\n");
    }
};

$assert(str_contains($source, "add_submenu_page("), 'admin view registers a submenu');
$assert(str_contains($source, "'manage_options'"), 'admin view requires manage_options');
$assert(str_contains($source, 'current_user_can('), 'render callback re-checks administrator permission');
$assert(str_contains($source, 'get_form_events_table_name'), 'admin view reads only the anonymous event table');
$assert(str_contains($source, 'get_leads_table_name'), 'admin view correlates an event with its saved lead by UUID');
$assert(str_contains($source, "['lead_id']"), 'admin view displays the linked lead id when one exists');
$assert(str_contains($source, "['event_sequence']"), 'admin view displays browser sequence when supplied');
$assert(str_contains($source, 'Шаг браузера'), 'admin view labels browser sequence in plain language');
$assert(str_contains($source, 'порядок прихода'), 'admin view explains that date and ID represent arrival order');
$assert(str_contains($source, 'ORDER BY events.created_at DESC, events.id DESC'), 'admin view preserves arrival order while showing browser sequence separately');
$assert(str_contains($source, '$wpdb->prepare('), 'pagination query is parameterized');
$assert(str_contains($source, 'esc_html('), 'event metadata is escaped before rendering');

foreach (['submission_id', 'event_name', 'event_detail', 'form_id', 'brand', 'cta_key', 'page_path', 'utm_source'] as $column) {
    $assert(str_contains($source, "['{$column}']"), "admin view renders {$column}");
}

foreach (['phone', 'email', 'message', 'source_block', 'user_agent', "['ip']"] as $forbidden) {
    $assert(!str_contains($source, $forbidden), "admin view does not expose unavailable sensitive field {$forbidden}");
}

echo $failures === 0 ? "PASS: {$tests} admin form event assertions\n" : "FAILURES: {$failures}/{$tests}\n";
exit($failures === 0 ? 0 : 1);

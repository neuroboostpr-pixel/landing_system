<?php
if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\DeepLinks\build_deep_link;

$prefix_filter = 'AI';
$cat_label = 'AI Readiness (AI1-AI3)';

if ($report === null) {
    echo '<div class="lp-audit-empty">Аудит ещё не запускался. Нажми «Запустить».</div>';
    return;
}

// Resolve results — if aggregate, find the right site (or merge all)
if (isset($report['sites']) && is_array($report['sites'])) {
    // Aggregate: show failures from all sites grouped by host
    $sites = $report['sites'];
} else {
    $sites = [$report];
}

$admin_root = is_multisite() ? \network_site_url('wp-admin/') : \admin_url();

?>
<h2><?php echo esc_html($cat_label); ?></h2>

<?php foreach ($sites as $site): ?>
    <h3 style="margin-top:24px;"><?php echo esc_html($site['host'] ?? '?'); ?></h3>
    <?php
    $blog_id = \LandingConfig\SEOAudit\Admin\host_to_blog_id($site['host'] ?? '') ?? 0;
    $results = $site['results'] ?? [];
    $cat_results = array_filter($results, static fn($r) =>
        str_starts_with((string)($r['id'] ?? ''), $prefix_filter));
    $cat_failures = array_filter($cat_results, static fn($r) => empty($r['passed']));
    if (empty($cat_failures)):
        ?>
        <p>✅ Все проверки этой категории пройдены.</p>
    <?php else: ?>
        <table class="lp-audit-table">
            <thead><tr>
                <th>ID</th><th>Severity</th><th>Описание</th><th>Evidence</th><th>Действие</th>
            </tr></thead>
            <tbody>
            <?php foreach ($cat_failures as $f):
                $deep_link = build_deep_link((string) $f['id'], $blog_id, $admin_root);
                // Severity comes from inline 'severity' field if site_report has it,
                // else fallback to fix_action.type
                $is_hard = !empty($f['severity']) && $f['severity'] === 'hard';
                $row_class = $is_hard ? 'is-hard' : 'is-soft';
                ?>
                <tr class="<?php echo esc_attr($row_class); ?>">
                    <td class="lp-id"><?php echo esc_html((string) $f['id']); ?></td>
                    <td><?php echo $is_hard ? '🔴 hard' : '🟡 soft'; ?></td>
                    <td><?php echo esc_html((string) ($f['desc'] ?? '')); ?></td>
                    <td class="lp-evidence"><?php echo esc_html((string) ($f['evidence'] ?? '')); ?></td>
                    <td>
                        <?php if ($deep_link && !empty($deep_link['url'])): ?>
                            <a class="button" href="<?php echo esc_url($deep_link['url']); ?>" target="_blank">
                                <?php echo esc_html((string) $deep_link['label']); ?>
                            </a>
                        <?php elseif ($deep_link): ?>
                            <span class="lp-suggestion"><?php echo esc_html((string) $deep_link['label']); ?></span>
                        <?php else: ?>
                            <span class="lp-suggestion">—</span>
                        <?php endif; ?>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    <?php endif; ?>
<?php endforeach; ?>

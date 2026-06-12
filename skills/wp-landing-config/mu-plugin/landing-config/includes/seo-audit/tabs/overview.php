<?php
/**
 * Overview tab — used by admin-network::render_page().
 * Available variables (from caller): $report (?array), $segment (string), $tab (string).
 */
if (!defined('ABSPATH')) { exit; }

use function LandingConfig\SEOAudit\Admin\load_cached_report;

/** Categorize check IDs into groups. */
function _lp_categorize_results(array $results): array {
    $out = ['HTML' => [], 'Network' => [], 'Schema' => [], 'AI' => []];
    foreach ($results as $r) {
        $id = (string) ($r['id'] ?? '');
        if (str_starts_with($id, 'H')) {
            $out['HTML'][] = $r;
        } elseif (str_starts_with($id, 'N')) {
            $out['Network'][] = $r;
        } elseif (str_starts_with($id, 'S')) {
            $out['Schema'][] = $r;
        } elseif (str_starts_with($id, 'AI')) {
            $out['AI'][] = $r;
        }
    }
    return $out;
}

function _lp_score(array $checks): array {
    $hard_total = 0; $hard_pass = 0;
    $soft_total = 0; $soft_pass = 0;
    foreach ($checks as $c) {
        if (!empty($c['_hard'])) {
            $hard_total++;
            if ($c['passed']) $hard_pass++;
        } else {
            $soft_total++;
            if ($c['passed']) $soft_pass++;
        }
    }
    return [
        'hard_pass' => $hard_pass, 'hard_total' => $hard_total,
        'soft_pass' => $soft_pass, 'soft_total' => $soft_total,
    ];
}

if ($report === null) {
    echo '<div class="lp-audit-empty">Аудит ещё не запускался для этого сегмента. Нажми «Запустить» выше.</div>';
    return;
}

// Determine if aggregate (multisite — has "sites" array) or single-site report
if (isset($report['sites']) && is_array($report['sites'])) {
    // Multisite aggregate
    ?>
    <h2>Сводка по сегментам</h2>
    <table class="lp-audit-table">
        <thead>
            <tr>
                <th>Сегмент</th>
                <th>HTML</th>
                <th>Network</th>
                <th>Schema</th>
                <th>AI</th>
                <th>Hard total</th>
            </tr>
        </thead>
        <tbody>
            <?php foreach ($report['sites'] as $site):
                // Inject _hard flag from thresholds inline (we have failures with severity but
                // need full hard/total counts — fall back to site-level counts).
                $h = (int) ($site['hard_passed'] ?? 0);
                $ht = (int) ($site['hard_total'] ?? 0);
                $passed = !empty($site['passed']);
                $icon = $passed ? '✅' : '❌';
                ?>
                <tr>
                    <td>
                        <a href="<?php echo esc_url(\add_query_arg([
                            'page' => \LandingConfig\SEOAudit\Admin\MENU_SLUG,
                            'tab' => 'html',
                            'segment' => (string) \LandingConfig\SEOAudit\Admin\host_to_blog_id($site['host'] ?? ''),
                        ], \network_admin_url('admin.php'))); ?>">
                            <?php echo esc_html($site['host'] ?? '?'); ?>
                        </a>
                    </td>
                    <?php
                    $by_cat = _lp_categorize_results($site['results'] ?? []);
                    foreach (['HTML', 'Network', 'Schema', 'AI'] as $cat):
                        $checks = $by_cat[$cat];
                        $total = count($checks);
                        $passed_n = count(array_filter($checks, static fn($c) => !empty($c['passed'])));
                        ?>
                        <td><?php echo $passed_n; ?>/<?php echo $total; ?></td>
                    <?php endforeach; ?>
                    <td><?php echo $icon . ' ' . $h . '/' . $ht; ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php
} else {
    // Single-site report
    $by_cat = _lp_categorize_results($report['results'] ?? []);
    $h = (int) ($report['hard_passed'] ?? 0);
    $ht = (int) ($report['hard_total'] ?? 0);
    $passed = !empty($report['passed']);
    ?>
    <h2><?php echo esc_html($report['host'] ?? ''); ?></h2>
    <p>
        <?php echo $passed ? '✅ <strong>PASS</strong>' : '❌ <strong>FAIL</strong>'; ?> —
        Hard gates: <strong><?php echo $h . '/' . $ht; ?></strong>
    </p>

    <table class="lp-audit-table">
        <thead><tr><th>Категория</th><th>Pass / Total</th></tr></thead>
        <tbody>
            <?php foreach (['HTML', 'Network', 'Schema', 'AI'] as $cat):
                $checks = $by_cat[$cat];
                $total = count($checks);
                $passed_n = count(array_filter($checks, static fn($c) => !empty($c['passed'])));
                $tab_key = strtolower($cat === 'AI' ? 'ai_readiness' : $cat);
                ?>
                <tr>
                    <td>
                        <a href="<?php echo esc_url(\add_query_arg([
                            'page' => \LandingConfig\SEOAudit\Admin\MENU_SLUG,
                            'tab' => $tab_key,
                            'segment' => $segment,
                        ], \network_admin_url('admin.php'))); ?>">
                            <?php echo esc_html($cat); ?>
                        </a>
                    </td>
                    <td><?php echo $passed_n . '/' . $total; ?></td>
                </tr>
            <?php endforeach; ?>
        </tbody>
    </table>
    <?php
}

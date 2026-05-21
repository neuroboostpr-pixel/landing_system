<?php
namespace LandingConfig\SegmentSelector;

if (!defined('ABSPATH')) { exit; }

/**
 * Render a network-admin dropdown for selecting which segment (subsite) to edit.
 * URL pattern: ?page=<slug>&segment=<blog_id|0>, where 0 = network default.
 */
function render(string $page_slug, int $current_segment = 0): void {
    $sites = \function_exists('get_sites') ? \get_sites(['number' => 0]) : [];
    $main_id = \function_exists('get_main_site_id') ? \get_main_site_id() : 1;
    ?>
    <div class="lp-segment-selector" style="background:#f6f7f7; padding:12px 16px; border:1px solid #c3c4c7; border-radius:4px; margin:16px 0;">
        <form method="get" style="display:inline;">
            <input type="hidden" name="page" value="<?php echo \esc_attr($page_slug); ?>">
            <label style="font-weight:600;">Сегмент:
                <select name="segment" onchange="this.form.submit()" style="min-width:280px;">
                    <option value="0" <?php \selected($current_segment, 0); ?>>— общие настройки (network default) —</option>
                    <?php foreach ($sites as $site):
                        $bid = (int) $site->blog_id;
                        $label = $site->domain . rtrim($site->path, '/');
                        if ($bid === $main_id) $label .= ' ★';
                    ?>
                        <option value="<?php echo $bid; ?>" <?php \selected($current_segment, $bid); ?>>
                            <?php echo \esc_html($label); ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </label>
            <noscript><button type="submit" class="button">Применить</button></noscript>
        </form>
        <?php if ($current_segment === 0): ?>
            <span style="margin-left:1em; color:#646970;">— редактируете <strong>сетевые дефолты</strong>. Применятся ко всем сегментам, у которых нет своего override.</span>
        <?php else: ?>
            <?php
            $site = null;
            foreach ($sites as $s) { if ((int) $s->blog_id === $current_segment) { $site = $s; break; } }
            $host = $site ? $site->domain : 'segment#' . $current_segment;
            ?>
            <span style="margin-left:1em; color:#646970;">— редактируете <strong>сегмент <?php echo \esc_html($host); ?></strong>. Поля показывают inherited значения с возможностью override.</span>
        <?php endif; ?>
    </div>
    <?php
}

/** Read current_segment from $_GET. 0 = network default. */
function current_from_request(): int {
    return isset($_GET['segment']) ? max(0, (int) $_GET['segment']) : 0;
}

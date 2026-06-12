<?php
// $settings is provided by render.php (Task 4).
if (!defined('ABSPATH')) { exit; }
?>
<div id="lp-cb" class="lp-cb lp-cb--floating-card-left" data-version="<?php echo esc_attr($settings['consent_version']); ?>" hidden role="dialog" aria-labelledby="lp-cb-title">
    <div class="lp-cb__inner">
        <h2 id="lp-cb-title" class="lp-cb__title"><?php echo esc_html($settings['title']); ?></h2>
        <p class="lp-cb__desc"><?php echo esc_html($settings['description']); ?></p>

        <?php if (!empty($settings['show_categories']) && !empty($settings['categories'])): ?>
            <div class="lp-cb__categories">
                <?php foreach ($settings['categories'] as $cat): ?>
                    <?php if (empty($cat['slug'])) continue; ?>
                    <label class="lp-cb__category">
                        <input type="checkbox"
                               data-slug="<?php echo esc_attr($cat['slug']); ?>"
                               <?php if (!empty($cat['locked'])) echo 'checked disabled'; ?>
                               <?php if (empty($cat['locked']) && !empty($cat['default_on'])) echo 'checked'; ?>>
                        <span class="lp-cb__category-name"><?php echo esc_html($cat['name'] ?? $cat['slug']); ?></span>
                        <?php if (!empty($cat['desc'])): ?>
                            <span class="lp-cb__category-desc"><?php echo esc_html($cat['desc']); ?></span>
                        <?php endif; ?>
                    </label>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>

        <div class="lp-cb__actions">
            <?php if (!empty($settings['policy_link_text'])): ?>
                <a class="lp-cb__policy" href="<?php echo esc_url($settings['policy_link_url']); ?>" target="_blank" rel="noopener">
                    <?php echo esc_html($settings['policy_link_text']); ?>
                </a>
            <?php endif; ?>
            <?php if (!empty($settings['show_categories'])): ?>
                <button type="button" class="lp-cb__btn lp-cb__btn--secondary" data-action="save">
                    <?php echo esc_html($settings['btn_save_text']); ?>
                </button>
            <?php endif; ?>
            <?php if (!empty($settings['btn_reject_text'])): ?>
                <button type="button" class="lp-cb__btn lp-cb__btn--ghost" data-action="reject"><?php echo esc_html($settings['btn_reject_text']); ?></button>
            <?php endif; ?>
            <button type="button" class="lp-cb__btn lp-cb__btn--primary" data-action="accept-all">
                <?php echo esc_html($settings['btn_accept_all_text']); ?>
            </button>
        </div>
    </div>
</div>
<button type="button" id="lp-cb-reopen" class="lp-cb-reopen" hidden><?php echo esc_html($settings['reopen_text']); ?></button>

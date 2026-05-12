<?php
/**
 * Block — Тарифы.
 * Auto-scaffolded by generate-theme.py --blocks-only.
 * Edit safely; will not be overwritten on regeneration.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

$nu_title = nu_field( 'title', 'Базовый — 50 000 ₽' );
?>
<section id="pricing" class="lp-block lp-block--pricing">
    <div class="lp-block__title"><?php echo esc_html( $nu_title ); ?></div>
</section>

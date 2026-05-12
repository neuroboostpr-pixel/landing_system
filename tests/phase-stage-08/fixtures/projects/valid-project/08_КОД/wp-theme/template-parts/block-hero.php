<?php
/**
 * Block — Hero.
 * Auto-scaffolded by generate-theme.py --blocks-only.
 * Edit safely; will not be overwritten on regeneration.
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

$nu_title = nu_field( 'title', 'Авторский курс Кирилла Безикова' );
$nu_lede = nu_field( 'lede', 'Описание курса для людей которые хотят освоить нейросети.' );
?>
<section id="hero" class="lp-block lp-block--hero">
    <div class="lp-block__title"><?php echo esc_html( $nu_title ); ?></div>
    <div class="lp-block__lede"><?php echo esc_html( $nu_lede ); ?></div>
</section>

<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class LP_Preview_Panel_Panel {

    public static function register() {
        add_action( 'wp_body_open', [ __CLASS__, 'render' ] );
        add_action( 'wp_enqueue_scripts', [ __CLASS__, 'enqueue' ] );
    }

    public static function should_show() {
        $axes = LP_Preview_Panel_Axes::all();
        if ( empty( $axes ) ) {
            return false;
        }
        if ( current_user_can( 'edit_theme_options' ) ) {
            return true;
        }
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        return ! empty( $opt['visible_to_anon'] );
    }

    public static function enqueue() {
        if ( ! self::should_show() ) {
            return;
        }
        wp_enqueue_style(
            'lp-preview-panel',
            LP_PREVIEW_PANEL_URL . 'assets/panel.css',
            [],
            '0.1.0'
        );
        wp_enqueue_script(
            'lp-preview-panel',
            LP_PREVIEW_PANEL_URL . 'assets/panel.js',
            [],
            '0.1.0',
            true
        );
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        wp_localize_script(
            'lp-preview-panel',
            'LP_PREVIEW_PANEL',
            [
                'axes'     => LP_Preview_Panel_Axes::all(),
                'defaults' => isset( $opt['defaults'] ) ? $opt['defaults'] : [],
            ]
        );
    }

    public static function render() {
        if ( ! self::should_show() ) {
            return;
        }
        $axes = LP_Preview_Panel_Axes::all();
        echo '<div class="lp-preview-panel" role="region" aria-label="Панель превью">';
        echo '<div class="lp-preview-panel__inner">';
        foreach ( $axes as $key => $axis ) {
            echo '<div class="lp-preview-panel__row">';
            printf(
                '<span class="lp-preview-panel__label">Превью %s:</span>',
                esc_html( $axis['label'] )
            );
            echo '<label class="lp-preview-panel__select-wrap">';
            echo '<span class="screen-reader-text">' . esc_html( $axis['label'] ) . '</span>';
            printf(
                '<select class="lp-preview-panel__select" data-lp-axis="%s">',
                esc_attr( $key )
            );
            foreach ( $axis['options'] as $val => $label ) {
                printf(
                    '<option value="%s">%s</option>',
                    esc_attr( $val ),
                    esc_html( $label )
                );
            }
            echo '</select>';
            echo '</label>';
            echo '<span class="lp-preview-panel__hint">выбор сохраняется</span>';
            echo '</div>';
        }
        echo '</div>';
        echo '</div>';
    }
}

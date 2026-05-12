<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

class LP_Preview_Panel_Settings {

    const PAGE_SLUG = 'lp-preview-panel';

    public static function register() {
        add_action( 'admin_menu', [ __CLASS__, 'menu' ] );
        add_action( 'admin_init', [ __CLASS__, 'register_setting' ] );
        add_action( 'admin_enqueue_scripts', [ __CLASS__, 'enqueue' ] );
    }

    public static function menu() {
        add_options_page(
            'Превью-панель',
            'Превью-панель',
            'manage_options',
            self::PAGE_SLUG,
            [ __CLASS__, 'render' ]
        );
    }

    public static function register_setting() {
        register_setting(
            'lp_preview_panel_group',
            LP_PREVIEW_PANEL_OPTION,
            [
                'type'              => 'array',
                'sanitize_callback' => [ __CLASS__, 'sanitize' ],
                'default'           => [
                    'visible_to_anon' => false,
                    'defaults'        => [],
                ],
            ]
        );
    }

    public static function sanitize( $input ) {
        $out = [
            'visible_to_anon' => ! empty( $input['visible_to_anon'] ),
            'defaults'        => [],
        ];
        $axes = LP_Preview_Panel_Axes::all();
        $defaults_in = isset( $input['defaults'] ) && is_array( $input['defaults'] ) ? $input['defaults'] : [];
        foreach ( $defaults_in as $axis_key => $value ) {
            if ( LP_Preview_Panel_Axes::is_valid_value( $axis_key, $value ) ) {
                $out['defaults'][ $axis_key ] = $value;
            } else {
                add_settings_error(
                    'lp_preview_panel',
                    'invalid_default_' . $axis_key,
                    sprintf( 'Invalid default for axis %s, ignored.', esc_html( $axis_key ) ),
                    'warning'
                );
            }
        }
        return $out;
    }

    public static function enqueue( $hook ) {
        if ( $hook !== 'settings_page_' . self::PAGE_SLUG ) {
            return;
        }
        wp_enqueue_script(
            'lp-preview-panel-admin',
            LP_PREVIEW_PANEL_URL . 'assets/admin.js',
            [],
            '0.1.0',
            true
        );
    }

    public static function render() {
        if ( ! current_user_can( 'manage_options' ) ) {
            return;
        }
        $opt = get_option( LP_PREVIEW_PANEL_OPTION, [] );
        $visible = ! empty( $opt['visible_to_anon'] );
        $defaults = isset( $opt['defaults'] ) && is_array( $opt['defaults'] ) ? $opt['defaults'] : [];
        $axes = LP_Preview_Panel_Axes::all();
        ?>
        <div class="wrap">
            <h1>Превью-панель</h1>
            <form method="post" action="options.php">
                <?php settings_fields( 'lp_preview_panel_group' ); ?>

                <h2>Видимость</h2>
                <label>
                    <input type="checkbox"
                           name="<?php echo esc_attr( LP_PREVIEW_PANEL_OPTION ); ?>[visible_to_anon]"
                           value="1" <?php checked( $visible ); ?>>
                    Показывать панель превью анонимным посетителям
                </label>
                <p class="description">Если выключено — панель видят только админы.</p>

                <h2>Текущие дефолты для всех посетителей</h2>
                <table class="form-table">
                <?php foreach ( $axes as $key => $axis ) :
                    $current = isset( $defaults[ $key ] ) ? $defaults[ $key ] : $axis['default'];
                    ?>
                    <tr>
                        <th scope="row"><label for="lp-default-<?php echo esc_attr( $key ); ?>"><?php echo esc_html( $axis['label'] ); ?></label></th>
                        <td>
                            <select id="lp-default-<?php echo esc_attr( $key ); ?>"
                                    name="<?php echo esc_attr( LP_PREVIEW_PANEL_OPTION ); ?>[defaults][<?php echo esc_attr( $key ); ?>]"
                                    data-lp-admin-axis="<?php echo esc_attr( $key ); ?>">
                                <?php foreach ( $axis['options'] as $val => $label ) : ?>
                                    <option value="<?php echo esc_attr( $val ); ?>" <?php selected( $current, $val ); ?>>
                                        <?php echo esc_html( $label ); ?>
                                    </option>
                                <?php endforeach; ?>
                            </select>
                        </td>
                    </tr>
                <?php endforeach; ?>
                </table>

                <p>
                    <button type="button" class="button" data-lp-fill-from-ls>
                        Зафиксировать мой текущий выбор как дефолт
                    </button>
                    <span class="description">(берёт значения из вашего localStorage в этом браузере)</span>
                </p>

                <?php submit_button( 'Сохранить дефолты' ); ?>
            </form>
        </div>
        <?php
    }
}

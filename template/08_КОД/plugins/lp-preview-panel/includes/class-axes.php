<?php
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Reads registered axes from the lp_preview_panel_axes filter,
 * normalises them, drops invalid entries.
 *
 * Axis shape:
 *   [
 *     'label'             => string,
 *     'default'           => string,        // must be a key of 'options'
 *     'body_class_prefix' => string,
 *     'options'           => [key => label]
 *   ]
 */
class LP_Preview_Panel_Axes {

    /** @return array<string, array> map of axis_key => normalised axis */
    public static function all() {
        $raw = apply_filters( 'lp_preview_panel_axes', [] );
        if ( ! is_array( $raw ) ) {
            return [];
        }
        $out = [];
        foreach ( $raw as $key => $axis ) {
            $norm = self::normalise( $key, $axis );
            if ( $norm !== null ) {
                $out[ $key ] = $norm;
            }
        }
        return $out;
    }

    /** @return array|null normalised axis or null if invalid */
    private static function normalise( $key, $axis ) {
        if ( ! is_string( $key ) || $key === '' ) {
            return null;
        }
        if ( ! is_array( $axis ) ) {
            return null;
        }
        $options = isset( $axis['options'] ) && is_array( $axis['options'] ) ? $axis['options'] : [];
        if ( empty( $options ) ) {
            return null;
        }
        $default = isset( $axis['default'] ) ? (string) $axis['default'] : '';
        if ( ! array_key_exists( $default, $options ) ) {
            // Fall back to first option key.
            $default = array_key_first( $options );
        }
        return [
            'label'             => isset( $axis['label'] ) ? (string) $axis['label'] : $key,
            'default'           => $default,
            'body_class_prefix' => isset( $axis['body_class_prefix'] ) ? (string) $axis['body_class_prefix'] : ( $key . '-' ),
            'options'           => $options,
        ];
    }

    /** Returns true if value is a known option for the given axis. */
    public static function is_valid_value( $axis_key, $value ) {
        $axes = self::all();
        if ( ! isset( $axes[ $axis_key ] ) ) {
            return false;
        }
        return array_key_exists( $value, $axes[ $axis_key ]['options'] );
    }
}

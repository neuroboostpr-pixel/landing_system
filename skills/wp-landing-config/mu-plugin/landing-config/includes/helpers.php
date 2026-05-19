<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Read landing-config value: per-site override → network default → $default.
 *
 * @param string $key      e.g. 'crm_amocrm_key' (without 'landing_' prefix)
 * @param mixed  $default  returned if neither per-site nor network has the key
 * @return mixed
 */
function landing_config_get(string $key, $default = '') {
    $site_value = get_option('landing_' . $key, null);
    if ($site_value !== null && $site_value !== false && $site_value !== '') {
        return $site_value;
    }
    $net_value = get_site_option('landing_defaults_' . $key, null);
    if ($net_value !== null && $net_value !== false && $net_value !== '') {
        return $net_value;
    }
    return $default;
}

/**
 * Write per-site value (overrides any network default).
 */
function landing_config_set(string $key, $value): bool {
    return update_option('landing_' . $key, $value);
}

/**
 * Write network default (applies to all subsites that don't override).
 */
function landing_config_set_network_default(string $key, $value): bool {
    return update_site_option('landing_defaults_' . $key, $value);
}

/**
 * Render head extras (counters, OG, GSC, raw HTML) — wp_head action callback.
 * Implementation completed in Phase A4.
 */
function landing_render_head_extras(): void {
    // A4 stub — actual output added in Task 14.
}

/**
 * Get URL/href for a CTA preset — used in theme block.php templates.
 * Implementation completed in Phase A3.
 */
function landing_get_cta(string $preset_name, ?string $url_override = null, array $context = []): string {
    if ($url_override !== null && $url_override !== '') {
        return $url_override;
    }
    $presets = get_option('landing_cta_presets', []);
    if (empty($presets)) {
        $presets = get_site_option('landing_defaults_cta_presets', []);
    }
    $p = $presets[$preset_name] ?? null;
    if (!$p) return '#';

    switch ($p['type']) {
        case 'tel':
            return !empty($p['phone']) ? 'tel:' . preg_replace('/[^0-9+]/', '', $p['phone']) : '#contact-form';
        case 'whatsapp':
            if (empty($p['phone'])) return '#contact-form';
            $msg = $p['message_template'] ?? '';
            $msg = strtr($msg, ['{block_context}' => $context['block_context'] ?? '']);
            foreach ($context as $k => $v) {
                $msg = str_replace('{' . $k . '}', (string)$v, $msg);
            }
            $phone_clean = preg_replace('/[^0-9]/', '', $p['phone']);
            return 'https://wa.me/' . $phone_clean . ($msg !== '' ? '?text=' . rawurlencode($msg) : '');
        case 'mailto':
            return !empty($p['target']) ? 'mailto:' . $p['target'] : '#';
        case 'modal':
            return '#';
        case 'scroll':
        case 'anchor':
            return !empty($p['target']) ? $p['target'] : '#contact-form';
        case 'url':
            return $p['target'] ?? '#';
        default:
            return '#';
    }
}

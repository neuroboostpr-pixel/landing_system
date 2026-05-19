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
    echo "\n<!-- landing-config head extras -->\n";

    $ga4 = landing_config_get('ga4_id');
    if ($ga4 !== '') {
        printf(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%1$s"></script>'
            . '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
            . 'gtag("js",new Date());gtag("config","%1$s");</script>' . "\n",
            esc_attr($ga4)
        );
    }

    $ym = landing_config_get('yandex_metrika_id');
    if ($ym !== '') {
        printf(
            '<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};'
            . 'm[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,'
            . 'a.parentNode.insertBefore(k,a)})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
            . 'ym(%1$s,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true});</script>'
            . '<noscript><div><img src="https://mc.yandex.ru/watch/%1$s" style="position:absolute;left:-9999px"/></div></noscript>'
            . "\n",
            esc_attr($ym)
        );
    }

    $fb = landing_config_get('fb_pixel_id');
    if ($fb !== '') {
        printf(
            '<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","%1$s");fbq("track","PageView");</script>'
            . "\n",
            esc_attr($fb)
        );
    }

    $gsc = landing_config_get('gsc_verification');
    if ($gsc !== '') {
        printf('<meta name="google-site-verification" content="%s">' . "\n", esc_attr($gsc));
    }

    $ym_wm = landing_config_get('yandex_webmaster_id');
    if ($ym_wm !== '') {
        printf('<meta name="yandex-verification" content="%s">' . "\n", esc_attr($ym_wm));
    }

    $og_image = landing_config_get('og_default_image');
    if ($og_image !== '') {
        printf('<meta property="og:image" content="%s">' . "\n", esc_url($og_image));
    }
    $og_title = landing_config_get('og_default_title');
    if ($og_title !== '') {
        printf('<meta property="og:title" content="%s">' . "\n", esc_attr($og_title));
    }
    $og_desc = landing_config_get('og_default_description');
    if ($og_desc !== '') {
        printf('<meta property="og:description" content="%s">' . "\n", esc_attr($og_desc));
    }

    $fonts = landing_config_get('fonts_google_url');
    if ($fonts !== '') {
        printf('<link rel="stylesheet" href="%s">' . "\n", esc_url($fonts));
    }

    $raw = landing_config_get('raw_html_head');
    if ($raw !== '') {
        echo $raw . "\n";
    }

    echo "<!-- /landing-config head extras -->\n";
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

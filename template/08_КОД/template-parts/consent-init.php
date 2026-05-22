<?php
/**
 * Google Consent Mode v2 — default DENIED.
 *
 * Включается в <head> темы ДО загрузки gtag.js, Yandex.Metrica или GTM
 * через get_template_part('template-parts/consent-init').
 *
 * После того как пользователь сохранит выбор в cookie-banner, JS вызовет
 * gtag('consent', 'update', {...}) — увидь cookie-banner.js.
 */
if (!defined('ABSPATH')) { exit; }
?>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'wait_for_update': 500
});
</script>

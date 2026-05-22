/**
 * Cookie-banner — категоризированное согласие с Google Consent Mode v2.
 *
 * Storage: localStorage key lp_cookie_consent = JSON {analytics, marketing, ts, version}.
 * Версия должна совпадать с data-version на #lp-cookie-banner DOM-элементе.
 *
 * При первом визите (или устаревшей версии) — показывает баннер.
 * После save — вызывает gtag('consent','update',...). Скрывает баннер.
 * В footer показывает кнопку 'Настройки cookies' — переоткрывает баннер.
 */
(function() {
    'use strict';

    var STORAGE_KEY = 'lp_cookie_consent';

    var banner = document.getElementById('lp-cookie-banner');
    if (!banner) return;

    var currentVersion = parseInt(banner.dataset.version, 10) || 1;
    var btnAcceptAll = document.getElementById('lp-cookie-accept-all');
    var btnSave = document.getElementById('lp-cookie-save');
    var btnReopen = document.getElementById('lp-cookie-reopen');
    var toggleAnalytics = document.getElementById('lp-cookie-analytics');
    var toggleMarketing = document.getElementById('lp-cookie-marketing');

    function loadConsent() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (typeof parsed !== 'object' || parsed === null) return null;
            return parsed;
        } catch (e) {
            return null;
        }
    }

    function saveConsent(analytics, marketing) {
        var payload = {
            analytics: !!analytics,
            marketing: !!marketing,
            ts: Math.floor(Date.now() / 1000),
            version: currentVersion
        };
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        } catch (e) {
            console.warn('[cookie-banner] localStorage save failed:', e);
        }
        applyGtagConsent(payload);
    }

    function applyGtagConsent(consent) {
        if (typeof window.gtag !== 'function') return;
        window.gtag('consent', 'update', {
            'analytics_storage': consent.analytics ? 'granted' : 'denied',
            'ad_storage': consent.marketing ? 'granted' : 'denied',
            'ad_user_data': consent.marketing ? 'granted' : 'denied',
            'ad_personalization': consent.marketing ? 'granted' : 'denied'
        });
    }

    function showBanner() {
        banner.hidden = false;
        if (btnReopen) btnReopen.hidden = true;
        var existing = loadConsent();
        if (existing) {
            if (toggleAnalytics) toggleAnalytics.checked = !!existing.analytics;
            if (toggleMarketing) toggleMarketing.checked = !!existing.marketing;
        }
    }

    function hideBanner() {
        banner.hidden = true;
        if (btnReopen) btnReopen.hidden = false;
    }

    // Determine on first paint
    var existing = loadConsent();
    if (existing === null || existing.version !== currentVersion) {
        showBanner();
    } else {
        hideBanner();
        applyGtagConsent(existing);
    }

    // Wire up buttons
    if (btnAcceptAll) {
        btnAcceptAll.addEventListener('click', function() {
            saveConsent(true, true);
            hideBanner();
        });
    }
    if (btnSave) {
        btnSave.addEventListener('click', function() {
            saveConsent(
                toggleAnalytics ? toggleAnalytics.checked : false,
                toggleMarketing ? toggleMarketing.checked : false
            );
            hideBanner();
        });
    }
    if (btnReopen) {
        btnReopen.addEventListener('click', function() {
            showBanner();
        });
    }
})();

(function () {
    'use strict';

    var cfg = window.LP_CB_CONFIG;
    if (!cfg) return;

    var banner = document.getElementById('lp-cb');
    var reopen = document.getElementById('lp-cb-reopen');
    if (!banner) return;

    var STORAGE_KEY = cfg.storage_key || 'lp_cookie_consent';

    function loadConsent() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            var parsed = JSON.parse(raw);
            if (typeof parsed !== 'object' || parsed === null) return null;
            return parsed;
        } catch (e) { return null; }
    }

    function saveConsent(consent) {
        var payload = {
            version: cfg.version,
            consent: consent,
            ts: Math.floor(Date.now() / 1000)
        };
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); }
        catch (e) { /* quota — proceed */ }
        applyGtag(consent);
    }

    function applyGtag(consent) {
        if (typeof window.gtag !== 'function') return;
        var update = {};
        var map = cfg.gtag_map || {};
        for (var slug in consent) {
            if (!Object.prototype.hasOwnProperty.call(consent, slug)) continue;
            var keys = map[slug] || [];
            for (var i = 0; i < keys.length; i++) {
                update[keys[i]] = consent[slug] ? 'granted' : 'denied';
            }
        }
        window.gtag('consent', 'update', update);
    }

    function showBanner() { banner.hidden = false; if (reopen) reopen.hidden = true; }
    function hideBanner() { banner.hidden = true;  if (reopen) reopen.hidden = false; }

    function consentFromCheckboxes() {
        var consent = {};
        var inputs = banner.querySelectorAll('[data-slug]');
        for (var i = 0; i < inputs.length; i++) {
            consent[inputs[i].dataset.slug] = !!inputs[i].checked;
        }
        return consent;
    }

    function consentAll(value) {
        var consent = {};
        var cats = cfg.categories || [];
        for (var i = 0; i < cats.length; i++) {
            if (!cats[i].slug) continue;
            consent[cats[i].slug] = cats[i].locked ? true : !!value;
        }
        return consent;
    }

    var existing = loadConsent();
    if (cfg.force_show) {
        // Admin preview mode — show banner regardless of stored consent.
        showBanner();
    } else if (!existing || existing.version !== cfg.version) {
        showBanner();
    } else {
        hideBanner();
        applyGtag(existing.consent || {});
    }

    banner.addEventListener('click', function (e) {
        var el = e.target && e.target.closest ? e.target.closest('[data-action]') : null;
        var action = el ? el.dataset.action : null;
        if (!action) return;
        if (action === 'accept-all') {
            saveConsent(consentAll(true));
            hideBanner();
        } else if (action === 'reject') {
            saveConsent(consentAll(false));
            hideBanner();
        } else if (action === 'save') {
            saveConsent(consentFromCheckboxes());
            hideBanner();
        }
    });
    if (reopen) reopen.addEventListener('click', showBanner);
})();

<?php
/**
 * Cookie-banner — категории necessary / analytics / marketing.
 *
 * Вставляется в footer.php через get_template_part('template-parts/cookie-banner').
 * Появляется при первом визите (если localStorage.lp_cookie_consent отсутствует
 * или версия устарела).
 *
 * Стили в cookie-banner.css. Логика в cookie-banner.js.
 */
if (!defined('ABSPATH')) { exit; }

// Версия согласия — bump при каждом изменении текста policy/consent.
// Должна совпадать с CONSENT_VERSION в cookie-banner.js.
$consent_version = 1;
?>

<div id="lp-cookie-banner" class="lp-cookie-banner" data-version="<?php echo (int) $consent_version; ?>" hidden role="dialog" aria-labelledby="lp-cookie-banner-title">
    <h2 id="lp-cookie-banner-title" class="lp-cookie-banner__title">Мы используем cookies</h2>
    <p class="lp-cookie-banner__desc">Cookies помогают нам обеспечить работу сайта и понять, как вы им пользуетесь. Вы можете выбрать какие категории разрешить.</p>

    <div class="lp-cookie-banner__categories">

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Необходимые</div>
                <div class="lp-cookie-banner__category-desc">Обеспечивают базовую работу сайта (сессия, сохранение выбора в баннере). Не могут быть отключены.</div>
            </div>
            <input type="checkbox" class="lp-cookie-banner__toggle lp-cookie-banner__toggle--locked" checked disabled aria-label="Необходимые cookies (всегда включены)">
        </div>

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Аналитические</div>
                <div class="lp-cookie-banner__category-desc">Помогают понять как посетители используют сайт (Яндекс.Метрика, Google Analytics).</div>
            </div>
            <input type="checkbox" id="lp-cookie-analytics" class="lp-cookie-banner__toggle" aria-label="Аналитические cookies">
        </div>

        <div class="lp-cookie-banner__category">
            <div class="lp-cookie-banner__category-info">
                <div class="lp-cookie-banner__category-name">Маркетинговые</div>
                <div class="lp-cookie-banner__category-desc">Используются для показа релевантной рекламы и ретаргетинга (Facebook Pixel, ВКонтакте, MyTarget).</div>
            </div>
            <input type="checkbox" id="lp-cookie-marketing" class="lp-cookie-banner__toggle" aria-label="Маркетинговые cookies">
        </div>

    </div>

    <div class="lp-cookie-banner__actions">
        <a href="/policy" class="lp-cookie-banner__policy-link" target="_blank">Политика обработки персональных данных</a>
        <button type="button" id="lp-cookie-save" class="lp-cookie-banner__btn lp-cookie-banner__btn--secondary">Сохранить настройки</button>
        <button type="button" id="lp-cookie-accept-all" class="lp-cookie-banner__btn lp-cookie-banner__btn--primary">Принять все</button>
    </div>
</div>

<button type="button" id="lp-cookie-reopen" class="lp-cookie-banner__reopen" hidden>Настройки cookies</button>

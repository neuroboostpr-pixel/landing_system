<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0E2B30">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div class="nu-theme-bar" role="region" aria-label="Переключатель палитры">
    <div class="nu-theme-bar__inner">
        <span class="nu-theme-bar__label">Превью палитры:</span>
        <label class="nu-theme-bar__select-wrap">
            <span class="screen-reader-text">Выбор палитры</span>
            <select class="nu-theme-bar__select" data-theme-switcher>
                <option value="h">H — Бумажный</option>
                <option value="i" selected>I — Тихий-тёмный</option>
                <option value="j">J — Бежевый</option>
                <option value="k">K — IQIDO Guideline</option>
            </select>
        </label>
        <span class="nu-theme-bar__hint">выбор сохраняется</span>
    </div>
</div>

<a class="nu-skip-link" href="#main">Перейти к содержимому</a>

<header class="nu-header" role="banner">
    <div class="nu-container nu-header__inner">
        <a class="nu-header__brand" href="<?php echo esc_url( home_url( '/' ) ); ?>" aria-label="IQIDO — на главную">
            <img
                class="nu-logo nu-logo--light"
                src="<?php echo esc_url( get_template_directory_uri() . '/assets/images/logo-iqido-light.png' ); ?>"
                alt="IQIDO"
                width="120" height="43"
                loading="eager"
                decoding="async">
            <img
                class="nu-logo nu-logo--dark"
                src="<?php echo esc_url( get_template_directory_uri() . '/assets/images/logo-iqido-dark.png' ); ?>"
                alt=""
                width="120" height="43"
                loading="eager"
                decoding="async"
                aria-hidden="true">
        </a>

        <nav class="nu-header__nav" aria-label="Основная навигация">
            <ul class="nu-header__list">
                <li><a href="#program">Программа</a></li>
                <li><a href="#pricing">Тарифы</a></li>
                <li><a href="#author-bio">Об авторе</a></li>
                <li><a href="#faq">FAQ</a></li>
            </ul>
        </nav>

        <a class="nu-btn nu-btn--coral nu-header__cta" href="#cta-final">Записаться</a>

        <button
            type="button"
            class="nu-header__burger"
            aria-label="Открыть меню"
            aria-expanded="false"
            aria-controls="nu-mobile-menu">
            <?php echo lp_render_icon( 'menu', 24 ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
        </button>
    </div>

    <div class="nu-mobile-menu" id="nu-mobile-menu" hidden>
        <ul>
            <li><a href="#program">Программа</a></li>
            <li><a href="#pricing">Тарифы</a></li>
            <li><a href="#author-bio">Об авторе</a></li>
            <li><a href="#faq">FAQ</a></li>
            <li><a class="nu-btn nu-btn--coral nu-btn--block" href="#cta-final">Записаться</a></li>
        </ul>
    </div>
</header>

#!/usr/bin/env bats
# PR-P: verify-composed-premium.sh содержит новые PR-P проверки
# и pass-ит на composed.html который их содержит.

PR_P_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
VERIFY="$PR_P_REPO_ROOT/scripts/verify-composed-premium.sh"

setup() {
    TMP="$(mktemp -d)"
}

teardown() {
    rm -rf "$TMP"
}

@test "verify-composed-premium: новые PR-P паттерны добавлены в CHECKS" {
    # Скрипт должен содержать каждую новую проверку
    grep -q "Scroll-driven анимации" "$VERIFY"
    grep -q "Hover-эффекты (PR-P §15)" "$VERIFY"
    grep -q "Glassmorphism backdrop-filter (PR-P §16)" "$VERIFY"
    grep -q "prefers-reduced-motion media query" "$VERIFY"
    grep -q "Нестандартные формы clip-path" "$VERIFY"
}

@test "verify-composed-premium: оригинальные 13 проверок сохранены" {
    grep -q "CSS-переменные в :root" "$VERIFY"
    grep -q "clamp() для адаптивной типографики" "$VERIFY"
    grep -q "Pulse-dot animation" "$VERIFY"
    grep -q "Lightbox для фото" "$VERIFY"
}

@test "verify-composed-premium: новые PR-Q паттерны добавлены в CHECKS" {
    grep -q "Focus-visible на интерактивах" "$VERIFY"
    grep -q "<title> с контентом" "$VERIFY"
    grep -q "<meta name=description" "$VERIFY"
    grep -q "OpenGraph мета-теги" "$VERIFY"
    grep -q "<meta viewport" "$VERIFY"
    grep -q "<html lang=" "$VERIFY"
    grep -q "Favicon link" "$VERIFY"
}

@test "verify-composed-premium: PR-Q v2 — typography/form/perf/touch проверки добавлены" {
    grep -q "tabular-nums для статистики" "$VERIFY"
    grep -q "text-wrap balance/pretty" "$VERIFY"
    grep -q "autocomplete= на полях" "$VERIFY"
    grep -q "type=email/tel/url/number" "$VERIFY"
    grep -q "loading=lazy на below-fold" "$VERIFY"
    grep -q "preconnect" "$VERIFY"
    grep -q "font-display: swap" "$VERIFY"
    grep -q "touch-action: manipulation" "$VERIFY"
    grep -q "env(safe-area-inset)" "$VERIFY"
    grep -q "<meta theme-color" "$VERIFY"
    grep -q "color-scheme CSS или meta" "$VERIFY"
}

@test "verify-composed-premium: PR-Q v2 — anti-patterns секция добавлена" {
    grep -q "ANTI_CHECKS" "$VERIFY"
    grep -q "user-scalable=no" "$VERIFY"
    grep -q "transition: all" "$VERIFY"
    grep -q "<div onclick" "$VERIFY"
    grep -q "onpaste с блокировкой" "$VERIFY"
}

@test "verify-composed-premium: pass на полном premium composed.html" {
    cat > "$TMP/composed.html" <<'HTML'
<!doctype html><html lang="ru"><head>
<title>Premium landing — test</title>
<meta name="description" content="Test premium landing">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0a1628">
<meta name="color-scheme" content="dark light">
<meta property="og:title" content="Premium">
<meta property="og:description" content="Desc">
<meta property="og:image" content="og.jpg">
<link rel="icon" href="data:image/svg+xml,<svg/>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
:root { --c: #000; --t: 0.3s; color-scheme: dark; }
@font-face { font-family: 'X'; font-display: swap; src: url(x.woff2); }
h1 { font-size: clamp(40px, 6vw, 80px); text-wrap: balance; }
.stat-number { font-variant-numeric: tabular-nums; }
.btn { touch-action: manipulation; padding-top: max(20px, env(safe-area-inset-top)); }
.nav.scrolled { backdrop-filter: blur(20px) saturate(180%); }
.reveal { opacity: 0; }
.reveal.visible { opacity: 1; }
.accent { -webkit-text-fill-color: transparent; background-clip: text; }
.card:hover { transform: translateY(-4px); }
.card { transition: transform 0.3s, opacity 0.3s; }
.slider-track { display: flex; }
.lightbox { position: fixed; }
html { scroll-behavior: smooth; }
@keyframes pulse { 0% { opacity: 1; } 100% { opacity: 0.5; } }
.angled { clip-path: polygon(0 0, 100% 0, 100% 90%, 0 100%); }
.text-overlay { mix-blend-mode: difference; }
@media (prefers-reduced-motion: no-preference) { .reveal { transition: 0.7s; } }
.btn:hover { transform: translateY(-3px); }
.btn:focus-visible { outline: 2px solid gold; outline-offset: 4px; }
</style></head>
<body>
<nav data-scroll-reveal></nav>
<form>
  <input type="email" name="email" autocomplete="email" placeholder="Email…">
  <input type="tel" name="phone" autocomplete="tel" placeholder="Телефон…">
</form>
<img src="below.jpg" width="600" height="400" loading="lazy" alt="">
<script>
const hero = document.querySelector('.hero-bg');
if (hero) hero.style.transform = 'translateY(' + (window.scrollY * 0.3) + 'px)';
const obs = new IntersectionObserver(() => {}, {});
function step() { requestAnimationFrame(step); } // count-up
</script>
</body></html>
HTML
    run bash "$VERIFY" "$TMP/composed.html"
    [ "$status" -eq 0 ]
}

@test "verify-composed-premium: fail на минимальном HTML без премиум-фич" {
    cat > "$TMP/bad.html" <<'HTML'
<!doctype html><html><body><h1>Hello</h1></body></html>
HTML
    run bash "$VERIFY" "$TMP/bad.html"
    [ "$status" -eq 1 ]
    # И конкретно — наши новые проверки должны падать
    echo "$output" | grep -q "Scroll-driven"
    echo "$output" | grep -q "Glassmorphism backdrop-filter"
    echo "$output" | grep -q "Focus-visible"
    echo "$output" | grep -q "OpenGraph"
    echo "$output" | grep -q "Favicon"
    echo "$output" | grep -q "tabular-nums"
    echo "$output" | grep -q "touch-action"
}

@test "verify-composed-premium: anti-pattern user-scalable=no — FAIL" {
    cat > "$TMP/anti.html" <<'HTML'
<!doctype html><html lang="ru"><head>
<title>X</title>
<meta name="description" content="X">
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
<meta name="theme-color" content="#000">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="X">
<meta property="og:image" content="x.jpg">
<meta property="og:description" content="X">
<link rel="icon" href="data:image/svg+xml,<svg/>">
<link rel="preconnect" href="https://x.com">
<style>
:root { --c: #000; color-scheme: dark; }
@font-face { font-family: X; font-display: swap; }
h1 { font-size: clamp(40px, 6vw, 80px); text-wrap: balance; }
.s { font-variant-numeric: tabular-nums; }
.btn { touch-action: manipulation; padding: env(safe-area-inset-top); }
.btn:focus-visible { outline: 2px solid red; }
.btn:hover { transform: translateY(-3px); }
.reveal { opacity: 0; backdrop-filter: blur(10px); }
.r { -webkit-text-fill-color: transparent; }
.s2 { clip-path: circle(50%); }
@media (prefers-reduced-motion: no-preference) {}
@keyframes pulse { 0% {} }
.slider-track {} .lightbox {}
</style></head>
<body>
<form><input type="email" autocomplete="email"></form>
<img src="x.jpg" loading="lazy" width="1" height="1">
<script>new IntersectionObserver(()=>{},{});requestAnimationFrame(()=>{});const y=window.scrollY*0.3;</script>
</body></html>
HTML
    run bash "$VERIFY" "$TMP/anti.html"
    [ "$status" -eq 1 ]
    echo "$output" | grep -q "user-scalable=no"
}

@test "verify-composed-premium: anti-pattern transition: all — FAIL" {
    # минимальный HTML с одним anti-pattern
    cat > "$TMP/anti2.html" <<'HTML'
<style>.x { transition: all 0.3s; }</style>
HTML
    run bash "$VERIFY" "$TMP/anti2.html"
    [ "$status" -eq 1 ]
    echo "$output" | grep -q "transition: all"
}

@test "verify-composed-premium: anti-pattern <div onclick=> — FAIL" {
    cat > "$TMP/anti3.html" <<'HTML'
<div onclick="alert(1)">click</div>
HTML
    run bash "$VERIFY" "$TMP/anti3.html"
    [ "$status" -eq 1 ]
    echo "$output" | grep -qE "div onclick|<span onclick"
}

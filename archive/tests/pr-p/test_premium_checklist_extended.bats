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

@test "verify-composed-premium: pass на полном premium composed.html" {
    cat > "$TMP/composed.html" <<'HTML'
<!doctype html><html><head><style>
:root { --c: #000; --t: 0.3s; }
h1 { font-size: clamp(40px, 6vw, 80px); }
.nav.scrolled { backdrop-filter: blur(20px) saturate(180%); }
.reveal { opacity: 0; }
.reveal.visible { opacity: 1; }
.accent { -webkit-text-fill-color: transparent; background-clip: text; }
.card:hover { transform: translateY(-4px); }
.slider-track { display: flex; }
.lightbox { position: fixed; }
html { scroll-behavior: smooth; }
@keyframes pulse { 0% { opacity: 1; } 100% { opacity: 0.5; } }
.angled { clip-path: polygon(0 0, 100% 0, 100% 90%, 0 100%); }
.text-overlay { mix-blend-mode: difference; }
@media (prefers-reduced-motion: no-preference) { .reveal { transition: 0.7s; } }
.btn:hover { transform: translateY(-3px); }
</style></head>
<body>
<nav data-scroll-reveal></nav>
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
}

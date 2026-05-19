#!/usr/bin/env bash
# verify-composed-premium.sh — проверяет, что composed.html соответствует
# premium-07b-checklist.md (обязательные интерактивные фичи).
#
# Usage: verify-composed-premium.sh <path-to-composed.html>
# Exit codes:
#   0 — все premium-фичи найдены
#   1 — одна или несколько фич отсутствуют
#   2 — файл не найден
#
# Полный стандарт: docs/standards/premium-07b-checklist.md

set -uo pipefail

FILE="${1:?ERROR: composed.html path required}"

[ -f "$FILE" ] || {
    echo "ERROR: composed.html not found at $FILE" >&2
    exit 2
}

# Format: each line is "PATTERN<TAB>DESCRIPTION"
# Pattern is a basic grep -E regex (ERE).
CHECKS=$(cat <<'EOF'
:root[[:space:]]*\{	CSS-переменные в :root
clamp\(	clamp() для адаптивной типографики
backdrop-filter:[[:space:]]*blur	Glassmorphism nav (backdrop-filter blur)
(scrollY|[^a-zA-Z_0-9]y)[[:space:]]*\*[[:space:]]*0\.[0-9]	Parallax hero (scrollY * 0.x)
IntersectionObserver	IntersectionObserver для reveal/count-up
\.reveal[^-a-z]	CSS-класс .reveal для fade-in
text-fill-color:[[:space:]]*transparent	Gradient text (background-clip)
translateY\(-[0-9]	Hover lift (translateY -Npx)
slider-track|swiper|slick	Слайдер (slider-track / swiper / slick)
lightbox	Lightbox для фото
requestAnimationFrame|count-up	Count-up анимация
scroll-behavior:[[:space:]]*smooth|behavior:[[:space:]]*['\"]smooth	Smooth scroll
@keyframes[[:space:]]+pulse	Pulse-dot animation
scroll-timeline|IntersectionObserver|data-scroll-reveal	Scroll-driven анимации (PR-P §14)
:hover[[:space:]]*\{	Hover-эффекты (PR-P §15)
backdrop-filter:	Glassmorphism backdrop-filter (PR-P §16)
@media[[:space:]]*\([[:space:]]*prefers-reduced-motion	prefers-reduced-motion media query (PR-P §19)
clip-path:|mask-image:	Нестандартные формы clip-path/mask (PR-P §20)
:focus-visible|:focus[[:space:]]*\{	Focus-visible на интерактивах (PR-Q §22)
<title>[^<]	<title> с контентом (PR-Q §24)
<meta[[:space:]]+name=[\"']description[\"']	<meta name=description (PR-Q §24)
<meta[[:space:]]+property=[\"']og:(title|image|description)	OpenGraph мета-теги (PR-Q §24)
<meta[[:space:]]+name=[\"']viewport[\"']	<meta viewport (PR-Q §24)
<html[[:space:]]+lang=	<html lang="..." (PR-Q §24)
<link[[:space:]]+rel=[\"']icon[\"']|<link[[:space:]]+rel=[\"']shortcut icon	Favicon link (PR-Q §24)
font-variant-numeric:[[:space:]]*tabular-nums	tabular-nums для статистики (PR-Q §25)
text-wrap:[[:space:]]*(balance|pretty)	text-wrap balance/pretty на заголовках (PR-Q §25)
autocomplete=[\"'][a-z]	autocomplete= на полях формы (PR-Q §26)
type=[\"'](email|tel|url|number)[\"']	Корректный type=email/tel/url/number (PR-Q §26)
loading=[\"']lazy[\"']	loading=lazy на below-fold картинках (PR-Q §28)
<link[[:space:]]+rel=[\"']preconnect[\"']	<link rel=preconnect для CDN/fonts (PR-Q §28)
font-display:[[:space:]]*swap|display=swap	font-display: swap (PR-Q §28)
touch-action:[[:space:]]*manipulation	touch-action: manipulation (PR-Q §29)
env\(safe-area-inset	env(safe-area-inset) для нотчей (PR-Q §29)
<meta[[:space:]]+name=[\"']theme-color[\"']	<meta theme-color (PR-Q §29)
color-scheme:|<meta[[:space:]]+name=[\"']color-scheme[\"']	color-scheme CSS или meta (PR-Q §29)
EOF
)

# Anti-patterns — НЕ должны встречаться. Если найдено — FAIL.
# Format: PATTERN<TAB>DESCRIPTION
ANTI_CHECKS=$(cat <<'EOF'
user-scalable=no	Запрет zoom user-scalable=no (Anti-pattern, accessibility violation)
maximum-scale=1[^0-9]	maximum-scale=1 блокирует zoom (Anti-pattern)
transition:[[:space:]]*all[[:space:]]	transition: all — антипаттерн анимации (PR-Q §27)
<(div|span)[[:space:]][^>]*[Oo]n[Cc]lick=	<div onclick=> / <span onclick=> вместо <button> (PR-Q §27)
onpaste=[\"'][^\"']*(return[[:space:]]+false|preventDefault)	onpaste с блокировкой вставки (PR-Q §26)
EOF
)

PASS=0
FAIL=0
FAILED_LIST=()

echo "═══════════════════════════════════════════════════════"
echo "Premium 07b verify — $FILE"
echo "═══════════════════════════════════════════════════════"

while IFS=$'\t' read -r pattern desc; do
    [ -z "$pattern" ] && continue
    if grep -qE -- "$pattern" "$FILE" 2>/dev/null; then
        printf "  \033[32m✓\033[0m  %s\n" "$desc"
        PASS=$((PASS + 1))
    else
        printf "  \033[31m✗\033[0m  %s\n" "$desc"
        FAIL=$((FAIL + 1))
        FAILED_LIST+=("$desc")
    fi
done <<< "$CHECKS"

# Anti-patterns — найдено = FAIL
echo "───────────────────────────────────────────────────────"
echo "Anti-patterns check (must NOT be present)"
echo "───────────────────────────────────────────────────────"

ANTI_FAIL=0
ANTI_FAILED_LIST=()

while IFS=$'\t' read -r pattern desc; do
    [ -z "$pattern" ] && continue
    if grep -qE -- "$pattern" "$FILE" 2>/dev/null; then
        printf "  \033[31m✗\033[0m  НАЙДЕНО: %s\n" "$desc"
        ANTI_FAIL=$((ANTI_FAIL + 1))
        ANTI_FAILED_LIST+=("$desc")
    else
        printf "  \033[32m✓\033[0m  отсутствует: %s\n" "$desc"
    fi
done <<< "$ANTI_CHECKS"

echo "───────────────────────────────────────────────────────"
echo "Positive: $PASS / $((PASS + FAIL))     Anti-patterns: $ANTI_FAIL found"

if [ "$FAIL" -gt 0 ] || [ "$ANTI_FAIL" -gt 0 ]; then
    echo ""
    echo "❌ HARD GATE 07b НЕ ПРОЙДЕН — composed.html не соответствует premium-стандарту."
    if [ "$FAIL" -gt 0 ]; then
        echo ""
        echo "Отсутствуют premium-фичи:"
        for f in "${FAILED_LIST[@]}"; do
            echo "  • $f"
        done
    fi
    if [ "$ANTI_FAIL" -gt 0 ]; then
        echo ""
        echo "Найдены запрещённые anti-patterns:"
        for f in "${ANTI_FAILED_LIST[@]}"; do
            echo "  • $f"
        done
    fi
    echo ""
    echo "См. полный стандарт: docs/standards/premium-07b-checklist.md"
    exit 1
fi

echo ""
echo "✅ Все premium-фичи на месте, anti-patterns отсутствуют. HARD GATE 07b можно проходить."
exit 0

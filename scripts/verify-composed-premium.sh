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

echo "───────────────────────────────────────────────────────"
echo "Passed: $PASS / $((PASS + FAIL))"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "❌ HARD GATE 07b НЕ ПРОЙДЕН — composed.html не соответствует premium-стандарту."
    echo ""
    echo "Отсутствуют:"
    for f in "${FAILED_LIST[@]}"; do
        echo "  • $f"
    done
    echo ""
    echo "См. полный стандарт: docs/standards/premium-07b-checklist.md"
    exit 1
fi

echo ""
echo "✅ Все premium-фичи на месте. HARD GATE 07b можно проходить."
exit 0

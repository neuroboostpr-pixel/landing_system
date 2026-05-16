#!/usr/bin/env bash
# scripts/landing-final-check.sh — bundle всех verify-скриптов системы.
set -uo pipefail

PROJECT="${1:?ERROR: project required}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_DIR="$PROJECT/10_QA"
REPORT="$REPORT_DIR/final-check-report.md"

mkdir -p "$REPORT_DIR"

# Список проверок: имя, скрипт, обязательная ли (пути в одинарных кавычках для безопасности с пробелами)
CHECKS=(
    "wiki-sync|bash '$REPO_ROOT/scripts/check-wiki-sync.sh'|no"
    "composed-premium|bash '$REPO_ROOT/scripts/verify-composed-premium.sh' '$PROJECT/07b_COMPOSED/composed.html'|yes"
    "content-preserved|bash '$REPO_ROOT/scripts/verify-content-preserved.sh' '$PROJECT'|yes"
    "photo-pipeline|bash '$REPO_ROOT/scripts/verify-photo-pipeline.sh' '$PROJECT'|yes"
    "identity-preserved|bash '$REPO_ROOT/scripts/verify-identity-preserved.sh' '$PROJECT'|yes"
    "visual-qa|bash '$REPO_ROOT/scripts/verify-visual-qa.sh' '$PROJECT'|no"
)

declare -a RESULTS
TOTAL_FAIL=0

{
    echo "# Final Check Report"
    echo ""
    echo "**Дата:** $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**Проект:** $(basename "$PROJECT")"
    echo ""
    echo "## Результаты"
    echo ""
} > "$REPORT"

for entry in "${CHECKS[@]}"; do
    IFS='|' read -r NAME CMD REQUIRED <<< "$entry"
    echo "▶ $NAME..." >&2
    OUTPUT=$(eval "$CMD" 2>&1) || EXIT=$?
    EXIT="${EXIT:-0}"

    if [ "$EXIT" -eq 0 ]; then
        STATUS="✅ PASS"
    elif [ "$REQUIRED" = "yes" ]; then
        STATUS="❌ FAIL"
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    else
        STATUS="⚠️ WARN (optional)"
    fi

    {
        echo "### $NAME — $STATUS"
        echo ""
        echo '```'
        echo "$OUTPUT" | head -20
        echo '```'
        echo ""
    } >> "$REPORT"

    RESULTS+=("$NAME: $STATUS")
    unset EXIT
done

echo "" >> "$REPORT"
if [ "$TOTAL_FAIL" -eq 0 ]; then
    echo "## ✅ Итог: ВСЕ обязательные проверки прошли" >> "$REPORT"
    SUMMARY="✅ Final check: PASS"
else
    echo "## ❌ Итог: $TOTAL_FAIL обязательных проверок FAIL" >> "$REPORT"
    SUMMARY="❌ Final check: FAIL ($TOTAL_FAIL)"
fi

echo ""
echo "$SUMMARY"
echo "📄 Отчёт: $REPORT"

for r in "${RESULTS[@]}"; do
    echo "  - $r"
done

[ "$TOTAL_FAIL" -eq 0 ] && exit 0 || exit 1

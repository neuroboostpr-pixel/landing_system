#!/usr/bin/env bash
# check_legal_blocks.sh — проверяет что в сгенерированной wp-theme есть
# cookie-banner, legal-block, consent-init.
#
# Usage: bash check_legal_blocks.sh <project-dir>
# Exit: 0 если всё OK, 1 если чего-то не хватает.

set -euo pipefail

PROJECT="${1:-}"
if [ -z "$PROJECT" ]; then
    echo "Usage: $0 <project-dir>" >&2
    exit 2
fi

THEME_DIR="$PROJECT/08_КОД/wp-theme"
[ -d "$THEME_DIR" ] || { echo "FAIL: theme dir not found: $THEME_DIR"; exit 1; }

MISSING=()

# 1. cookie-banner.php присутствует
[ -f "$THEME_DIR/template-parts/cookie-banner.php" ] || MISSING+=("cookie-banner.php")
# 2. consent-init.php присутствует
[ -f "$THEME_DIR/template-parts/consent-init.php" ] || MISSING+=("consent-init.php")
# 3. legal-block.php присутствует
[ -f "$THEME_DIR/template-parts/legal-block.php" ] || MISSING+=("legal-block.php")
# 4. footer.php содержит вызов cookie-banner
if [ -f "$THEME_DIR/footer.php" ]; then
    grep -q "cookie-banner" "$THEME_DIR/footer.php" || MISSING+=("footer.php missing cookie-banner reference")
else
    MISSING+=("footer.php")
fi
# 5. header.php содержит consent-init (ДО analytics)
if [ -f "$THEME_DIR/header.php" ]; then
    grep -q "consent-init" "$THEME_DIR/header.php" || MISSING+=("header.php missing consent-init reference")
else
    MISSING+=("header.php")
fi
# 6. Хотя бы один блок-шаблон ссылается на legal-block
BLOCK_REFS=$(grep -rl "legal-block" "$THEME_DIR/blocks/" 2>/dev/null | wc -l)
if [ "$BLOCK_REFS" -lt 1 ]; then
    MISSING+=("no block templates reference legal-block (forms missing PD checkbox)")
fi

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "✅ legal_blocks_present: OK"
    exit 0
fi

echo "❌ legal_blocks_present: missing:"
for m in "${MISSING[@]}"; do
    echo "   - $m"
done
exit 1

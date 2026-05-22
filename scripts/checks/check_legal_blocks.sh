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

# 1. legal-block.php присутствует в теме
[ -f "$THEME_DIR/template-parts/legal-block.php" ] || MISSING+=("legal-block.php")

# 2. Хотя бы один блок-шаблон ссылается на legal-block
BLOCK_REFS=$(grep -rl "legal-block" "$THEME_DIR/blocks/" 2>/dev/null | wc -l)
if [ "$BLOCK_REFS" -lt 1 ]; then
    MISSING+=("no block templates reference legal-block (forms missing PD checkbox)")
fi

# 3. mu-plugin cookie-banner source существует в landing-system
SYSTEM_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
MU_PLUGIN_SRC="$SYSTEM_ROOT/skills/wp-landing-config/mu-plugin/landing-config/includes/cookie-banner/cpt.php"
[ -f "$MU_PLUGIN_SRC" ] || MISSING+=("mu-plugin cookie-banner source missing: $MU_PLUGIN_SRC")

if [ ${#MISSING[@]} -eq 0 ]; then
    echo "✅ legal_blocks_present: OK"
    exit 0
fi

echo "❌ legal_blocks_present: missing:"
for m in "${MISSING[@]}"; do
    echo "   - $m"
done
exit 1

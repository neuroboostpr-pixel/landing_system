#!/usr/bin/env bash
# codex-generate-fallback.sh — generate ONE photo via codex image_gen for a missing slot.
# Clones generate-atlas.sh pattern: snapshot ~/.codex/generated_images, exec, copy fresh PNG.
#
# Usage:
#   bash codex-generate-fallback.sh <project_dir> <slot_id> <width> <height> <ratio> <slot_hint>
#
# Env:
#   CODEX_BIN  — path to codex binary (default: codex). Override for testing.
#   FORCE=1    — overwrite existing ai-generated.jpg

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_ID="${2:?ERROR: slot_id required}"
WIDTH="${3:?ERROR: width required}"
HEIGHT="${4:?ERROR: height required}"
RATIO="${5:?ERROR: ratio required}"
SLOT_HINT="${6:?ERROR: slot_hint required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/generate-fallback.md"

OUT_DIR="$PROJECT_DIR/07c_PHOTOS/processed/$SLOT_ID"
mkdir -p "$OUT_DIR"
OUT_JPG="$OUT_DIR/ai-generated.jpg"

# Skip-if-exists (FORCE=1 overrides)
if [ -f "$OUT_JPG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_JPG exists. Set FORCE=1 to override."
    exit 0
fi

# Extract prompt body and substitute positional placeholders
RAW_FILE="$(mktemp)"
python3 - "$TEMPLATE" "$WIDTH" "$HEIGHT" "$RATIO" "$SLOT_HINT" "$RAW_FILE" <<'PYEOF'
import re, sys
template, width, height, ratio, slot_hint, raw_out = sys.argv[1:7]
text = open(template).read()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: generate-fallback.md missing Prompt body section")
body = m.group(1)
body = body.replace("[WIDTH]", width).replace("[HEIGHT]", height)
body = body.replace("[RATIO]", ratio).replace("[SLOT_HINT]", slot_hint)
with open(raw_out, "w") as f:
    f.write(body)
PYEOF

# Render remaining brand/design placeholders (VISUAL_STYLE, BRAND_MOOD, etc.)
PROMPT_FILE="$(mktemp)"
python3 "$SCRIPT_DIR/render-prompt.py" "$RAW_FILE" "$PROJECT_DIR" > "$PROMPT_FILE"
rm -f "$RAW_FILE"

# Save the rendered prompt for reference
cp "$PROMPT_FILE" "$OUT_DIR/ai-prompt.txt"

# Snapshot existing codex image dirs (paralaximus pattern from generate-atlas.sh)
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
echo "→ Generating fallback for slot $SLOT_ID..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >&2 || {
    rc=$?
    echo "ERROR: codex exec failed (rc=$rc)" >&2
    rm -f "$PROMPT_FILE" "$TMP_BEFORE"
    exit "$rc"
}
rm -f "$PROMPT_FILE"

# Find new session dir created during this run
TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER"

# Fall back to most-recent dir if comm found nothing (codex reused an existing session)
if [ -z "$NEW_DIR" ]; then
    echo "WARN: no new session dir detected — falling back to most-recent dir" >&2
    NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
fi

[ -n "$NEW_DIR" ] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_PNG="$(ls -1t "$HOME/.codex/generated_images/$NEW_DIR"/*.png 2>/dev/null | head -1 || true)"
[ -n "$SRC_PNG" ] || { echo "ERROR: no PNG produced in $HOME/.codex/generated_images/$NEW_DIR" >&2; exit 4; }

# Convert PNG → JPG via Pillow
python3 -c "
from PIL import Image
img = Image.open('$SRC_PNG').convert('RGB')
img.save('$OUT_JPG', 'JPEG', quality=88)
"
SIZE_KB=$(( $(stat -f%z "$OUT_JPG" 2>/dev/null || stat -c%s "$OUT_JPG") / 1024 ))
echo "→ Source kept at: $SRC_PNG"
echo "✓ Generated: $OUT_JPG (${SIZE_KB} KB)"

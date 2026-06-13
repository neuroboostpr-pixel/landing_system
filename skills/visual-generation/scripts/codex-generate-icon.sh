#!/usr/bin/env bash
# codex-generate-icon.sh — generate ONE PNG icon via codex image_gen.
# Clones paralaximus generate-atlas.sh snapshot+comm+copy pattern.
#
# Usage:
#   bash codex-generate-icon.sh <project_dir> <slot_name> <hint>

set -euo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../../scripts/lib/python-cmd.sh
. "$__SCRIPT_DIR__/../../../scripts/lib/python-cmd.sh"
PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_NAME="${2:?ERROR: slot_name required}"
HINT="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/icon-prompt.md"

OUT_DIR="$PROJECT_DIR/07d_VISUALS/icons"
mkdir -p "$OUT_DIR"
OUT_PNG="$OUT_DIR/${SLOT_NAME}.png"

# Skip-if-exists (open-design imagegen.ts pattern)
if [ -f "$OUT_PNG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_PNG exists. Set FORCE=1 to override."
    exit 0
fi

# Render prompt by extracting body from template + substituting placeholders
PROMPT_FILE="$(mktemp)"
$PYTHON_CMD - "$TEMPLATE" "$PROJECT_DIR" "$HINT" "$SLOT_NAME" "$PROMPT_FILE" <<'PYEOF'
import sys, re, json
from pathlib import Path

template_path = sys.argv[1]
project_dir = sys.argv[2]
hint = sys.argv[3]
slot_name = sys.argv[4]
out_file = sys.argv[5]

text = Path(template_path).read_text(encoding="utf-8")
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: icon-prompt.md missing Prompt body section")
body = m.group(1)

# Load brand context from tokens.json
tokens_path = Path(project_dir) / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
tokens = json.loads(tokens_path.read_text(encoding="utf-8")) if tokens_path.exists() else {}
brand_accent = tokens.get("colors", {}).get("accent", "#1e3a8a")
visual_style = tokens.get("design", {}).get("visual_style", "Minimalism")
icon_style = tokens.get("design", {}).get("icon_style", "outlined")

# Niche
niche = ""
niche_path = Path(project_dir) / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
if niche_path.exists():
    nm = re.search(r"\*\*Niche:\*\*\s*(.+)$", niche_path.read_text(encoding="utf-8"), re.MULTILINE)
    if nm:
        niche = nm.group(1).strip()

slot_hint = hint if hint else slot_name.replace("-", " ").replace("_", " ")
chroma = "#00ff00"

body = (body
    .replace("[SLOT_HINT]", slot_hint)
    .replace("[VISUAL_STYLE]", visual_style)
    .replace("[BRAND_ACCENT]", brand_accent)
    .replace("[ICON_STYLE]", icon_style)
    .replace("[NICHE]", niche)
    .replace("[CHROMA_KEY]", chroma))

Path(out_file).write_text(body)
PYEOF

# Snapshot existing codex image dirs
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07d_VISUALS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_icon_${SLOT_NAME}.log"

{
    echo "=== ICON GEN: $SLOT_NAME ($HINT) ==="
    echo "=== PROMPT ==="
    cat "$PROMPT_FILE"
    echo "=== RESPONSE ==="
} > "$LOG"

echo "→ Generating icon: $SLOT_NAME..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >>"$LOG" 2>&1 || {
    rc=$?
    echo "ERROR: codex exec failed (rc=$rc). See $LOG" >&2
    rm -f "$PROMPT_FILE" "$TMP_BEFORE"
    exit "$rc"
}

TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER" "$PROMPT_FILE"

[ -n "$NEW_DIR" ] || NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
[ -n "$NEW_DIR" ] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_PNG="$(ls -1t "$HOME/.codex/generated_images/$NEW_DIR"/*.png 2>/dev/null | head -1 || true)"
[ -n "$SRC_PNG" ] || { echo "ERROR: no PNG produced" >&2; exit 4; }

cp "$SRC_PNG" "$OUT_PNG"
echo "✓ Icon generated: $OUT_PNG"

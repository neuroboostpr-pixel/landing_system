#!/usr/bin/env bash
# codex-generate-infographic.sh — generate ONE PNG infographic via codex image_gen.
#
# Usage:
#   bash codex-generate-infographic.sh <project_dir> <slot_name> <chart_type> <data_json>

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
SLOT_NAME="${2:?ERROR: slot_name required}"
CHART_TYPE="${3:-number}"
DATA_JSON="${4:-{}}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../templates/infographic-prompt.md"

OUT_DIR="$PROJECT_DIR/07d_VISUALS/infographics"
mkdir -p "$OUT_DIR"
OUT_PNG="$OUT_DIR/${SLOT_NAME}.png"

if [ -f "$OUT_PNG" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "SKIP: $OUT_PNG exists. Set FORCE=1 to override."
    exit 0
fi

PROMPT_FILE="$(mktemp)"
python3 - "$TEMPLATE" "$PROJECT_DIR" "$CHART_TYPE" "$DATA_JSON" "$PROMPT_FILE" <<'PYEOF'
import sys, re, json
from pathlib import Path

template_path, project_dir, chart_type, data_json, out_file = sys.argv[1:6]

text = Path(template_path).read_text()
m = re.search(r"## Prompt body\s*\n+```\s*\n(.+?)\n```", text, re.DOTALL)
if not m:
    sys.exit("ERROR: infographic-prompt.md missing Prompt body section")
body = m.group(1)

tokens_path = Path(project_dir) / "05_ДИЗАЙН-СИСТЕМА" / "tokens.json"
tokens = json.loads(tokens_path.read_text()) if tokens_path.exists() else {}
brand_accent = tokens.get("colors", {}).get("accent", "#1e3a8a")
visual_style = tokens.get("design", {}).get("visual_style", "Minimalism")

niche = ""
niche_path = Path(project_dir) / "01a_АНАЛИЗ_НИШИ" / "market-profile.md"
if niche_path.exists():
    nm = re.search(r"\*\*Niche:\*\*\s*(.+)$", niche_path.read_text(), re.MULTILINE)
    if nm:
        niche = nm.group(1).strip()

body = (body
    .replace("[CHART_TYPE]", chart_type)
    .replace("[CHART_DATA]", data_json)
    .replace("[VISUAL_STYLE]", visual_style)
    .replace("[BRAND_ACCENT]", brand_accent)
    .replace("[NICHE]", niche)
    .replace("[CHROMA_KEY]", "#00ff00"))

Path(out_file).write_text(body)
PYEOF

TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

CODEX_BIN="${CODEX_BIN:-codex}"
LOGS_DIR="$PROJECT_DIR/07d_VISUALS/.logs"
mkdir -p "$LOGS_DIR"
TS="$(date +%Y-%m-%d_%H%M%S)"
LOG="$LOGS_DIR/${TS}_infographic_${SLOT_NAME}.log"

{
    echo "=== INFOGRAPHIC GEN: $SLOT_NAME ($CHART_TYPE) ==="
    echo "=== PROMPT ==="
    cat "$PROMPT_FILE"
    echo "=== RESPONSE ==="
} > "$LOG"

echo "→ Generating infographic: $SLOT_NAME..."
"$CODEX_BIN" exec --skip-git-repo-check "$(cat "$PROMPT_FILE")" >>"$LOG" 2>&1 || {
    rc=$?
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
echo "✓ Infographic generated: $OUT_PNG"

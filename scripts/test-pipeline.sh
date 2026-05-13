#!/usr/bin/env bash
# test-pipeline.sh — Complete PR-A test for ANY project in one command.
#
# Creates a new project, drops a prototype, runs the full pipeline:
#   prototype.md/pdf  →  prototype.yaml  →  wireframe.html  →  composed.html
#
# Usage:
#   bash scripts/test-pipeline.sh <slug> <path-to-prototype>
#
# Examples:
#   bash scripts/test-pipeline.sh coffee-shop ~/Downloads/my-prototype.pdf
#   bash scripts/test-pipeline.sh saas-product ./samples/example-prototype.md
#   bash scripts/test-pipeline.sh leysan-dubai ~/Downloads/Книга.pdf
#
# Optional env vars:
#   TOKENS_FILE   — path to existing tokens.json. Default: built-in stub
#   NICHE         — services|b2c|local. Default: derived from prototype or asks
#   SKIP_OPEN     — set to 1 to skip opening files at the end

set -euo pipefail

SLUG="${1:-}"
PROTOTYPE="${2:-}"

if [ -z "$SLUG" ] || [ -z "$PROTOTYPE" ]; then
  cat <<EOF >&2
Usage: $0 <slug> <path-to-prototype>

  <slug>             — kebab-case project name (e.g. coffee-shop, saas-product)
  <path-to-prototype> — your prototype file (.md or .pdf)

Example:
  $0 coffee-shop ~/Downloads/coffee-prototype.pdf
EOF
  exit 1
fi

# --- Resolve paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT="$HOME/Lendings/$SLUG"

# Resolve absolute path of prototype (handle ~ and relative)
PROTOTYPE_ABS="$(cd "$(dirname "$PROTOTYPE")" 2>/dev/null && pwd)/$(basename "$PROTOTYPE")" || {
  echo "❌ Prototype file not found: $PROTOTYPE" >&2
  exit 2
}
[ -f "$PROTOTYPE_ABS" ] || { echo "❌ Prototype not found: $PROTOTYPE_ABS" >&2; exit 2; }

EXT="${PROTOTYPE_ABS##*.}"
case "$EXT" in
  md|MD|markdown)  PROTO_KIND="md"  ;;
  pdf|PDF)         PROTO_KIND="pdf" ;;
  *)
    echo "❌ Unsupported prototype format: .$EXT (only .md and .pdf supported)" >&2
    exit 3
    ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ PR-A Test Pipeline                                          ║"
echo "║                                                              ║"
echo "║ Project slug : $SLUG"
echo "║ Prototype     : $PROTOTYPE_ABS"
echo "║ Format        : $PROTO_KIND"
echo "║ Output folder : $PROJECT"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# --- Step 1: Create project ---
if [ -d "$PROJECT" ]; then
  echo "⚠️  Project folder already exists at $PROJECT"
  echo "   Skipping init.sh (will overwrite per-project artifacts only)."
else
  echo "▸ Step 1/6: Create project from template"
  bash "$LS_ROOT/skills/landing-project-init/scripts/init.sh" "$PROJECT"
fi

# Make sure the new stage folders exist (older projects predate PR-A)
mkdir -p "$PROJECT/07_ПРОТОТИП/source" "$PROJECT/07a_WIREFRAME" "$PROJECT/07b_COMPOSED" "$PROJECT/05_ДИЗАЙН-СИСТЕМА"

# --- Step 2: Drop prototype into source/ ---
echo ""
echo "▸ Step 2/6: Copy prototype to source/"
cp "$PROTOTYPE_ABS" "$PROJECT/07_ПРОТОТИП/source/prototype.$PROTO_KIND"
echo "   → $PROJECT/07_ПРОТОТИП/source/prototype.$PROTO_KIND"

# --- Step 3: Extract / convert to prototype.yaml ---
echo ""
echo "▸ Step 3/6: Parse prototype into machine-readable YAML"

if [ "$PROTO_KIND" = "pdf" ]; then
  echo "   Trying PDF text extraction..."
  if python3 "$LS_ROOT/skills/prototype-import/scripts/extract-pdf-text.py" \
       "$PROJECT/07_ПРОТОТИП/source/prototype.pdf" \
       > "$PROJECT/07_ПРОТОТИП/source/extracted-text.txt" 2>/dev/null; then
    echo "   ✓ Extracted text to source/extracted-text.txt"
    echo ""
    echo "   ⚠️  IMPORTANT: PDF extraction gives raw text, not structured blocks."
    echo "   You need to convert it into Markdown by hand or have an agent do it:"
    echo "     1. Read source/extracted-text.txt"
    echo "     2. Write 07_ПРОТОТИП/source/prototype.md in the structured format:"
    echo "          # Project: $SLUG"
    echo "          # Niche: services|b2c|local"
    echo "          ## Block 1: hero"
    echo "          - headline: ..."
    echo "     3. Re-run this script with prototype.md instead"
    echo ""
    echo "   Skipping md→yaml step (no structured md yet)."
    SKIP_YAML=1
  else
    echo "   ❌ PDF text extraction failed (likely scanned PDF)."
    echo "   Use anthropic-skills:pdf for OCR, then convert to md manually."
    exit 4
  fi
else
  # Markdown — convert directly
  cp "$PROJECT/07_ПРОТОТИП/source/prototype.md" "$PROJECT/07_ПРОТОТИП/source/prototype.md.orig" 2>/dev/null || true
  python3 "$LS_ROOT/skills/prototype-import/scripts/md-to-yaml.py" \
    "$PROJECT/07_ПРОТОТИП/source/prototype.md" \
    "$PROJECT/07_ПРОТОТИП/prototype.yaml"
  cp "$PROJECT/07_ПРОТОТИП/source/prototype.md" "$PROJECT/07_ПРОТОТИП/prototype.md"
  echo "   ✓ Wrote prototype.yaml + prototype.md"
fi

[ "${SKIP_YAML:-0}" = "1" ] && {
  echo ""
  echo "🛑 Stopped at Step 3 — prototype.md needs to be written manually first."
  echo "   When ready, re-run: bash $0 $SLUG $PROJECT/07_ПРОТОТИП/source/prototype.md"
  exit 0
}

# --- Step 3b: Enrich quiz funnel ---
echo ""
echo "▸ Step 3b: Quiz-funnel enrichment (Marquiz/Tilda/Skillbox best-practices)"
python3 "$LS_ROOT/skills/wireframe-rendering/scripts/enrich-quiz-funnel.py" \
  --input "$PROJECT/07_ПРОТОТИП/prototype.yaml" \
  --output "$PROJECT/07_ПРОТОТИП/prototype.yaml" \
  --log "$PROJECT/07_ПРОТОТИП/enrichment-log.md"
echo "   ✓ Enrichment done (see enrichment-log.md for details)"

# Validate
echo ""
echo "▸ Validating prototype schema..."
python3 "$LS_ROOT/skills/prototype-import/scripts/validate-prototype.py" \
  "$PROJECT/07_ПРОТОТИП/prototype.yaml"

# --- Step 4: Render wireframe ---
echo ""
echo "▸ Step 4/6: Render interactive wireframe (with ui-ux-pro-max integration)"
python3 "$LS_ROOT/skills/wireframe-rendering/scripts/render-wireframe.py" \
  --project "$PROJECT" \
  --library "$LS_ROOT/block-library" \
  --template "$LS_ROOT/skills/wireframe-rendering/templates/wireframe-shell.html"

# --- Step 5: Create tokens.json (stub if missing) ---
TOKENS_PATH="$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
if [ ! -f "$TOKENS_PATH" ]; then
  echo ""
  echo "▸ Step 5/6: Create design-tokens stub (real Design.md is Stage 05, not in PR-A scope)"
  cat > "$TOKENS_PATH" <<'JSON'
{
  "color": {
    "bg": "#ffffff",
    "fg": "#111111",
    "accent": "#0066cc",
    "border": "#e0e0e0"
  },
  "font": {
    "display": "Inter, system-ui, sans-serif",
    "body": "Inter, system-ui, sans-serif"
  },
  "spacing": {
    "md": "16px",
    "lg": "48px"
  }
}
JSON
  echo "   ✓ Stub tokens.json created (customize colors/fonts later via Stage 05)"
fi

# Auto-select first variant for each block (user normally does this in browser)
echo ""
echo "▸ Auto-selecting first variant per block (replace with real selections later)"
python3 - <<PY
import yaml
from datetime import datetime, timezone

c = yaml.safe_load(open("$PROJECT/07a_WIREFRAME/candidates.yaml"))
sel = []
for b in c["blocks"]:
    if b["candidates"]:
        sel.append({"block_position": b["block_position"], "chosen_variant": b["candidates"][0]})

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
out = {"project_slug": "$SLUG", "selections": sel, "confirmed_at": now}
with open("$PROJECT/07a_WIREFRAME/selections.yaml", "w") as f:
    yaml.dump(out, f, sort_keys=False, allow_unicode=True)
print(f"   ✓ Auto-picked {len(sel)} variants. Override in wireframe.html → Confirm.")
PY

# --- Step 6: Compose final ---
echo ""
echo "▸ Step 6/6: Compose final macros (composed.html + composed-mobile.html)"
python3 "$LS_ROOT/skills/block-composition/scripts/validate-selections.py" \
  "$PROJECT/07a_WIREFRAME/selections.yaml"
python3 "$LS_ROOT/skills/block-composition/scripts/compose-blocks.py" \
  --project "$PROJECT" \
  --library "$LS_ROOT/block-library"

# --- Done ---
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ ✅ Pipeline complete                                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Project folder: $PROJECT"
echo ""
echo "🎨 Open these files:"
echo ""
echo "   1) Wireframe (interactive — variant picker per block):"
echo "      open \"$PROJECT/07a_WIREFRAME/wireframe.html\""
echo ""
echo "   2) Composed final (with tokens applied):"
echo "      open \"$PROJECT/07b_COMPOSED/composed.html\""
echo ""
echo "   3) Block library gallery (all 35 blocks browsable):"
echo "      open \"$LS_ROOT/block-library/gallery.html\""
echo ""

if [ "${SKIP_OPEN:-0}" != "1" ] && command -v open >/dev/null 2>&1; then
  open "$PROJECT/07a_WIREFRAME/wireframe.html" \
       "$PROJECT/07b_COMPOSED/composed.html" \
       "$LS_ROOT/block-library/gallery.html" 2>/dev/null || true
fi

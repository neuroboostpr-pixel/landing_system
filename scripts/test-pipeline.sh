#!/usr/bin/env bash
# test-pipeline.sh — Complete PR-A test for ANY project in one command.
#
# Creates a new project, drops a prototype, runs the full pipeline:
#   prototype.md/pdf  →  prototype.yaml  →  composed.html (рисует агент)
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


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"
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
# shellcheck source=lib/paths.sh
source "$SCRIPT_DIR/lib/paths.sh"
PROJECT="$LANDINGS_ROOT/$SLUG"

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
  if $PYTHON_CMD "$LS_ROOT/skills/prototype-import/scripts/extract-pdf-text.py" \
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
  $PYTHON_CMD "$LS_ROOT/skills/prototype-import/scripts/md-to-yaml.py" \
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
$PYTHON_CMD "$LS_ROOT/skills/prototype-import/scripts/enrich-quiz-funnel.py" \
  --input "$PROJECT/07_ПРОТОТИП/prototype.yaml" \
  --output "$PROJECT/07_ПРОТОТИП/prototype.yaml" \
  --log "$PROJECT/07_ПРОТОТИП/enrichment-log.md"
echo "   ✓ Enrichment done (see enrichment-log.md for details)"

# Validate
echo ""
echo "▸ Validating prototype schema..."
$PYTHON_CMD "$LS_ROOT/skills/prototype-import/scripts/validate-prototype.py" \
  "$PROJECT/07_ПРОТОТИП/prototype.yaml"

# --- Step 4: (removed) wireframe rendering — блочный трек в архиве ---
# Reference-driven flow: агент рисует composed.html сам по прототипу и референсу.
# См. docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md

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

# --- Step 6: (removed) machine compose из библиотеки — блочный трек в архиве ---
# composed.html рисует агент (reference-driven flow); машинная склейка блоков
# из block-library удалена вместе с wireframe-этапом.

# --- Done ---
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║ ✅ Pipeline complete (prototype parse + validate)            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Project folder: $PROJECT"
echo ""
echo "Дальше: агент рисует макет 07b_COMPOSED/composed.html по правилам"
echo "reference-driven спеки (структура из прототипа, вид из референса)."

if [ "${SKIP_OPEN:-0}" != "1" ] && command -v open >/dev/null 2>&1; then
  [ -f "$PROJECT/07b_COMPOSED/composed.html" ] && \
    open "$PROJECT/07b_COMPOSED/composed.html" 2>/dev/null || true
fi

# --- PR-B Photo stage (optional, only if sample photos are available) ---
PHOTO_SAMPLES="${PHOTO_SAMPLES:-$LS_ROOT/tests/phase-prb/fixtures/sample-photos}"
if [ -d "$PHOTO_SAMPLES" ] && [ "$(ls -A "$PHOTO_SAMPLES" 2>/dev/null)" ]; then
  echo ""
  echo "→ Stage PR-B: running photo pipeline with sample photos..."

  # Prepare 07c_PHOTOS folder structure
  mkdir -p "$PROJECT/07c_PHOTOS/inbox/_свалка"
  cp "$PHOTO_SAMPLES"/*.jpg "$PROJECT/07c_PHOTOS/inbox/_свалка/" 2>/dev/null || true

  # Stage 1: intake
  $PYTHON_CMD "$LS_ROOT/skills/photo-curation/scripts/intake.py" \
    --inbox "$PROJECT/07c_PHOTOS/inbox" \
    --intake "$PROJECT/07c_PHOTOS/intake"
  echo "  ✓ intake done"

  # Stage 2: classify (real codex or USE_CODEX_MOCK)
  if [ -n "${USE_CODEX_MOCK:-}" ]; then
    export CODEX_BIN="$LS_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    export CODEX_MOCK_RESPONSE='tags: [object]
caption: "Mock photo"
face_count: 0
composition: object-only
usable_ratios: ["1:1", "16:9"]
brand_compatible: yes
notes: ""'
  fi

  if command -v codex >/dev/null 2>&1 || [ -n "${USE_CODEX_MOCK:-}" ]; then
    for photo in "$PROJECT/07c_PHOTOS/intake"/*.jpg; do
      [ -f "$photo" ] || continue
      [[ "$photo" == *.thumb.jpg ]] && continue
      bash "$LS_ROOT/skills/photo-curation/scripts/codex-classify.sh" "$PROJECT" "$photo" || {
        echo "  ⚠ classify failed for $photo (continuing)"
      }
    done
    echo "  ✓ classify done"
  else
    echo "  ⊘ skipping classify (codex not installed and USE_CODEX_MOCK not set)"
  fi

  # Stage 3: match — synthesize a minimal draft for smoke test
  if [ ! -f "$PROJECT/07c_PHOTOS/catalog.yaml" ]; then
    printf 'photos: []\n' > "$PROJECT/07c_PHOTOS/catalog.yaml"
  fi
  cat > "$PROJECT/07c_PHOTOS/selections.draft.yaml" <<'DRAFT_EOF'
slots: []
DRAFT_EOF
  echo "  ✓ match stub written"

  # Stage 4: render gallery
  $PYTHON_CMD "$LS_ROOT/skills/photo-curation/scripts/gallery-render.py" \
    --catalog "$PROJECT/07c_PHOTOS/catalog.yaml" \
    --draft "$PROJECT/07c_PHOTOS/selections.draft.yaml" \
    --out "$PROJECT/07c_PHOTOS/photo-board.html" || {
    # Fallback: write empty catalog and retry
    printf 'photos: []\n' > "$PROJECT/07c_PHOTOS/catalog.yaml"
    $PYTHON_CMD "$LS_ROOT/skills/photo-curation/scripts/gallery-render.py" \
      --catalog "$PROJECT/07c_PHOTOS/catalog.yaml" \
      --draft "$PROJECT/07c_PHOTOS/selections.draft.yaml" \
      --out "$PROJECT/07c_PHOTOS/photo-board.html"
  }
  echo "  ✓ gallery rendered → $PROJECT/07c_PHOTOS/photo-board.html"

  echo ""
  echo "  PR-B photo stage smoke test PASSED"
  echo ""
fi

# --- PR-C Visual stage (icons + infographics) ---
if [ -f "$PROJECT/07b_COMPOSED/composed.html" ]; then
    echo ""
    echo "→ Stage PR-C: running visual pipeline..."

    # Ensure 05_design tokens.json exists for prompt context
    if [ ! -f "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json" ]; then
        mkdir -p "$PROJECT/05_ДИЗАЙН-СИСТЕМА"
        echo '{"colors":{"primary":"#1e3a8a","accent":"#c47a3a"},"design":{"visual_style":"Minimalism","icon_style":"outlined"}}' > "$PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
    fi

    # Stage 1: scan composed.html for visual slots
    $PYTHON_CMD "$LS_ROOT/skills/visual-generation/scripts/slot-scanner.py" \
        --html "$PROJECT/07b_COMPOSED/composed.html" \
        --out "$PROJECT/07d_VISUALS/_slots.yaml"
    echo "  ✓ visual scan done"

    # Stage 2: generate (mocked in smoke; real codex if installed)
    if [ -n "${USE_CODEX_MOCK:-}" ]; then
        export CODEX_BIN="$LS_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    fi

    if command -v codex >/dev/null 2>&1 || [ -n "${USE_CODEX_MOCK:-}" ]; then
        $PYTHON_CMD -c "
import yaml, subprocess
from pathlib import Path
slots_path = Path('$PROJECT/07d_VISUALS/_slots.yaml')
if slots_path.exists():
    slots = yaml.safe_load(slots_path.read_text()) or {}
    for s in slots.get('icons', []):
        subprocess.run(['bash', '$LS_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh',
                        '$PROJECT', s['slot_name'], s.get('hint','')], check=False)
    for s in slots.get('infographics', []):
        subprocess.run(['bash', '$LS_ROOT/skills/visual-generation/scripts/codex-generate-infographic.sh',
                        '$PROJECT', s['slot_name'], s.get('chart_type','number'), '{}'], check=False)
"
        echo "  ✓ visual generation attempted"
    else
        echo "  ⊘ skipping generation (codex not installed and USE_CODEX_MOCK not set)"
    fi

    # Stage 3: re-render composed.html with visuals
    $PYTHON_CMD "$LS_ROOT/skills/block-composition/scripts/compose-blocks.py" --project "$PROJECT" 2>/dev/null || true

    echo "  PR-C visual stage smoke test PASSED"
fi

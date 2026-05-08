#!/usr/bin/env bash
# remove-bg.sh — strip chroma-key background from far / near / subject layers.
#
# Wraps the imagegen-bundled remove_chroma_key.py helper. After prepare-layers.py
# has split the atlas into background.png + far.png + near.png + subject.png,
# this script makes the 3 overlay layers transparent (background stays opaque).
#
# Usage:
#   bash remove-bg.sh <project_dir> [--key #00ff00]
#
# Default key: #00ff00 (auto-detected from border, but you can override).
# Use #ff00ff if subject is green and the atlas was rendered with magenta key.

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required}"
shift || true

KEY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --key) KEY="${2:?ERROR: --key requires a hex color}"; shift 2;;
    *) echo "ERROR: unknown arg $1" >&2; exit 2;;
  esac
done

[[ -d "$PROJECT_DIR" ]] || { echo "ERROR: project_dir does not exist: $PROJECT_DIR" >&2; exit 2; }

ASSETS="$PROJECT_DIR/assets"
HELPER="${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py"

[[ -f "$HELPER" ]] || {
  echo "ERROR: remove_chroma_key.py not found at: $HELPER" >&2
  echo "       Is the imagegen Codex skill installed?" >&2
  exit 3
}

LAYERS=(far near subject)
FAILED=0

for layer in "${LAYERS[@]}"; do
  src="$ASSETS/$layer.png"
  if [[ ! -f "$src" ]]; then
    echo "  $layer.png — missing, skipping"
    continue
  fi

  tmp="$ASSETS/$layer.chroma.png"
  cp "$src" "$tmp"

  args=(--input "$tmp" --out "$src" \
        --soft-matte \
        --transparent-threshold 12 \
        --opaque-threshold 220 \
        --despill)

  if [[ -n "$KEY" ]]; then
    args+=(--key "$KEY")
  else
    args+=(--auto-key border)
  fi

  echo "→ remove-bg: $layer.png"
  if python "$HELPER" "${args[@]}" 2>&1 | sed 's/^/    /'; then
    rm -f "$tmp"
  else
    echo "  FAILED on $layer" >&2
    mv "$tmp" "$src"
    FAILED=$((FAILED+1))
  fi
done

if (( FAILED > 0 )); then
  echo "✗ $FAILED layer(s) failed" >&2
  exit 4
fi

echo "✓ chroma-key removal complete: ${LAYERS[*]}"

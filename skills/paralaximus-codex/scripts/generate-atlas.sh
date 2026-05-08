#!/usr/bin/env bash
# generate-atlas.sh — wrap codex exec to produce a parallax atlas in the project.
#
# Codex generates images into ~/.codex/generated_images/<session-uuid>/ and is
# blocked by its own sandbox policy from copying them into the project. So we
# call codex, then copy the freshest PNG ourselves.
#
# Usage:
#   bash generate-atlas.sh <project_dir> <prompt_file>
#   bash generate-atlas.sh <project_dir> --prompt "..."
#
# Requires:
#   - codex CLI logged in (codex login)
#   - Pillow for prepare-layers.py downstream

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required (where assets/atlas.png will be saved)}"
shift

if [[ "${1:-}" == "--prompt" ]]; then
  PROMPT="${2:?ERROR: --prompt requires a value}"
elif [[ -f "${1:-}" ]]; then
  PROMPT="$(cat "$1")"
else
  echo "ERROR: second argument must be a prompt file or --prompt \"...\"" >&2
  exit 2
fi

[[ -d "$PROJECT_DIR" ]] || { echo "ERROR: project_dir does not exist: $PROJECT_DIR" >&2; exit 2; }
ASSETS="$PROJECT_DIR/assets"
mkdir -p "$ASSETS"
ATLAS_OUT="$ASSETS/atlas.png"

# Snapshot existing image dirs so we can detect the new one created by this run.
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

echo "→ Calling codex exec to generate atlas …"
# --skip-git-repo-check: codex does not need to be inside a git repo.
# We send a single instruction to generate the image. Codex will save it under
# ~/.codex/generated_images/<new-uuid>/ig_*.png and complain about not being
# able to copy. We ignore that complaint.
codex exec --skip-git-repo-check "$PROMPT" >&2 || {
  rc=$?
  echo "ERROR: codex exec exited with $rc" >&2
  rm -f "$TMP_BEFORE"
  exit "$rc"
}

# Find the freshest session dir (created during this run).
TMP_AFTER="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_AFTER" || true
NEW_DIR="$(comm -13 "$TMP_BEFORE" "$TMP_AFTER" | tail -1 || true)"
rm -f "$TMP_BEFORE" "$TMP_AFTER"

if [[ -z "$NEW_DIR" ]]; then
  echo "WARN: no new session dir detected — falling back to most-recent dir" >&2
  NEW_DIR="$(ls -1t ~/.codex/generated_images/ 2>/dev/null | head -1)"
fi

[[ -n "$NEW_DIR" ]] || { echo "ERROR: no codex generated_images dir found" >&2; exit 3; }

SRC_DIR="$HOME/.codex/generated_images/$NEW_DIR"
SRC_PNG="$(ls -1t "$SRC_DIR"/*.png 2>/dev/null | head -1 || true)"

[[ -n "$SRC_PNG" && -f "$SRC_PNG" ]] || {
  echo "ERROR: no PNG produced in $SRC_DIR" >&2
  exit 4
}

cp "$SRC_PNG" "$ATLAS_OUT"
SIZE_KB=$(( $(stat -c%s "$ATLAS_OUT" 2>/dev/null || stat -f%z "$ATLAS_OUT") / 1024 ))
echo "→ Atlas copied: $ATLAS_OUT (${SIZE_KB} KB)"
echo "→ Source kept at: $SRC_PNG"
echo "✓ Done."

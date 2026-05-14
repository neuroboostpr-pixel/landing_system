#!/usr/bin/env bash
# generate-atlas.sh — wrap codex exec to produce a parallax atlas in the project.
#
# Codex generates images into ~/.codex/generated_images/<session-uuid>/ and is
# blocked by its own sandbox policy from copying them into the project. So we
# call codex, then copy the freshest PNG ourselves.
#
# Usage:
#   bash generate-atlas.sh <project_dir> <prompt_file> [--ref-person <dir>] [--ref-style <dir>]
#   bash generate-atlas.sh <project_dir> --prompt "..." [--ref-person <dir>] [--ref-style <dir>]
#
# --ref-person <dir>  pass every .png/.jpg/.jpeg/.webp from <dir> to codex via
#                     -i (image input), used as facial-identity reference for
#                     the subject quadrant. Recommended: 2–3 photos, different
#                     angles. The skill auto-injects a "use these as facial
#                     identity references" block into the prompt.
# --ref-style <dir>   same, but used as style reference for the whole atlas
#                     (palette, lighting, mood). Optional.
#
# Requires:
#   - codex CLI logged in (codex login)
#   - Pillow for prepare-layers.py downstream

set -euo pipefail

PROJECT_DIR="${1:?ERROR: project_dir required (where assets/atlas.png will be saved)}"
shift

PROMPT=""
REF_PERSON_DIR=""
REF_STYLE_DIR=""

# First positional arg: prompt file or --prompt "..."
if [[ "${1:-}" == "--prompt" ]]; then
  PROMPT="${2:?ERROR: --prompt requires a value}"
  shift 2
elif [[ -n "${1:-}" && -f "$1" ]]; then
  PROMPT="$(cat "$1")"
  shift
else
  echo "ERROR: second argument must be a prompt file or --prompt \"...\"" >&2
  exit 2
fi

# Optional flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ref-person) REF_PERSON_DIR="${2:?--ref-person needs a dir}"; shift 2;;
    --ref-style)  REF_STYLE_DIR="${2:?--ref-style needs a dir}"; shift 2;;
    *) echo "ERROR: unknown arg $1" >&2; exit 2;;
  esac
done

[[ -d "$PROJECT_DIR" ]] || { echo "ERROR: project_dir does not exist: $PROJECT_DIR" >&2; exit 2; }

# Collect reference images and assemble prompt blocks
collect_imgs() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0
  find "$dir" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' \) | sort
}

REF_IMG_ARGS=()
if [[ -n "$REF_PERSON_DIR" ]]; then
  while IFS= read -r img; do
    REF_IMG_ARGS+=(-i "$img")
  done < <(collect_imgs "$REF_PERSON_DIR")
  PERSON_FILES=$(collect_imgs "$REF_PERSON_DIR" | xargs -I{} basename "{}" | sed 's/^/[/;s/$/]/' | tr '\n' ',' | sed 's/,$//;s/,/, /g')
  if [[ -n "$PERSON_FILES" ]]; then
    PERSON_BLOCK="

REFERENCE — PERSON (facial identity, applies to the BOTTOM-RIGHT subject quadrant only):
Use the uploaded photos $PERSON_FILES as facial identity references. The highest priority is preserving the exact identity of the referenced person. Do not generate a new face inspired by the reference; reproduce the same recognizable person. Preserve the face shape, facial proportions, eye shape, nose structure, lip shape, eyebrow shape, beard shape and color, skin tone, hairstyle, and overall likeness with high fidelity. The face must remain recognizable at first glance as the same real person from the uploaded reference. Apply lighting, texture, color treatment, atmosphere, and rendering quality from this scene's style, but do not redesign, beautify away, or alter the facial anatomy. The subject's face should occupy a clear and important portion of the bottom-right quadrant."
    PROMPT="${PROMPT}${PERSON_BLOCK}"
  fi
fi

if [[ -n "$REF_STYLE_DIR" ]]; then
  while IFS= read -r img; do
    REF_IMG_ARGS+=(-i "$img")
  done < <(collect_imgs "$REF_STYLE_DIR")
  STYLE_FILES=$(collect_imgs "$REF_STYLE_DIR" | xargs -I{} basename "{}" | sed 's/^/[/;s/$/]/' | tr '\n' ',' | sed 's/,$//;s/,/, /g')
  if [[ -n "$STYLE_FILES" ]]; then
    STYLE_BLOCK="

REFERENCE — STYLE (applies to the entire atlas):
Use the uploaded images $STYLE_FILES as a style reference for the entire scene. Apply its visual language — color palette, lighting, texture, and rendering style — across the composition, including background, environment, and the subject. Do not replicate specific characters or objects from the style reference. Only transfer its aesthetic qualities."
    PROMPT="${PROMPT}${STYLE_BLOCK}"
  fi
fi

echo "→ Reference images attached: $(( ${#REF_IMG_ARGS[@]} / 2 ))"
ASSETS="$PROJECT_DIR/assets"
mkdir -p "$ASSETS"
ATLAS_OUT="$ASSETS/atlas.png"

# Snapshot existing image dirs so we can detect the new one created by this run.
TMP_BEFORE="$(mktemp)"
ls -1 ~/.codex/generated_images/ 2>/dev/null | sort > "$TMP_BEFORE" || true

echo "→ Calling codex exec to generate atlas …"
# --skip-git-repo-check: codex does not need to be inside a git repo.
# Pass prompt via stdin (positional arg conflicts with -i flags), and image
# refs via -i. Codex saves under ~/.codex/generated_images/<new-uuid>/ and
# gets blocked by its own sandbox from copying. We copy ourselves below.
printf '%s' "$PROMPT" | codex exec --skip-git-repo-check "${REF_IMG_ARGS[@]}" - >&2 || {
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

#!/usr/bin/env bash
# landing-from-context: create new landing inheriting context from parent agency project
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: from-context.sh <target-path> [--cinematic]"
  echo "  Run from inside a parent agency project folder."
  exit 1
fi

TARGET="$1"
CINEMATIC_FLAG=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --cinematic) CINEMATIC_FLAG="--cinematic"; shift ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

PARENT="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
INIT_SH="$SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh"

if [ ! -x "$INIT_SH" ]; then
  echo "❌ landing-project-init/init.sh not found or not executable"
  exit 2
fi

# --- Step 1: create blank project ---
echo "📦 Creating project skeleton..."
"$INIT_SH" "$TARGET" $CINEMATIC_FLAG

# --- Step 2: snapshot parent context ---
echo "📋 Snapshotting parent context from $PARENT ..."

# Track what was actually copied
COPIED_ENTRIES=()

# 01_контекст → 01_КОНТЕКСТ (copy contents)
if [ -d "$PARENT/01_контекст" ]; then
  cp -R "$PARENT/01_контекст/." "$TARGET/01_КОНТЕКСТ/"
  COPIED_ENTRIES+=("  - source: 01_контекст\n    target: 01_КОНТЕКСТ")
  echo "  ✓ 01_контекст copied"
fi

# 05_исследования → 01_КОНТЕКСТ/исследования
if [ -d "$PARENT/05_исследования" ]; then
  mkdir -p "$TARGET/01_КОНТЕКСТ/исследования"
  cp -R "$PARENT/05_исследования/." "$TARGET/01_КОНТЕКСТ/исследования/"
  COPIED_ENTRIES+=("  - source: 05_исследования\n    target: 01_КОНТЕКСТ/исследования")
  echo "  ✓ 05_исследования copied"
fi

# Prototype: look for files matching 'прототип-*.md' or 'prototype-*.md' in 04_документы
if [ -d "$PARENT/04_документы" ]; then
  mkdir -p "$TARGET/07_КОНТЕНТ"
  # First matching pattern wins; warn if multiple files match
  proto=""
  for pattern in "прототип-*.md" "prototype-*.md" "прототип*.md"; do
    matches=$(find "$PARENT/04_документы" -maxdepth 1 -name "$pattern" -type f 2>/dev/null)
    match_count=$(echo "$matches" | grep -c . 2>/dev/null || true)
    if [ "$match_count" -gt 1 ]; then
      echo "⚠️  Multiple prototype files matched pattern '$pattern':"
      echo "$matches" | sed 's/^/    /'
      proto=$(echo "$matches" | head -1)
      echo "    Using: $proto"
      echo "    To use a different file, copy it manually to 07_КОНТЕНТ/prototype.md after."
      break
    elif [ "$match_count" -eq 1 ]; then
      proto="$matches"
      break
    fi
  done
  if [ -n "$proto" ]; then
    cp "$proto" "$TARGET/07_КОНТЕНТ/prototype.md"
    COPIED_ENTRIES+=("  - source: 04_документы (prototype match)\n    target: 07_КОНТЕНТ/prototype.md")
    echo "  ✓ Prototype copied: $(basename "$proto")"
  fi
fi

# --- Step 3: write source-references.yaml ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Escape embedded double-quotes in path values for safe YAML
PARENT_ESCAPED="${PARENT//\"/\\\"}"
PARENT_BASENAME_ESCAPED="$(basename "$PARENT" | sed 's/"/\\"/g')"

# Build the copied: block (empty list or indented entries)
if [ ${#COPIED_ENTRIES[@]} -eq 0 ]; then
  COPIED_BLOCK="copied: []"
else
  COPIED_BLOCK="copied:"$'\n'"$(printf "%b\n" "${COPIED_ENTRIES[@]}")"
fi

cat > "$TARGET/01_КОНТЕКСТ/source-references.yaml" <<EOF
# Snapshot manifest — created by landing-from-context
created: $TIMESTAMP
parent_path: "$PARENT_ESCAPED"
parent_basename: "$PARENT_BASENAME_ESCAPED"
$COPIED_BLOCK
note: |
  This is a snapshot. Changes in the parent project will NOT propagate here.
  To re-snapshot, delete 01_КОНТЕКСТ/* and run from-context.sh again.
EOF

# --- Step 4: extra commit in target ---
git -C "$TARGET" add -A >/dev/null
git -C "$TARGET" commit -m "chore: snapshot parent context" >/dev/null 2>&1 || true

echo ""
echo "✅ Project created with parent context: $TARGET"
echo ""
echo "Next:"
echo "  cd $TARGET"
echo "  claude"
echo "  > /landing-status"

#!/usr/bin/env bash
# landing-project-init: creates a new landing project from template
set -euo pipefail

# --- Args ---
if [ $# -lt 1 ]; then
  echo "Usage: init.sh <target-path> [--cinematic]"
  echo "  target-path: absolute or relative path to new project folder"
  exit 1
fi

TARGET="$1"
CINEMATIC=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --cinematic) CINEMATIC="true"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Resolve paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TEMPLATE_DIR="$SYSTEM_ROOT/template"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "❌ Template not found at $TEMPLATE_DIR"
  exit 2
fi

# --- Refuse overwrite ---
if [ -e "$TARGET" ]; then
  echo "❌ Path already exists: $TARGET"
  echo "   Choose another name or remove the existing folder."
  exit 3
fi

# --- Project name from path ---
PROJECT_NAME="$(basename "$TARGET")"

# --- Copy template ---
echo "📦 Copying template to $TARGET ..."
mkdir -p "$TARGET"
# Copy contents (including hidden files via .gitkeep, .env.example, .gitignore)
cp -R "$TEMPLATE_DIR/." "$TARGET/"

# --- Substitute placeholders ---
echo "✏️  Substituting placeholders..."
# README.md
if [ -f "$TARGET/README.md" ]; then
  # macOS sed needs '' after -i; Linux differs. Use a portable approach.
  sed -i.bak "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TARGET/README.md"
  rm -f "$TARGET/README.md.bak"
fi
# .env.example
if [ -f "$TARGET/.env.example" ]; then
  sed -i.bak "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TARGET/.env.example"
  rm -f "$TARGET/.env.example.bak"
fi

# --- Initialize git ---
echo "🌱 Initializing git..."
git -C "$TARGET" init -b main >/dev/null
git -C "$TARGET" add -A >/dev/null
git -C "$TARGET" commit -m "chore: scaffold project from landing-system template" >/dev/null 2>&1 || true

# --- Optional: cinematic flag ---
if [ "$CINEMATIC" = "true" ]; then
  echo "CINEMATIC=true" >> "$TARGET/00_БРИФ/.flags"
  echo "🎬 Cinematic mode enabled"
fi

# --- Success ---
echo ""
echo "✅ Project created: $TARGET"
echo ""
echo "Next steps:"
echo "  cd $TARGET"
echo "  cp .env.example .env  # fill in secrets"
echo "  claude                # open Claude Code"
echo "  > /landing-status     # see what's next"

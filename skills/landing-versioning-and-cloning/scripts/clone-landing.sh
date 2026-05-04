#!/usr/bin/env bash
# skills/landing-versioning-and-cloning/scripts/clone-landing.sh
# Клонирует проект в новую папку для A/B теста
# Usage: clone-landing.sh <project-dir> <new-slug>
set -euo pipefail

PROJECT="$(realpath "$1")"
NEW_SLUG="${2:?Usage: clone-landing.sh <project-dir> <new-slug>}"
PARENT_DIR="$(dirname "$PROJECT")"
CLONE_DIR="$PARENT_DIR/$NEW_SLUG"

[ -d "$CLONE_DIR" ] && { echo "❌ $CLONE_DIR уже существует"; exit 1; }

cp -r "$PROJECT" "$CLONE_DIR"
echo "✅ A/B клон → $CLONE_DIR"
echo "   Следующий шаг: /landing-deploy в $CLONE_DIR на новый поддомен"

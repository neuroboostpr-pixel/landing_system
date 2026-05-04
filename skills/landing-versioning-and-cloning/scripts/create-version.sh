#!/usr/bin/env bash
# skills/landing-versioning-and-cloning/scripts/create-version.sh
# Создаёт версионный снапшот wp-theme в 09_ВЕРСИИ/
# Usage: create-version.sh <project-dir> [version-label]
set -euo pipefail

PROJECT="$(realpath "$1")"
VERSION="${2:-v$(date +%Y%m%d%H%M)}"
VERSIONS_DIR="$PROJECT/09_ВЕРСИИ"
SNAPSHOT_DIR="$VERSIONS_DIR/$VERSION"

mkdir -p "$SNAPSHOT_DIR"
cp -r "$PROJECT/08_КОД/wp-theme" "$SNAPSHOT_DIR/"
cp -r "$PROJECT/08_КОД/acf-fields.json" "$SNAPSHOT_DIR/" 2>/dev/null || true

echo "$VERSION" > "$VERSIONS_DIR/current.txt"
echo "✅ Версия $VERSION сохранена → $SNAPSHOT_DIR"

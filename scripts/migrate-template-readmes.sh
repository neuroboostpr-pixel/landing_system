#!/usr/bin/env bash
# migrate-template-readmes.sh — copy missing READMEs from template/ into an existing project.
#
# Idempotent: existing READMEs preserved (no overwrite). Creates missing subfolders
# (e.g. 04_БРЕНД/logos/) if absent.
#
# Usage: bash migrate-template-readmes.sh <project_dir>

set -euo pipefail

PROJECT="${1:?ERROR: project dir required}"
[ -d "$PROJECT" ] || { echo "ERROR: $PROJECT not found" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$LS_ROOT/template"

[ -d "$TEMPLATE" ] || { echo "ERROR: template/ not found at $TEMPLATE" >&2; exit 2; }

added=0
created_dirs=0

while IFS= read -r -d '' template_file; do
    rel="${template_file#$TEMPLATE/}"
    target="$PROJECT/$rel"
    target_dir="$(dirname "$target")"

    if [ ! -d "$target_dir" ]; then
        mkdir -p "$target_dir"
        created_dirs=$((created_dirs + 1))
    fi

    if [ -e "$target" ]; then
        continue
    fi

    cp "$template_file" "$target"
    added=$((added + 1))
done < <(find "$TEMPLATE" -type f -print0)

echo "Migration done."
echo "   Added files: $added"
echo "   Created dirs: $created_dirs"

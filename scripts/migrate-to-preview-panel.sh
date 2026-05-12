#!/usr/bin/env bash
# migrate-to-preview-panel.sh <project-path> <library-path>
# One-shot migration: replaces hard-coded nu-theme-bar with lp-preview-panel plugin
# and seeds the project + library palette files from existing CSS.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: migrate-to-preview-panel.sh <project-path> <library-path>" >&2
  exit 2
fi

PROJECT="$1"
LIBRARY="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 1. Strip nu-theme-bar from header.php (the entire <div class="nu-theme-bar">...</div> block).
python "$ROOT/scripts/_migrate-strip-header.py" "$PROJECT/08_КОД/wp-theme/header.php"

# 2. Strip initThemeSwitcher from main.js (function declaration + invocation).
python "$ROOT/scripts/_migrate-strip-js.py" "$PROJECT/08_КОД/wp-theme/assets/js/main.js"

# 3. Extract H/I/J/K palettes from main.css → 04_БРЕНД/palettes.yaml as nu-paper/nu-quiet-dark/nu-beige/nu-iqido.
python "$ROOT/scripts/_migrate-extract-palettes.py" \
    --css "$PROJECT/08_КОД/wp-theme/assets/css/main.css" \
    --project "$PROJECT"

# 4. Export newly-created palettes into the global library.
python "$ROOT/scripts/export-palettes-to-library.py" --project "$PROJECT" --library "$LIBRARY"

# 5. Copy plugin from template (idempotent: rm -rf then cp).
mkdir -p "$PROJECT/08_КОД/plugins"
rm -rf "$PROJECT/08_КОД/plugins/lp-preview-panel"
cp -r "$ROOT/template/08_КОД/plugins/lp-preview-panel" "$PROJECT/08_КОД/plugins/"

# 6. Generate palette CSS and axes filter PHP.
python "$ROOT/scripts/generate-palette-css.py" --project "$PROJECT"
python "$ROOT/scripts/generate-axes-filter.py" \
    --project "$PROJECT" \
    --default-palette nu-iqido \
    --hero static,parallax \
    --default-hero static

# 7. Inject require_once into functions.php, idempotent.
FN="$PROJECT/08_КОД/wp-theme/functions.php"
LINE="require_once get_template_directory() . '/inc/lp-preview-panel-axes.php';"
if ! grep -qF "lp-preview-panel-axes.php" "$FN"; then
  printf "\n%s\n" "$LINE" >> "$FN"
fi

echo "migration complete for $PROJECT"

#!/usr/bin/env bash
# scripts/landing-rename.sh — rename a landing project and update internal references
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 2 ]; then
    echo "Usage: landing-rename.sh <old-slug> <new-slug>"
    exit 1
fi

OLD_SLUG="$1"
NEW_SLUG="$2"
LANDINGS_ROOT="${LANDINGS_ROOT:-$(python -c "import sys; sys.path.insert(0,'$REPO_ROOT'); from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")}"
OLD_DIR="$LANDINGS_ROOT/$OLD_SLUG"
NEW_DIR="$LANDINGS_ROOT/$NEW_SLUG"

if ! echo "$OLD_SLUG" | grep -qE '^[a-z0-9-]+$'; then
    echo "❌ Slug должен быть kebab-case (только строчные буквы, цифры, дефис)"
    exit 1
fi

# Validate old slug
if [ ! -d "$OLD_DIR" ]; then
    echo "❌ Проект '$OLD_SLUG' не найден в $LANDINGS_ROOT"
    exit 1
fi
if [ ! -f "$OLD_DIR/.landing-state.yaml" ]; then
    echo "❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)"
    exit 1
fi

# Validate new slug
if [ -d "$NEW_DIR" ]; then
    echo "❌ Проект '$NEW_SLUG' уже существует в $LANDINGS_ROOT"
    exit 1
fi
if ! echo "$NEW_SLUG" | grep -qE '^[a-z0-9-]+$'; then
    echo "❌ Slug должен быть kebab-case (только строчные буквы, цифры, дефис)"
    exit 1
fi

# Move folder
# On Windows, git object files are ReadOnly which causes POSIX `mv` to fail.
# Detect Windows and use PowerShell + robocopy (handles read-only files), otherwise mv.
_os="$(uname -s 2>/dev/null || true)"
if [[ "$_os" == MINGW* || "$_os" == CYGWIN* || "$_os" == MSYS* ]] && command -v powershell.exe &>/dev/null; then
    # Convert POSIX paths to Windows paths for PowerShell
    OLD_WIN="$(cygpath -w "$OLD_DIR" 2>/dev/null || echo "$OLD_DIR" | sed 's|/|\\|g')"
    NEW_WIN="$(cygpath -w "$NEW_DIR" 2>/dev/null || echo "$NEW_DIR" | sed 's|/|\\|g')"
    # Use PowerShell to invoke robocopy — avoids MinGW slash-as-path mangling
    ROBO_EXIT="$(powershell.exe -NoProfile -Command "
        robocopy '$OLD_WIN' '$NEW_WIN' /E /MOVE /NFL /NDL /NJH /NJS /NP | Out-Null
        exit \$LASTEXITCODE
    " 2>/dev/null; echo $?)"
    # robocopy exit codes: 0=no files, 1=files copied, 2=extra files, 3=both — all ok; >=8 = error
    if [ "${ROBO_EXIT:-0}" -ge 8 ]; then
        echo "❌ Не удалось переименовать папку (robocopy exit $ROBO_EXIT)"
        exit 1
    fi
    # Remove source dir if robocopy left empty shell (edge case)
    [ -d "$OLD_DIR" ] && rm -rf "$OLD_DIR"
else
    mv "$OLD_DIR" "$NEW_DIR"
fi

# Update .landing-state.yaml
yq e ".project = \"$NEW_SLUG\"" -i "$NEW_DIR/.landing-state.yaml"

# GNU sed (Git Bash on Windows) supports -i without suffix; BSD sed needs -i ''
UPDATED=0

# Update README.md
if [ -f "$NEW_DIR/README.md" ]; then
    if grep -q "$OLD_SLUG" "$NEW_DIR/README.md"; then
        sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/README.md"
        UPDATED=$((UPDATED + 1))
    fi
fi

# Update brief.md
if [ -f "$NEW_DIR/00_БРИФ/brief.md" ]; then
    if grep -q "$OLD_SLUG" "$NEW_DIR/00_БРИФ/brief.md"; then
        sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/00_БРИФ/brief.md"
        UPDATED=$((UPDATED + 1))
    fi
fi

# Update wiki/pipeline-map.md
if [ -f "$NEW_DIR/wiki/pipeline-map.md" ]; then
    if grep -q "$OLD_SLUG" "$NEW_DIR/wiki/pipeline-map.md"; then
        sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/wiki/pipeline-map.md"
        UPDATED=$((UPDATED + 1))
    fi
fi

echo ""
echo "✅ Проект переименован: $OLD_SLUG → $NEW_SLUG"
echo "Папка: $NEW_DIR"
echo "Обновлено файлов: $UPDATED"

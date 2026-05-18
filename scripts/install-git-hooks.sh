#!/bin/bash
# PR-G: Идемпотентная установка git hooks для wiki + локов.
# Запускается одноразово после клонирования репо или из onboarding.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

HOOKS_DIR=".githooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Папка $HOOKS_DIR не найдена в репо" >&2
    exit 1
fi

# Установка
git config core.hooksPath "$HOOKS_DIR"
chmod +x "$HOOKS_DIR/"*

echo "✅ Git hooks подключены: core.hooksPath = $HOOKS_DIR"
echo "   Active hooks:"
for h in "$HOOKS_DIR"/*; do
    [ -f "$h" ] && [ -x "$h" ] && echo "   - $(basename "$h")"
done

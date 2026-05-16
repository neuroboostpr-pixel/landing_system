#!/usr/bin/env bash
# PR-K test helpers.

PR_K_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PR_K_REPO_ROOT

# Создать JPEG нужного размера (для проверки ratio).
pr_k_make_jpg() {
    local path="$1"
    local w="${2:-1920}"
    local h="${3:-1080}"
    python3 -c "
from PIL import Image
import os
os.makedirs(os.path.dirname('$path'), exist_ok=True)
Image.new('RGB', (${w}, ${h}), (120, 130, 140)).save('$path', 'JPEG', quality=80)
"
}

# Создать project-skeleton (07c_PHOTOS/inbox).
pr_k_make_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07c_PHOTOS/inbox"
    mkdir -p "$tmpdir/07b_COMPOSED"
    mkdir -p "$tmpdir/07c_PHOTOS/processed"
    echo "$tmpdir"
}

# Записать .classifications.json (фикстура).
pr_k_write_classifications() {
    local inbox="$1"
    local payload="$2"
    echo "$payload" > "$inbox/.classifications.json"
}

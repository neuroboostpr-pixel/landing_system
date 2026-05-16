#!/usr/bin/env bash
# PR-M test helpers.

PR_M_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PR_M_REPO_ROOT

# Создать проект с минимальным composed.html
make_project_with_composed() {
    local tmpdir
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/07b_COMPOSED"
    cat > "$tmpdir/07b_COMPOSED/composed.html" <<'HTML'
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>test</title></head>
<body><h1>Test landing</h1></body></html>
HTML
    echo "$tmpdir"
}

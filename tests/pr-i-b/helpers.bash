#!/usr/bin/env bash
PR_I_B_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

make_minimal_html() {
    local tmpdir
    tmpdir=$(mktemp -d)
    cat > "$tmpdir/composed.html" <<'HTML'
<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"><title>Test</title></head>
<body style="background:#1a1a1a;color:white;padding:40px;font-family:sans-serif">
<section data-block="hero-1"><h1>Test heading</h1></section>
</body></html>
HTML
    echo "$tmpdir"
}

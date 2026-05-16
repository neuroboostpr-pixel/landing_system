#!/usr/bin/env bats
# PR-O: take-page-screenshot.py делает desktop.png + mobile.png из локального test.html.

PR_O_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
SCRIPT="$PR_O_REPO_ROOT/scripts/import-blocks/take-page-screenshot.py"

setup() {
    TMP="$(mktemp -d)"
    cat > "$TMP/test.html" <<'HTML'
<!doctype html><html><head><meta charset="utf-8"><title>t</title></head>
<body style="margin:0">
  <header style="height:200px;background:#222;color:#fff;padding:24px">Hero</header>
  <section style="height:600px;background:#f4f4f4;padding:24px">Features</section>
  <footer style="height:120px;background:#111;color:#fff;padding:24px">Footer</footer>
</body></html>
HTML
}

teardown() {
    rm -rf "$TMP"
}

@test "take-page-screenshot: создаёт desktop.png и mobile.png из локального HTML" {
    if ! python3 -c "import playwright" 2>/dev/null; then
        skip "playwright не установлен"
    fi
    run python3 "$SCRIPT" "file://$TMP/test.html" --out "$TMP/screenshots/"
    [ "$status" -eq 0 ]
    [ -f "$TMP/screenshots/desktop.png" ]
    [ -f "$TMP/screenshots/mobile.png" ]
    [ -s "$TMP/screenshots/desktop.png" ]
    [ -s "$TMP/screenshots/mobile.png" ]
}

@test "take-page-screenshot: требует --out" {
    run python3 "$SCRIPT" "file://$TMP/test.html"
    [ "$status" -ne 0 ]
}

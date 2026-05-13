#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

setup() { TMP="$(mktemp -d)"; }
teardown() { rm -rf "$TMP"; }

@test "verify-composed-has-visuals: clean html → exit 0" {
    echo '<html><body><img src="real-icon.png" class="lp-icon"></body></html>' > "$TMP/composed.html"
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/composed.html"
    [ "$status" -eq 0 ]
}

@test "verify-composed-has-visuals: still has [SLOT: ...] → exit 1" {
    echo '<html><body>[SLOT: feature-1-icon]</body></html>' > "$TMP/composed.html"
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/composed.html"
    [ "$status" -eq 1 ]
}

@test "verify-composed-has-visuals: missing file → exit 2" {
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/nonexistent.html"
    [ "$status" -eq 2 ]
}

@test "verify-php-syntax: valid PHP → exit 0" {
    if ! command -v php >/dev/null 2>&1; then skip "php not installed"; fi
    mkdir -p "$TMP/wp-theme"
    echo '<?php echo "hello"; ?>' > "$TMP/wp-theme/index.php"
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/wp-theme"
    [ "$status" -eq 0 ]
}

@test "verify-php-syntax: broken PHP → exit 1" {
    if ! command -v php >/dev/null 2>&1; then skip "php not installed"; fi
    mkdir -p "$TMP/wp-theme"
    echo '<?php this is not php; }}}' > "$TMP/wp-theme/broken.php"
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/wp-theme"
    [ "$status" -ne 0 ]
}

@test "verify-php-syntax: missing dir → exit 2" {
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/nonexistent"
    [ "$status" -eq 2 ]
}

@test "verify-gutenberg-json: valid block.json files → exit 0" {
    mkdir -p "$TMP/blocks/hero"
    cat > "$TMP/blocks/hero/block.json" <<'EOF'
{"apiVersion": 3, "name": "lp/hero", "title": "Hero", "category": "design"}
EOF
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 0 ]
}

@test "verify-gutenberg-json: invalid JSON → exit 1" {
    mkdir -p "$TMP/blocks/hero"
    echo 'NOT JSON' > "$TMP/blocks/hero/block.json"
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 1 ]
}

@test "verify-gutenberg-json: empty dir → exit 0" {
    mkdir -p "$TMP/blocks"
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 0 ]
}

@test "verify-site-url: state without deploy_url → exit 2" {
    cat > "$TMP/.landing-state.yaml" <<'EOF'
project: test
stages: {}
EOF
    run bash "$REPO/scripts/verify-site-url.sh" "$TMP/.landing-state.yaml"
    [ "$status" -eq 2 ]
}

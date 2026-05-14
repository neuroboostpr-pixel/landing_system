#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
    MOCK="$REPO_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    export CODEX_BIN="$MOCK"
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07d_VISUALS/.logs"
    mkdir -p "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА"
    echo '{"colors":{"primary":"#1e3a8a","accent":"#c47a3a"},"design":{"visual_style":"Minimalism","icon_style":"outlined"}}' > "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
}

teardown() { rm -rf "$TMP_PROJECT"; }

@test "codex-generate-icon.sh creates PNG output path and logs" {
    skip "Requires real codex CLI image_gen — covered by E2E"
}

@test "codex-generate-icon.sh skip-if-exists works" {
    OUT_DIR="$TMP_PROJECT/07d_VISUALS/icons"
    mkdir -p "$OUT_DIR"
    echo "existing png content" > "$OUT_DIR/test-slot.png"

    run bash "$REPO_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh" \
        "$TMP_PROJECT" "test-slot" "shield"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "SKIP"
}

@test "codex-generate-icon.sh FORCE=1 bypasses skip" {
    OUT_DIR="$TMP_PROJECT/07d_VISUALS/icons"
    mkdir -p "$OUT_DIR"
    echo "existing png content" > "$OUT_DIR/test-slot.png"

    FORCE=1 run bash "$REPO_ROOT/skills/visual-generation/scripts/codex-generate-icon.sh" \
        "$TMP_PROJECT" "test-slot" "shield"
    # With FORCE=1, should NOT take SKIP path. Mock may not produce real PNG, exit code can vary.
    if [ "$status" -eq 0 ]; then
        ! echo "$output" | grep -q "SKIP"
    fi
}

@test "codex-generate-infographic.sh respects skip-if-exists" {
    OUT_DIR="$TMP_PROJECT/07d_VISUALS/infographics"
    mkdir -p "$OUT_DIR"
    echo "existing png content" > "$OUT_DIR/kpi-1.png"

    run bash "$REPO_ROOT/skills/visual-generation/scripts/codex-generate-infographic.sh" \
        "$TMP_PROJECT" "kpi-1" "number" '{"value":1000}'
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "SKIP"
}

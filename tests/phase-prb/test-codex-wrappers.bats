#!/usr/bin/env bats
# Tests for codex CLI wrappers.

setup() {
    REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
    MOCK="$REPO_ROOT/tests/phase-prb/fixtures/codex-mock.sh"
    export CODEX_BIN="$MOCK"
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07c_PHOTOS/.logs"
    mkdir -p "$TMP_PROJECT/07c_PHOTOS/intake"
    mkdir -p "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА"
    echo '{"colors":{"primary":"#1e3a8a"},"design":{"visual_style":"Minimalism"}}' > "$TMP_PROJECT/05_ДИЗАЙН-СИСТЕМА/tokens.json"
}

teardown() {
    rm -rf "$TMP_PROJECT"
}

@test "codex-classify.sh calls codex and writes catalog entry" {
    cp "$REPO_ROOT/tests/phase-prb/fixtures/red.jpg" "$TMP_PROJECT/07c_PHOTOS/intake/photo_test.jpg"

    export CODEX_MOCK_RESPONSE='tags: [portrait]
caption: "Test"
face_count: 1
composition: medium-shot
usable_ratios: ["1:1"]
brand_compatible: yes
notes: ""'

    run bash "$REPO_ROOT/skills/photo-curation/scripts/codex-classify.sh" \
        "$TMP_PROJECT" "$TMP_PROJECT/07c_PHOTOS/intake/photo_test.jpg"
    [ "$status" -eq 0 ]
    [ -f "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" ]
    grep -q "photo_test" "$TMP_PROJECT/07c_PHOTOS/catalog.yaml"
}

@test "codex-match.sh produces selections.draft.yaml" {
    cat > "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" <<'EOF'
photos:
  - id: photo_001
    tags: [portrait]
    caption: ""
    usable_ratios: ["1:1"]
EOF
    cat > "$TMP_PROJECT/07c_PHOTOS/_slots-input.yaml" <<'EOF'
slots:
  - slot_id: hero-bg
    block_id: ru-hero-01
    ratio: "16:9"
    hint: object photo
EOF

    export CODEX_MOCK_RESPONSE='slots:
  - slot_id: hero-bg
    candidates: []
    ai_fallback_needed: true
    required_user_approval: false
    ai_prompt: "test prompt"'

    run bash "$REPO_ROOT/skills/photo-curation/scripts/codex-match.sh" \
        "$TMP_PROJECT" \
        "$TMP_PROJECT/07c_PHOTOS/catalog.yaml" \
        "$TMP_PROJECT/07c_PHOTOS/_slots-input.yaml"
    [ "$status" -eq 0 ]
    [ -f "$TMP_PROJECT/07c_PHOTOS/selections.draft.yaml" ]
    grep -q "hero-bg" "$TMP_PROJECT/07c_PHOTOS/selections.draft.yaml"
}

@test "codex-generate-fallback.sh creates PNG output" {
    skip "Requires real codex CLI with image_gen — covered by E2E only"
}

@test "all wrappers log to 07c_PHOTOS/.logs/" {
    cp "$REPO_ROOT/tests/phase-prb/fixtures/red.jpg" "$TMP_PROJECT/07c_PHOTOS/intake/photo_x.jpg"
    export CODEX_MOCK_RESPONSE='tags: [object]
caption: "x"
face_count: 0
composition: object-only
usable_ratios: ["1:1"]
brand_compatible: yes
notes: ""'
    bash "$REPO_ROOT/skills/photo-curation/scripts/codex-classify.sh" \
        "$TMP_PROJECT" "$TMP_PROJECT/07c_PHOTOS/intake/photo_x.jpg"
    log_count=$(ls -1 "$TMP_PROJECT/07c_PHOTOS/.logs/" 2>/dev/null | wc -l)
    [ "$log_count" -gt 0 ]
}

#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export REPO_ROOT
    export TMP_PROJ="$(mktemp -d)/test-proj"
    mkdir -p "$TMP_PROJ"
}

teardown() {
    rm -rf "$TMP_PROJ"
}

@test "legacy bypass fails when stage not in legacy_allowed list" {
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "08_build":
    status: locked
    legacy: true
    legacy_reason: "old project"
EOF
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build \
        --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"not in legacy_allowed"* ]] || [[ "$output" == *"legacy_allowed"* ]]
}

@test "legacy bypass fails when legacy_reason missing" {
    # Temporarily add 06_stack to legacy_allowed for this test
    ALLOWLIST_BACKUP="$(mktemp)"
    cp "$REPO_ROOT/config/stage-gates.yaml" "$ALLOWLIST_BACKUP"
    yq -i '.legacy_allowed = ["06_stack"]' "$REPO_ROOT/config/stage-gates.yaml"

    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "06_stack":
    status: locked
    legacy: true
EOF
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 06_stack \
        --project "$TMP_PROJ" --auto
    rc=$status
    cp "$ALLOWLIST_BACKUP" "$REPO_ROOT/config/stage-gates.yaml"
    [ "$rc" -ne 0 ]
    [[ "$output" == *"legacy_reason"* ]]
}

@test "legacy bypass succeeds when stage allowlisted AND reason provided" {
    ALLOWLIST_BACKUP="$(mktemp)"
    cp "$REPO_ROOT/config/stage-gates.yaml" "$ALLOWLIST_BACKUP"
    yq -i '.legacy_allowed = ["06_stack"]' "$REPO_ROOT/config/stage-gates.yaml"

    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "06_stack":
    status: locked
    legacy: true
    legacy_reason: "migrated from v1"
EOF
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 06_stack \
        --project "$TMP_PROJ" --auto
    rc=$status
    cp "$ALLOWLIST_BACKUP" "$REPO_ROOT/config/stage-gates.yaml"
    [ "$rc" -eq 0 ]
    [[ "$output" == *"LEGACY BYPASS"* ]]
}

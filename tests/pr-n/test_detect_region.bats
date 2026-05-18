#!/usr/bin/env bats

PR_N_REPO_ROOT="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
DETECT="$PR_N_REPO_ROOT/skills/photo-curation/scripts/detect-region.py"

setup() {
    PROJECT="$(mktemp -d)"
}

teardown() {
    rm -rf "$PROJECT"
}

@test "detect-region: market-profile.md с **Geo:** Dubai → Dubai" {
    mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ"
    cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" <<'MD'
# Market profile
**Geo:** Dubai
MD
    run python3 "$DETECT" "$PROJECT"
    [ "$status" -eq 0 ]
    [ "$output" = "Dubai" ]
}

@test "detect-region: brief.md с Region: Moscow → Moscow" {
    mkdir -p "$PROJECT/00_БРИФ"
    cat > "$PROJECT/00_БРИФ/brief.md" <<'MD'
# Brief
Region: Moscow
MD
    run python3 "$DETECT" "$PROJECT"
    [ "$status" -eq 0 ]
    [ "$output" = "Moscow" ]
}

@test "detect-region: проект без файлов → global" {
    run python3 "$DETECT" "$PROJECT"
    [ "$status" -eq 0 ]
    [ "$output" = "global" ]
}

@test "detect-region: market-profile приоритетнее brief" {
    mkdir -p "$PROJECT/01a_АНАЛИЗ_НИШИ" "$PROJECT/00_БРИФ"
    cat > "$PROJECT/01a_АНАЛИЗ_НИШИ/market-profile.md" <<'MD'
**Geo:** Dubai, UAE
MD
    cat > "$PROJECT/00_БРИФ/brief.md" <<'MD'
Region: Moscow
MD
    run python3 "$DETECT" "$PROJECT"
    [ "$status" -eq 0 ]
    [ "$output" = "Dubai, UAE" ]
}

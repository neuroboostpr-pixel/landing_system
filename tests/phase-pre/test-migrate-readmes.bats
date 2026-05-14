#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
SCRIPT="$REPO/scripts/migrate-template-readmes.sh"

setup() {
    TMP="$(mktemp -d)"
    cp -r "$REPO/template/." "$TMP/project/"
    find "$TMP/project" -name "README.md" -delete 2>/dev/null || true
}
teardown() { rm -rf "$TMP"; }

@test "migrate adds README to project folder if missing" {
    run bash "$SCRIPT" "$TMP/project"
    [ "$status" -eq 0 ]
    [ -f "$TMP/project/00_БРИФ/README.md" ]
    [ -f "$TMP/project/04_БРЕНД/logos/README.md" ]
    [ -f "$TMP/project/07_ПРОТОТИП/source/README.md" ]
}

@test "migrate is idempotent" {
    bash "$SCRIPT" "$TMP/project"
    bash "$SCRIPT" "$TMP/project"
    [ -f "$TMP/project/00_БРИФ/README.md" ]
}

@test "migrate skips existing READMEs (no overwrite)" {
    mkdir -p "$TMP/project/00_БРИФ"
    echo "CUSTOM README" > "$TMP/project/00_БРИФ/README.md"
    bash "$SCRIPT" "$TMP/project"
    grep -q "CUSTOM README" "$TMP/project/00_БРИФ/README.md"
}

@test "migrate creates logos/ subfolder if missing" {
    rm -rf "$TMP/project/04_БРЕНД/logos"
    bash "$SCRIPT" "$TMP/project"
    [ -d "$TMP/project/04_БРЕНД/logos" ]
}

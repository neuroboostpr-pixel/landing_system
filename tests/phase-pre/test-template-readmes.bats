#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "every template folder has README.md" {
    for d in "$REPO/template/"*/; do
        [ -d "$d" ] || continue
        [ -f "$d/README.md" ] || {
            echo "Missing README: $d"; return 1
        }
    done
}

@test "04_БРЕНД has logos/ subfolder with README" {
    [ -d "$REPO/template/04_БРЕНД/logos" ]
    [ -f "$REPO/template/04_БРЕНД/logos/README.md" ]
}

@test "07_ПРОТОТИП has source/ subfolder with README" {
    [ -d "$REPO/template/07_ПРОТОТИП/source" ]
    [ -f "$REPO/template/07_ПРОТОТИП/source/README.md" ]
}

@test "logos README mentions logo.png and favicon" {
    grep -qE "logo\.(svg|png)" "$REPO/template/04_БРЕНД/logos/README.md"
    grep -qE "favicon" "$REPO/template/04_БРЕНД/logos/README.md"
}

@test "prototype source README mentions prototype.pdf" {
    grep -q "prototype.pdf" "$REPO/template/07_ПРОТОТИП/source/README.md"
}

#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "template/07d_VISUALS exists with README" {
    [ -d "$REPO/template/07d_VISUALS" ]
    [ -f "$REPO/template/07d_VISUALS/README.md" ]
}

@test "README is in Russian and mentions /landing-visuals" {
    body=$(cat "$REPO/template/07d_VISUALS/README.md")
    echo "$body" | grep -qE "иконк|инфограф"
    echo "$body" | grep -q "/landing-visuals"
}

@test "README explains icons + infographics + cache" {
    body=$(cat "$REPO/template/07d_VISUALS/README.md")
    echo "$body" | grep -qi "icon"
    echo "$body" | grep -qi "infograph"
    echo "$body" | grep -qi "cache\|кэш"
}

#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "visual-curator agent exists with frontmatter" {
    [ -f "$REPO/agents/visual-curator.md" ]
    head -10 "$REPO/agents/visual-curator.md" | grep -q "^name: visual-curator$"
}

@test "icon-generator agent exists with frontmatter" {
    [ -f "$REPO/agents/icon-generator.md" ]
    head -10 "$REPO/agents/icon-generator.md" | grep -q "^name: icon-generator$"
}

@test "infographic-builder agent exists with frontmatter" {
    [ -f "$REPO/agents/infographic-builder.md" ]
    head -10 "$REPO/agents/infographic-builder.md" | grep -q "^name: infographic-builder$"
}

@test "visual-curator references both sub-agents and /landing-visuals" {
    body=$(cat "$REPO/agents/visual-curator.md")
    echo "$body" | grep -q "icon-generator"
    echo "$body" | grep -q "infographic-builder"
    echo "$body" | grep -q "/landing-visuals"
}

@test "visual-curator references stage gates 05_design and 07b composed" {
    body=$(cat "$REPO/agents/visual-curator.md")
    echo "$body" | grep -qi "05_design\|05_ДИЗАЙН"
    echo "$body" | grep -qi "07b\|composed"
}

#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "photo-curator agent has frontmatter with name + description" {
    [ -f "$REPO/agents/photo-curator.md" ]
    head -10 "$REPO/agents/photo-curator.md" | grep -q "^name: photo-curator$"
    head -10 "$REPO/agents/photo-curator.md" | grep -q "^description:"
}

@test "photo-classifier agent has correct frontmatter" {
    [ -f "$REPO/agents/photo-classifier.md" ]
    head -10 "$REPO/agents/photo-classifier.md" | grep -q "^name: photo-classifier$"
}

@test "photo-matcher agent has correct frontmatter" {
    [ -f "$REPO/agents/photo-matcher.md" ]
    head -10 "$REPO/agents/photo-matcher.md" | grep -q "^name: photo-matcher$"
}

@test "photo-preview-board agent has correct frontmatter" {
    [ -f "$REPO/agents/photo-preview-board.md" ]
    head -10 "$REPO/agents/photo-preview-board.md" | grep -q "^name: photo-preview-board$"
}

@test "all 4 agents reference IDENTITY_SAFE.md" {
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-curator.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-classifier.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-matcher.md"
    grep -q "IDENTITY_SAFE" "$REPO/agents/photo-preview-board.md"
}

@test "photo-curator references all 3 sub-agents and /landing-photos command" {
    body=$(cat "$REPO/agents/photo-curator.md")
    echo "$body" | grep -q "photo-classifier"
    echo "$body" | grep -q "photo-matcher"
    echo "$body" | grep -q "photo-preview-board"
    echo "$body" | grep -q "/landing-photos"
}

@test "photo-curator references stage gates 05 design and 07a wireframe" {
    body=$(cat "$REPO/agents/photo-curator.md")
    echo "$body" | grep -qi "05_design\|05 design\|05_ДИЗАЙН"
    echo "$body" | grep -qi "07a_wireframe\|07a wireframe\|07a_WIREFRAME"
}

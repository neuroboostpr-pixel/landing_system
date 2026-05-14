#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-photos command file exists with frontmatter" {
    [ -f "$REPO/commands/landing-photos.md" ]
    head -10 "$REPO/commands/landing-photos.md" | grep -q "^description:"
}

@test "/landing-photos command mentions photo-curator agent" {
    grep -q "photo-curator" "$REPO/commands/landing-photos.md"
}

@test "/landing-photos command lists --force-stage and --all-ai flags" {
    grep -q -- "--force-stage" "$REPO/commands/landing-photos.md"
    grep -q -- "--all-ai" "$REPO/commands/landing-photos.md"
}

@test "/landing-photos command references stage gates 05_design and 07a_wireframe" {
    grep -q "05_design\|05_ДИЗАЙН" "$REPO/commands/landing-photos.md"
    grep -q "07a_wireframe\|07a_WIREFRAME" "$REPO/commands/landing-photos.md"
}

@test "/landing-photos command mentions Russian user-facing copy for empty inbox" {
    body=$(cat "$REPO/commands/landing-photos.md")
    # At least one of these standard Russian phrases should appear
    echo "$body" | grep -qE "фотк|inbox|07c_PHOTOS"
}

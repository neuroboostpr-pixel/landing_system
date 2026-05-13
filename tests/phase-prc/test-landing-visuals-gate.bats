#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-visuals command exists with frontmatter" {
    [ -f "$REPO/commands/landing-visuals.md" ]
    head -10 "$REPO/commands/landing-visuals.md" | grep -q "^description:"
}

@test "/landing-visuals mentions visual-curator agent" {
    grep -q "visual-curator" "$REPO/commands/landing-visuals.md"
}

@test "/landing-visuals lists --type --force --slot flags" {
    grep -q -- "--type" "$REPO/commands/landing-visuals.md"
    grep -q -- "--force" "$REPO/commands/landing-visuals.md"
    grep -q -- "--slot" "$REPO/commands/landing-visuals.md"
}

@test "/landing-visuals references stage gates 05_design + 07b_COMPOSED" {
    grep -qE "05_design|05_ДИЗАЙН" "$REPO/commands/landing-visuals.md"
    grep -qE "07b_COMPOSED|composed.html|composed" "$REPO/commands/landing-visuals.md"
}

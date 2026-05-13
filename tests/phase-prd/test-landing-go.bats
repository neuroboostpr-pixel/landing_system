#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-go command file exists with frontmatter" {
    [ -f "$REPO/commands/landing-go.md" ]
    head -10 "$REPO/commands/landing-go.md" | grep -q "^description:"
}

@test "/landing-go mentions auto-resume from state.yaml" {
    grep -qE "state\.yaml|state\.|auto.?resume|resume" "$REPO/commands/landing-go.md"
}

@test "/landing-go mentions key flags --auto-fix and --skip-gate" {
    grep -q -- "--auto-fix" "$REPO/commands/landing-go.md"
    grep -q -- "--skip-gate" "$REPO/commands/landing-go.md"
}

@test "/landing-go mentions landing-orchestrator agent" {
    grep -q "landing-orchestrator" "$REPO/commands/landing-go.md"
}

@test "/landing-go documents prototype-first entry" {
    body=$(cat "$REPO/commands/landing-go.md")
    echo "$body" | grep -qE "prototype|07_ПРОТОТИП"
    echo "$body" | grep -q "07a_prototype"
}

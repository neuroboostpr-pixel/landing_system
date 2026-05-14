#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
CMD="$REPO/commands/landing-start.md"

@test "/landing-start command file exists with frontmatter" {
    [ -f "$CMD" ]
    head -10 "$CMD" | grep -q "^description:"
}

@test "/landing-start references landing-onboarding-wizard agent" {
    grep -q "landing-onboarding-wizard" "$CMD"
}

@test "/landing-start documents 4 steps" {
    grep -q "Прототип" "$CMD"
    grep -q "Фото" "$CMD"
    grep -qE "Логотип|логотип" "$CMD"
    grep -qE "Референс|референс" "$CMD"
}

@test "/landing-start mentions /landing-go as next step" {
    grep -q "/landing-go" "$CMD"
}

@test "/landing-start mentions it's the main entry point" {
    body=$(cat "$CMD")
    echo "$body" | grep -qE "главн|main|основн|first|первая"
}

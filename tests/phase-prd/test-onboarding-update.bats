#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
ONB="$REPO/skills/landing-onboarding/SKILL.md"

@test "onboarding references install-codex.sh" {
    grep -q "install-codex" "$ONB"
}

@test "onboarding explains /landing-go entry point" {
    grep -q "/landing-go" "$ONB"
}

@test "onboarding explains prototype-first flow" {
    grep -qE "prototype-first|07_ПРОТОТИП/source|положи prototype" "$ONB"
}

@test "onboarding mentions both PR-B and PR-C commands" {
    grep -q "/landing-photos" "$ONB"
    grep -q "/landing-visuals" "$ONB"
}

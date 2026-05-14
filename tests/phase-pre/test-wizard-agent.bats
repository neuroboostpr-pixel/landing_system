#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
AGENT="$REPO/agents/landing-onboarding-wizard.md"

@test "wizard agent file exists with frontmatter" {
    [ -f "$AGENT" ]
    head -10 "$AGENT" | grep -q "^name: landing-onboarding-wizard$"
    head -10 "$AGENT" | grep -q "^description:"
}

@test "wizard explains 3-paragraph welcome" {
    grep -q "Добро пожаловать" "$AGENT"
}

@test "wizard documents all 4 material steps" {
    grep -q "ШАГ 1" "$AGENT"
    grep -q "ШАГ 2" "$AGENT"
    grep -q "ШАГ 3" "$AGENT"
    grep -q "ШАГ 4" "$AGENT"
}

@test "wizard mentions step 1 prototype is REQUIRED" {
    grep -qE "ОБЯЗАТЕЛЬНО|обязательн|required" "$AGENT"
}

@test "wizard references wizard-check-materials.py" {
    grep -q "wizard-check-materials" "$AGENT"
}

@test "wizard references landing-project-init skill" {
    grep -q "landing-project-init" "$AGENT"
}

@test "wizard ends by suggesting /landing-go" {
    grep -q "/landing-go" "$AGENT"
}

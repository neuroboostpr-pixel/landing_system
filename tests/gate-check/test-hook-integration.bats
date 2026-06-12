#!/usr/bin/env bats

@test "settings.json contains PreToolUse hook for enforce_stage_gate" {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    [ -f "$REPO_ROOT/.claude/settings.json" ]
    grep -q "enforce_stage_gate" "$REPO_ROOT/.claude/settings.json"
}

@test "enforce_stage_gate.py is executable" {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    [ -x "$REPO_ROOT/scripts/hooks/enforce_stage_gate.py" ]
}

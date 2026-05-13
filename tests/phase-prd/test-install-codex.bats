#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "install-codex.sh exists and is executable" {
    [ -x "$REPO/scripts/install-codex.sh" ]
}

@test "install-codex.sh --check reports installed when codex on PATH" {
    if ! command -v codex >/dev/null 2>&1; then skip "codex not installed locally"; fi
    run bash "$REPO/scripts/install-codex.sh" --check
    [ "$status" -eq 0 ]
    echo "$output" | grep -qiE "уже установлен|already installed"
}

@test "install-codex.sh --check exits non-zero when codex absent (in mock PATH)" {
    run env PATH="/usr/bin:/bin" bash "$REPO/scripts/install-codex.sh" --check
    [ "$status" -ne 0 ]
}

@test "install-codex.sh --dry-run prints commands without running them" {
    run env PATH="/usr/bin:/bin" bash "$REPO/scripts/install-codex.sh" --dry-run
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "npm i -g @openai/codex"
}

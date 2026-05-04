#!/usr/bin/env bats
# tests/phase-5/integration/test-phase5-setup.bats
REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

@test "preflight.sh exists and is executable" {
  [ -f "$REPO_ROOT/scripts/preflight.sh" ]
  [ -x "$REPO_ROOT/scripts/preflight.sh" ]
}

@test "preflight.sh output contains section headers" {
  run bash "$REPO_ROOT/scripts/preflight.sh"
  [[ "$output" == *"Preflight Check"* ]]
}

@test "system.yaml.template exists" {
  [ -f "$REPO_ROOT/config/system.yaml.template" ]
}

@test ".env.example exists" {
  [ -f "$REPO_ROOT/.env.example" ]
}

@test ".env.example contains BEGET_USER" {
  grep -q "BEGET_USER" "$REPO_ROOT/.env.example"
}

@test ".env.example contains TG_BOT_TOKEN" {
  grep -q "TG_BOT_TOKEN" "$REPO_ROOT/.env.example"
}

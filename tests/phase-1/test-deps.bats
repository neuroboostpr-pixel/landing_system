#!/usr/bin/env bats

@test "bats-core installed" {
  run bats --version
  [ "$status" -eq 0 ]
}

@test "git installed" {
  run git --version
  [ "$status" -eq 0 ]
}

@test "node installed and version >= 20" {
  run node --version
  [ "$status" -eq 0 ]
  # node --version returns "v22.x.x" — strip "v" and compare major
  major=$(echo "$output" | sed 's/v//' | cut -d. -f1)
  [ "$major" -ge 20 ]
}

@test "bash version >= 5" {
  major=$(bash --version | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 | cut -d. -f1)
  [ "$major" -ge 5 ]
}

@test "check-deps.sh exists and executable" {
  [ -x "scripts/check-deps.sh" ]
}

@test "check-deps.sh exits 0 when all deps present" {
  run scripts/check-deps.sh
  [ "$status" -eq 0 ]
}

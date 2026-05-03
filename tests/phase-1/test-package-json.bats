#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "package.json exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/package.json"
}

@test "package.json is valid JSON" {
  run node -e "JSON.parse(require('fs').readFileSync('$LANDING_SYSTEM_ROOT/package.json', 'utf8'))"
  [ "$status" -eq 0 ]
}

@test "package.json has correct name" {
  run node -e "console.log(require('$LANDING_SYSTEM_ROOT/package.json').name)"
  [ "$output" = "landing-system" ]
}

@test "package.json has test script using bats" {
  run node -e "console.log(require('$LANDING_SYSTEM_ROOT/package.json').scripts.test)"
  [[ "$output" =~ "bats" ]]
}

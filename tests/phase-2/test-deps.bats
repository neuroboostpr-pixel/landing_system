#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "python3 installed and >= 3.10" {
  run python3 --version
  [ "$status" -eq 0 ]
  major=$(echo "$output" | sed -E 's/Python ([0-9]+).([0-9]+).*/\1/')
  minor=$(echo "$output" | sed -E 's/Python ([0-9]+).([0-9]+).*/\2/')
  [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]
}

@test "requirements.txt exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/requirements.txt"
}

@test "requirements.txt lists core deps" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "Pillow"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "colorthief"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "Jinja2"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "trafilatura"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "playwright"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "beautifulsoup4"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "pytest"
  assert_file_contains "$LANDING_SYSTEM_ROOT/requirements.txt" "responses"
}

@test "playwright Chromium installed" {
  run python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); b.close(); p.stop()"
  [ "$status" -eq 0 ]
}

@test "pytest can discover phase-2 tests folder" {
  cd "$LANDING_SYSTEM_ROOT"
  run python3 -m pytest tests/phase-2/python --collect-only -q 2>&1
  # Either collects something OR returns "no tests collected" (acceptable on first run)
  [ "$status" -eq 0 ] || [ "$status" -eq 5 ]
}

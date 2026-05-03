#!/usr/bin/env bash
# Shared test helpers for landing-system

# Create a temp directory for test isolation
setup_temp_dir() {
  TEST_TEMP=$(mktemp -d -t "landing-test-XXXXXX")
  export TEST_TEMP
}

# Cleanup
teardown_temp_dir() {
  if [ -n "${TEST_TEMP:-}" ] && [ -d "$TEST_TEMP" ]; then
    rm -rf "$TEST_TEMP"
  fi
}

# Assert directory exists
assert_dir_exists() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    echo "Expected directory '$dir' to exist"
    return 1
  fi
}

# Assert file exists
assert_file_exists() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "Expected file '$file' to exist"
    return 1
  fi
}

# Assert file contains string
assert_file_contains() {
  local file="$1"
  local needle="$2"
  if ! grep -q "$needle" "$file"; then
    echo "Expected file '$file' to contain '$needle'"
    echo "Actual content:"
    cat "$file"
    return 1
  fi
}

# Path to landing-system root (for tests)
LANDING_SYSTEM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export LANDING_SYSTEM_ROOT

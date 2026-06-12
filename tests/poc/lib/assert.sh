#!/usr/bin/env bash
# Tiny assertion helpers. Each test script source-s this and uses pass/fail/info.

# Colors (no-op on Windows Git Bash if not a TTY).
if [ -t 1 ]; then
  C_OK="\033[32m"; C_FAIL="\033[31m"; C_WARN="\033[33m"; C_INFO="\033[36m"; C_OFF="\033[0m"
else
  C_OK=""; C_FAIL=""; C_WARN=""; C_INFO=""; C_OFF=""
fi

CURRENT_TEST="${CURRENT_TEST:-unknown}"
TEST_FAILED=0

info() { echo -e "${C_INFO}[info]${C_OFF} $*"; }
warn() { echo -e "${C_WARN}[warn]${C_OFF} $*"; }

pass() {
  echo -e "${C_OK}[PASS]${C_OFF} $*"
}

fail() {
  echo -e "${C_FAIL}[FAIL]${C_OFF} $*"
  TEST_FAILED=1
}

assert_contains() {
  # assert_contains "<haystack>" "<needle>" "<description>"
  if echo "$1" | grep -qF "$2"; then
    pass "$3 (found: $2)"
  else
    fail "$3 (missing: $2)"
  fi
}

assert_not_contains() {
  if echo "$1" | grep -qF "$2"; then
    fail "$3 (unexpectedly found: $2)"
  else
    pass "$3 (correctly absent: $2)"
  fi
}

assert_http_status() {
  # assert_http_status <url> <expected_code> [user_agent]
  local url="$1" want="$2" ua="${3:-Mozilla/5.0 (POC)}"
  local got
  got=$(curl -k -s -o /dev/null -w "%{http_code}" -A "$ua" "$url" || echo "000")
  if [ "$got" = "$want" ]; then
    pass "HTTP $got from $url"
  else
    fail "HTTP $got from $url (wanted $want)"
  fi
}

curl_fetch() {
  # curl_fetch <url> [user_agent]
  local url="$1" ua="${2:-Mozilla/5.0 (POC)}"
  curl -k -s -A "$ua" "$url"
}

finish_test() {
  if [ "$TEST_FAILED" -eq 0 ]; then
    echo -e "\n${C_OK}=== $CURRENT_TEST: GREEN ===${C_OFF}\n"
    exit 0
  else
    echo -e "\n${C_FAIL}=== $CURRENT_TEST: RED ===${C_OFF}\n"
    exit 1
  fi
}

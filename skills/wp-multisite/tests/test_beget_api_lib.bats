#!/usr/bin/env bats
# Unit tests for lib/beget-api.sh — beget_api wrapper

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    # Mock curl: write expected stub responses
    MOCK_DIR="$(mktemp -d)"
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Mock curl that prints fixture based on method in URL
url=""
for arg in "$@"; do
    case "$arg" in
        https://*) url="$arg" ;;
    esac
done
case "$url" in
    *getAccountInfo*)
        echo '{"status":"success","answer":{"status":"success","result":{"plan_name":"Blog"}}}'
        ;;
    *getList*)
        echo '{"status":"success","answer":{"status":"success","result":[{"id":12513532,"fqdn":"example.ru"}]}}'
        ;;
    *)
        echo '{"status":"success","answer":{"status":"error","errors":[{"error_code":"UNEXPECTED","error_text":"mock fallthrough"}]}}'
        ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    PATH="$MOCK_DIR:$PATH"
    export PATH
    export BEGET_API="https://api.beget.com/api"
    export BEGET_LOGIN="testuser"
    export BEGET_PASSWD="testpass"
    source "$HERE/beget-api.sh"
}

teardown() {
    rm -rf "$MOCK_DIR"
}

@test "beget_api wraps a successful call and returns the JSON body" {
    run beget_api "user/getAccountInfo"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"plan_name":"Blog"'* ]]
}

@test "beget_ok returns 0 when both outer and inner status are success" {
    resp='{"status":"success","answer":{"status":"success","result":true}}'
    run beget_ok "$resp"
    [ "$status" -eq 0 ]
}

@test "beget_ok returns 1 when inner status is error" {
    resp='{"status":"success","answer":{"status":"error","errors":[{"error_text":"x"}]}}'
    run beget_ok "$resp"
    [ "$status" -eq 1 ]
}

@test "beget_ok returns 1 when outer status is error" {
    resp='{"status":"error","error_text":"auth"}'
    run beget_ok "$resp"
    [ "$status" -eq 1 ]
}

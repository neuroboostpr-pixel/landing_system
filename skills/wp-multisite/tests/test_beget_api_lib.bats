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

@test "beget_error_text: standard nested errors array" {
    resp='{"answer":{"errors":[{"error_text":"foo"}]}}'
    run beget_error_text "$resp"
    [ "$status" -eq 0 ]
    [ "$output" = "foo" ]
}

@test "beget_error_text: top-level auth error" {
    resp='{"status":"error","error_text":"auth"}'
    run beget_error_text "$resp"
    [ "$status" -eq 0 ]
    [ "$output" = "auth" ]
}

@test "beget_error_text: garbage input returns parse_error or unknown" {
    run beget_error_text "not json at all"
    [ "$status" -eq 0 ]
    [[ "$output" = "parse_error" || "$output" = "unknown" ]]
}

@test "beget_api fails clearly when BEGET_LOGIN is empty" {
    BEGET_LOGIN=""
    run beget_api "user/getAccountInfo"
    [ "$status" -eq 1 ]
    # bats merges stderr into $output; check combined output
    [[ "$output" == *"missing required env vars"* ]]
}

@test "beget_subdomain_exists returns 0 when subdomain present in list" {
    # Override mock to return one subdomain
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[{"id":42,"fqdn":"alpha.example.ru","domain_id":1}]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_exists "alpha.example.ru"
    [ "$status" -eq 0 ]
}

@test "beget_subdomain_exists returns 1 when subdomain absent" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_exists "alpha.example.ru"
    [ "$status" -eq 1 ]
}

@test "beget_subdomain_add returns the new subdomain id on success" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":99}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_add "alpha" 12513532
    [ "$status" -eq 0 ]
    [ "$output" = "99" ]
}

@test "beget_subdomain_id returns id of named subdomain when present" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[{"id":77,"fqdn":"beta.example.ru"}]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_id "beta.example.ru"
    [ "$status" -eq 0 ]
    [ "$output" = "77" ]
}

@test "beget_subdomain_exists handles fqdn with quotes safely (no injection)" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[{"id":1,"fqdn":"alpha.example.ru"}]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    # This input would inject Python code in vulnerable impl, but should just not-match
    run beget_subdomain_exists "alpha'; import os; os.system('echo PWNED'); x='"
    [ "$status" -eq 1 ]  # not found, but did not execute injected code
    [[ "$output" != *"PWNED"* ]]
}

@test "beget_subdomain_add rejects invalid subdomain chars" {
    run beget_subdomain_add 'bad"slug' 12345
    [ "$status" -eq 1 ]
    [[ "$output" == *"invalid subdomain"* ]]
}

@test "beget_subdomain_add rejects non-numeric root_id" {
    run beget_subdomain_add "alpha" "not-a-number"
    [ "$status" -eq 1 ]
    [[ "$output" == *"numeric"* ]]
}

@test "beget_subdomain_add accepts wildcard '*' as subdomain" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":555}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_add "*" 12345
    [ "$status" -eq 0 ]
    [ "$output" = "555" ]
}

@test "beget_set_php rejects malformed version" {
    run beget_set_php "alpha.example.ru" "not-a-version"
    [ "$status" -eq 1 ]
    [[ "$output" == *"version"* ]]
}

@test "beget_api passes input_data JSON verbatim (no spurious closing brace)" {
    # Regression for bug: local input_data="${2:-{}}" appended extra } to value.
    # Mock prints out the input_data parameter so we can verify exact bytes.
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Extract input_data argument verbatim and echo it (one per --data-urlencode pair)
for arg in "$@"; do
    case "$arg" in
        input_data=*) echo "${arg#input_data=}"; exit 0 ;;
    esac
done
echo "NO_INPUT_DATA"
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_api "domain/addSubdomainVirtual" '{"subdomain":"test","domain_id":12345}'
    [ "$status" -eq 0 ]
    [ "$output" = '{"subdomain":"test","domain_id":12345}' ]
    # critically: no trailing }} or other corruption
    [[ "$output" != *'}}' ]]
}

@test "beget_api defaults input_data to {} when not provided" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
for arg in "$@"; do
    case "$arg" in
        input_data=*) echo "${arg#input_data=}"; exit 0 ;;
    esac
done
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_api "user/getAccountInfo"
    [ "$status" -eq 0 ]
    [ "$output" = '{}' ]
}

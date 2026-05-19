#!/usr/bin/env bats
# Integration-ish tests for migrate-to-multisite.sh
# Uses mock curl + mock ssh for all Beget/SSH calls.

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/migrate-to-multisite.sh"
    LIB_DIR="$BATS_TEST_DIRNAME/../scripts/lib"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"
    # Minimal .landing-state.yaml + .env for project
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.single.yaml" "$PROJECT_DIR/.landing-state.yaml"
    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_LOGIN=testuser
BEGET_PASSWD=testpass
BEGET_API=https://api.beget.com/api
BEGET_SSH_KEY=/tmp/fake_key
BEGET_DOMAIN_ID=12345
BEGET_PATH=/home/t/testuser/example.ru/public_html
ROOT_DOMAIN=example.ru
BEGET_SITE_ID=99999
EOF

    # Mock curl returns success-shape JSON for all calls
    # getSubdomainList call counter lives in BATS_TMPDIR
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Track each call by writing to log
echo "CURL $*" >> "$BATS_TMPDIR/curl_calls.log"
# Route by method
case "$*" in
    *getSubdomainList*)
        # First call (beget_subdomain_exists): return empty list → triggers addSubdomainVirtual.
        # Second call (beget_subdomain_id): return the wildcard entry.
        COUNT_FILE="$BATS_TMPDIR/getsubdomainlist_count"
        COUNT=$(cat "$COUNT_FILE" 2>/dev/null || echo 0)
        COUNT=$((COUNT + 1))
        echo "$COUNT" > "$COUNT_FILE"
        if [ "$COUNT" -eq 1 ]; then
            echo '{"status":"success","answer":{"status":"success","result":[]}}'
        else
            echo '{"status":"success","answer":{"status":"success","result":[{"id":777,"fqdn":"*.example.ru"}]}}'
        fi
        ;;
    *addSubdomainVirtual*)
        echo '{"status":"success","answer":{"status":"success","result":888}}'
        ;;
    *)
        echo '{"status":"success","answer":{"status":"success","result":true}}'
        ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"

    # Mock ssh prints commands instead of running them
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
echo "MOCK_OK"
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f "$BATS_TMPDIR/curl_calls.log" "$BATS_TMPDIR/ssh_calls.log" "$BATS_TMPDIR/getsubdomainlist_count"
    PATH="$MOCK_DIR:$PATH"
    export PATH MOCK_DIR PROJECT_DIR BATS_TMPDIR
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "migrate exits early when state.multisite already true" {
    # Replace single state with multisite state
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$PROJECT_DIR/.landing-state.yaml"
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"already multisite"* ]]
}

@test "migrate creates wildcard subdomain via Beget API" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "addSubdomainVirtual" "$BATS_TMPDIR/curl_calls.log"
}

@test "migrate calls WP_ALLOW_MULTISITE config set" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "config set WP_ALLOW_MULTISITE" "$BATS_TMPDIR/ssh_calls.log"
}

@test "migrate calls core multisite-convert" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "core multisite-convert" "$BATS_TMPDIR/ssh_calls.log"
}

@test "migrate writes .htaccess" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q ".htaccess" "$BATS_TMPDIR/ssh_calls.log"
}

@test "migrate network-activates lazy-blocks + seo-by-rank-math" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "plugin install lazy-blocks" "$BATS_TMPDIR/ssh_calls.log"
    grep -q "plugin install seo-by-rank-math" "$BATS_TMPDIR/ssh_calls.log"
    grep -q "activate-network" "$BATS_TMPDIR/ssh_calls.log"
}

@test "migrate sets multisite=true in state after success" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "^multisite: true" "$PROJECT_DIR/.landing-state.yaml"
}

@test "migrate sets PHP 8.3 for root + wildcard FQDNs" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "changePhpVersion" "$BATS_TMPDIR/curl_calls.log"
}

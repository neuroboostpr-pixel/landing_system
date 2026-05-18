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
EOF

    # Mock curl returns success-shape JSON for all calls
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Track each call by writing to log
echo "CURL $*" >> "$BATS_TMPDIR/curl_calls.log"
# Default success response
echo '{"status":"success","answer":{"status":"success","result":true}}'
MOCK
    chmod +x "$MOCK_DIR/curl"

    # Mock ssh prints commands instead of running them
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
echo "MOCK_OK"
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f "$BATS_TMPDIR/curl_calls.log" "$BATS_TMPDIR/ssh_calls.log"
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

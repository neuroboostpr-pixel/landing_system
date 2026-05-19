#!/usr/bin/env bats
# Tests for install-mu-plugin.sh — uses mock rsync + ssh

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/install-mu-plugin.sh"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"

    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_SSH_KEY=/tmp/fake_key
BEGET_PATH=/home/t/testuser/example.ru/public_html
EOF

    cat > "$MOCK_DIR/rsync" <<'MOCK'
#!/bin/bash
echo "RSYNC $*" >> "$BATS_TMPDIR/rsync_calls.log"
echo "sent 100 bytes  received 50 bytes"
MOCK
    chmod +x "$MOCK_DIR/rsync"

    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
echo "OK"
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f "$BATS_TMPDIR/rsync_calls.log" "$BATS_TMPDIR/ssh_calls.log"
    PATH="$MOCK_DIR:$PATH"
    export PATH
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "install-mu-plugin exits 2 when project-dir missing" {
    run bash "$SCRIPT"
    [ "$status" -eq 2 ]
    [[ "$output" == *"Usage:"* ]]
}

@test "install-mu-plugin exits 1 when .env missing" {
    rm "$PROJECT_DIR/.env"
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 1 ]
    [[ "$output" == *".env"* ]]
}

@test "install-mu-plugin runs rsync of mu-plugin to remote" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "RSYNC" "$BATS_TMPDIR/rsync_calls.log"
    grep -q "landing-config" "$BATS_TMPDIR/rsync_calls.log"
    grep -q "wp-content/mu-plugins" "$BATS_TMPDIR/rsync_calls.log"
}

@test "install-mu-plugin triggers init via wp eval over ssh" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "wp-cli.phar" "$BATS_TMPDIR/ssh_calls.log"
}

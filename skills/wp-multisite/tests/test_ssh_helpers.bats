#!/usr/bin/env bats
# Unit tests for lib/ssh-helpers.sh — uses mock ssh

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    MOCK_DIR="$(mktemp -d)"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "MOCK_SSH_CALLED $*"
MOCK
    chmod +x "$MOCK_DIR/ssh"
    PATH="$MOCK_DIR:$PATH"
    export PATH
    export BEGET_USER="testuser"
    export BEGET_HOST="example.beget.tech"
    export BEGET_SSH_KEY="/tmp/fake_key"
    source "$HERE/ssh-helpers.sh"
}

teardown() { rm -rf "$MOCK_DIR"; }

@test "ssh_beget runs ssh with -i key and user@host" {
    run ssh_beget "echo hello"
    [ "$status" -eq 0 ]
    [[ "$output" == *"MOCK_SSH_CALLED"* ]]
    [[ "$output" == *"-i /tmp/fake_key"* ]]
    [[ "$output" == *"testuser@example.beget.tech"* ]]
    [[ "$output" == *"echo hello"* ]]
}

@test "wp_remote prepends REMOTE_WP path to args and quotes them" {
    run wp_remote "/wp/path" "option get siteurl"
    [ "$status" -eq 0 ]
    [[ "$output" == *"cd /wp/path"* ]]
    [[ "$output" == *"/usr/local/bin/php8.3"* ]]
    [[ "$output" == *"option get siteurl"* ]]
}

@test "wp_remote_url prepends --url flag" {
    run wp_remote_url "/wp/path" "http://alpha.example.ru" "post list"
    [ "$status" -eq 0 ]
    [[ "$output" == *"--url=http://alpha.example.ru"* ]]
    [[ "$output" == *"post list"* ]]
}

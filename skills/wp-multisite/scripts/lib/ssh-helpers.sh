#!/usr/bin/env bash
# SSH + wp-cli wrappers for Beget shared.
# Required env: BEGET_USER, BEGET_HOST, BEGET_SSH_KEY

# wp-cli on Beget: default /usr/local/bin/wp shim runs PHP 7.4. We need 8.3,
# so always call wp-cli.phar directly with php8.3 binary.
REMOTE_WP_BIN="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar"

ssh_opts() {
    echo "-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
}

ssh_beget() {
    # ssh_beget "<remote-command>"
    local opts; opts=$(ssh_opts)
    ssh $opts "${BEGET_USER}@${BEGET_HOST}" "$1"
}

wp_remote() {
    # wp_remote <wp-path> <wp-cli-args> — run wp-cli inside wp directory
    local wp_path="$1"; shift
    ssh_beget "cd $wp_path && $REMOTE_WP_BIN $*"
}

wp_remote_url() {
    # wp_remote_url <wp-path> <url> <wp-cli-args> — adds --url for multisite
    local wp_path="$1" url="$2"; shift 2
    ssh_beget "cd $wp_path && $REMOTE_WP_BIN --url=$url $*"
}

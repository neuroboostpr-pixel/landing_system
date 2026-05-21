#!/usr/bin/env bash
# SSH helper for Beget.

ssh_run() {
  # ssh_run "<command>"
  ssh $BEGET_SSH_OPTS "${BEGET_SSH_USER}@${BEGET_SSH_HOST}" "$1"
}

ssh_run_in_wp() {
  # ssh_run_in_wp "<command>"
  # Runs command with cwd = wp installation directory.
  ssh $BEGET_SSH_OPTS "${BEGET_SSH_USER}@${BEGET_SSH_HOST}" "cd ${TEST_WP_PATH} && $1"
}

ssh_wp() {
  # ssh_wp "<wp-cli args>"
  # Runs wp-cli inside wp directory with PHP 8.3.
  ssh_run_in_wp "${REMOTE_WP} $1"
}

scp_to() {
  # scp_to <local_file> <remote_path_relative_to_home>
  scp $BEGET_SSH_OPTS "$1" "${BEGET_SSH_USER}@${BEGET_SSH_HOST}:$2"
}

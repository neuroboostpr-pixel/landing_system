#!/usr/bin/env bash
# POC environment template.
# Copy to env.sh and fill in real values. env.sh is gitignored.

# Beget API (https://beget.com/ru/kb/api/)
export BEGET_LOGIN="YOUR_LOGIN"
export BEGET_PASSWD='YOUR_API_PASSWORD'   # NOT main account password — API-specific password
export BEGET_API="https://api.beget.com/api"

# SSH access (Beget shared default host: <login>.beget.tech)
export BEGET_SSH_HOST="YOUR_LOGIN.beget.tech"
export BEGET_SSH_USER="YOUR_LOGIN"
export BEGET_SSH_KEY="$HOME/.ssh/beget_poc"
export BEGET_SSH_OPTS="-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

# Test playground domain (must be already in your Beget account, NS on Beget)
export TEST_DOMAIN="example.ru"

# MySQL DB (will be created by 00-setup via mysql/addDb)
export TEST_DB_NAME="${BEGET_LOGIN}_poc"
export TEST_DB_USER="${BEGET_LOGIN}_poc"
export TEST_DB_PASS='ChangeMe2026Aa1!'

export TEST_WP_PATH="/home/${BEGET_SSH_USER:0:1}/${BEGET_SSH_USER}/${TEST_DOMAIN}/public_html"
export TEST_WP_URL="https://${TEST_DOMAIN}"

# Subsites created by 00-setup
export SUBSITE_1="alpha.${TEST_DOMAIN}"
export SUBSITE_2="bravo.${TEST_DOMAIN}"
export SUBSITE_3="clone.${TEST_DOMAIN}"  # used by 10-clone test

# PHP binary on Beget (CLI default is 5.6, we need 8.3)
export REMOTE_PHP="/usr/local/bin/php8.3"
export REMOTE_WP="$REMOTE_PHP /usr/local/bin/wp-cli.phar"

# Logs/results
export POC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LOGS_DIR="$POC_DIR/logs"
mkdir -p "$LOGS_DIR"

#!/usr/bin/env bash
# install-codex.sh — verify codex CLI is installed; install via npm if not.
#
# Usage:
#   bash install-codex.sh             # check + install if missing + prompt login
#   bash install-codex.sh --check     # just report status, no install
#   bash install-codex.sh --dry-run   # print what would happen

set -euo pipefail

CHECK_ONLY=0
DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --check) CHECK_ONLY=1 ;;
        --dry-run) DRY_RUN=1 ;;
    esac
done

print_install_cmd() {
    echo "-> Would run: npm i -g @openai/codex"
}

if command -v codex >/dev/null 2>&1; then
    echo "codex CLI уже установлен ($(codex --version 2>&1 | head -1))"
    exit 0
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "codex CLI не найден на PATH"
    exit 1
fi

if [ "$DRY_RUN" -eq 1 ]; then
    print_install_cmd
    echo "-> Would prompt: codex login"
    exit 0
fi

echo "-> codex CLI не найден. Устанавливаю через npm..."

if ! command -v npm >/dev/null 2>&1; then
    cat >&2 <<EOF
npm не установлен. Установи Node.js + npm с https://nodejs.org/
   После установки запусти этот скрипт снова.
EOF
    exit 2
fi

if ! npm i -g @openai/codex 2>/tmp/codex-install.err; then
    if grep -qi "eacces\|permission denied" /tmp/codex-install.err; then
        cat >&2 <<EOF
npm install failed (permission denied).
   Попробуй: sudo npm i -g @openai/codex
   Или настрой npm prefix без sudo: https://docs.npmjs.com/resolving-eacces-permissions-errors
EOF
    else
        cat /tmp/codex-install.err >&2
    fi
    exit 1
fi

echo "codex установлен. Проверяю авторизацию..."
if ! codex auth status >/dev/null 2>&1; then
    echo "-> codex не залогинен. Запускаю codex login..."
    codex login || {
        echo "codex login пропущен. Запусти 'codex login' вручную перед использованием /landing-photos или /landing-visuals." >&2
    }
fi

echo "codex готов к работе"

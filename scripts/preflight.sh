#!/usr/bin/env bash
# scripts/preflight.sh — system-wide preflight check
# Delegates to setup-flag.sh + validate-all.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)/.."
cd "$REPO_ROOT" || exit 2

echo "=== Landing System Preflight Check ==="

if ! bash scripts/setup-flag.sh is_complete; then
    echo "❌ Onboarding не пройден. Запусти /landing-onboarding"
    exit 1
fi

bash scripts/validate-all.sh

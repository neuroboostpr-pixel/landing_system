#!/usr/bin/env bash
# Phase 1 dependency checker
set -euo pipefail

errors=0

check() {
  local name="$1"
  local cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "✅ $name: $($cmd --version 2>&1 | head -1)"
  else
    echo "❌ $name not found"
    errors=$((errors + 1))
  fi
}

echo "=== Landing System: Dependency Check ==="
check "bats-core" bats
check "git" git
check "node" node
check "bash" bash

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "⚠️  Missing $errors dependencies. Install them and re-run."
  echo "   macOS: brew install bats-core node git"
  echo "   Linux: apt-get install bats node git"
  exit 1
fi

echo ""
echo "✅ All dependencies OK."
exit 0

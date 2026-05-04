#!/usr/bin/env bash
# scripts/preflight.sh — Landing System dependency check
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

_ok()   { echo "  ✅ $1"; }
_fail() { echo "  ❌ $1 — $2"; FAIL=1; }

echo "=== Landing System Preflight Check ==="
echo ""

echo "▶ Окружение"
python3 -c 'import sys; assert sys.version_info >= (3,10)' 2>/dev/null \
  && _ok "Python 3.10+" || _fail "Python 3.10+" "Установи Python 3.10+"

python3 -c 'import yaml, jinja2, requests, PIL' 2>/dev/null \
  && _ok "Python пакеты (yaml, jinja2, requests, pillow)" \
  || _fail "Python пакеты" "pip install pyyaml jinja2 requests pillow"

bats --version >/dev/null 2>&1 \
  && _ok "bats-core" || _fail "bats-core" "brew install bats-core"

wp --version >/dev/null 2>&1 \
  && _ok "wp-cli" || _fail "wp-cli" "brew install wp-cli"

echo ""
echo "▶ Конфигурация"

[ -f "$REPO_ROOT/.env" ] \
  && _ok ".env существует" || _fail ".env" "cp $REPO_ROOT/.env.example $REPO_ROOT/.env"

if [ -f "$REPO_ROOT/.env" ]; then
  grep -q "FIRECRAWL_API_KEY=." "$REPO_ROOT/.env" 2>/dev/null \
    && _ok "FIRECRAWL_API_KEY задан" \
    || _fail "FIRECRAWL_API_KEY" "Добавь ключ в .env (получить на firecrawl.dev)"
fi

[ -f "$REPO_ROOT/config/system.yaml" ] \
  && _ok "config/system.yaml существует" \
  || _fail "config/system.yaml" "Запусти /landing-setup чтобы создать"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "✅ Все проверки пройдены — система готова к работе"
  exit 0
else
  echo "❌ Исправь ошибки выше и запусти preflight.sh снова"
  exit 1
fi

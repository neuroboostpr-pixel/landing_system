#!/usr/bin/env bash
# scripts/wizard.sh — interactive onboarding for landing-system
set -uo pipefail


# Cross-platform python detection (sets PYTHON_CMD).
__SCRIPT_DIR__="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/python-cmd.sh
. "$__SCRIPT_DIR__/lib/python-cmd.sh"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NONINTERACTIVE="${WIZARD_NONINTERACTIVE:-0}"

prompt() {
    if [ "$NONINTERACTIVE" = "1" ]; then
        echo "[noninteractive] $1"
        return 0
    fi
    read -r -p "$1 (Enter to continue): " _
}

cat <<'EOF'
═══════════════════════════════════════════════════════════════════
                  Landing System Onboarding
═══════════════════════════════════════════════════════════════════

Этот мастер проведёт через настройку всех необходимых API и
зависимостей. Без полной настройки команды /landing-* работать
не будут.

Документация: docs/SETUP.md
EOF
prompt "Готов начать?"

echo ""
echo "▶ Локальные зависимости"
deps_ok=1
for cmd in wp ssh rsync bats $PYTHON_CMD jq; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  ✅ $cmd"
    else
        echo "  ❌ $cmd — установи (macOS: brew install $cmd)"
        deps_ok=0
    fi
done
[ "$deps_ok" = "0" ] && echo "  ⚠️  Установи недостающее и запусти /landing-onboarding снова"

echo ""
echo "▶ Python пакеты"
$PYTHON_CMD -c 'import yaml, jinja2, requests, PIL, pytest, responses' 2>/dev/null \
    && echo "  ✅ pyyaml, jinja2, requests, pillow, pytest, responses" \
    || { echo "  ❌ pip install -r requirements.txt"; deps_ok=0; }

echo ""
echo "▶ Superpowers plugin"
if claude plugins list 2>/dev/null | grep -q superpowers; then
    echo "  ✅ superpowers"
else
    echo "  ⚠️  superpowers не найден. Установи: claude plugins install superpowers@claude-plugins-official"
fi

echo ""
echo "▶ Firecrawl MCP"
if grep -q firecrawl "$HOME/.claude/settings.json" 2>/dev/null; then
    echo "  ✅ firecrawl MCP настроен"
else
    echo "  ⚠️  firecrawl MCP не найден в ~/.claude/settings.json"
fi

echo ""
echo "▶ .env"
if [ -f "$REPO_ROOT/.env" ]; then
    echo "  ✅ .env существует"
else
    echo "  ❌ .env отсутствует. Создаю из .env.example..."
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo "  📝 Отредактируй $REPO_ROOT/.env и заполни ключи. Регистрация:"
    echo "     - Firecrawl:    https://firecrawl.dev"
    echo "     - Pexels:       https://www.pexels.com/api/"
    echo "     - Unsplash:     https://unsplash.com/developers"
    echo "     - Pixabay:      https://pixabay.com/api/docs/"
    echo "     - HuggingFace:  https://huggingface.co/settings/tokens"
    echo "     - Yandex OAuth: https://oauth.yandex.ru"
    echo "     - Telegram:     @BotFather"
    echo "     - amoCRM:       https://www.amocrm.ru/developers"
    echo "     - Bitrix24:     https://www.bitrix24.com/apps/dev.php"
    echo "     - Beget:        https://beget.com/ru/kb/api"
fi

echo ""
echo "▶ API-ключи (валидация)"
if [ -f "$REPO_ROOT/.env" ]; then
    bash "$REPO_ROOT/scripts/validate-all.sh" || true
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ "$deps_ok" = "1" ] && [ -f "$REPO_ROOT/.env" ] && bash "$REPO_ROOT/scripts/validate-all.sh" >/dev/null 2>&1; then
    bash "$SCRIPT_DIR/setup-flag.sh" mark_complete
    echo "  ✅ Onboarding завершён. Можешь запускать /landing-new"
else
    echo "  ⚠️  Onboarding не завершён. Исправь ошибки выше и запусти ещё раз."
fi
echo "═══════════════════════════════════════════════════════════════"

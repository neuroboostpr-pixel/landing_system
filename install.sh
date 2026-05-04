#!/usr/bin/env bash
# install.sh — Установка landing-system как Claude Code плагина
# Usage: bash install.sh
set -euo pipefail

REPO_URL="https://github.com/neuroboostpr-pixel/landing_system.git"
PLUGIN_NAME="landing-system"
MARKETPLACE_NAME="landing-system"

echo "=== Landing System — Установка плагина ==="
echo ""

# Проверяем наличие Claude Code CLI
if ! command -v claude &>/dev/null; then
  echo "❌ Claude Code CLI не найден. Установи: https://claude.ai/code"
  exit 1
fi

echo "1. Добавляем marketplace..."
# Добавляем репозиторий как marketplace (если ещё не добавлен)
if claude plugins marketplace list 2>/dev/null | grep -q "$MARKETPLACE_NAME"; then
  echo "   ✅ Marketplace уже добавлен"
else
  claude plugins marketplace add "github:neuroboostpr-pixel/landing_system" 2>/dev/null || {
    echo "   ⚠️  Не удалось добавить marketplace через CLI"
    echo "   Попробуем прямую установку..."
  }
fi

echo ""
echo "2. Устанавливаем плагин..."
if claude plugins install "$PLUGIN_NAME" 2>/dev/null; then
  echo "   ✅ Плагин установлен"
else
  echo ""
  echo "   ⚠️  Автоматическая установка не удалась."
  echo "   Установи вручную:"
  echo ""
  echo "   git clone $REPO_URL ~/.claude/plugins/cache/landing-system/1.0.0"
  echo "   # Затем добавь запись в ~/.claude/plugins/installed_plugins.json"
  echo ""
  echo "   Или просто работай из папки проекта (команды уже в .claude/commands/)"
fi

echo ""
echo "3. Проверяем зависимости..."
if [ -f "$(dirname "$0")/scripts/check-deps.sh" ]; then
  bash "$(dirname "$0")/scripts/check-deps.sh"
elif [ -f "scripts/check-deps.sh" ]; then
  bash scripts/check-deps.sh
fi

echo ""
echo "=== Готово! ==="
echo ""
echo "Команды доступны в Claude Code:"
echo "  /landing-new <slug>          — новый проект"
echo "  /landing-from-context <slug> — проект из папки агентства"
echo "  /landing-status              — статус системы"
echo "  /landing-help                — справка"
echo ""
echo "Перед первым проектом:"
echo "  1. cp .env.example .env"
echo "  2. Заполни ключи (Beget, API и т.д.)"
echo "  3. /landing-setup"

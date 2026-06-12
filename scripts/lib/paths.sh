#!/usr/bin/env bash
# Общий помощник для путей и кодировки в bash-скриптах.
#
# Назначение:
#   - Найти корневую папку с лендингами (LANDINGS_ROOT) кросс-платформенно.
#   - Принудительно включить UTF-8 для вывода (Windows Git Bash / PowerShell).
#
# Использование:
#   #!/usr/bin/env bash
#   set -euo pipefail
#   source "$(dirname "$0")/lib/paths.sh"
#   # Теперь доступны: $LANDINGS_ROOT, $REPO_ROOT
#   PROJECT="$LANDINGS_ROOT/my-landing"
#
# Если скрипт лежит глубже (например skills/wp-multisite/scripts/X.sh) —
# подставь правильный относительный путь к scripts/lib/paths.sh.

# ──────────────────────────────────────────────────────────────────
# 1. UTF-8 для вывода
# ──────────────────────────────────────────────────────────────────

# Без этого на Windows русские строки в echo/cat могут выводиться
# вопросиками в некоторых консолях.
export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"
export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

# ──────────────────────────────────────────────────────────────────
# 2. Найти корень репозитория landing_system
# ──────────────────────────────────────────────────────────────────

# Поднимаемся от текущего файла до папки с CLAUDE.md и agents/.
_paths_find_repo_root() {
    local here
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local p="$here"
    while [[ "$p" != "/" && "$p" != "" ]]; do
        if [[ -f "$p/CLAUDE.md" && -d "$p/agents" ]]; then
            echo "$p"
            return 0
        fi
        p="$(dirname "$p")"
    done
    # Fallback: два уровня вверх от scripts/lib/.
    echo "$here/../.."
}

REPO_ROOT="$(_paths_find_repo_root)"
export REPO_ROOT

# ──────────────────────────────────────────────────────────────────
# 3. Найти корень папки с лендингами
# ──────────────────────────────────────────────────────────────────

_paths_find_landings_root() {
    # Правило 1: явная переменная окружения.
    if [[ -n "${LANDINGS_ROOT:-}" ]]; then
        # Раскрыть тильду если есть.
        echo "${LANDINGS_ROOT/#\~/$HOME}"
        return 0
    fi

    # Правило 2: рядом с landing_system.
    local sibling="$REPO_ROOT/../Lendings"
    if [[ -d "$sibling" ]]; then
        (cd "$sibling" && pwd)
        return 0
    fi

    # Правило 3: домашняя папка.
    local home_path="$HOME/Lendings"
    if [[ -d "$home_path" ]]; then
        echo "$home_path"
        return 0
    fi

    # Ничего не нашли — возвращаем sibling-вариант для предсказуемости.
    echo "$sibling"
}

LANDINGS_ROOT="$(_paths_find_landings_root)"
export LANDINGS_ROOT

# ──────────────────────────────────────────────────────────────────
# 4. Хелпер «проверь что папка реально есть»
# ──────────────────────────────────────────────────────────────────

# Вызвать в скрипте который не может работать без папки лендингов:
#   require_landings_root
# Выведет понятное сообщение и завершит скрипт если папки нет.
require_landings_root() {
    if [[ -d "$LANDINGS_ROOT" ]]; then
        return 0
    fi
    cat >&2 <<EOF
[paths] Не найдена папка с лендингами.
  Пробовали: $LANDINGS_ROOT
  Реши одним из способов:
    1. Создай папку: mkdir -p "$LANDINGS_ROOT"
    2. Задай переменную: export LANDINGS_ROOT=/path/to/your/Lendings
    3. Добавь LANDINGS_ROOT в .env (см. .env.example)
EOF
    exit 1
}

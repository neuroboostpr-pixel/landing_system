---
type: script
name: paths 2
language: bash
sources: ["scripts/lib/paths 2.sh"]
updated: 2026-05-18
---

# paths 2.sh

Общий помощник для путей и кодировки в bash-скриптах.

Назначение:
- Найти корневую папку с лендингами (LANDINGS_ROOT) кросс-платформенно.
- Принудительно включить UTF-8 для вывода (Windows Git Bash / PowerShell).

Использование:
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib/paths.sh"
# Теперь доступны: $LANDINGS_ROOT, $REPO_ROOT
PROJECT="$LANDINGS_ROOT/my-landing"

Если скрипт лежит глубже (например skills/wp-multisite/scripts/X.sh) —
подставь правильный относительный путь к scripts/lib/paths.sh.
──────────────────────────────────────────────────────────────────
1. UTF-8 для вывода
──────────────────────────────────────────────────────────────────
Без этого на Windows русские строки в echo/cat могут выводиться
вопросиками в некоторых консолях.

## Источник

- `scripts/lib/paths 2.sh`

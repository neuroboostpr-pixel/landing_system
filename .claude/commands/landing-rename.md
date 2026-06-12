---
description: Rename a landing project and update all internal references
argument-hint: <old-slug> <new-slug>
allowed-tools: Bash
---

# /landing-rename

Переименовывает проект в `~/Lendings/` и обновляет все внутренние ссылки на slug.

## Steps

1. Run:
   ```bash
   bash "${CLAUDE_PROJECT_DIR:-.}/scripts/landing-rename.sh" $ARGUMENTS
   ```
2. The script handles all validation and file updates.

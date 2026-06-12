---
description: Safely delete a landing project with confirmation
argument-hint: <project-slug>
allowed-tools: Bash
---

# /landing-delete

Удаляет проект из `~/Lendings/<slug>/` с явным подтверждением.

## Steps

1. Run:
   ```bash
   bash "${CLAUDE_PROJECT_DIR:-.}/scripts/landing-delete.sh" $ARGUMENTS
   ```
2. The script handles all validation and confirmation interactively.

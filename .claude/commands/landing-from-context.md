---
description: Create a new landing project, snapshotting context from the current parent agency project folder
argument-hint: <project-slug> [--cinematic]
allowed-tools: Bash, Read, Write, Edit, Task
---

# /landing-from-context

Create a new landing project that **inherits context** (audience, research, prototype) from the parent agency folder you're currently in.

## When to use

You're in a folder like:
```
~/Desktop/Агентство лидогенерации/04_документы/курс-копирайтинг/
```
which contains `01_контекст/`, `05_исследования/`, etc. You want to create a new landing for this product.

## Argument

- `$1` — project slug
- `--cinematic` (optional)

## Implementation

```bash
SLUG="$1"
if [ -z "$SLUG" ]; then
  echo "Usage: /landing-from-context <slug> [--cinematic]"
  exit 1
fi

case "$SLUG" in
  /*|./*|../*) TARGET="$SLUG" ;;
  *) TARGET="$HOME/Lendings/$SLUG" ;;
esac

SCRIPT="${CLAUDE_PROJECT_DIR:-.}/.skills/landing-from-context/scripts/from-context.sh"
bash "$SCRIPT" "$TARGET" "${@:2}"
```

After project is created with parent snapshot, dispatch `landing-orchestrator` starting from Stage 02 (Materials) — Stages 00–01 are partially pre-filled from snapshot.

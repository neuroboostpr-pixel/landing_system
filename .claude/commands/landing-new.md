---
description: Create a new landing project from scratch
argument-hint: <project-slug> [--cinematic]
allowed-tools: Bash, Read, Write, Edit, Task
---

# /landing-new

Create a new landing project from scratch using the `landing-project-init` skill.

## Argument

- `$1` — project slug (kebab-case, e.g. `lp-курс-марафон`)
- `--cinematic` (optional) — enable cinematic premium mode

## Steps

1. Invoke the `landing-project-init` skill with the given slug.
2. The skill resolves target path:
   - If slug is absolute or relative path — use as-is.
   - Otherwise default to `~/Lendings/<slug>/`.
3. Run `init.sh` (script of the skill).
4. After project is created, hand off to `landing-orchestrator` agent for Stage 00 (brief).

## Implementation

```bash
# Get slug from $ARGUMENTS
SLUG="$1"
if [ -z "$SLUG" ]; then
  echo "Usage: /landing-new <slug> [--cinematic]"
  exit 1
fi

# Resolve target
case "$SLUG" in
  /*|./*|../*) TARGET="$SLUG" ;;
  *) TARGET="$HOME/Lendings/$SLUG" ;;
esac

# Run skill script
SCRIPT="${CLAUDE_PROJECT_DIR:-.}/.skills/landing-project-init/scripts/init.sh"
bash "$SCRIPT" "$TARGET" "${@:2}"
```

After successful run, dispatch `landing-orchestrator` agent to lead the user through Stage 00 (brief).

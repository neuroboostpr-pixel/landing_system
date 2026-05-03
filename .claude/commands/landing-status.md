---
description: Show current state of the landing system and active projects
allowed-tools: Read, Bash
---

# /landing-status

Show the current state of the master system and any active project in the cwd.

## Algorithm

1. **Master system check** (cwd is `landing-system/` or contains `.skills/landing-project-init/`):
   - Print version (from `package.json`).
   - Print current Phase status: "Phase 1 — Skeleton & Infrastructure (in progress / complete)".
   - List installed skills and agents.

2. **Active project check** (cwd looks like a landing project: contains `00_БРИФ/`, `08_КОД/`, etc):
   - Read `00_БРИФ/brief.md` if exists, extract project name.
   - Determine current stage by checking which numbered folders contain non-trivial content:
     - 00_БРИФ has brief.md → Stage 00 done
     - 01_КОНТЕКСТ has files → Stage 01 done
     - ...
   - Print: "Project <name>, Stage X of 12: <stage_name>"

3. **Neither** — print: "Not in a landing system or project folder."

## Implementation

```bash
CWD="$(pwd)"

# Helper: returns true only if dir exists and has files other than .gitkeep
dir_has_real_content() {
  [ -d "$1" ] && [ -n "$(ls -A "$1" 2>/dev/null | grep -Fv -- '.gitkeep')" ]
}

# Master system?
if [ -d "$CWD/.skills/landing-project-init" ]; then
  echo "📦 Landing System (master)"
  if [ -f "$CWD/package.json" ]; then
    VERSION=$(grep -E '"version"' "$CWD/package.json" | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/' || echo "unknown")
    echo "   Version: $VERSION"
  fi
  echo "   Phase 1: Skeleton & Infrastructure"
  echo ""
  echo "   Skills:"
  for skill in "$CWD"/.skills/*/SKILL.md; do
    name=$(basename "$(dirname "$skill")")
    echo "     - $name"
  done
  echo ""
  echo "   Agents:"
  for agent in "$CWD"/.agents/*.md; do
    name=$(basename "$agent" .md)
    echo "     - $name"
  done
  exit 0
fi

# Project?
if [ -d "$CWD/00_БРИФ" ] && [ -d "$CWD/08_КОД" ]; then
  echo "🏗  Landing Project: $(basename "$CWD")"
  STAGE=0
  [ -s "$CWD/00_БРИФ/brief.md" ] && STAGE=1
  dir_has_real_content "$CWD/01_КОНТЕКСТ" && STAGE=2
  dir_has_real_content "$CWD/02_МАТЕРИАЛЫ_КЛИЕНТА" && STAGE=3
  [ -f "$CWD/03_РЕФЕРЕНСЫ/moodboard.md" ] && STAGE=4
  [ -f "$CWD/04_БРЕНД/brand-kit.md" ] && STAGE=5
  [ -f "$CWD/05_ДИЗАЙН-СИСТЕМА/DESIGN.md" ] && STAGE=6
  [ -f "$CWD/06_СТЕК/design-stack.yaml" ] && STAGE=7
  [ -f "$CWD/07_КОНТЕНТ/final-copy.md" ] && STAGE=8
  [ -d "$CWD/08_КОД/wp-theme" ] && STAGE=9
  [ -f "$CWD/09_ДЕПЛОЙ/deploy.sh" ] && STAGE=10
  [ -f "$CWD/10_QA/checklist.md" ] && STAGE=11

  echo "   Stage $STAGE of 12"
  echo ""
  case "$STAGE" in
    0) echo "   Next: fill out 00_БРИФ/brief.md (run landing-orchestrator)" ;;
    1) echo "   Next: 02 Materials — gather client photos/videos/reviews" ;;
    *) echo "   Next: see master plan for Phase 2+ commands" ;;
  esac
  exit 0
fi

echo "❌ Not in a landing-system or landing project folder."
echo "   Try: cd to landing-system/ or to a project created by /landing-new"
```

# /landing-delete and /landing-rename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Two safe CLI commands — `/landing-delete <slug>` and `/landing-rename <old> <new>` — with full internal state update and confirmation guards.

**Architecture:** Bash scripts in `scripts/` do all work; slash-commands in `.claude/commands/` are thin wrappers passing `$ARGUMENTS`. Follows the existing `landing-project-init` / `gate-check.sh` pattern. LANDINGS_ROOT resolved via `python -c "from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)"`. Tested with bats.

**Tech Stack:** Bash, yq v4, GNU sed, bats

---

## File Structure

- Create: `scripts/landing-delete.sh`
- Create: `scripts/landing-rename.sh`
- Create: `.claude/commands/landing-delete.md`
- Create: `.claude/commands/landing-rename.md`
- Create: `tests/scripts/test-landing-delete.bats`
- Create: `tests/scripts/test-landing-rename.bats`

---

### Task 1: `landing-delete.sh` script (TDD)

**Files:**
- Create: `tests/scripts/test-landing-delete.bats`
- Create: `scripts/landing-delete.sh`

- [ ] **Step 1: Create test file with failing tests**

```bash
# tests/scripts/test-landing-delete.bats
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/landing-delete.sh"
    # Create a fake LANDINGS_ROOT in tmpdir
    export LANDINGS_ROOT="$BATS_TEST_TMPDIR/Lendings"
    mkdir -p "$LANDINGS_ROOT"
}

_make_project() {
    local slug="$1"
    local dir="$LANDINGS_ROOT/$slug"
    mkdir -p "$dir/00_БРИФ"
    cat > "$dir/.landing-state.yaml" <<EOF
project: $slug
current_stage: 03_references
stages:
  "03_references": {status: locked, timestamp: ""}
EOF
    echo "# $slug" > "$dir/README.md"
}

@test "no args prints usage and exits 1" {
    run bash "$SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "non-existent slug exits 1 with error" {
    run bash "$SCRIPT" no-such-project
    [ "$status" -eq 1 ]
    [[ "$output" == *"не найден"* ]]
}

@test "folder without .landing-state.yaml exits 1" {
    mkdir -p "$LANDINGS_ROOT/not-a-project"
    run bash "$SCRIPT" not-a-project
    [ "$status" -eq 1 ]
    [[ "$output" == *"не лендинг-проект"* ]]
}

@test "wrong confirmation aborts deletion" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "wrong-name"
    [ "$status" -eq 1 ]
    [[ "$output" == *"отменено"* ]]
    [ -d "$LANDINGS_ROOT/myproject" ]
}

@test "correct confirmation deletes folder" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "myproject"
    [ "$status" -eq 0 ]
    [[ "$output" == *"удалён"* ]]
    [ ! -d "$LANDINGS_ROOT/myproject" ]
}

@test "summary shows project name and stage before confirmation" {
    _make_project myproject
    run bash "$SCRIPT" myproject <<< "wrong"
    [[ "$output" == *"myproject"* ]]
    [[ "$output" == *"03_references"* ]]
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
bats tests/scripts/test-landing-delete.bats
```

Expected: all tests FAIL (script doesn't exist yet)

- [ ] **Step 3: Create `scripts/landing-delete.sh`**

```bash
#!/usr/bin/env bash
# scripts/landing-delete.sh — safely delete a landing project
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 1 ]; then
    echo "Usage: landing-delete.sh <slug>"
    exit 1
fi

SLUG="$1"
LANDINGS_ROOT="${LANDINGS_ROOT:-$(python -c "import sys; sys.path.insert(0,'$REPO_ROOT'); from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")}"
TARGET="$LANDINGS_ROOT/$SLUG"

if [ ! -d "$TARGET" ]; then
    echo "❌ Проект '$SLUG' не найден в $LANDINGS_ROOT"
    exit 1
fi

if [ ! -f "$TARGET/.landing-state.yaml" ]; then
    echo "❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)"
    exit 1
fi

STAGE=$(yq e '.current_stage // "unknown"' "$TARGET/.landing-state.yaml" 2>/dev/null || echo "unknown")
FILE_COUNT=$(find "$TARGET" | wc -l | tr -d ' ')

echo ""
echo "Проект: $SLUG"
echo "Папка:  $TARGET"
echo "Файлов: $FILE_COUNT"
echo "Этап:   $STAGE"
echo ""
printf "Для подтверждения введи имя проекта: "
read -r CONFIRM

if [ "$CONFIRM" != "$SLUG" ]; then
    echo "❌ Имя не совпадает. Удаление отменено."
    exit 1
fi

rm -rf "$TARGET"
echo "✅ Проект $SLUG удалён."
```

- [ ] **Step 4: Make script executable**

```bash
chmod +x scripts/landing-delete.sh
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
bats tests/scripts/test-landing-delete.bats
```

Expected: all 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/landing-delete.sh tests/scripts/test-landing-delete.bats
git commit -m "feat(B21): add landing-delete.sh with confirmation guard"
```

---

### Task 2: `/landing-delete` slash-command

**Files:**
- Create: `.claude/commands/landing-delete.md`

- [ ] **Step 1: Create slash-command file**

```markdown
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
```

- [ ] **Step 2: Verify command is visible**

```bash
ls .claude/commands/landing-delete.md
```

Expected: file exists

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/landing-delete.md
git commit -m "feat(B21): add /landing-delete slash-command"
```

---

### Task 3: `landing-rename.sh` script (TDD)

**Files:**
- Create: `tests/scripts/test-landing-rename.bats`
- Create: `scripts/landing-rename.sh`

- [ ] **Step 1: Create test file with failing tests**

```bash
# tests/scripts/test-landing-rename.bats
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$BATS_TEST_DIRNAME/../.."
    SCRIPT="$REPO_ROOT/scripts/landing-rename.sh"
    export LANDINGS_ROOT="$BATS_TEST_TMPDIR/Lendings"
    mkdir -p "$LANDINGS_ROOT"
}

_make_project() {
    local slug="$1"
    local dir="$LANDINGS_ROOT/$slug"
    mkdir -p "$dir/00_БРИФ"
    cat > "$dir/.landing-state.yaml" <<EOF
project: $slug
current_stage: 03_references
stages:
  "03_references": {status: locked, timestamp: ""}
EOF
    echo "# Project $slug readme" > "$dir/README.md"
    mkdir -p "$dir/00_БРИФ"
    echo "# Brief for $slug" > "$dir/00_БРИФ/brief.md"
}

@test "no args prints usage and exits 1" {
    run bash "$SCRIPT"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "one arg prints usage and exits 1" {
    run bash "$SCRIPT" old-slug
    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage"* ]]
}

@test "old slug not found exits 1" {
    run bash "$SCRIPT" no-such-project new-name
    [ "$status" -eq 1 ]
    [[ "$output" == *"не найден"* ]]
}

@test "old folder without .landing-state.yaml exits 1" {
    mkdir -p "$LANDINGS_ROOT/not-a-project"
    run bash "$SCRIPT" not-a-project new-name
    [ "$status" -eq 1 ]
    [[ "$output" == *"не лендинг-проект"* ]]
}

@test "new slug already exists exits 1" {
    _make_project old-name
    _make_project already-exists
    run bash "$SCRIPT" old-name already-exists
    [ "$status" -eq 1 ]
    [[ "$output" == *"уже существует"* ]]
}

@test "invalid new slug (uppercase) exits 1" {
    _make_project old-name
    run bash "$SCRIPT" old-name NewName
    [ "$status" -eq 1 ]
    [[ "$output" == *"kebab-case"* ]]
}

@test "invalid new slug (spaces) exits 1" {
    _make_project old-name
    run bash "$SCRIPT" old-name "new name"
    [ "$status" -eq 1 ]
    [[ "$output" == *"kebab-case"* ]]
}

@test "successful rename moves folder" {
    _make_project old-name
    run bash "$SCRIPT" old-name new-name
    [ "$status" -eq 0 ]
    [ ! -d "$LANDINGS_ROOT/old-name" ]
    [ -d "$LANDINGS_ROOT/new-name" ]
}

@test "successful rename updates project field in .landing-state.yaml" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    VALUE=$(yq e '.project' "$LANDINGS_ROOT/new-name/.landing-state.yaml")
    [ "$VALUE" = "new-name" ]
}

@test "successful rename updates old slug in README.md" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    run grep "old-name" "$LANDINGS_ROOT/new-name/README.md"
    [ "$status" -ne 0 ]
}

@test "successful rename updates old slug in brief.md if exists" {
    _make_project old-name
    bash "$SCRIPT" old-name new-name
    run grep "old-name" "$LANDINGS_ROOT/new-name/00_БРИФ/brief.md"
    [ "$status" -ne 0 ]
}

@test "rename prints success message" {
    _make_project old-name
    run bash "$SCRIPT" old-name new-name
    [[ "$output" == *"old-name"* ]]
    [[ "$output" == *"new-name"* ]]
    [[ "$output" == *"✅"* ]]
}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
bats tests/scripts/test-landing-rename.bats
```

Expected: all tests FAIL (script doesn't exist yet)

- [ ] **Step 3: Create `scripts/landing-rename.sh`**

```bash
#!/usr/bin/env bash
# scripts/landing-rename.sh — rename a landing project and update internal references
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ $# -lt 2 ]; then
    echo "Usage: landing-rename.sh <old-slug> <new-slug>"
    exit 1
fi

OLD_SLUG="$1"
NEW_SLUG="$2"
LANDINGS_ROOT="${LANDINGS_ROOT:-$(python -c "import sys; sys.path.insert(0,'$REPO_ROOT'); from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")}"
OLD_DIR="$LANDINGS_ROOT/$OLD_SLUG"
NEW_DIR="$LANDINGS_ROOT/$NEW_SLUG"

# Validate old
if [ ! -d "$OLD_DIR" ]; then
    echo "❌ Проект '$OLD_SLUG' не найден в $LANDINGS_ROOT"
    exit 1
fi
if [ ! -f "$OLD_DIR/.landing-state.yaml" ]; then
    echo "❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)"
    exit 1
fi

# Validate new
if [ -d "$NEW_DIR" ]; then
    echo "❌ Проект '$NEW_SLUG' уже существует в $LANDINGS_ROOT"
    exit 1
fi
if ! echo "$NEW_SLUG" | grep -qE '^[a-z0-9-]+$'; then
    echo "❌ Slug должен быть kebab-case (только строчные буквы, цифры, дефис)"
    exit 1
fi

# Move
mv "$OLD_DIR" "$NEW_DIR"

# Update .landing-state.yaml
yq e ".project = \"$NEW_SLUG\"" -i "$NEW_DIR/.landing-state.yaml"

# Update README.md
if [ -f "$NEW_DIR/README.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/README.md"
fi

# Update brief.md
if [ -f "$NEW_DIR/00_БРИФ/brief.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/00_БРИФ/brief.md"
fi

# Update wiki/pipeline-map.md
if [ -f "$NEW_DIR/wiki/pipeline-map.md" ]; then
    sed -i "s/$OLD_SLUG/$NEW_SLUG/g" "$NEW_DIR/wiki/pipeline-map.md"
fi

UPDATED=0
[ -f "$NEW_DIR/README.md" ] && UPDATED=$((UPDATED + 1))
[ -f "$NEW_DIR/00_БРИФ/brief.md" ] && UPDATED=$((UPDATED + 1))
[ -f "$NEW_DIR/wiki/pipeline-map.md" ] && UPDATED=$((UPDATED + 1))

echo ""
echo "✅ Проект переименован: $OLD_SLUG → $NEW_SLUG"
echo "Папка: $NEW_DIR"
echo "Обновлено файлов: $UPDATED"
```

- [ ] **Step 4: Make script executable**

```bash
chmod +x scripts/landing-rename.sh
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
bats tests/scripts/test-landing-rename.bats
```

Expected: all 12 tests PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/landing-rename.sh tests/scripts/test-landing-rename.bats
git commit -m "feat(B22): add landing-rename.sh with full internal state update"
```

---

### Task 4: `/landing-rename` slash-command + remove from backlog

**Files:**
- Create: `.claude/commands/landing-rename.md`
- Modify: `docs/BACKLOG.md` — remove B21 and B22 entries

- [ ] **Step 1: Create slash-command file**

```markdown
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
```

- [ ] **Step 2: Remove B21 and B22 from BACKLOG.md**

Open `docs/BACKLOG.md` and remove the entire sections for `### B21. /landing-delete` and `### B22. /landing-rename` (including their bullet points). Update the progress line from `B5–B22` to `B5–B20`.

- [ ] **Step 3: Verify command files exist**

```bash
ls .claude/commands/landing-delete.md .claude/commands/landing-rename.md
```

Expected: both files listed

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/landing-rename.md docs/BACKLOG.md
git commit -m "feat(B22): add /landing-rename slash-command; remove B21/B22 from backlog"
```

---

### Task 5: Smoke test end-to-end

**Files:** no new files

- [ ] **Step 1: Create a test project**

```bash
LANDINGS_ROOT=$(python -c "from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)")
bash skills/landing-project-init/scripts/init.sh "$LANDINGS_ROOT/smoke-test-project"
```

Expected: `✅ Project created: smoke-test-project`

- [ ] **Step 2: Rename it**

```bash
bash scripts/landing-rename.sh smoke-test-project smoke-test-renamed
```

Expected output contains `✅ Проект переименован: smoke-test-project → smoke-test-renamed`

- [ ] **Step 3: Verify state file updated**

```bash
yq e '.project' "$LANDINGS_ROOT/smoke-test-renamed/.landing-state.yaml"
```

Expected: `smoke-test-renamed`

- [ ] **Step 4: Delete it**

```bash
bash scripts/landing-delete.sh smoke-test-renamed <<< "smoke-test-renamed"
```

Expected: `✅ Проект smoke-test-renamed удалён.`

- [ ] **Step 5: Verify folder gone**

```bash
ls "$LANDINGS_ROOT/smoke-test-renamed" 2>&1
```

Expected: `No such file or directory`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: smoke test pass for landing-delete and landing-rename"
```

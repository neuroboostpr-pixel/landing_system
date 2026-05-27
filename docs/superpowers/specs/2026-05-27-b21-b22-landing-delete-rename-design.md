# /landing-delete and /landing-rename — Design Spec (B21, B22)

**Goal:** Two CLI commands for safe project deletion and renaming with full internal state update.

**Architecture:** Bash scripts in `scripts/` + slash-commands in `.claude/commands/`. Follows existing `landing-project-init` pattern. Tested with `bats`.

**Tech Stack:** Bash, `sed`, `yq` (for yaml field update), `bats` (tests)

---

## File Structure

- Create: `scripts/landing-delete.sh`
- Create: `scripts/landing-rename.sh`
- Create: `.claude/commands/landing-delete.md`
- Create: `.claude/commands/landing-rename.md`
- Create: `tests/scripts/test-landing-delete.bats`
- Create: `tests/scripts/test-landing-rename.bats`

---

## `/landing-delete <slug>`

### Slash-command: `.claude/commands/landing-delete.md`

Thin wrapper — passes `$ARGUMENTS` to `scripts/landing-delete.sh`.

### Script: `scripts/landing-delete.sh <slug>`

```
Usage: landing-delete.sh <slug>
```

**Steps:**

1. Resolve `TARGET="$LANDINGS_ROOT/<slug>"` via `python -c "from scripts.lib.paths import LANDINGS_ROOT; print(LANDINGS_ROOT)"`.
2. Check `TARGET` exists — exit 1 with message if not.
3. Check `TARGET/.landing-state.yaml` exists — exit 1 if not a landing project.
4. Read `project:` and `current_stage:` from `.landing-state.yaml` via `yq`.
5. Count files: `find "$TARGET" | wc -l`.
6. Print summary:
   ```
   Проект: <slug>
   Папка:  <TARGET>
   Файлов: <N>
   Этап:   <current_stage> (<status>)
   ```
7. Prompt: `"Для подтверждения введи имя проекта: "` — read input.
8. If input != slug → abort with message.
9. `rm -rf "$TARGET"` → print `✅ Проект <slug> удалён.`

**Error cases:**
- Slug not provided → usage message, exit 1
- Folder not found → `❌ Проект '<slug>' не найден в <LANDINGS_ROOT>`, exit 1
- No `.landing-state.yaml` → `❌ Папка существует, но это не лендинг-проект (нет .landing-state.yaml)`, exit 1
- Confirmation mismatch → `❌ Имя не совпадает. Удаление отменено.`, exit 1

---

## `/landing-rename <old-slug> <new-slug>`

### Slash-command: `.claude/commands/landing-rename.md`

Thin wrapper — passes `$ARGUMENTS` to `scripts/landing-rename.sh`.

### Script: `scripts/landing-rename.sh <old-slug> <new-slug>`

```
Usage: landing-rename.sh <old-slug> <new-slug>
```

**Steps:**

1. Resolve `OLD="$LANDINGS_ROOT/<old-slug>"`, `NEW="$LANDINGS_ROOT/<new-slug>"`.
2. Check `OLD` exists, has `.landing-state.yaml` — exit 1 if not.
3. Check `NEW` does not exist — exit 1 if already taken.
4. Validate `new-slug` is kebab-case (`[a-z0-9-]+`) — exit 1 if not.
5. `mv "$OLD" "$NEW"`.
6. Update internal references in `NEW/`:
   - `.landing-state.yaml` → `project:` field via `yq e '.project = "<new-slug>"' -i`
   - `README.md` → `sed -i "s/<old-slug>/<new-slug>/g"`
   - `00_БРИФ/brief.md` → `sed -i "s/<old-slug>/<new-slug>/g"` (if exists)
   - `wiki/pipeline-map.md` → `sed -i "s/<old-slug>/<new-slug>/g"` (if exists)
7. Print:
   ```
   ✅ Проект переименован: <old-slug> → <new-slug>
   Папка: <NEW>
   Обновлено файлов: <N>
   ```

**Error cases:**
- Wrong number of args → usage message, exit 1
- Old folder not found → `❌ Проект '<old-slug>' не найден`, exit 1
- No `.landing-state.yaml` in old → `❌ Это не лендинг-проект`, exit 1
- New slug already exists → `❌ Проект '<new-slug>' уже существует`, exit 1
- Invalid new slug format → `❌ Slug должен быть kebab-case (только строчные буквы, цифры, дефис)`, exit 1

---

## Tests

### `tests/scripts/test-landing-delete.bats`

- delete existing project → success, folder removed
- delete non-existent slug → exit 1, error message
- delete folder without `.landing-state.yaml` → exit 1
- wrong confirmation input → exit 1, folder not deleted
- no args → exit 1, usage shown

### `tests/scripts/test-landing-rename.bats`

- rename existing project → success, old gone, new exists
- `.landing-state.yaml` project field updated
- `README.md` old slug replaced
- old slug not found → exit 1
- new slug already exists → exit 1
- invalid new slug (spaces, uppercase) → exit 1
- no args → exit 1, usage shown

---

## Out of scope

- Git history preservation (rename is `mv`, history stays in local git)
- Multisite subsite cleanup (separate concern, no `.landing-state.yaml` changes needed for subsites on delete)
- Undo/rollback command

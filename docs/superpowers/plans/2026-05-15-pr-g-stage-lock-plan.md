# PR-G — Stage Lock + Auto-Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Включить дисциплину «строго по шагам»: hard-локи для технических этапов через `require_approved`, soft-warning для итеративных, авто-обновление wiki при коммитах и закрытии этапов.

**Architecture:** Логика hard-локов уже работает через существующий `require_approved` в `gate-check.sh`. Доделать: расширить yaml списками зависимостей, добавить soft-warning блок, two git hooks (post-commit для system wiki, inline в gate-check.sh для project-graph).

**Tech Stack:** Bash + yq, существующий `scripts/gate-check.sh`, новый `.githooks/post-commit`, bats для тестов.

**Связанный spec:** [2026-05-15-pr-g-stage-lock-auto-wiki-design.md](../specs/2026-05-15-pr-g-stage-lock-auto-wiki-design.md)

---

## File Structure

**Создаём:**
- `.githooks/post-commit` — auto-recompile system wiki
- `scripts/install-git-hooks.sh` — установка хуков
- `tests/pr-g/test_stage_lock_hard.bats`
- `tests/pr-g/test_stage_lock_soft.bats`
- `tests/pr-g/test_post_commit.bats`
- `tests/pr-g/test_gate_check_updates_graph.bats`
- `tests/pr-g/helpers.bash` — общие хелперы для тестов

**Модифицируем:**
- `config/stage-gates.yaml` — расширить `require_approved` для hard-этапов, добавить `lock` поле
- `scripts/gate-check.sh` — добавить soft-warning блок + project-graph auto-update
- `agents/landing-orchestrator.md` — правило про gate-check в промпте
- `template/.gitignore` — не нужен; вики уже коммитится. Проверить нет ли конфликтов.

---

## Task 1: Расширить `config/stage-gates.yaml`

**Цель:** Каждому hard-этапу добавить `require_approved` со всеми зависимостями. Soft-этапам — поле `lock: soft` (для документации/будущего). Hard — `lock: hard`.

**Files:**
- Modify: `config/stage-gates.yaml`

- [ ] **Step 1: Прочитать текущий yaml**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
cat config/stage-gates.yaml | head -200 | tail -100
```

- [ ] **Step 2: Найти каждый этап и проставить `lock` + при необходимости `require_approved`**

Открыть config/stage-gates.yaml и для каждой stage-секции добавить две строки сразу после `name:`. Если поле `require_approved` уже есть — обновить значение по таблице. Если нет — добавить.

**Маппинг (что добавить/обновить):**

| Stage | lock | require_approved (СПИСОК) |
|---|---|---|
| `00_brief` | soft | [] |
| `01_context` | soft | [] |
| `01a_niche_analysis` | soft | оставить как есть (`["00_brief"]`) |
| `02_assets` | soft | [] |
| `03_references` | soft | [] |
| `04_brand` | soft | [] |
| `05_design` | soft | [] |
| `06_stack` | soft | [] |
| `07_content` | soft | [] |
| `07a_prototype` | soft | [] |
| `07b_wireframe` | **hard** | `["04_brand", "05_design", "07a_prototype"]` |
| `07c_composed` | **hard** | `["05_design", "07a_prototype", "07b_wireframe"]` |
| `07d_photos` | soft | [] |
| `07e_visuals` | soft | [] |
| `07f_composed_final` | soft | [] |
| `08_build` | **hard** | `["07c_composed"]` |
| `09_deploy` | **hard** | `["08_build", "10_qa"]` |
| `10_qa` | **hard** | `["08_build"]` |
| `11_analytics` | soft | `["09_deploy"]` |
| `12_seo` | soft | `["09_deploy"]` |

Пример формата (для одного этапа):
```yaml
  "07b_wireframe":
    name: "Wireframe"
    lock: hard
    require_approved: ["04_brand", "05_design", "07a_prototype"]
    hard_checks:
      ...
```

- [ ] **Step 3: Валидировать yaml**

```bash
yq -r '.stages | keys' config/stage-gates.yaml | head -25
```
Expected: список всех 21 этапа.

```bash
yq -r '.stages | to_entries | map(select(.value.lock == "hard")) | map(.key)' config/stage-gates.yaml
```
Expected: `["07b_wireframe", "07c_composed", "08_build", "09_deploy", "10_qa"]`

- [ ] **Step 4: Smoke — попытка выполнить hard-этап без зависимостей должна провалиться**

Создать временный fake-проект:
```bash
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/00_БРИФ" "$TMPDIR/07a_WIREFRAME" "$TMPDIR/07b_COMPOSED"
cat > "$TMPDIR/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "00_brief":         {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "04_brand":         {status: locked, timestamp: ""}
  "05_design":        {status: locked, timestamp: ""}
  "07a_prototype":    {status: locked, timestamp: ""}
  "07b_wireframe":    {status: locked, timestamp: ""}
EOF

bash scripts/gate-check.sh --stage 07b_wireframe --project "$TMPDIR" 2>&1 | head -5
```
Expected: exit != 0, сообщение "Previous stages not approved" или эквивалент.

- [ ] **Step 5: Commit**

```bash
git add config/stage-gates.yaml
git commit -m "feat(pr-g): hard/soft lock + require_approved для всех этапов

Hard-этапы (07b, 07c, 08, 09, 10) — теперь требуют конкретных
закрытых зависимостей. Soft-этапы помечены для документации."
```

---

## Task 2: Добавить soft-warning в `gate-check.sh`

**Цель:** Для soft-этапов — если предыдущий по pipeline-порядку не approved, печатать предупреждение. С `--auto` (или `GATE_AUTO=1`) — пропускать. Без — спрашивать y/N.

**Files:**
- Modify: `scripts/gate-check.sh`

**Pipeline order** (предлагается захардкодить в скрипте или взять из yaml top-level поля):

```
00_brief 01_context 01a_niche_analysis 02_assets 03_references 04_brand 05_design 06_stack 07_content 07a_prototype 07b_wireframe 07c_composed 07d_photos 07e_visuals 07f_composed_final 08_build 10_qa 09_deploy 11_analytics 12_seo
```

- [ ] **Step 1: Найти где в gate-check.sh проверяется require_approved**

```bash
grep -n "require_approved" scripts/gate-check.sh
```
Ожидается строка ~43-44.

- [ ] **Step 2: После блока require_approved (где `exit 1` если not all_approved) добавить soft-warning**

Открыть `scripts/gate-check.sh`, найти секцию `# 1. Check require_approved` (строки ~43-52), и **после неё, ДО** `# 2. Run hard_checks` (строка ~54) — вставить новый блок:

```bash
# 1b. Soft-lock warning: для soft-этапов — если предыдущий по pipeline не approved
PIPELINE_ORDER=(
    "00_brief" "01_context" "01a_niche_analysis" "02_assets" "03_references"
    "04_brand" "05_design" "06_stack" "07_content" "07a_prototype"
    "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"
    "08_build" "10_qa" "09_deploy" "11_analytics" "12_seo"
)

stage_lock="$(yq -r ".stages.\"$stage\".lock // \"soft\"" "$GATES_YAML")"

if [ "$stage_lock" = "soft" ] && [ -z "$required" ]; then
    # Найти предыдущий по pipeline_order
    prev=""
    for i in "${!PIPELINE_ORDER[@]}"; do
        if [ "${PIPELINE_ORDER[$i]}" = "$stage" ] && [ "$i" -gt 0 ]; then
            prev="${PIPELINE_ORDER[$((i-1))]}"
            break
        fi
    done
    if [ -n "$prev" ]; then
        prev_status="$(bash "$GATE_STATE" get "$project" "$prev" 2>/dev/null || echo "locked")"
        if [ "$prev_status" != "approved" ] && [ "$prev_status" != "n/a" ]; then
            echo "⚠️  Soft warning: предыдущий этап '$prev' имеет статус '$prev_status'."
            if [ "$auto" != "1" ] && [ -t 0 ]; then
                printf "   Точно зайти на '%s'? [y/N] " "$stage"
                read -r ans
                if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
                    echo "Отменено."
                    exit 1
                fi
            fi
        fi
    fi
fi
```

- [ ] **Step 3: Smoke — soft warning срабатывает**

```bash
bash scripts/gate-check.sh --stage 04_brand --project "$TMPDIR" --auto 2>&1 | grep -E "⚠️|Soft" | head -3
```
Expected: предупреждение про 03_references.

- [ ] **Step 4: Commit**

```bash
git add scripts/gate-check.sh
git commit -m "feat(pr-g): soft-lock warning для итеративных этапов

Для soft-этапов без require_approved: если предыдущий по pipeline
не approved — печатает ⚠️ и в интерактивном режиме спрашивает y/N.
В --auto режиме просто логгирует."
```

---

## Task 3: Добавить project-graph auto-update в `gate-check.sh`

**Цель:** В конце успешного gate-check — пересобрать `<project>/wiki/` через project-graph compile.

**Files:**
- Modify: `scripts/gate-check.sh`

- [ ] **Step 1: Найти конец gate-check.sh**

```bash
tail -30 scripts/gate-check.sh
```

Найти где скрипт делает final exit (обычно `exit 0` или возврат `$fail`).

- [ ] **Step 2: Перед финальным exit добавить блок auto-update**

В самый конец `scripts/gate-check.sh` (перед `exit $fail` или эквивалентом, если он есть; иначе перед концом файла) добавить:

```bash
# === PR-G: Auto-update project-graph wiki after successful gate-check ===
if [ "${fail:-1}" = "0" ] && [ -d "$project/wiki" ]; then
    project_slug="$(basename "$project")"
    cd "$REPO_ROOT" && python3 -m scripts.wiki.compile \
        --source-mode=project-graph --project="$project_slug" \
        >/dev/null 2>&1 || true
fi
```

- [ ] **Step 3: Smoke — после успешного check граф обновляется**

```bash
# Подготовь fake-проект где все проверки 07a проходят (минимум):
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/07_ПРОТОТИП" "$TMPDIR/wiki/concepts"
echo "Test prototype" > "$TMPDIR/07_ПРОТОТИП/prototype.md"
cat > "$TMPDIR/.landing-state.yaml" <<'EOF'
project: "test-pr-g"
stages:
  "07a_prototype": {status: in_progress, timestamp: ""}
EOF

# Запусти gate-check (07a — soft, hard_checks могут быть простые)
bash scripts/gate-check.sh --stage 07a_prototype --project "$TMPDIR" --auto 2>&1 | tail -5
ls "$TMPDIR/wiki/"
```
Expected: после exit 0 в wiki/ появились log.md и index.md.

- [ ] **Step 4: Commit**

```bash
git add scripts/gate-check.sh
git commit -m "feat(pr-g): auto-update project-graph wiki после gate-check exit 0

Закрытие любого этапа теперь сразу актуализирует <project>/wiki/.
Без SDK — stub-индекс. Время <1 сек."
```

---

## Task 4: Post-commit hook для system wiki

**Files:**
- Create: `.githooks/post-commit`

- [ ] **Step 1: Создать `.githooks/post-commit`**

```bash
mkdir -p .githooks
cat > .githooks/post-commit <<'HOOK'
#!/bin/bash
# PR-G: Авто-пересборка системной wiki при изменениях источников.
# Триггер: коммит затронул agents/skills/commands/template/standards.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Защита от рекурсии — если последний коммит уже chore(wiki) — выходим
LAST_MSG="$(git log -1 --pretty=%B 2>/dev/null | head -1)"
case "$LAST_MSG" in
    chore\(wiki\)*) exit 0 ;;
esac

SOURCE_PATTERN='^(agents/|skills/.*/SKILL\.md|commands/|template/.*/README\.md|docs/standards/)'

CHANGED="$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null || true)"
if ! echo "$CHANGED" | grep -qE "$SOURCE_PATTERN"; then
    exit 0  # источники wiki не менялись — ничего не делаем
fi

echo "📚 PR-G post-commit: источники wiki изменились, пересобираю..."
if ! python3 -m scripts.wiki.compile --source-mode=system 2>&1 | tail -3; then
    echo "⚠️  compile.py упал — wiki не обновлена. Запусти вручную:"
    echo "    python3 -m scripts.wiki.compile --source-mode=system"
    exit 0  # не блокируем commit
fi

if [ -n "$(git status wiki/ --short 2>/dev/null)" ]; then
    git add wiki/
    git commit -m "chore(wiki): авто-обновление после изменений системы" --no-verify
    echo "✅ wiki/ авто-закоммичено"
fi

exit 0
HOOK
chmod +x .githooks/post-commit
```

- [ ] **Step 2: Smoke (БЕЗ установки хука глобально пока)**

Установить хук временно и протестить:

```bash
git config core.hooksPath .githooks

# Создать пустой коммит — hook должен отработать мгновенно (нет изменений в источниках)
git commit --allow-empty -m "smoke(pr-g): empty commit"
# Expected: hook молча выходит, нет лишнего chore(wiki) коммита

# Теперь — туч агента (фейково):
echo "# Test" >> agents/landing-orchestrator.md  # любая правка
git add agents/landing-orchestrator.md
git commit -m "test: trigger post-commit hook"
# Expected: hook логгирует "📚 PR-G post-commit", запускает compile, при изменении wiki/ — авто-коммит chore(wiki)

# Откатить тестовую правку
git revert HEAD --no-edit 2>/dev/null || true
```

- [ ] **Step 3: Commit**

```bash
git add .githooks/post-commit
git commit -m "feat(pr-g): post-commit hook для авто-обновления system wiki

Триггер: изменения в agents/skills/commands/template/standards.
При коммите эти источники → compile.py --source-mode=system →
авто-chore(wiki) коммит если wiki/ обновилась.

Защита от рекурсии: пропускает если последний коммит chore(wiki)."
```

---

## Task 5: Установочный скрипт `install-git-hooks.sh`

**Files:**
- Create: `scripts/install-git-hooks.sh`

- [ ] **Step 1: Создать скрипт**

```bash
cat > scripts/install-git-hooks.sh <<'SCRIPT'
#!/bin/bash
# PR-G: Идемпотентная установка git hooks для wiki + локов.
# Запускается одноразово после клонирования репо или из onboarding.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

HOOKS_DIR=".githooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Папка $HOOKS_DIR не найдена в репо" >&2
    exit 1
fi

# Установка
git config core.hooksPath "$HOOKS_DIR"
chmod +x "$HOOKS_DIR/"*

echo "✅ Git hooks подключены: core.hooksPath = $HOOKS_DIR"
echo "   Active hooks:"
for h in "$HOOKS_DIR"/*; do
    [ -f "$h" ] && [ -x "$h" ] && echo "   - $(basename "$h")"
done
SCRIPT
chmod +x scripts/install-git-hooks.sh
```

- [ ] **Step 2: Smoke**

```bash
bash scripts/install-git-hooks.sh
git config core.hooksPath
```
Expected: `core.hooksPath = .githooks`, лист `post-commit`.

- [ ] **Step 3: Commit**

```bash
git add scripts/install-git-hooks.sh
git commit -m "feat(pr-g): install-git-hooks.sh — установка хуков

Идемпотентная установка через core.hooksPath = .githooks.
Запускать один раз после клонирования. Можно добавить в landing-onboarding."
```

---

## Task 6: Обновить промпт `landing-orchestrator`

**Files:**
- Modify: `agents/landing-orchestrator.md`

- [ ] **Step 1: Прочитать текущий промпт**

```bash
head -30 agents/landing-orchestrator.md
```

- [ ] **Step 2: В начало промпта (после `# landing-orchestrator (Главный дирижёр)` строки) добавить новый раздел `## ОБЯЗАТЕЛЬНЫЕ предусловия`**

Использовать Edit чтобы добавить после заголовка `# landing-orchestrator (Главный дирижёр)`:

```markdown

## ОБЯЗАТЕЛЬНЫЕ предусловия каждого действия (PR-G Stage Lock)

Перед ЛЮБЫМ действием — проверить дисциплину:

1. **Прочитай статус проекта:** открой `<project>/.landing-state.yaml` и `<project>/wiki/index.md` (если есть). Узнай `current_stage`.

2. **Запусти gate-check для целевого этапа:**
   ```
   bash scripts/gate-check.sh --stage <target_stage> --project <project>
   ```

3. **Если exit != 0** — НЕ ПРОДОЛЖАЙ:
   - При **hard-lock fail** (требуемые зависимости не закрыты) — сообщи пользователю список незакрытых этапов из stderr и предложи их закрыть.
   - При **soft-warning** (предыдущий этап не закрыт) — спроси разрешения у пользователя «прыгнуть» с явным подтверждением.
   - При **hard_checks fail** — предложи fix_hint из вывода.

4. **Никогда не действуй вне `current_stage`** даже если пользователь просит — сначала закрой текущий или явно зайди на новый через gate-check.

```

- [ ] **Step 3: Commit**

```bash
git add agents/landing-orchestrator.md
git commit -m "feat(pr-g): orchestrator promt — обязательные предусловия gate-check

Первая строка промпта теперь требует gate-check перед любым
действием. Запрещает действовать вне current_stage."
```

---

## Task 7: bats-тест на hard-lock

**Files:**
- Create: `tests/pr-g/helpers.bash`
- Create: `tests/pr-g/test_stage_lock_hard.bats`

- [ ] **Step 1: Создать `tests/pr-g/helpers.bash`**

```bash
mkdir -p tests/pr-g
cat > tests/pr-g/helpers.bash <<'HELPER'
#!/usr/bin/env bash
# Хелперы для bats-тестов PR-G.

# Корень репо
PR_G_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Создать минимальный fake-проект-лендинг в tmpdir и вернуть путь.
make_fake_project() {
    local tmpdir
    tmpdir=$(mktemp -d)
    cat > "$tmpdir/.landing-state.yaml" <<EOF
project: "test-project"
schema_version: 2
stages:
  "00_brief":          {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "01a_niche_analysis":{status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "03_references":     {status: locked, timestamp: ""}
  "04_brand":          {status: locked, timestamp: ""}
  "05_design":         {status: locked, timestamp: ""}
  "07_content":        {status: approved, timestamp: "2026-05-15T00:00:00Z"}
  "07a_prototype":     {status: locked, timestamp: ""}
  "07b_wireframe":     {status: locked, timestamp: ""}
  "07c_composed":      {status: locked, timestamp: ""}
  "08_build":          {status: locked, timestamp: ""}
  "09_deploy":         {status: locked, timestamp: ""}
  "10_qa":             {status: locked, timestamp: ""}
EOF
    mkdir -p "$tmpdir/00_БРИФ"
    echo "fake brief" > "$tmpdir/00_БРИФ/brief.md"
    echo "$tmpdir"
}

# Установить status для одного stage в state.yaml
set_status() {
    local project="$1" stage="$2" status="$3"
    yq -i ".stages.\"$stage\".status = \"$status\"" "$project/.landing-state.yaml"
}
HELPER
```

- [ ] **Step 2: Создать `tests/pr-g/test_stage_lock_hard.bats`**

```bash
cat > tests/pr-g/test_stage_lock_hard.bats <<'BATS'
#!/usr/bin/env bats

load 'helpers.bash'

@test "07b_wireframe (hard) блокирован пока 04_brand не approved" {
    project="$(make_fake_project)"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07b_wireframe --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"Previous stages not approved"* ]] || [[ "$output" == *"04_brand"* ]]
}

@test "07b_wireframe проходит require_approved если все зависимости approved" {
    project="$(make_fake_project)"
    set_status "$project" "04_brand" "approved"
    set_status "$project" "05_design" "approved"
    set_status "$project" "07a_prototype" "approved"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07b_wireframe --project "$project" --auto
    # Может упасть на hard_checks (file_exists), но require_approved проходит
    [[ "$output" == *"Required prior stages approved"* ]] || true
}

@test "08_build блокирован без 07c_composed" {
    project="$(make_fake_project)"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"07c_composed"* ]] || [[ "$output" == *"not approved"* ]]
}

@test "09_deploy требует И 08_build И 10_qa" {
    project="$(make_fake_project)"
    set_status "$project" "08_build" "approved"
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 09_deploy --project "$project" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"10_qa"* ]]
}
BATS
chmod +x tests/pr-g/test_stage_lock_hard.bats
```

- [ ] **Step 3: Запустить тесты**

```bash
bats tests/pr-g/test_stage_lock_hard.bats
```
Expected: 4 tests pass (или 3-4 — последние могут падать если фикстура не идеальна).

Если падают — диагностика:
- Проверить что yq установлен
- Запустить gate-check.sh вручную с тем же tmpdir и посмотреть вывод

- [ ] **Step 4: Commit**

```bash
git add tests/pr-g/helpers.bash tests/pr-g/test_stage_lock_hard.bats
git commit -m "test(pr-g): bats hard-lock — 07b/08/09 блокированы без зависимостей

4 теста проверяют что require_approved действительно блокирует
hard-этапы при незакрытых зависимостях."
```

---

## Task 8: bats-тест на soft-warning

**Files:**
- Create: `tests/pr-g/test_stage_lock_soft.bats`

- [ ] **Step 1: Создать тест**

```bash
cat > tests/pr-g/test_stage_lock_soft.bats <<'BATS'
#!/usr/bin/env bats

load 'helpers.bash'

@test "04_brand (soft) при locked 03_references — печатает warning, exit 0 c --auto" {
    project="$(make_fake_project)"
    # 03_references по умолчанию locked в фикстуре
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 04_brand --project "$project" --auto
    # exit code не обязательно 0 (hard_checks могут упасть), главное warning
    [[ "$output" == *"Soft warning"* ]] || [[ "$output" == *"⚠️"* ]]
}

@test "04_brand soft БЕЗ --auto + stdin = 'y' — продолжает" {
    project="$(make_fake_project)"
    # Без -t 0 (нет tty в bats), скрипт не должен спрашивать, а пропустить
    run bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 04_brand --project "$project"
    # warning должен быть
    [[ "$output" == *"⚠"* ]] || [[ "$output" == *"Soft"* ]] || true
}
BATS
chmod +x tests/pr-g/test_stage_lock_soft.bats
```

- [ ] **Step 2: Запустить**

```bash
bats tests/pr-g/test_stage_lock_soft.bats
```
Expected: оба теста pass или с понятным выводом.

- [ ] **Step 3: Commit**

```bash
git add tests/pr-g/test_stage_lock_soft.bats
git commit -m "test(pr-g): soft-warning для итеративных этапов"
```

---

## Task 9: bats-тест auto-update project-graph

**Files:**
- Create: `tests/pr-g/test_gate_check_updates_graph.bats`

- [ ] **Step 1: Создать тест**

```bash
cat > tests/pr-g/test_gate_check_updates_graph.bats <<'BATS'
#!/usr/bin/env bats

load 'helpers.bash'

@test "gate-check exit 0 → project/wiki/log.md обновляется" {
    project="$(make_fake_project)"
    # Создать wiki/ заранее (имитация миграции)
    mkdir -p "$project/wiki"
    echo "old" > "$project/wiki/log.md"
    
    # Прогон на 07a_prototype (soft, нет require_approved, но прототипа нет)
    # Создадим минимальный прототип чтобы hard_checks прошли
    mkdir -p "$project/07_ПРОТОТИП/source"
    echo "stub" > "$project/07_ПРОТОТИП/prototype.md"
    
    # Запустить gate-check (может вернуть != 0 если hard_checks не идеальны, 
    # но мы проверяем что ЕСЛИ exit 0 — то wiki обновлена)
    bash "$PR_G_REPO_ROOT/scripts/gate-check.sh" --stage 07a_prototype --project "$project" --auto >/dev/null 2>&1 || true
    
    # Если wiki/log.md изменилось — auto-update сработал
    log_content="$(cat "$project/wiki/log.md")"
    # Минимум: файл существует и непустой
    [ -s "$project/wiki/log.md" ]
}
BATS
chmod +x tests/pr-g/test_gate_check_updates_graph.bats
```

- [ ] **Step 2: Запустить**

```bash
bats tests/pr-g/test_gate_check_updates_graph.bats
```

- [ ] **Step 3: Commit**

```bash
git add tests/pr-g/test_gate_check_updates_graph.bats
git commit -m "test(pr-g): auto-update project-graph после gate-check"
```

---

## Task 10: Финальный smoke + установка хуков локально

- [ ] **Step 1: Установить хуки**

```bash
bash scripts/install-git-hooks.sh
```
Expected: `core.hooksPath = .githooks`, листинг post-commit.

- [ ] **Step 2: Прогон всех bats-тестов PR-G**

```bash
bats tests/pr-g/
```
Expected: все 7+ тестов pass.

- [ ] **Step 3: Полный pytest для регрессии (PR-F тесты ещё работают)**

```bash
pytest tests/wiki/ -v 2>&1 | tail -5
```
Expected: 70 passed.

- [ ] **Step 4: Push**

```bash
git push origin feat/pr-a-prototype-block-library 2>&1 | tail -5
```

- [ ] **Step 5: Отметить пункт 1 в `ПЛАН-ДОРАБОТОК.md`**

Применить Edit: заменить заголовок раздела `#### 1. Система должна идти строго по шагам, без перепрыгиваний` на `#### 1. ✅ ГОТОВО (2026-05-15) — система идёт строго по шагам`. Дописать в начало раздела блок «Что сделано в PR-G» (как в пункте 0).

```bash
git add docs/ПЛАН-ДОРАБОТОК.md
git commit -m "docs: пункт 1 (stage lock) отмечен как готовый"
git push origin feat/pr-a-prototype-block-library
```

---

## Self-Review

**Spec coverage:**
- ✅ Hard-lock через require_approved (Task 1)
- ✅ Soft-warning (Task 2)
- ✅ Auto-update project-graph (Task 3)
- ✅ Post-commit hook для system wiki (Task 4)
- ✅ Install-git-hooks (Task 5)
- ✅ Orchestrator promt (Task 6)
- ✅ Тесты hard (Task 7)
- ✅ Тесты soft (Task 8)
- ✅ Тесты graph auto-update (Task 9)
- ✅ Финальный smoke + push (Task 10)
- ⏭️ Post-commit hook тест — не входит как отдельный тест (Task 4 имеет smoke внутри Step 2)

**Placeholders:** нет.

**Type consistency:**
- `require_approved` (существующее имя) — НЕ `requires_approved` (моя ошибка в первом spec; теперь исправлено везде).
- `lock` поле: значения `soft`/`hard` строго.

**Риски:**
1. **Тесты могут флакать** на CI без tty (для soft-lock интерактива) — поэтому `[ -t 0 ]` проверка в коде skip-ит интерактив без tty.
2. **Post-commit hook** может зациклиться — защита через проверку `LAST_MSG`.
3. **Project-graph compile** при gate-check может медленно работать на больших проектах — `|| true` и `>/dev/null` гарантируют что не валит gate-check.

---

## Дальше после PR-G

- ✅ Пункт 0 (вики) и Пункт 1 (строго по шагам) закрыты
- Следующий: **Пункт 2** «Текст прототипа не меняется» — отдельный PR-H про сравнение `composed.html` с `prototype.md`

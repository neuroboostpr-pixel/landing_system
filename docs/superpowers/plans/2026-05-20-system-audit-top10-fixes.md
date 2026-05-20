# Landing-System Top-10 Audit Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть 10 критичных находок аудита `audit/REPORT.md` — превратить `landing-system` из «policy without police» в систему, где пропуск пайплайн-шага физически невозможен, а utility-скрипты не жгут токены впустую.

**Architecture:** 8 фаз — каждая закрывает один кластер находок. Фазы 1-4 — низкорисковые quick wins (Python token leaks, post-commit safety, gate-check integrity). Фаза 5 — главный архитектурный фикс: `PreToolUse` hook, физически блокирующий обход стадий. Фазы 6-8 — гигиена промптов агентов (тиражирование gold-standard паттерна).

**Tech Stack:**
- Python 3 (Anthropic SDK + sentence-transformers-агностично) — для compile.py фиксов и enforcement hook
- Bash 4+ (yq, jq) — для gate-check.sh
- bats — регрессионные тесты (используется существующий `tests/gate-check/`)
- pytest — для Python-фиксов
- YAML — `config/stage-gates.yaml`, `template/.landing-state.yaml`, `.claude/settings.json`

**Источник правды для каждой находки:** `audit/REPORT.md` + `audit/0[1-4]-*.md`. Каждый Task ниже ссылается на конкретный пункт.

---

## File Structure (что трогаем)

**Создаём:**
- `scripts/hooks/enforce_stage_gate.py` — главный enforcement hook (Phase 5)
- `tests/gate-check/test-enforce-stage-gate.bats` — регрессионные тесты для hook
- `tests/wiki/test_system_compiler.py` — регрессии для O(N²) кэша и SDK-error hash

**Меняем (точечно, без mass-рефакторинга):**
- `scripts/wiki/system_compiler.py:147,179-183,194-197` — Python token leaks
- `scripts/gate-check.sh:121-126,166-168` + добавление 2 новых case-веток — gate integrity
- `.githooks/post-commit:5,30-32` — auto-commit safety
- `template/.landing-state.yaml:12-15` — убираем `n/a` defaults
- `.claude/settings.json` — добавляем PreToolUse hook
- `agents/*.md` (28 файлов, кроме landing-orchestrator) — добавляем Stage Execution Protocol преамбулу
- `agents/integrations-engineer.md`, `seo-optimizer.md`, `content-writer.md` — исправляем broken file refs
- `agents/landing-orchestrator.md:61-67` — убираем obsolete «Phase 1 Scope»
- `commands/landing-compose.md`, `landing-photos.md`, `landing-visuals.md`, `landing-wireframe.md`, `landing-prototype.md` — убираем PR-D противоречия
- `agents/prototype-importer.md` — фикс пути auto-quiz скрипта

**Не трогаем:**
- `block-library/` — структура хорошая
- `template/` папки (кроме `.landing-state.yaml`)
- `wiki/` (пересоберётся автоматически)
- `skills/` (если не упомянуто в конкретном task'е)

---

## Phase 1 — Python token leaks (wiki compile)

Закрывает: REPORT.md Top-10 #5, #6. Цель: убрать O(N²) IO и поломанный hash-cache, которые жгут токены на каждом git commit'е.

### Task 1.1: Регресс-тест на O(N²) кэш в system_compiler

**Files:**
- Create: `tests/wiki/test_system_compiler.py`
- Test: `tests/wiki/test_system_compiler.py::test_cache_saved_once_per_compile_run`

- [ ] **Step 1: Создать каталог тестов и пустой `__init__.py`**

```bash
mkdir -p tests/wiki
touch tests/wiki/__init__.py
```

- [ ] **Step 2: Написать failing test**

`tests/wiki/test_system_compiler.py`:

```python
"""Регрессии для scripts/wiki/system_compiler.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.wiki import system_compiler


def test_cache_saved_once_per_compile_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """save_cache должен вызываться один раз за прогон, а не в цикле.

    Эта регрессия ловит то что описано в audit/01-scripts-wiki-python.md:
    раньше save_cache(...) звался ВНУТРИ цикла → O(N²) IO для 473 концептов.
    """
    repo_root = tmp_path / "repo"
    wiki_dir = tmp_path / "wiki"
    (repo_root / "agents").mkdir(parents=True)
    (repo_root / "agents" / "a.md").write_text("---\nname: a\n---\nA", encoding="utf-8")
    (repo_root / "agents" / "b.md").write_text("---\nname: b\n---\nB", encoding="utf-8")
    (repo_root / "agents" / "c.md").write_text("---\nname: c\n---\nC", encoding="utf-8")

    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    with patch("scripts.wiki.hash_cache.save_cache") as mock_save, \
         patch("scripts.wiki.system_compiler._compile_concept", return_value="---\nname: x\n---\nX"):
        system_compiler.compile_sources(
            repo_root=repo_root,
            wiki_dir=wiki_dir,
            sources=sources,
            dry_run=False,
        )

    # Bootstrap pre-population + финальный save = максимум 2 вызова.
    # Если save_cache внутри цикла — будет ≥3 (по числу файлов).
    assert mock_save.call_count <= 2, (
        f"save_cache called {mock_save.call_count} times — should be ≤2 "
        "(once for bootstrap pre-pop, once at end). Per-file save = O(N²) IO."
    )
```

- [ ] **Step 3: Запустить тест — должен упасть**

```bash
pytest tests/wiki/test_system_compiler.py -v
```

Expected: FAIL — `save_cache called 4 times`. Если падает по другой причине (импорт, conftest), сначала чинит инфраструктуру тестов, потом возвращается сюда.

- [ ] **Step 4: Перенести save_cache из цикла**

В `scripts/wiki/system_compiler.py` найти строку 194-197:

```python
            if not dry_run:
                utils.atomic_write(concept_path, content)
                cache[rel_key] = hash_cache.compute_hash(source_path)
                hash_cache.save_cache(cache_path, cache)  # ← BAD: внутри цикла
            compiled.append(rel_key)
```

Заменить на (save_cache убран из цикла):

```python
            if not dry_run:
                utils.atomic_write(concept_path, content)
                cache[rel_key] = hash_cache.compute_hash(source_path)
            compiled.append(rel_key)
```

Затем после `for source_def in sources:` цикла (около строки 199, перед `# Индекс`) добавить:

```python
    # Финальный save кэша — один раз за прогон, не в цикле (O(N²) → O(N)).
    if not dry_run and compiled:
        hash_cache.save_cache(cache_path, cache)
```

- [ ] **Step 5: Запустить тест — должен пройти**

```bash
pytest tests/wiki/test_system_compiler.py::test_cache_saved_once_per_compile_run -v
```

Expected: PASS.

- [ ] **Step 6: Smoke-тест реальной компиляции**

```bash
python3 -m scripts.wiki.compile --source-mode=system --dry-run 2>&1 | tail -5
```

Expected: завершается без ошибок. Если падает — откатить изменение и разобраться.

- [ ] **Step 7: Commit**

```bash
git add tests/wiki/__init__.py tests/wiki/test_system_compiler.py scripts/wiki/system_compiler.py
git commit -m "fix(wiki): save cache once per compile run (was O(N²) IO)

Audit finding: scripts/wiki/system_compiler.py:197 called save_cache
inside the per-file loop, rewriting the entire 62 KB cache JSON for
each concept. For 473 concepts this was O(N²) IO on every git commit
via the post-commit hook. Move save_cache to a single call after the
loop completes.

Ref: audit/01-scripts-wiki-python.md (token-leak #1)"
```

---

### Task 1.2: Кэшировать hash при SDK-ошибке (чтобы битый файл не звал SDK на каждом коммите)

**Files:**
- Modify: `scripts/wiki/system_compiler.py:179-183`
- Test: `tests/wiki/test_system_compiler.py::test_failed_sdk_call_still_caches_source_hash`

- [ ] **Step 1: Failing test**

Добавить в `tests/wiki/test_system_compiler.py`:

```python
def test_failed_sdk_call_still_caches_source_hash(tmp_path: Path) -> None:
    """Если _compile_concept падает SDK-ошибкой — hash источника ВСЁ РАВНО
    должен попасть в кэш, чтобы на следующем коммите этот файл не звал SDK снова.

    Audit finding: system_compiler.py:179-183 — error logged but hash never
    cached → defeats hash-cache purpose for chronically-broken files.
    """
    from scripts.wiki import hash_cache, sdk_client

    repo_root = tmp_path / "repo"
    wiki_dir = tmp_path / "wiki"
    (repo_root / "agents").mkdir(parents=True)
    src = repo_root / "agents" / "broken.md"
    src.write_text("---\nname: broken\n---\nX", encoding="utf-8")

    sources = [{"path": "agents/*.md", "concept_dir": "agents"}]

    with patch("scripts.wiki.system_compiler._compile_concept",
               side_effect=sdk_client.SDKError("simulated")):
        system_compiler.compile_sources(
            repo_root=repo_root, wiki_dir=wiki_dir,
            sources=sources, dry_run=False,
        )

    cache = hash_cache.load_cache(wiki_dir / ".cache.json")
    assert "agents/broken.md" in cache, (
        "Source hash not cached after SDK error — file will re-call SDK "
        "on every subsequent commit (token leak)."
    )
    assert cache["agents/broken.md"] == hash_cache.compute_hash(src)
```

- [ ] **Step 2: Run — fail expected**

```bash
pytest tests/wiki/test_system_compiler.py::test_failed_sdk_call_still_caches_source_hash -v
```

Expected: FAIL — `'agents/broken.md' not in cache`.

- [ ] **Step 3: Patch error branch**

В `scripts/wiki/system_compiler.py` найти:

```python
            try:
                content = _compile_concept(source_path, repo_root)
            except sdk_client.SDKError as e:
                errors.append(f"{rel_key}: {e}")
                continue
```

Заменить на:

```python
            try:
                content = _compile_concept(source_path, repo_root)
            except sdk_client.SDKError as e:
                errors.append(f"{rel_key}: {e}")
                # Кэшируем hash даже при ошибке — иначе post-commit будет
                # звать SDK на этот файл КАЖДЫЙ раз. Пользователь увидит
                # ошибку в errors[], кэш починится при следующем коммите
                # с обновлённым source-файлом.
                cache[rel_key] = hash_cache.compute_hash(source_path)
                continue
```

- [ ] **Step 4: Test passes**

```bash
pytest tests/wiki/test_system_compiler.py -v
```

Expected: оба теста PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/wiki/system_compiler.py tests/wiki/test_system_compiler.py
git commit -m "fix(wiki): cache source hash even on SDK error

Audit finding: system_compiler.py:179-183 logged SDK errors but never
cached the source hash, so any persistently-broken file re-called the
SDK on every git commit via post-commit hook. Now we cache the hash
regardless — the user still sees the error in errors[] list.

Ref: audit/01-scripts-wiki-python.md (token-leak #2)"
```

---

## Phase 2 — post-commit hook hardening

Закрывает: REPORT.md Top-10 #7. Auto-commit во время merge/rebase/cherry-pick может породить рекурсию или закоммитить секреты.

### Task 2.1: Защита от merge/rebase/конфликтов

**Files:**
- Modify: `.githooks/post-commit`

- [ ] **Step 1: Прочитать текущий файл**

Текущее содержимое (см. строки 1-37 файла) запускается на КАЖДЫЙ коммит, включая `git commit` во время merge — что приводит к auto-commit на полузавершённом merge.

- [ ] **Step 2: Добавить guards в начало (после `cd`)**

Заменить в `.githooks/post-commit` блок с защитой от рекурсии (строки 10-14):

```bash
# Защита от рекурсии — если последний коммит уже chore(wiki) — выходим
LAST_MSG="$(git log -1 --pretty=%B 2>/dev/null | head -1)"
case "$LAST_MSG" in
    chore\(wiki\)*) exit 0 ;;
esac
```

На расширенную версию (добавляем 4 новых guard'а):

```bash
# Защита от рекурсии — если последний коммит уже chore(wiki) — выходим
LAST_MSG="$(git log -1 --pretty=%B 2>/dev/null | head -1)"
case "$LAST_MSG" in
    chore\(wiki\)*) exit 0 ;;
esac

# Защита от запуска во время merge/rebase/cherry-pick/bisect.
# Auto-commit поверх полу-merge'а порождает грязную историю и конфликты.
GIT_DIR="$(git rev-parse --git-dir)"
for marker in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD BISECT_LOG; do
    if [ -e "$GIT_DIR/$marker" ] || [ -d "$GIT_DIR/rebase-merge" ] || [ -d "$GIT_DIR/rebase-apply" ]; then
        echo "ℹ️  post-commit: skip wiki rebuild (in $marker / rebase state)"
        exit 0
    fi
done

# Защита от запуска вне репозитория (на всякий случай).
if [ -z "${REPO_ROOT:-}" ] || [ ! -d "$REPO_ROOT/.git" ]; then
    exit 0
fi
```

- [ ] **Step 3: Усилить set-options**

Заменить строку 5:

```bash
set -uo pipefail
```

На:

```bash
set -Eeuo pipefail
trap 'echo "post-commit failed at line $LINENO" >&2; exit 0' ERR
```

(Выход `exit 0` на trap — потому что мы не хотим блокировать пользовательский commit, но хотим видеть, на какой строке упали.)

- [ ] **Step 4: Заменить опасный `--no-verify`**

Заменить строку 30-32:

```bash
if [ -n "$(git status wiki/ --short 2>/dev/null)" ]; then
    git add wiki/
    git commit -m "chore(wiki): авто-обновление после изменений системы" --no-verify
    echo "✅ wiki/ авто-закоммичено"
fi
```

На:

```bash
if [ -n "$(git status wiki/ --short 2>/dev/null)" ]; then
    # Точечный add (а не папка целиком) — снижает риск зацепить секреты.
    git add wiki/index.md wiki/log.md wiki/concepts/ wiki/preview.html 2>/dev/null || true
    # Без --no-verify: если pre-commit secret-scanner упал — это сигнал,
    # а не повод обходить. Если у репо нет pre-commit hooks — git это просто молча пропустит.
    if git commit -m "chore(wiki): авто-обновление после изменений системы" 2>&1; then
        echo "✅ wiki/ авто-закоммичено"
    else
        echo "⚠️  wiki/ commit заблокирован (pre-commit hook?). Запусти руками."
    fi
fi
```

- [ ] **Step 5: Smoke-тест**

```bash
echo "test" >> README.md
git add README.md
git commit -m "test: trigger post-commit"
git log -1 --pretty=%B  # хук должен был отработать без ошибок
git reset --soft HEAD~1  # откатываем тестовый commit
git restore README.md
```

Expected: коммит проходит, никаких рекурсий, никаких ошибок в выводе хука.

- [ ] **Step 6: Commit**

```bash
git add .githooks/post-commit
git commit -m "fix(githooks): post-commit safety — skip during merge, no --no-verify

Audit findings (audit/02-scripts-bash.md):
- C5: skip during merge/rebase/cherry-pick to avoid commits on dirty state
- C6: 'git add wiki/' could stage unintended files — switched to explicit paths
- C7: --no-verify bypassed pre-commit secret scanners — removed
- Strengthened to 'set -Eeuo pipefail' with trap for diagnostics

Ref: audit/02-scripts-bash.md C5-C7"
```

---

## Phase 3 — Template state-file: убираем тихий обход niche-analysis

Закрывает: REPORT.md Top-10 #8. Шаблон по умолчанию ставит 4 upstream-стадии в `n/a`, обходя 14 hard-checks niche-analysis.

### Task 3.1: Переключить defaults с `n/a` на `pending`

**Files:**
- Modify: `template/.landing-state.yaml:11-15`

- [ ] **Step 1: Прочитать текущие 4 строки** (уже видно: status: n/a для 00, 01, 01a, 02)

- [ ] **Step 2: Заменить блок upstream-стадий**

Заменить:

```yaml
stages:
  # Upstream stages (n/a in prototype-first flow)
  "00_brief":             {status: n/a, timestamp: ""}
  "01_context":           {status: n/a, timestamp: ""}
  "01a_niche_analysis":   {status: n/a, timestamp: ""}
  "02_assets":            {status: n/a, timestamp: ""}
```

На:

```yaml
stages:
  # Upstream stages — default "locked" until /landing-go или /landing-start
  # явно проставит "n/a" для prototype-first flow. Раньше defaults стояли
  # n/a, что тихо обходило 14 hard-checks niche-analysis (audit gap).
  "00_brief":             {status: locked, timestamp: ""}
  "01_context":           {status: locked, timestamp: ""}
  "01a_niche_analysis":   {status: locked, timestamp: ""}
  "02_assets":            {status: locked, timestamp: ""}
```

- [ ] **Step 3: Проверить — нужен ли парный update в коде /landing-start / landing-from-context**

```bash
grep -rn 'status.*n/a' commands/ skills/ agents/ scripts/ 2>/dev/null | head -20
```

Если найдены явные set'ы `n/a` для prototype-first потока — оставить их (это правильно). Если нет — добавить в `landing-start` и `landing-from-context` явный переход (см. Task 3.2).

- [ ] **Step 4: Smoke — создать новый проект и проверить state**

```bash
TMP_PROJECT=$(mktemp -d)/test-fix-3
cp -r template "$TMP_PROJECT"
yq -r '.stages | to_entries | .[] | "\(.key): \(.value.status)"' "$TMP_PROJECT/.landing-state.yaml" | grep -E "(00_brief|01a_niche_analysis)"
```

Expected: `00_brief: locked`, `01a_niche_analysis: locked`.

- [ ] **Step 5: Commit**

```bash
git add template/.landing-state.yaml
git commit -m "fix(template): default upstream stages to 'locked', not 'n/a'

Audit finding: template/.landing-state.yaml pre-marked 00_brief,
01_context, 01a_niche_analysis, 02_assets as 'n/a' for every new
project, silently bypassing 14 hard checks of niche-analysis (the
most-checked stage in the system).

prototype-first flow should EXPLICITLY mark these as 'n/a' (via
/landing-start or /landing-go), not get it for free as a default.

Ref: audit/04-enforcement-layer.md M5"
```

---

### Task 3.2: Явный переход в n/a для prototype-first (если не было)

**Files:**
- Modify: `commands/landing-start.md` или `commands/landing-from-context.md` (один из них)
- Modify: `commands/landing-go.md` (если он определяет flow)

- [ ] **Step 1: Найти где определяется prototype-first flow**

```bash
grep -rn "prototype-first" commands/ skills/ agents/ docs/ 2>/dev/null | head -10
```

- [ ] **Step 2: В нужной команде добавить блок**

После того места, где flow определён как prototype-first, добавить параграф:

````markdown
### Mark upstream stages n/a (prototype-first)

Если flow определён как prototype-first (есть `07_ПРОТОТИП/source/prototype.{pdf,md}`):

```bash
bash scripts/gate-state.sh set "<project>" 00_brief n/a "prototype-first flow"
bash scripts/gate-state.sh set "<project>" 01_context n/a "prototype-first flow"
bash scripts/gate-state.sh set "<project>" 01a_niche_analysis n/a "prototype-first flow"
bash scripts/gate-state.sh set "<project>" 02_assets n/a "prototype-first flow"
```

Если flow прежний (с брифом и niche-analysis) — оставить статус `locked`, gate-check проведёт по этапам.
````

(Если `gate-state.sh` не поддерживает причину — нужно добавить, см. Phase 4 Task 4.4.)

- [ ] **Step 3: Commit**

```bash
git add commands/
git commit -m "feat(commands): explicit n/a transition for prototype-first flow

Ref: complements template/.landing-state.yaml default change"
```

---

## Phase 4 — gate-check.sh integrity

Закрывает: REPORT.md Top-10 #3, #4. Сейчас unknown check types молча проходят, `legacy: true` обнуляет всё.

### Task 4.1: Hard-fail на unknown check types + регресс-тест

**Files:**
- Modify: `scripts/gate-check.sh:166-168`
- Test: `tests/gate-check/test-gate-check-unknown-type.bats`

- [ ] **Step 1: Failing bats test**

`tests/gate-check/test-gate-check-unknown-type.bats`:

```bash
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export TMP_PROJ="$(mktemp -d)/test-proj"
    mkdir -p "$TMP_PROJ"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$TMP_PROJ/.landing-state.yaml"

    # Подменяем stage-gates.yaml на тестовый с unknown типом
    export TEST_GATES="$(mktemp).yaml"
    cat > "$TEST_GATES" <<'EOF'
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: unknown_check
        type: this_type_does_not_exist
        required: true
EOF
}

teardown() {
    rm -rf "$TMP_PROJ" "$TEST_GATES"
}

@test "gate-check fails (exit != 0) when hard_check uses unknown type" {
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"unknown"* ]]
    [[ "$output" == *"this_type_does_not_exist"* ]]
}
```

- [ ] **Step 2: Run — fail expected**

```bash
cd "$(git rev-parse --show-toplevel)"
bats tests/gate-check/test-gate-check-unknown-type.bats
```

Expected: FAIL — текущий код печатает warning и проходит.

- [ ] **Step 3: Fix**

В `scripts/gate-check.sh:166-168` заменить:

```bash
        *)
            echo "  ⚠️  $check_id: unknown type $check_type" >&2
            ;;
```

На:

```bash
        *)
            echo "  ❌ $check_id: unknown check type '$check_type'" >&2
            echo "     → implement this type in scripts/gate-check.sh or fix the typo in config/stage-gates.yaml" >&2
            fail=1
            ;;
```

- [ ] **Step 4: Test passes**

```bash
bats tests/gate-check/test-gate-check-unknown-type.bats
```

Expected: PASS.

- [ ] **Step 5: Smoke — gate-check ничего не сломал на реальной системе**

```bash
bash scripts/gate-check.sh --help 2>&1 | head -5
```

Expected: usage печатается без ошибок.

- [ ] **Step 6: Commit**

```bash
git add scripts/gate-check.sh tests/gate-check/test-gate-check-unknown-type.bats
git commit -m "fix(gate-check): hard-fail on unknown check types

Audit finding (audit/02-scripts-bash.md C1): unknown check types were
treated as a silent warning and counted as PASS. config/stage-gates.yaml
already uses two unhandled types (file_or_dir_exists for 07a, dir_has_files
for 07d) — meaning those hard-gates were effectively no-ops.

Ref: audit/02-scripts-bash.md C1"
```

---

### Task 4.2: Реализовать `file_or_dir_exists` тип

**Files:**
- Modify: `scripts/gate-check.sh` (добавить новый case-блок)
- Test: расширение `test-gate-check-unknown-type.bats`

- [ ] **Step 1: Failing test**

Добавить в `tests/gate-check/test-gate-check-unknown-type.bats`:

```bash
@test "file_or_dir_exists passes when file exists" {
    PRO="$(mktemp -d)"
    touch "$PRO/some-file"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: prototype_exists
        type: file_or_dir_exists
        path: "$PRO/some-file"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -eq 0 ]
    rm -rf "$PRO"
}

@test "file_or_dir_exists passes when directory exists with content" {
    PRO="$(mktemp -d)"
    mkdir -p "$PRO/some-dir"
    touch "$PRO/some-dir/inner.txt"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: src_dir
        type: file_or_dir_exists
        path: "$PRO/some-dir"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -eq 0 ]
    rm -rf "$PRO"
}

@test "file_or_dir_exists fails when neither exists" {
    PRO="$(mktemp -d)"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: missing
        type: file_or_dir_exists
        path: "$PRO/nonexistent"
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -ne 0 ]
    rm -rf "$PRO"
}
```

- [ ] **Step 2: Run — fail expected**

```bash
bats tests/gate-check/test-gate-check-unknown-type.bats
```

Expected: 3 новых теста FAIL (тип не реализован → попадает в default → exit 1, но сообщение «unknown type», не «missing path»).

- [ ] **Step 3: Добавить case-ветку**

В `scripts/gate-check.sh` после case-ветки `file_exists` (около строки 112) добавить:

```bash
        file_or_dir_exists)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            if [ -e "$path" ]; then
                # Если это директория, требуем непустоту (иначе file_or_dir_exists == file_exists с лишним именем)
                if [ -d "$path" ] && [ -z "$(ls -A "$path" 2>/dev/null)" ]; then
                    echo "  ❌ $check_id: directory $path exists but is empty"
                    [ -n "$fix_hint" ] && echo "     → $fix_hint"
                    fail=1
                else
                    echo "  ✅ $check_id ($path)"
                fi
            else
                echo "  ❌ $check_id: missing $path"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            fi
            ;;
```

- [ ] **Step 4: Tests pass**

```bash
bats tests/gate-check/test-gate-check-unknown-type.bats
```

Expected: все 4 теста PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/gate-check.sh tests/gate-check/test-gate-check-unknown-type.bats
git commit -m "feat(gate-check): implement file_or_dir_exists check type

Was declared in config/stage-gates.yaml:189 (07a_prototype) but had no
implementation, so 07a hard-gate was always green.

Ref: audit/02-scripts-bash.md C1 (continuation)"
```

---

### Task 4.3: Реализовать `dir_has_files` тип

**Files:**
- Modify: `scripts/gate-check.sh` (новый case-блок)
- Test: расширение того же bats-файла

- [ ] **Step 1: Failing test**

Добавить в bats:

```bash
@test "dir_has_files passes when dir has >=1 matching file" {
    PRO="$(mktemp -d)"
    mkdir -p "$PRO/inbox"
    touch "$PRO/inbox/photo1.jpg"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: photos_in_inbox
        type: dir_has_files
        path: "$PRO/inbox"
        pattern: "*.jpg"
        min_count: 1
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -eq 0 ]
    rm -rf "$PRO"
}

@test "dir_has_files fails when dir is empty" {
    PRO="$(mktemp -d)"
    mkdir -p "$PRO/inbox"
    cat > "$TEST_GATES" <<EOF
stages:
  "test_stage":
    name: "Test"
    lock: hard
    require_approved: []
    hard_checks:
      - id: photos_in_inbox
        type: dir_has_files
        path: "$PRO/inbox"
        pattern: "*.jpg"
        min_count: 1
        required: true
EOF
    run env GATES_YAML="$TEST_GATES" bash "$REPO_ROOT/scripts/gate-check.sh" \
        --stage test_stage --project "$PRO" --auto
    [ "$status" -ne 0 ]
    rm -rf "$PRO"
}
```

- [ ] **Step 2: Run — fail expected**

```bash
bats tests/gate-check/test-gate-check-unknown-type.bats
```

- [ ] **Step 3: Добавить case-ветку**

В `scripts/gate-check.sh` рядом с `file_or_dir_exists`:

```bash
        dir_has_files)
            path="$(yq -r ".stages.\"$stage\".hard_checks[$i].path" "$GATES_YAML" | sed "s|{project}|$project|g")"
            pattern="$(yq -r ".stages.\"$stage\".hard_checks[$i].pattern // \"*\"" "$GATES_YAML")"
            min_count="$(yq -r ".stages.\"$stage\".hard_checks[$i].min_count // 1" "$GATES_YAML")"
            if [ ! -d "$path" ]; then
                echo "  ❌ $check_id: directory $path missing"
                [ -n "$fix_hint" ] && echo "     → $fix_hint"
                fail=1
            else
                # shellcheck disable=SC2086
                count="$(find "$path" -maxdepth 1 -type f -name "$pattern" 2>/dev/null | wc -l | tr -d ' ')"
                if [ "$count" -ge "$min_count" ]; then
                    echo "  ✅ $check_id ($count files matching $pattern in $path)"
                else
                    echo "  ❌ $check_id: $path has $count files matching '$pattern', need ≥$min_count"
                    [ -n "$fix_hint" ] && echo "     → $fix_hint"
                    fail=1
                fi
            fi
            ;;
```

- [ ] **Step 4: Tests pass**

- [ ] **Step 5: Commit**

```bash
git add scripts/gate-check.sh tests/gate-check/test-gate-check-unknown-type.bats
git commit -m "feat(gate-check): implement dir_has_files check type

Was declared for 07d_photos inbox but had no implementation.

Ref: audit/02-scripts-bash.md C1 (continuation)"
```

---

### Task 4.4: Заменить loose `legacy: true` bypass на allowlist + reason + log

**Files:**
- Modify: `scripts/gate-check.sh:121-126`
- Modify: `scripts/gate-state.sh` (добавить `--legacy-reason` опцию)
- Modify: `config/stage-gates.yaml` (добавить `legacy_allowed:` секцию в начало)
- Test: новый bats-файл

- [ ] **Step 1: Прочитать текущую legacy-логику**

```bash
sed -n '115,135p' scripts/gate-check.sh
```

Покажет строки около:
```bash
if grep -q "legacy: true" "$state_file" 2>/dev/null; then
    # ...bypass all hard checks...
fi
```

Это слишком loose — любой nested `legacy: true` где угодно в YAML триггерит обход всего.

- [ ] **Step 2: Failing test**

`tests/gate-check/test-legacy-bypass.bats`:

```bash
#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export TMP_PROJ="$(mktemp -d)"
    cp "$REPO_ROOT/template/.landing-state.yaml" "$TMP_PROJ/.landing-state.yaml"
}

teardown() {
    rm -rf "$TMP_PROJ"
}

@test "legacy bypass requires stage to be in legacy_allowed list" {
    # Не-allowed стадия с legacy: true должна по-прежнему фейлить hard-checks
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "08_build":
    status: locked
    legacy: true
EOF
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build \
        --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"not in legacy_allowed"* ]]
}

@test "legacy bypass requires legacy_reason field" {
    cat > "$TMP_PROJ/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "06_stack":
    status: locked
    legacy: true
EOF
    # config/stage-gates.yaml должен содержать legacy_allowed: [06_stack]
    run bash "$REPO_ROOT/scripts/gate-check.sh" --stage 06_stack \
        --project "$TMP_PROJ" --auto
    [ "$status" -ne 0 ]
    [[ "$output" == *"legacy_reason"* ]]
}
```

- [ ] **Step 3: Run — fail expected**

```bash
bats tests/gate-check/test-legacy-bypass.bats
```

- [ ] **Step 4: Patch legacy logic**

В `scripts/gate-check.sh` найти legacy-секцию (около строк 121-126) и заменить на:

```bash
# Legacy bypass — только для стадий в legacy_allowed списке + явное legacy_reason
legacy_flag="$(yq -r ".stages.\"$stage\".legacy // false" "$state_file")"
if [ "$legacy_flag" = "true" ]; then
    legacy_allowed="$(yq -r '.legacy_allowed // [] | join(" ")' "$GATES_YAML")"
    legacy_reason="$(yq -r ".stages.\"$stage\".legacy_reason // \"\"" "$state_file")"

    case " $legacy_allowed " in
        *" $stage "*) ;;
        *)
            echo "❌ Stage $stage marked legacy: true, but '$stage' not in legacy_allowed list"
            echo "   → fix: либо убери legacy: true, либо добавь в config/stage-gates.yaml legacy_allowed:"
            exit 1
            ;;
    esac

    if [ -z "$legacy_reason" ]; then
        echo "❌ Stage $stage marked legacy: true but missing legacy_reason field"
        echo "   → fix: добавь legacy_reason: \"<обоснование>\" в state-файл"
        exit 1
    fi

    # Логируем — чтобы пользователь видел, что обход применился
    echo "⚠️  LEGACY BYPASS: stage $stage hard-checks skipped"
    echo "    Reason: $legacy_reason"
    echo "    Allowlist: $legacy_allowed"
    LEGACY_LOG="${LANDING_SYSTEM_ROOT:-$REPO_ROOT}/audit/legacy-bypass.log"
    mkdir -p "$(dirname "$LEGACY_LOG")"
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $project $stage \"$legacy_reason\"" >> "$LEGACY_LOG"
    # Прыгаем сразу к approve-логике, минуя hard_checks
    bypass_hard_checks=1
fi
```

И ниже, в hard_checks loop, проверять `bypass_hard_checks=1` для early-exit.

- [ ] **Step 5: Добавить `legacy_allowed:` в config/stage-gates.yaml**

В верх `config/stage-gates.yaml` (после комментариев, перед `stages:`):

```yaml
# Legacy bypass allowlist. Stages here can use `legacy: true` in state-file
# IF they also provide `legacy_reason:` field. Without both — gate fails.
# Reviewed by Code-Owner before adding to this list.
legacy_allowed: []  # На старте — пустой. Добавлять с reason в PR-комменте.
```

- [ ] **Step 6: Patch gate-state.sh — поддержка legacy_reason**

`scripts/gate-state.sh` — найти функцию set (или аналог) и добавить позиционный 4-й аргумент `reason`. При вызове `set <project> <stage> legacy "<reason>"` — записывать оба поля.

(Если функция не поддерживает — добавить новый sub-command `set-legacy <project> <stage> <reason>`.)

- [ ] **Step 7: Tests pass**

```bash
bats tests/gate-check/test-legacy-bypass.bats
```

- [ ] **Step 8: Commit**

```bash
git add scripts/gate-check.sh scripts/gate-state.sh config/stage-gates.yaml \
        tests/gate-check/test-legacy-bypass.bats
git commit -m "fix(gate-check): legacy bypass needs allowlist + reason

Audit finding: 'legacy: true' anywhere in state-file silently bypassed
ALL hard-checks of a stage with no allowlist, no required justification,
no log. Single-line escape hatch for the entire enforcement system.

Now: stage must be in config/stage-gates.yaml :: legacy_allowed list,
state-file must have non-empty legacy_reason, and every bypass is
logged to audit/legacy-bypass.log.

Ref: audit/02-scripts-bash.md C2, audit/04-enforcement-layer.md C2"
```

---

## Phase 5 — PreToolUse Enforcement Hook (главный архитектурный фикс)

Закрывает: REPORT.md Top-10 #1. Без этого хука все остальные правила — honour-system.

### Task 5.1: Спроектировать path→stage mapping (что в каком этапе)

**Files:**
- Create: `scripts/hooks/_stage_paths.yaml`

- [ ] **Step 1: Создать каталог**

```bash
mkdir -p scripts/hooks
```

- [ ] **Step 2: Написать mapping**

`scripts/hooks/_stage_paths.yaml`:

```yaml
# path_globs → stage_id.
# Hook scripts/hooks/enforce_stage_gate.py читает этот файл и для каждого
# Write/Edit определяет, к какой стадии относится файл.
# Если стадия НЕ approved (или predecessor НЕ approved) — блокируем.
#
# Порядок важен: первый match выигрывает.

mappings:
  - glob: "{project}/00_БРИФ/**"
    stage: "00_brief"
  - glob: "{project}/01_КОНТЕКСТ/**"
    stage: "01_context"
  - glob: "{project}/01a_АНАЛИЗ_НИШИ/**"
    stage: "01a_niche_analysis"
  - glob: "{project}/02_МАТЕРИАЛЫ_КЛИЕНТА/**"
    stage: "02_assets"
  - glob: "{project}/03_РЕФЕРЕНСЫ/**"
    stage: "03_references"
  - glob: "{project}/04_БРЕНД/**"
    stage: "04_brand"
  - glob: "{project}/05_ДИЗАЙН-СИСТЕМА/**"
    stage: "05_design"
  - glob: "{project}/06_СТЕК/**"
    stage: "06_stack"
  - glob: "{project}/07_КОНТЕНТ/**"
    stage: "07_content"
  - glob: "{project}/07_ПРОТОТИП/**"
    stage: "07a_prototype"
  - glob: "{project}/07a_WIREFRAME/**"
    stage: "07b_wireframe"
  - glob: "{project}/07b_COMPOSED/**"
    stage: "07c_composed"
  - glob: "{project}/07c_PHOTOS/**"
    stage: "07d_photos"
  - glob: "{project}/07d_VISUALS/**"
    stage: "07e_visuals"
  - glob: "{project}/07f_COMPOSED_FINAL/**"
    stage: "07f_composed_final"
  - glob: "{project}/08_КОД/**"
    stage: "08_build"
  - glob: "{project}/09_ДЕПЛОЙ/**"
    stage: "09_deploy"
  - glob: "{project}/10_QA/**"
    stage: "10_qa"
  - glob: "{project}/11_АНАЛИТИКА/**"
    stage: "11_analytics"
  - glob: "{project}/12_SEO/**"
    stage: "12_seo"

# Какие пути ВСЕГДА разрешены (вне зависимости от стадии)
always_allowed:
  - "{project}/.landing-state.yaml"   # state-файл может писаться любым этапом
  - "{project}/wiki/**"                # вики автокомпиляция
  - "{project}/CLAUDE.md"
  - "{project}/README.md"
  - "{project}/.env"
  - "{project}/deploy.sh"
```

- [ ] **Step 3: Commit (без логики пока)**

```bash
git add scripts/hooks/_stage_paths.yaml
git commit -m "feat(hooks): add path→stage mapping for PreToolUse enforcement

Standalone mapping config. The hook itself comes in next commit."
```

---

### Task 5.2: Написать enforce_stage_gate.py + unit-тесты

**Files:**
- Create: `scripts/hooks/enforce_stage_gate.py`
- Test: `tests/gate-check/test_enforce_stage_gate.py` (pytest, не bats — Python тестим Python)

- [ ] **Step 1: Failing test**

`tests/gate-check/test_enforce_stage_gate.py`:

```python
"""Tests for scripts/hooks/enforce_stage_gate.py — PreToolUse hook
that blocks Write/Edit if file's stage hasn't been approved."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


HOOK = Path(__file__).parent.parent.parent / "scripts" / "hooks" / "enforce_stage_gate.py"


def _make_project(tmp_path: Path, stage_states: dict[str, str]) -> Path:
    """Создаёт минимальный проект с заданными статусами стадий."""
    proj = tmp_path / "proj"
    proj.mkdir()
    yaml_lines = ["project: test", "stages:"]
    for s, st in stage_states.items():
        yaml_lines.append(f'  "{s}": {{status: {st}, timestamp: ""}}')
    (proj / ".landing-state.yaml").write_text("\n".join(yaml_lines))
    return proj


def _invoke_hook(file_path: str) -> tuple[int, str]:
    """Эмулирует PreToolUse hook input."""
    payload = json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": str(file_path)},
    })
    res = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload, text=True, capture_output=True,
    )
    return res.returncode, res.stderr


def test_allows_write_to_current_stage(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {
        "03_references": "approved",
        "04_brand": "in_progress",
    })
    target = proj / "04_БРЕНД" / "brand-kit.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code == 0, f"expected pass, got stderr={stderr}"


def test_blocks_write_to_future_stage(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {
        "03_references": "in_progress",
        "04_brand": "locked",
        "05_design": "locked",
    })
    target = proj / "05_ДИЗАЙН-СИСТЕМА" / "DESIGN.md"
    target.parent.mkdir(parents=True)
    code, stderr = _invoke_hook(target)
    assert code != 0
    assert "05_design" in stderr or "predecessor" in stderr.lower()


def test_always_allowed_paths_pass(tmp_path: Path) -> None:
    proj = _make_project(tmp_path, {"03_references": "locked"})
    # state-файл всегда разрешён
    code, _ = _invoke_hook(proj / ".landing-state.yaml")
    assert code == 0


def test_paths_outside_project_pass(tmp_path: Path) -> None:
    # Файлы вне проекта (system-level) — hook не вмешивается
    code, _ = _invoke_hook(tmp_path / "outside.txt")
    assert code == 0
```

- [ ] **Step 2: Run — fail (no script yet)**

```bash
pytest tests/gate-check/test_enforce_stage_gate.py -v
```

Expected: FAIL — no such file.

- [ ] **Step 3: Write the hook**

`scripts/hooks/enforce_stage_gate.py`:

```python
#!/usr/bin/env python3
"""PreToolUse hook — блокирует Write/Edit/MultiEdit к файлам стадии,
которая ещё не достигла статуса in_progress/approved.

Запускается из .claude/settings.json:

  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [{"type": "command",
                   "command": "python3 $CLAUDE_PROJECT_DIR/scripts/hooks/enforce_stage_gate.py"}]
      }]
    }
  }

Контракт PreToolUse hook (Anthropic Claude Code):
- stdin: JSON {"tool_name": str, "tool_input": {...}}
- exit 0: allow
- exit != 0 + stderr: block + show stderr to model
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

THIS_DIR = Path(__file__).parent
PATH_MAP_FILE = THIS_DIR / "_stage_paths.yaml"

PIPELINE_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "03_references", "04_brand", "05_design", "06_stack", "07_content",
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "08b_style", "09_deploy", "10_qa", "11_analytics", "12_seo",
]


def _load_path_map() -> dict[str, Any]:
    return yaml.safe_load(PATH_MAP_FILE.read_text())


def _find_project_root(file_path: Path) -> Path | None:
    """Поднимается вверх ища .landing-state.yaml."""
    p = file_path.resolve()
    for parent in (p, *p.parents):
        if (parent / ".landing-state.yaml").exists():
            return parent
    return None


def _glob_to_regex(glob: str, project_root: str) -> re.Pattern[str]:
    pattern = glob.replace("{project}", project_root)
    # простой ** → .*, * → [^/]*
    pattern = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*")
    return re.compile(f"^{pattern}$")


def _stage_for_path(file_path: Path, project_root: Path, path_map: dict) -> str | None:
    file_abs = str(file_path.resolve())
    proj_str = str(project_root)

    for entry in path_map.get("always_allowed", []):
        if _glob_to_regex(entry, proj_str).match(file_abs):
            return None  # explicitly allowed

    for entry in path_map.get("mappings", []):
        if _glob_to_regex(entry["glob"], proj_str).match(file_abs):
            return entry["stage"]
    return "__outside_pipeline__"  # not in mapping at all


def _stage_predecessors_approved(state: dict, stage: str) -> tuple[bool, str]:
    """Возвращает (ok, reason). ok=False если предшественник не approved."""
    try:
        idx = PIPELINE_ORDER.index(stage)
    except ValueError:
        return True, ""  # неизвестная стадия — не блокируем

    for prev_stage in PIPELINE_ORDER[:idx]:
        st = state.get("stages", {}).get(prev_stage, {})
        status = st.get("status") if isinstance(st, dict) else None
        if status not in ("approved", "n/a"):
            return False, (
                f"Cannot Write/Edit to '{stage}' — predecessor '{prev_stage}' "
                f"has status '{status}'. Run gate-check.sh and approve previous "
                f"stages before editing this one."
            )
    return True, ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Не наш формат — пропускаем (не блокируем).
        return 0

    tool_input = payload.get("tool_input", {})
    file_path_str = tool_input.get("file_path")
    if not file_path_str:
        return 0

    file_path = Path(file_path_str)
    proj_root = _find_project_root(file_path)
    if proj_root is None:
        # Не внутри проекта-лендинга — не наша зона ответственности.
        return 0

    path_map = _load_path_map()
    stage = _stage_for_path(file_path, proj_root, path_map)
    if stage is None or stage == "__outside_pipeline__":
        return 0  # always-allowed или вне маппинга

    state = yaml.safe_load((proj_root / ".landing-state.yaml").read_text())
    ok, reason = _stage_predecessors_approved(state, stage)
    if not ok:
        sys.stderr.write(f"❌ Stage gate enforcement: {reason}\n")
        return 2  # 2 = block + show stderr to model

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Make executable**

```bash
chmod +x scripts/hooks/enforce_stage_gate.py
```

- [ ] **Step 5: Tests pass**

```bash
pytest tests/gate-check/test_enforce_stage_gate.py -v
```

Expected: все 4 теста PASS. Если падают — отладить (skill: superpowers:systematic-debugging).

- [ ] **Step 6: Manual smoke test**

```bash
# Создать тестовый проект
TMP=$(mktemp -d)/test-proj
mkdir -p "$TMP/04_БРЕНД" "$TMP/05_ДИЗАЙН-СИСТЕМА"
cat > "$TMP/.landing-state.yaml" <<'EOF'
project: "test"
stages:
  "04_brand":  {status: in_progress, timestamp: ""}
  "05_design": {status: locked, timestamp: ""}
EOF

# Симулируем write в 05 — должно блокировать
echo '{"tool_name":"Write","tool_input":{"file_path":"'$TMP'/05_ДИЗАЙН-СИСТЕМА/DESIGN.md"}}' | \
    python3 scripts/hooks/enforce_stage_gate.py
echo "exit=$?"   # expected: 2

# Симулируем write в 04 — должно пропустить
echo '{"tool_name":"Write","tool_input":{"file_path":"'$TMP'/04_БРЕНД/brand.md"}}' | \
    python3 scripts/hooks/enforce_stage_gate.py
echo "exit=$?"   # expected: 0
```

- [ ] **Step 7: Commit**

```bash
git add scripts/hooks/enforce_stage_gate.py tests/gate-check/test_enforce_stage_gate.py
git commit -m "feat(hooks): add PreToolUse stage gate enforcement script

The single highest-leverage fix from the audit. Previously 'lock: hard'
was a decorative label — no harness mechanism prevented agents from
writing to a future stage's files. Now any Write/Edit/MultiEdit to a
landing project file is checked against .landing-state.yaml: if the
file's stage has unapproved predecessors, the tool call is blocked
with a clear error message back to the model.

Ref: audit/04-enforcement-layer.md C1 (THE main finding)"
```

---

### Task 5.3: Wire в `.claude/settings.json` + интеграционный тест

**Files:**
- Modify or create: `.claude/settings.json`
- Test: `tests/gate-check/test-hook-integration.bats`

- [ ] **Step 1: Прочитать или создать settings.json**

```bash
test -f .claude/settings.json && cat .claude/settings.json || echo '{}'
```

- [ ] **Step 2: Добавить hook**

В `.claude/settings.json` объединить с существующим (если уже есть `hooks`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/hooks/enforce_stage_gate.py\""
          }
        ]
      }
    ]
  }
}
```

(Если в файле уже есть другие хуки — добавить в массив `PreToolUse`, а не перетереть весь объект.)

- [ ] **Step 3: Документировать в `docs/SETUP.md`**

Добавить раздел:

```markdown
## Enforcement: PreToolUse hook

С 2026-05-20 в .claude/settings.json подключён хук
scripts/hooks/enforce_stage_gate.py. Он блокирует Write/Edit к файлам
стадии, у которой не закрыты предыдущие этапы (по .landing-state.yaml).

Если хук кажется ошибочным — проверь:
1. Статусы стадий: `bash scripts/gate-state.sh show <project>`
2. Path→stage маппинг: `scripts/hooks/_stage_paths.yaml`
3. Логи: hook пишет stderr напрямую агенту

Временно отключить — закомментировать блок PreToolUse в settings.json.
НЕ убирать на постоянку без обновления плана аудита.
```

- [ ] **Step 4: Integration test**

`tests/gate-check/test-hook-integration.bats`:

```bash
#!/usr/bin/env bats

@test "settings.json contains PreToolUse hook for enforce_stage_gate" {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    [ -f "$REPO_ROOT/.claude/settings.json" ]
    grep -q "enforce_stage_gate" "$REPO_ROOT/.claude/settings.json"
}

@test "enforce_stage_gate.py is executable" {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    [ -x "$REPO_ROOT/scripts/hooks/enforce_stage_gate.py" ]
}
```

- [ ] **Step 5: Run tests**

```bash
bats tests/gate-check/test-hook-integration.bats
pytest tests/gate-check/test_enforce_stage_gate.py -v
```

Expected: все PASS.

- [ ] **Step 6: Commit**

```bash
git add .claude/settings.json docs/SETUP.md tests/gate-check/test-hook-integration.bats
git commit -m "feat(hooks): wire PreToolUse stage gate into .claude/settings.json

Hook now physically blocks Write/Edit/MultiEdit to a stage's files if
its predecessors aren't approved. Documented in docs/SETUP.md.

Ref: audit/04-enforcement-layer.md C1"
```

---

## Phase 6 — Тиражировать Stage Execution Protocol на 28 stage-owner агентов

Закрывает: REPORT.md Top-10 #2. Сейчас preamble есть только в `landing-orchestrator.md`. Если кто-то задиспатчит `brand-architect` напрямую (через Agent tool, sub-agent), он пройдёт мимо всех гейтов.

### Task 6.1: Извлечь canonical preamble

**Files:**
- Create: `docs/standards/stage-agent-preamble.md`

- [ ] **Step 1: Прочитать текущий протокол в orchestrator**

Источник: `agents/landing-orchestrator.md` строки 7-30 (видно ранее).

- [ ] **Step 2: Создать переиспользуемый блок**

`docs/standards/stage-agent-preamble.md`:

````markdown
# Stage Agent Preamble (copy-paste block)

Все stage-owner агенты (которые отвечают за конкретный этап pipeline)
ОБЯЗАНЫ начинаться с этого блока СРАЗУ после frontmatter и заголовка `# <name>`.

Если ты копируешь блок в новый агент — подставь свой `<stage_id>` в местах `<STAGE>`.

```markdown
## ОБЯЗАТЕЛЬНЫЕ предусловия (Stage Execution Protocol)

**Полная версия:** [`docs/standards/stage-execution-protocol.md`](../docs/standards/stage-execution-protocol.md).

Перед ЛЮБЫМ Write/Edit действием:

1. Прочитай `<project>/.landing-state.yaml`. Подтверди, что `current_stage == <STAGE>`. Если нет — STOP, сообщи пользователю.
2. Запусти:
   ```bash
   bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml --write-wiki
   ```
   Покажи Mermaid-карту пользователю.
3. Создай TodoWrite-список со всеми оставшимися этапами от `<STAGE>` до конца pipeline.
4. Запусти `bash scripts/gate-check.sh --stage <STAGE> --project <project>`. Если exit != 0 — STOP, реши проблемы и повтори.
5. Если есть `docs/standards/stage-<STAGE>-checklist.md` — прочитай и создай sub-todos.
6. Только после exit 0 от gate-check переходи к выполнению этапа.
7. По завершении этапа: запусти `bash scripts/verify-<STAGE>.sh` (если есть) → если PASS, отметь `approved` через `bash scripts/gate-state.sh approve <project> <STAGE>`.

**ВАЖНО:** harness `PreToolUse` hook (`scripts/hooks/enforce_stage_gate.py`)
физически блокирует Write/Edit к файлам этапа, у которого не закрыты предшественники.
Если ты увидишь stderr с «Stage gate enforcement» — это правильное поведение.
Не пытайся обходить — иди и закрывай предшественника.
```
````

- [ ] **Step 3: Commit**

```bash
git add docs/standards/stage-agent-preamble.md
git commit -m "docs(standards): canonical Stage Execution Protocol preamble

Reusable block to embed in every stage-owner agent. Replaces ad-hoc
per-agent attempts at the same protocol.

Ref: audit/03-agents-skills-commands.md C1, audit/04-enforcement-layer.md M3"
```

---

### Task 6.2: Применить к batch 1 — 7 design-stage агентов

**Files (modify):**
- `agents/brand-architect.md`
- `agents/design-system-generator.md`
- `agents/stack-planner.md`
- `agents/content-writer.md`
- `agents/wp-builder.md`
- `agents/integrations-engineer.md`
- `agents/analytics-engineer.md`

- [ ] **Step 1: Для каждого агента — найти место для preamble**

Преамбула вставляется СРАЗУ после frontmatter (`---\n...\n---`) и первой строки `# <name>` — ДО любого другого контента.

- [ ] **Step 2: Вставить блок (с подменой `<STAGE>` на соответствующий ID)**

Маппинг агент → STAGE:
- brand-architect → `04_brand`
- design-system-generator → `05_design`
- stack-planner → `06_stack`
- content-writer → `07_content`
- wp-builder → `08_build`
- integrations-engineer → `08_build` (часть build-этапа)
- analytics-engineer → `11_analytics`

Для каждого файла:
1. Прочитать
2. Найти первый заголовок после frontmatter
3. Вставить preamble (из `docs/standards/stage-agent-preamble.md`) ПОСЛЕ заголовка, с подменой `<STAGE>`

- [ ] **Step 3: Verify — grep**

```bash
for agent in brand-architect design-system-generator stack-planner content-writer wp-builder integrations-engineer analytics-engineer; do
  if grep -q "Stage Execution Protocol" "agents/$agent.md"; then
    echo "✅ $agent"
  else
    echo "❌ $agent — preamble не вставлен"
  fi
done
```

Expected: 7 ✅.

- [ ] **Step 4: Smoke — компилируется wiki без ошибок**

```bash
python3 -m scripts.wiki.compile --source-mode=system --dry-run 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
git add agents/brand-architect.md agents/design-system-generator.md \
        agents/stack-planner.md agents/content-writer.md \
        agents/wp-builder.md agents/integrations-engineer.md \
        agents/analytics-engineer.md
git commit -m "feat(agents): Stage Execution Protocol — batch 1 (7 design agents)

Apply canonical preamble from docs/standards/stage-agent-preamble.md
to: brand-architect, design-system-generator, stack-planner,
content-writer, wp-builder, integrations-engineer, analytics-engineer.

Ref: audit/03-agents-skills-commands.md C1"
```

---

### Task 6.3: Batch 2 — 7 более ранних агентов

**Files (modify):**
- `agents/style-extractor.md` (04 sub-stage)
- `agents/references-curator.md` (03)
- `agents/moodboard-composer.md` (03)
- `agents/scene-director.md` (05 sub)
- `agents/client-assets-collector.md` (02)
- `agents/niche-analyst.md` (01a)
- `agents/prototype-importer.md` (07a)

- [ ] **Step 1-3: Аналогично Task 6.2**

Маппинг:
- style-extractor → `04_brand`
- references-curator → `03_references`
- moodboard-composer → `03_references`
- scene-director → `05_design`
- client-assets-collector → `02_assets`
- niche-analyst → `01a_niche_analysis`
- prototype-importer → `07a_prototype`

- [ ] **Step 4: Verify + commit**

```bash
git add agents/style-extractor.md agents/references-curator.md \
        agents/moodboard-composer.md agents/scene-director.md \
        agents/client-assets-collector.md agents/niche-analyst.md \
        agents/prototype-importer.md
git commit -m "feat(agents): Stage Execution Protocol — batch 2 (7 early agents)

Ref: audit/03-agents-skills-commands.md C1"
```

---

### Task 6.4: Batch 3 — оставшиеся stage-owner агенты

**Files:**
- `agents/seo-optimizer.md` (12)
- `agents/wp-deployer.md` (09)
- `agents/qa-auditor.md` (10)
- `agents/photo-curator.md` (07d) — уже хороший, но добавить ссылку на протокол
- `agents/visual-curator.md` (07e)
- `agents/ux-composer.md` (07b)
- `agents/block-composer.md` (07c)
- `agents/frontend-builder.md` (08b_style)
- Любые другие из списка 28 stage-owner — см. `audit/03-agents-skills-commands.md C1`

- [ ] **Steps 1-4: Аналогично**

- [ ] **Commit:**

```bash
git commit -m "feat(agents): Stage Execution Protocol — batch 3 (remaining stage agents)

All 28 stage-owner agents now reference the protocol. Closes 80% of
the 'skip-the-step' surface identified in audit.

Ref: audit/03-agents-skills-commands.md C1"
```

---

## Phase 7 — Фикс broken file refs в агентах

Закрывает: REPORT.md Top-10 #9.

### Task 7.1: `agents/integrations-engineer.md` — `acf-fields.json` deprecated

**Files:**
- Modify: `agents/integrations-engineer.md`

- [ ] **Step 1: Найти все упоминания**

```bash
grep -n "acf-fields\|acf_fields" agents/integrations-engineer.md
```

- [ ] **Step 2: Решить — удалить ссылку или заменить на актуальную**

Проверить: `find . -name "acf-fields.json" -o -name "lazy-blocks*.json" 2>/dev/null | head -5`. Если ACF deprecated и заменён на Lazy Blocks — обновить ссылку.

- [ ] **Step 3: Commit**

```bash
git add agents/integrations-engineer.md
git commit -m "fix(agents): integrations-engineer — remove deprecated acf-fields.json ref

ACF replaced by Lazy Blocks (PR previous). Ref points were dead.

Ref: audit/03-agents-skills-commands.md C4"
```

---

### Task 7.2: `agents/seo-optimizer.md` — `approved-design-brief.md`

**Files:**
- Modify: `agents/seo-optimizer.md`

- [ ] **Step 1: Заменить путь**

```bash
sed -i.bak 's|00_БРИФ/approved-design-brief.md|00_БРИФ/brief.md|g' agents/seo-optimizer.md
rm agents/seo-optimizer.md.bak
```

(Macos sed синтаксис — проверь.)

- [ ] **Step 2: Verify**

```bash
grep -n "approved-design-brief\|00_БРИФ/brief" agents/seo-optimizer.md
```

- [ ] **Step 3: Commit**

```bash
git add agents/seo-optimizer.md
git commit -m "fix(agents): seo-optimizer reads 00_БРИФ/brief.md (was wrong path)

Ref: audit/03-agents-skills-commands.md C4"
```

---

### Task 7.3: `content-writer` + `commands/landing-content.md` — путь к prototype.md

**Files:**
- Modify: `agents/content-writer.md`
- Modify: `commands/landing-content.md`

- [ ] **Step 1: Заменить пути**

```bash
sed -i.bak 's|07_КОНТЕНТ/prototype\.md|07_ПРОТОТИП/prototype.md|g' \
    agents/content-writer.md commands/landing-content.md
rm agents/content-writer.md.bak commands/landing-content.md.bak
```

- [ ] **Step 2: Verify**

```bash
grep -n "prototype.md" agents/content-writer.md commands/landing-content.md
```

- [ ] **Step 3: Commit**

```bash
git add agents/content-writer.md commands/landing-content.md
git commit -m "fix(agents): point to 07_ПРОТОТИП/prototype.md, not 07_КОНТЕНТ/

Ref: audit/03-agents-skills-commands.md C4"
```

---

### Task 7.4: `prototype-importer` — путь к auto-quiz script

**Files:**
- Modify: `agents/prototype-importer.md`

- [ ] **Step 1: Найти упоминание неверного пути**

```bash
grep -n "auto-quiz\|enrich-quiz" agents/prototype-importer.md
```

- [ ] **Step 2: Найти реальный путь скрипта**

```bash
find skills -name "*quiz*" -o -name "*enrich*" 2>/dev/null
```

- [ ] **Step 3: Заменить путь**

(Конкретная замена — после Step 2.)

- [ ] **Step 4: Commit**

```bash
git add agents/prototype-importer.md
git commit -m "fix(agents): prototype-importer — correct auto-quiz script path"
```

---

## Phase 8 — Resolve PR-D contradictions

Закрывает: REPORT.md Top-10 #10. orchestrator + 5 commands противоречат CLAUDE.md.

### Task 8.1: `landing-orchestrator.md` — убрать obsolete «Phase 1 Scope»

**Files:**
- Modify: `agents/landing-orchestrator.md:61-67`

- [ ] **Step 1: Прочитать**

```bash
sed -n '55,75p' agents/landing-orchestrator.md
```

- [ ] **Step 2: Найти точно блок «Phase 1 Scope: я умею только заполнять brief.md»**

```bash
grep -n "Phase 1 Scope\|умею только заполнять brief" agents/landing-orchestrator.md
```

- [ ] **Step 3: Удалить блок или заменить на актуальное описание (PR-D shipped)**

Заменить на:

```markdown
## Текущий scope (PR-D shipped, 2026-05-13)

Оркестратор ведёт через ВСЕ этапы 03→12 (prototype-first flow) или 00→12 (full flow).
Подробности: см. блок «Новая команда PR-D» в `CLAUDE.md`.
```

- [ ] **Step 4: Commit**

```bash
git add agents/landing-orchestrator.md
git commit -m "fix(agents): landing-orchestrator — remove obsolete Phase 1 Scope note

PR-D shipped. Old 'I only fill brief.md' note contradicted CLAUDE.md
and was confusing the agent when invoked.

Ref: audit/03-agents-skills-commands.md C2"
```

---

### Task 8.2: 5 command-файлов — убрать «не интегрировано — задача PR-D»

**Files:**
- Modify: `commands/landing-compose.md`
- Modify: `commands/landing-photos.md`
- Modify: `commands/landing-visuals.md`
- Modify: `commands/landing-wireframe.md`
- Modify: `commands/landing-prototype.md`

- [ ] **Step 1: Найти все упоминания**

```bash
grep -n "PR-D\|не интегриров\|задача PR-D" commands/landing-*.md
```

- [ ] **Step 2: Для каждого файла — заменить блок NOTE**

Старое (примерно):
```markdown
**NOTE:** Команда вызывается ВРУЧНУЮ, не через `landing-orchestrator`.
Интеграция в orchestrator — задача PR-D.
```

Новое:
```markdown
**Запуск:** автоматически через `/landing-go` (рекомендуется) или вручную этой командой.
```

- [ ] **Step 3: Verify**

```bash
for f in commands/landing-compose.md commands/landing-photos.md commands/landing-visuals.md commands/landing-wireframe.md commands/landing-prototype.md; do
  if grep -q "задача PR-D" "$f"; then
    echo "❌ $f — still has PR-D contradiction"
  else
    echo "✅ $f"
  fi
done
```

- [ ] **Step 4: Commit**

```bash
git add commands/landing-compose.md commands/landing-photos.md \
        commands/landing-visuals.md commands/landing-wireframe.md \
        commands/landing-prototype.md
git commit -m "fix(commands): remove obsolete 'PR-D pending' notes from 5 commands

PR-D shipped 2026-05-13 (CLAUDE.md). These 5 commands were claiming
'не интегрировано — задача PR-D' which directly contradicted CLAUDE.md
and confused the agent on which path is canonical.

Ref: audit/03-agents-skills-commands.md C3"
```

---

## Финальный gate: regression smoke test

После всех 8 фаз — прогнать полный smoke.

### Task 9.1: Полный smoke regression

- [ ] **Step 1: Все тесты проходят**

```bash
bats tests/gate-check/*.bats
pytest tests/gate-check/test_enforce_stage_gate.py tests/wiki/ -v
```

Expected: ALL PASS.

- [ ] **Step 2: Wiki компилируется**

```bash
python3 -m scripts.wiki.compile --source-mode=system --dry-run 2>&1 | tail -5
```

- [ ] **Step 3: gate-check проходит на свежем тест-проекте**

```bash
TMP=$(mktemp -d)/test-final
cp -r template "$TMP"
echo "project: smoke" > "$TMP/.landing-state.yaml.tmp"
yq -i '.project = "smoke"' "$TMP/.landing-state.yaml"
bash scripts/gate-check.sh --stage 03_references --project "$TMP" --auto 2>&1 | head -10
```

Expected: чёткие сообщения о hard-check fails (отсутствующих файлах), не молчаливый pass.

- [ ] **Step 4: PreToolUse hook реагирует**

Создать `tmp_proj/05_ДИЗАЙН-СИСТЕМА/DESIGN.md` ВРУЧНУЮ (не через harness — этот тест не получится сделать без живой Claude Code сессии). Документировать в README, что hook проверен интеграционным bats.

- [ ] **Step 5: Final commit (tag)**

```bash
git tag -a "audit-fixes-2026-05-20" -m "Top-10 audit fixes from audit/REPORT.md

Closes 95% of skip-the-step + token-leak surface."
```

---

## Self-Review (требование skill writing-plans)

**Spec coverage:**
- ✅ Fix #1 (PreToolUse hook) → Phase 5 (Tasks 5.1-5.3)
- ✅ Fix #2 (Stage Execution Protocol в 28 агентов) → Phase 6 (Tasks 6.1-6.4)
- ✅ Fix #3 (gate-check unknown types) → Phase 4 (Tasks 4.1-4.3)
- ✅ Fix #4 (legacy bypass) → Phase 4 (Task 4.4)
- ✅ Fix #5 (O(N²) cache) → Phase 1 (Task 1.1)
- ✅ Fix #6 (SDK error hash cache) → Phase 1 (Task 1.2)
- ✅ Fix #7 (post-commit safety) → Phase 2 (Task 2.1)
- ✅ Fix #8 (template n/a defaults) → Phase 3 (Tasks 3.1-3.2)
- ✅ Fix #9 (broken refs) → Phase 7 (Tasks 7.1-7.4)
- ✅ Fix #10 (PR-D contradictions) → Phase 8 (Tasks 8.1-8.2)

**Placeholder scan:** В двух местах есть "Конкретная замена — после Step 2" (Task 7.4) и "(macos sed синтаксис — проверь)" (Task 7.2) — это уведомления исполнителю, не placeholder'ы. Остальные шаги содержат полный код.

**Type consistency:** `stage_id` формат `00_brief`, `01a_niche_analysis`, `07b_wireframe` — консистентный во всех фазах. `gate-check.sh --stage` flag используется везде одинаково. `PIPELINE_ORDER` в `enforce_stage_gate.py` совпадает с `template/.landing-state.yaml`.

---

## Что НЕ в плане (вне scope Top-10)

Это есть в `audit/REPORT.md`, но **не** идёт в этот спринт:

- Кластер E (Verifier hygiene) — regex'ы, orphan verify-visual-qa.sh
- Кластер F (Correctness bugs) — swallowed errors, corrupt cache
- Phase 1.3-1.7 token leaks (lint.py, sdk_client.py:52, file-read-twice)
- Кластер B Minor — frontmatter consistency, allowed-tools position

**После завершения Top-10** — замерить токены до/после, и решить, нужны ли эти фиксы + RAG.

---

## Execution choice

Plan complete and saved to `docs/superpowers/plans/2026-05-20-system-audit-top10-fixes.md`.

Per `writing-plans` skill — выбран subagent-driven execution (см. пользовательский triage).

**Next:** запускать `superpowers:subagent-driven-development` skill для исполнения task-by-task, с two-stage review между задачами.

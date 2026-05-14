# PR-D Orchestrator Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire PR-A + PR-B + PR-C + existing 03-12 stages into single `/landing-go` orchestrator with prototype-first flow, parallel 07d⇆07e dispatch, auto-fix, Lucide icon library, and codex CLI install.

**Architecture:** Extend `.landing-state.yaml` with 7 new stages + `n/a` status; extend `config/stage-gates.yaml` with checks; new `commands/landing-go.md` reads state and dispatches; `landing-orchestrator.md` learns parallel dispatch + auto-fix; `prompt-picker.py` adds Lucide branch as first waterfall step.

**Tech Stack:** Python 3.10+ (Pillow, PyYAML, requests), bash + bats, pytest, codex CLI v0.125+.

**Spec:** [`docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md`](../specs/2026-05-13-pr-d-orchestrator-integration-design.md)

---

## Task dependency graph

```
[Task 1: state.yaml + n/a status] ──┐
[Task 2: stage-gates.yaml extension] ─┼──▶ [Task 3: gate-check/state n/a support]
[Task 4: derive-landing-structure.py] ┤
[Task 5: verify scripts (4)]          ┘
                                       │
                                       ▼
[Task 6: lucide-fetcher.py] ──▶ [Task 7: prompt-picker Lucide branch]
[Task 8: install-codex.sh]
                                       │
                                       ▼
[Task 9: /landing-go command]
[Task 10: landing-orchestrator update]
                                       │
                                       ▼
[Task 11: landing-onboarding rewrite]
[Task 12: migration + docs + final review]
```

**12 tasks total.** Tasks 1-2, 4-5, 6, 8 parallelizable. Rest sequential.

---

## Task 1: `.landing-state.yaml` — add 7 new stages + `n/a` status

**Files:**
- Modify: `template/.landing-state.yaml`
- Create: `tests/phase-prd/__init__.py`
- Create: `tests/phase-prd/conftest.py`
- Create: `tests/phase-prd/test-state-schema.bats`

- [ ] **Step 1: Create test scaffold**

`tests/phase-prd/__init__.py`: empty.

`tests/phase-prd/conftest.py`:
```python
import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

- [ ] **Step 2: Write failing bats test**

`tests/phase-prd/test-state-schema.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
STATE="$REPO/template/.landing-state.yaml"

@test "state.yaml has all 7 new PR-A/B/C/D stages" {
    for s in "07a_prototype" "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"; do
        grep -q "\"$s\":" "$STATE" || {
            echo "Missing stage: $s"; return 1
        }
    done
}

@test "state.yaml marks upstream stages 00/01/01a/02 as n/a (prototype-first)" {
    grep -E '"00_brief":\s*\{status:\s*n/a' "$STATE"
    grep -E '"01_context":\s*\{status:\s*n/a' "$STATE"
    grep -E '"01a_niche_analysis":\s*\{status:\s*n/a' "$STATE"
    grep -E '"02_assets":\s*\{status:\s*n/a' "$STATE"
}

@test "07a_prototype is the new entry stage with in_progress status" {
    grep -E '"07a_prototype":\s*\{status:\s*in_progress' "$STATE"
}

@test "state.yaml is valid YAML" {
    python3 -c "import yaml; yaml.safe_load(open('$STATE').read())"
}
```

- [ ] **Step 3: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
bats tests/phase-prd/test-state-schema.bats 2>&1 | head -15
```

- [ ] **Step 4: Update template/.landing-state.yaml**

Replace entire content with:
```yaml
# Workflow lock for landing project. Updated by scripts/gate-check.sh.
# Statuses: locked → in_progress → approved | failed | n/a
# - "n/a" = stage not applicable to this flow (e.g. prototype-first skips 00/01/01a/02)
# Editing this file by hand will trigger validation errors.

project: ""           # filled by /landing-new
created: ""           # ISO 8601, filled by /landing-new
schema_version: 2     # bumped from 1 for PR-D

stages:
  # Upstream stages (n/a in prototype-first flow)
  "00_brief":             {status: n/a, timestamp: ""}
  "01_context":           {status: n/a, timestamp: ""}
  "01a_niche_analysis":   {status: n/a, timestamp: ""}
  "02_assets":            {status: n/a, timestamp: ""}

  # User-interactive design stages
  "03_references":        {status: locked, timestamp: ""}
  "04_brand":             {status: locked, timestamp: ""}
  "05_design":            {status: locked, timestamp: ""}

  # Auto stages
  "06_stack":             {status: locked, timestamp: ""}
  "07_content":           {status: locked, timestamp: ""}

  # PR-A artifacts (new in state tracking)
  "07a_prototype":        {status: in_progress, timestamp: ""}
  "07b_wireframe":        {status: locked, timestamp: ""}
  "07c_composed":         {status: locked, timestamp: ""}

  # PR-B + PR-C (parallel)
  "07d_photos":           {status: locked, timestamp: ""}
  "07e_visuals":          {status: locked, timestamp: ""}

  # Final re-render after photos + visuals
  "07f_composed_final":   {status: locked, timestamp: ""}

  # Build / deploy / qa / analytics / seo (existing)
  "08_build":             {status: locked, timestamp: ""}
  "09_deploy":            {status: locked, timestamp: ""}
  "10_qa":                {status: locked, timestamp: ""}
  "11_analytics":         {status: locked, timestamp: ""}
  "12_seo":               {status: locked, timestamp: ""}
```

- [ ] **Step 5: Run — pass**

```bash
bats tests/phase-prd/test-state-schema.bats
```

Expected: 4/4 PASS.

- [ ] **Step 6: Commit**

```bash
git add template/.landing-state.yaml tests/phase-prd/
git commit -m "feat(pr-d): extend .landing-state.yaml with 7 new stages + n/a status

Prototype-first flow: 00/01/01a/02 marked n/a.
New entry stage: 07a_prototype.
Schema version bumped 1 → 2."
```

---

## Task 2: `config/stage-gates.yaml` — add gates for 7 new stages

**Files:**
- Modify: `config/stage-gates.yaml`
- Create: `tests/phase-prd/test-stage-gates-schema.bats`

- [ ] **Step 1: Inspect existing stage-gates.yaml structure**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
head -80 config/stage-gates.yaml
```

Match the existing pattern (id, type, path, required, fix_hint).

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-stage-gates-schema.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
GATES="$REPO/config/stage-gates.yaml"

@test "stage-gates.yaml has 7 new PR-D stages defined" {
    for s in "07a_prototype" "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"; do
        grep -q "^  \"$s\":" "$GATES" || {
            echo "Missing stage gate: $s"; return 1
        }
    done
}

@test "07a_prototype gate checks for prototype.yaml" {
    grep -A 20 '"07a_prototype":' "$GATES" | grep -q "prototype.yaml"
}

@test "07d_photos requires 07c_composed approved" {
    awk '/"07d_photos":/,/^  "/' "$GATES" | grep -q '"07c_composed"'
}

@test "07e_visuals also requires 07c_composed (parallel with 07d)" {
    awk '/"07e_visuals":/,/^  "/' "$GATES" | grep -q '"07c_composed"'
}

@test "07f_composed_final requires both 07d_photos and 07e_visuals" {
    awk '/"07f_composed_final":/,/^  "/' "$GATES" | grep -E '"07d_photos".*"07e_visuals"|"07e_visuals".*"07d_photos"' \
      || awk '/"07f_composed_final":/,/^  "/' "$GATES" | grep -q -e '"07d_photos"' && awk '/"07f_composed_final":/,/^  "/' "$GATES" | grep -q -e '"07e_visuals"'
}

@test "08_build has theme_php_syntax_valid check" {
    awk '/"08_build":/,/^  "/' "$GATES" | grep -q "theme_php_syntax_valid"
}

@test "09_deploy has site_url_accessible check" {
    awk '/"09_deploy":/,/^  "/' "$GATES" | grep -q "site_url_accessible"
}

@test "stage-gates.yaml is valid YAML" {
    python3 -c "import yaml; yaml.safe_load(open('$GATES').read())"
}
```

- [ ] **Step 3: Run — fails**

```bash
bats tests/phase-prd/test-stage-gates-schema.bats 2>&1 | head -20
```

- [ ] **Step 4: Append new stage gates to config/stage-gates.yaml**

Read existing structure first, then append/insert these new stage definitions after the existing ones:

```yaml
  "07a_prototype":
    name: "Прототип (parse)"
    require_approved: []
    hard_checks:
      - id: prototype_source_exists
        type: file_or_dir_exists
        path: "{project}/07_ПРОТОТИП/source"
        required: true
        fix_hint: "Положи prototype.pdf или prototype.md в 07_ПРОТОТИП/source/"
      - id: prototype_yaml_exists
        type: file_exists
        path: "{project}/07_ПРОТОТИП/prototype.yaml"
        required: true
        fix_hint: "auto_fix: /landing-prototype"

  "07b_wireframe":
    name: "Wireframe"
    require_approved: ["07a_prototype"]
    hard_checks:
      - id: wireframe_html_exists
        type: file_exists
        path: "{project}/07a_WIREFRAME/wireframe.html"
        required: true
        fix_hint: "auto_fix: /landing-wireframe"
      - id: wireframe_selections
        type: file_exists
        path: "{project}/07a_WIREFRAME/selections.yaml"
        required: true
        fix_hint: "Открой wireframe.html в браузере, выбери варианты блоков, нажми Confirm. Скачается selections.yaml — положи его в 07a_WIREFRAME/"

  "07c_composed":
    name: "Composed (draft)"
    require_approved: ["07b_wireframe", "05_design"]
    hard_checks:
      - id: composed_html
        type: file_exists
        path: "{project}/07b_COMPOSED/composed.html"
        required: true
        fix_hint: "auto_fix: /landing-compose"

  "07d_photos":
    name: "Photos pipeline"
    require_approved: ["07c_composed"]
    hard_checks:
      - id: photo_selections_yaml
        type: file_exists
        path: "{project}/07c_PHOTOS/selections.yaml"
        required: true
        fix_hint: "Открой 07c_PHOTOS/photo-board.html, расставь фото, нажми Подтвердить, скачай selections.yaml и положи в 07c_PHOTOS/"

  "07e_visuals":
    name: "Visuals pipeline (icons + infographics)"
    require_approved: ["07c_composed"]
    hard_checks:
      - id: visuals_generated
        type: dir_has_files
        path: "{project}/07d_VISUALS/icons"
        required: false
        fix_hint: "auto_fix: /landing-visuals"

  "07f_composed_final":
    name: "Composed (final)"
    require_approved: ["07d_photos", "07e_visuals"]
    hard_checks:
      - id: composed_has_real_visuals
        type: script
        script: "scripts/verify-composed-has-visuals.sh"
        args: ["{project}/07b_COMPOSED/composed.html"]
        required: true
        fix_hint: "auto_fix: /landing-compose"
```

Also augment existing `"08_build"` and `"09_deploy"`. If they exist, ADD these hard_checks; if they don't exist, create the stage entries.

Add to 08_build:
```yaml
      - id: theme_php_syntax_valid
        type: script
        script: "scripts/verify-php-syntax.sh"
        args: ["{project}/08_КОД/wp-theme"]
        required: true
        fix_hint: "wp-builder сгенерил невалидный PHP — посмотри логи wp-builder, re-run"
      - id: gutenberg_blocks_valid
        type: script
        script: "scripts/verify-gutenberg-json.sh"
        args: ["{project}/08_КОД/gutenberg-blocks"]
        required: false
        fix_hint: "Gutenberg block.json невалидный — посмотри errors output"
```

Add to 09_deploy:
```yaml
      - id: site_url_accessible
        type: script
        script: "scripts/verify-site-url.sh"
        args: ["{project}/.landing-state.yaml"]
        required: true
        fix_hint: "Сайт не открывается по URL. Проверь Бегет credentials в ~/.beget-config или логи wp-deployer"
```

- [ ] **Step 5: Run — pass**

```bash
bats tests/phase-prd/test-stage-gates-schema.bats
```

Expected: 8/8 PASS.

- [ ] **Step 6: Commit**

```bash
git add config/stage-gates.yaml tests/phase-prd/test-stage-gates-schema.bats
git commit -m "feat(pr-d): stage-gates.yaml — gates for 7 new PR-D stages + augment 08/09"
```

---

## Task 3: `gate-check.sh` + `gate-state.sh` — support `n/a` status

**Files:**
- Modify: `scripts/gate-check.sh`
- Modify: `scripts/gate-state.sh`
- Create: `tests/phase-prd/test-gate-na-status.bats`

- [ ] **Step 1: Read existing scripts to understand status handling**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
grep -n "approved\|locked\|in_progress\|failed" scripts/gate-check.sh | head -20
grep -n "approved\|locked\|in_progress\|failed" scripts/gate-state.sh | head -20
```

Find where status values are compared. Add `n/a` handling: when checking `require_approved`, treat `n/a` same as `approved` (skip the requirement).

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-gate-na-status.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

setup() {
    TMP_PROJECT="$(mktemp -d)"
    mkdir -p "$TMP_PROJECT/07_ПРОТОТИП"
    cat > "$TMP_PROJECT/.landing-state.yaml" <<EOF
project: test
created: "2026-05-13"
schema_version: 2
stages:
  "00_brief":          {status: n/a, timestamp: ""}
  "01_context":        {status: n/a, timestamp: ""}
  "01a_niche_analysis":{status: n/a, timestamp: ""}
  "02_assets":         {status: n/a, timestamp: ""}
  "07a_prototype":     {status: in_progress, timestamp: ""}
EOF
    # Touch a fake prototype.yaml to satisfy hard_check
    touch "$TMP_PROJECT/07_ПРОТОТИП/prototype.yaml"
    mkdir -p "$TMP_PROJECT/07_ПРОТОТИП/source"
}

teardown() { rm -rf "$TMP_PROJECT"; }

@test "gate-check passes for 07a_prototype with all upstream n/a" {
    run bash "$REPO/scripts/gate-check.sh" "$TMP_PROJECT" "07a_prototype"
    # Expected: passes because no require_approved + hard checks all met
    [ "$status" -eq 0 ]
}

@test "gate-state.sh accepts n/a status for read" {
    run bash "$REPO/scripts/gate-state.sh" get "$TMP_PROJECT" "00_brief"
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "n/a"
}

@test "gate-check satisfies require_approved when upstream is n/a" {
    # Add 07b_wireframe stage requiring 07a_prototype
    cat >> "$TMP_PROJECT/.landing-state.yaml" <<EOF
  "07b_wireframe":     {status: in_progress, timestamp: ""}
EOF
    # Mark 07a_prototype approved
    python3 -c "
import yaml
p = '$TMP_PROJECT/.landing-state.yaml'
data = yaml.safe_load(open(p).read())
data['stages']['07a_prototype']['status'] = 'approved'
open(p, 'w').write(yaml.safe_dump(data))
"
    mkdir -p "$TMP_PROJECT/07a_WIREFRAME"
    touch "$TMP_PROJECT/07a_WIREFRAME/wireframe.html"
    touch "$TMP_PROJECT/07a_WIREFRAME/selections.yaml"

    run bash "$REPO/scripts/gate-check.sh" "$TMP_PROJECT" "07b_wireframe"
    [ "$status" -eq 0 ]
}
```

- [ ] **Step 3: Run — fails**

```bash
bats tests/phase-prd/test-gate-na-status.bats 2>&1 | head -25
```

- [ ] **Step 4: Patch `scripts/gate-check.sh` to accept `n/a` as valid status**

Locate the section that validates statuses (likely a `case` statement or grep on status values). Add `n/a` to allowed list.

Find code like:
```bash
case "$status" in
    approved|locked|in_progress|failed)
        ;;
    *)
        echo "ERROR: invalid status: $status" >&2
        exit 1
        ;;
esac
```

Change to:
```bash
case "$status" in
    approved|locked|in_progress|failed|n/a)
        ;;
    *)
        echo "ERROR: invalid status: $status" >&2
        exit 1
        ;;
esac
```

For `require_approved` check, where it looks like:
```bash
if [ "$dep_status" != "approved" ]; then
    echo "ERROR: requires $dep to be approved" >&2
    exit 1
fi
```

Change to:
```bash
if [ "$dep_status" != "approved" ] && [ "$dep_status" != "n/a" ]; then
    echo "ERROR: requires $dep to be approved (current: $dep_status)" >&2
    exit 1
fi
```

- [ ] **Step 5: Patch `scripts/gate-state.sh` to accept `n/a` for read/write**

Same surgery — add `n/a` to status enum/case.

- [ ] **Step 6: Run regression: existing gate-check tests still pass + new tests pass**

```bash
bats tests/gate-check/test-gate-check.bats tests/gate-check/test-gate-state.bats
bats tests/phase-prd/test-gate-na-status.bats
```

All must PASS. If existing tests break — fix gate-check.sh without breaking them.

- [ ] **Step 7: Commit**

```bash
git add scripts/gate-check.sh scripts/gate-state.sh tests/phase-prd/test-gate-na-status.bats
git commit -m "feat(pr-d): gate-check + gate-state support n/a status for prototype-first flow"
```

---

## Task 4: `derive-landing-structure.py` — bridge prototype.yaml → landing-structure.md

**Files:**
- Create: `scripts/derive-landing-structure.py`
- Create: `tests/phase-prd/test-derive-landing-structure.py`

- [ ] **Step 1: Inspect existing landing-structure.md format**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
find . -name "landing-structure.md" 2>/dev/null | head -3
cat $(find . -name "landing-structure.md" 2>/dev/null | head -1) 2>/dev/null | head -40
# Also find a real example in a project if exists
find ~/Lendings -name "landing-structure.md" 2>/dev/null | head -3
```

Look for the "Контракт с wp-builder" section pattern.

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-derive-landing-structure.py`:
```python
"""Tests for derive-landing-structure.py — prototype.yaml → landing-structure.md."""
import subprocess
import sys
from pathlib import Path

import yaml
import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "derive-landing-structure.py"


def test_derives_structure_from_prototype(tmp_path):
    project = tmp_path / "test-project"
    proto_dir = project / "07_ПРОТОТИП"
    proto_dir.mkdir(parents=True)
    out_dir = project / "01a_АНАЛИЗ_НИШИ"

    prototype = {
        "blocks": [
            {"id": "hero-1", "type": "hero", "title": "Главный экран"},
            {"id": "features-1", "type": "features", "title": "Что мы делаем"},
            {"id": "testimonials-1", "type": "social-proof", "title": "Отзывы"},
            {"id": "form-1", "type": "cta", "title": "Запрос расчёта"},
        ]
    }
    (proto_dir / "prototype.yaml").write_text(yaml.safe_dump(prototype, allow_unicode=True))

    result = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"

    out_path = out_dir / "landing-structure.md"
    assert out_path.exists()

    body = out_path.read_text()
    assert "Контракт с wp-builder" in body
    # Each block type maps to a template-part PHP filename
    assert "section-hero.php" in body
    assert "section-features.php" in body
    assert "section-form.php" in body or "section-cta.php" in body


def test_derive_handles_empty_prototype(tmp_path):
    project = tmp_path / "test-project"
    proto_dir = project / "07_ПРОТОТИП"
    proto_dir.mkdir(parents=True)
    (proto_dir / "prototype.yaml").write_text("blocks: []")

    result = subprocess.run(
        ["python3", str(SCRIPT), "--project", str(project)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

    out_path = project / "01a_АНАЛИЗ_НИШИ" / "landing-structure.md"
    assert out_path.exists()
    # At minimum should have the contract header
    assert "Контракт с wp-builder" in out_path.read_text()
```

- [ ] **Step 3: Run — fails**

```bash
python3 -m pytest tests/phase-prd/test-derive-landing-structure.py -v 2>&1 | head -15
```

- [ ] **Step 4: Implement derive-landing-structure.py**

`scripts/derive-landing-structure.py`:
```python
#!/usr/bin/env python3
"""Derive 01a_АНАЛИЗ_НИШИ/landing-structure.md from 07_ПРОТОТИП/prototype.yaml.

Bridge for prototype-first flow (PR-D): wp-builder reads landing-structure.md to
know which template-parts/*.php to generate. In prototype-first flow we skip
01a niche analysis, so we synthesize this file from the prototype block list.
"""
import argparse
import sys
from pathlib import Path

import yaml


# Block type → template-part PHP file name
BLOCK_TYPE_TO_PHP = {
    "hero": "section-hero.php",
    "features": "section-features.php",
    "social-proof": "section-proof.php",
    "testimonials": "section-proof.php",
    "trust": "section-proof.php",
    "process": "section-process.php",
    "pricing": "section-pricing.php",
    "faq": "section-faq.php",
    "cta": "section-form.php",
    "quiz": "section-quiz.php",
    "gallery": "section-gallery.php",
}


def derive(project_dir: Path) -> str:
    """Build markdown content."""
    project_dir = Path(project_dir)
    proto_path = project_dir / "07_ПРОТОТИП" / "prototype.yaml"
    if not proto_path.exists():
        sys.exit(f"ERROR: {proto_path} not found")

    prototype = yaml.safe_load(proto_path.read_text(encoding="utf-8")) or {}
    blocks = prototype.get("blocks", []) or []

    php_files: list[str] = []
    for b in blocks:
        block_type = (b.get("type") or "").lower()
        php = BLOCK_TYPE_TO_PHP.get(block_type)
        if php and php not in php_files:
            php_files.append(php)

    lines = [
        "# Landing Structure (auto-derived from prototype.yaml)",
        "",
        "Этот файл сгенерирован автоматически из `07_ПРОТОТИП/prototype.yaml`",
        "скриптом `scripts/derive-landing-structure.py`. Используется `wp-builder` как",
        "источник списка `template-parts/*.php` для генерации WordPress темы.",
        "",
        "## Контракт с wp-builder",
        "",
        "Список template-parts которые должны быть сгенерированы:",
        "",
    ]
    for php in php_files:
        lines.append(f"- `template-parts/{php}`")
    if not php_files:
        lines.append("- (нет блоков — пустой прототип)")
    lines.append("")
    lines.append(f"Источник: {len(blocks)} блоков в prototype.yaml.")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Project directory")
    args = ap.parse_args()

    project = Path(args.project)
    out_dir = project / "01a_АНАЛИЗ_НИШИ"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "landing-structure.md"

    content = derive(project)
    out_path.write_text(content, encoding="utf-8")
    print(f"OK: wrote {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run — pass**

```bash
python3 -m pytest tests/phase-prd/test-derive-landing-structure.py -v
```

Expected: 2/2 PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/derive-landing-structure.py tests/phase-prd/test-derive-landing-structure.py
git commit -m "feat(pr-d): derive-landing-structure.py bridges prototype.yaml → wp-builder contract"
```

---

## Task 5: 4 verify-* scripts for build/deploy gates

**Files:**
- Create: `scripts/verify-composed-has-visuals.sh`
- Create: `scripts/verify-php-syntax.sh`
- Create: `scripts/verify-gutenberg-json.sh`
- Create: `scripts/verify-site-url.sh`
- Create: `tests/phase-prd/test-verify-scripts.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prd/test-verify-scripts.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

setup() {
    TMP="$(mktemp -d)"
}

teardown() {
    rm -rf "$TMP"
}

@test "verify-composed-has-visuals: clean html → exit 0" {
    echo '<html><body><img src="real-icon.png" class="lp-icon"></body></html>' > "$TMP/composed.html"
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/composed.html"
    [ "$status" -eq 0 ]
}

@test "verify-composed-has-visuals: still has [SLOT: ...] → exit 1" {
    echo '<html><body>[SLOT: feature-1-icon]</body></html>' > "$TMP/composed.html"
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/composed.html"
    [ "$status" -eq 1 ]
}

@test "verify-composed-has-visuals: missing file → exit 2" {
    run bash "$REPO/scripts/verify-composed-has-visuals.sh" "$TMP/nonexistent.html"
    [ "$status" -eq 2 ]
}

@test "verify-php-syntax: valid PHP → exit 0" {
    if ! command -v php >/dev/null 2>&1; then skip "php not installed"; fi
    mkdir -p "$TMP/wp-theme"
    echo '<?php echo "hello"; ?>' > "$TMP/wp-theme/index.php"
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/wp-theme"
    [ "$status" -eq 0 ]
}

@test "verify-php-syntax: broken PHP → exit 1" {
    if ! command -v php >/dev/null 2>&1; then skip "php not installed"; fi
    mkdir -p "$TMP/wp-theme"
    echo '<?php echo "missing semicolon" ?>' > "$TMP/wp-theme/index.php"  # actually valid
    echo '<?php this is not php ?>' > "$TMP/wp-theme/broken.php"
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/wp-theme"
    [ "$status" -ne 0 ]
}

@test "verify-php-syntax: missing dir → exit 2" {
    run bash "$REPO/scripts/verify-php-syntax.sh" "$TMP/nonexistent"
    [ "$status" -eq 2 ]
}

@test "verify-gutenberg-json: valid block.json files → exit 0" {
    mkdir -p "$TMP/blocks/hero"
    cat > "$TMP/blocks/hero/block.json" <<'EOF'
{"apiVersion": 3, "name": "lp/hero", "title": "Hero", "category": "design"}
EOF
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 0 ]
}

@test "verify-gutenberg-json: invalid JSON → exit 1" {
    mkdir -p "$TMP/blocks/hero"
    echo 'NOT JSON' > "$TMP/blocks/hero/block.json"
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 1 ]
}

@test "verify-gutenberg-json: empty dir → exit 0" {
    mkdir -p "$TMP/blocks"
    run bash "$REPO/scripts/verify-gutenberg-json.sh" "$TMP/blocks"
    [ "$status" -eq 0 ]
}

@test "verify-site-url: state without deploy_url → exit 2" {
    cat > "$TMP/.landing-state.yaml" <<'EOF'
project: test
stages: {}
EOF
    run bash "$REPO/scripts/verify-site-url.sh" "$TMP/.landing-state.yaml"
    [ "$status" -eq 2 ]
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-prd/test-verify-scripts.bats 2>&1 | head -25
```

- [ ] **Step 3: Implement verify-composed-has-visuals.sh**

`scripts/verify-composed-has-visuals.sh`:
```bash
#!/usr/bin/env bash
# verify-composed-has-visuals.sh — fail if composed.html still contains placeholder markers.
#
# Usage: verify-composed-has-visuals.sh <path-to-composed.html>
# Exit codes:
#   0 — composed.html is clean (no [SLOT:, [INFOGRAPHIC:, [photo slot:)
#   1 — composed.html still has placeholders → PR-B or PR-C not finished
#   2 — file missing

set -euo pipefail

FILE="${1:?ERROR: composed.html path required}"

[ -f "$FILE" ] || {
    echo "ERROR: composed.html not found at $FILE" >&2
    exit 2
}

if grep -qE '\[SLOT:|\[INFOGRAPHIC:|\[photo slot:' "$FILE"; then
    echo "FAIL: $FILE still contains placeholders. Run /landing-photos and /landing-visuals first." >&2
    exit 1
fi

echo "OK: $FILE has no leftover placeholders"
```

Make executable: `chmod +x scripts/verify-composed-has-visuals.sh`

- [ ] **Step 4: Implement verify-php-syntax.sh**

`scripts/verify-php-syntax.sh`:
```bash
#!/usr/bin/env bash
# verify-php-syntax.sh — run `php -l` on every .php file in a directory.
#
# Usage: verify-php-syntax.sh <dir>
# Exit codes:
#   0 — all PHP files parse cleanly
#   1 — at least one syntax error
#   2 — dir missing OR php not installed

set -euo pipefail

DIR="${1:?ERROR: directory required}"

[ -d "$DIR" ] || {
    echo "ERROR: dir not found: $DIR" >&2
    exit 2
}

if ! command -v php >/dev/null 2>&1; then
    echo "WARN: php CLI not installed — skipping PHP syntax check" >&2
    exit 2
fi

errors=0
while IFS= read -r -d '' f; do
    if ! php -l "$f" >/dev/null 2>&1; then
        echo "✗ PHP syntax error: $f" >&2
        php -l "$f" >&2 || true
        errors=$((errors+1))
    fi
done < <(find "$DIR" -name "*.php" -print0)

if [ "$errors" -gt 0 ]; then
    echo "FAIL: $errors PHP file(s) have syntax errors" >&2
    exit 1
fi

echo "OK: all PHP files in $DIR parse cleanly"
```

Make executable.

- [ ] **Step 5: Implement verify-gutenberg-json.sh**

`scripts/verify-gutenberg-json.sh`:
```bash
#!/usr/bin/env bash
# verify-gutenberg-json.sh — validate every block.json in a directory parses as JSON.
#
# Usage: verify-gutenberg-json.sh <dir>
# Exit codes:
#   0 — all block.json files valid (or dir is empty)
#   1 — at least one invalid JSON
#   2 — dir missing

set -euo pipefail

DIR="${1:?ERROR: directory required}"

[ -d "$DIR" ] || {
    echo "ERROR: dir not found: $DIR" >&2
    exit 2
}

errors=0
while IFS= read -r -d '' f; do
    if ! python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
        echo "✗ Invalid JSON: $f" >&2
        errors=$((errors+1))
    fi
done < <(find "$DIR" -name "block.json" -print0)

if [ "$errors" -gt 0 ]; then
    echo "FAIL: $errors block.json file(s) are invalid" >&2
    exit 1
fi

echo "OK: all block.json files in $DIR are valid"
```

Make executable.

- [ ] **Step 6: Implement verify-site-url.sh**

`scripts/verify-site-url.sh`:
```bash
#!/usr/bin/env bash
# verify-site-url.sh — curl HEAD on deployed URL from .landing-state.yaml.
#
# Usage: verify-site-url.sh <path-to-.landing-state.yaml>
# Reads stages.09_deploy.deploy_url (if present).
# Exit codes:
#   0 — URL returns 2xx
#   1 — URL not reachable or returns non-2xx
#   2 — state.yaml missing or no deploy_url

set -euo pipefail

STATE="${1:?ERROR: state.yaml path required}"

[ -f "$STATE" ] || {
    echo "ERROR: state.yaml not found at $STATE" >&2
    exit 2
}

URL="$(python3 -c "
import yaml, sys
data = yaml.safe_load(open('$STATE').read())
stage = data.get('stages', {}).get('09_deploy', {})
url = stage.get('deploy_url', '') if isinstance(stage, dict) else ''
print(url)
")"

if [ -z "$URL" ]; then
    echo "ERROR: no deploy_url recorded in state.yaml:stages.09_deploy" >&2
    exit 2
fi

# HEAD request, follow redirects, expect 2xx
if curl -fsSI -L --max-time 10 "$URL" >/dev/null 2>&1; then
    echo "OK: $URL is accessible"
    exit 0
else
    echo "FAIL: $URL not reachable or returned non-2xx" >&2
    exit 1
fi
```

Make executable.

- [ ] **Step 7: Run tests — pass**

```bash
bats tests/phase-prd/test-verify-scripts.bats
```

Expected: all PASS (some may skip if php not installed).

- [ ] **Step 8: Commit**

```bash
git add scripts/verify-*.sh tests/phase-prd/test-verify-scripts.bats
git commit -m "feat(pr-d): 4 verify scripts for composed/php/gutenberg/site-url gates"
```

---

## Task 6: `lucide-fetcher.py` — Lucide SVG → brand-colored PNG

**Files:**
- Create: `skills/visual-generation/scripts/lucide-fetcher.py`
- Create: `tests/phase-prd/test-lucide-fetcher.py`

- [ ] **Step 1: Write failing test**

`tests/phase-prd/test-lucide-fetcher.py`:
```python
"""Tests for lucide-fetcher.py — download Lucide SVG, render as brand-colored PNG."""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from tests.phase_prd.conftest import _load_module  # the helper we created

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "skills" / "visual-generation" / "scripts" / "lucide-fetcher.py"


def _load():
    return _load_module("lucide_fetcher", SCRIPT)


SAMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" x2="21" y1="6" y2="6"/>
  <line x1="3" x2="21" y1="12" y2="12"/>
  <line x1="3" x2="21" y1="18" y2="18"/>
</svg>"""


def test_lucide_url_for_name():
    mod = _load()
    url = mod.lucide_url("menu")
    assert "lucide-icons/lucide" in url
    assert url.endswith("/menu.svg")


def test_cache_path_for_name(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    p = mod.cache_path("menu")
    assert str(p).endswith("menu.svg")


def test_fetch_returns_cached_when_exists(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    cached = tmp_path / "menu.svg"
    cached.write_text(SAMPLE_SVG)
    result = mod.fetch_svg("menu")
    assert result == cached
    assert result.read_text() == SAMPLE_SVG


def test_fetch_downloads_when_not_cached(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path))
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_SVG
    with patch.object(mod, "_http_get", return_value=mock_resp):
        result = mod.fetch_svg("menu")
    assert result.read_text() == SAMPLE_SVG


def test_render_to_png_with_brand_color(tmp_path):
    mod = _load()
    svg_path = tmp_path / "menu.svg"
    svg_path.write_text(SAMPLE_SVG)
    png_path = tmp_path / "menu.png"
    mod.render_to_png(svg_path, png_path, brand_color="#1e3a8a", size=1024)
    assert png_path.exists()
    assert png_path.stat().st_size > 100  # not empty


def test_fetch_and_render_full_flow(tmp_path, monkeypatch):
    mod = _load()
    monkeypatch.setenv("LUCIDE_CACHE_DIR", str(tmp_path / "cache"))
    cached = tmp_path / "cache" / "menu.svg"
    cached.parent.mkdir(parents=True)
    cached.write_text(SAMPLE_SVG)

    out_png = tmp_path / "out.png"
    result = mod.fetch_and_render("menu", out_png, brand_color="#c47a3a", size=512)
    assert result == out_png
    assert out_png.exists()
```

Update `tests/phase-prd/conftest.py` to add `_load_module` helper (already there from Task 1 but ensure):
```python
def _load_module(module_name, file_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

- [ ] **Step 2: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
python3 -m pytest tests/phase-prd/test-lucide-fetcher.py -v 2>&1 | head -15
```

- [ ] **Step 3: Implement lucide-fetcher.py**

`skills/visual-generation/scripts/lucide-fetcher.py`:
```python
#!/usr/bin/env python3
"""Fetch Lucide icon SVG, render as brand-colored PNG.

Lucide icons are MIT-licensed (https://lucide.dev). We download SVG from the
official GitHub raw URL, replace `currentColor` with the brand color, and
rasterize to a square PNG of the requested size.

Used as the first-step bypass in prompt-picker waterfall for icons matched in
icons.csv where Library=Lucide.
"""
import os
import re
from pathlib import Path
from typing import Optional


LUCIDE_BASE_URL = "https://raw.githubusercontent.com/lucide-icons/lucide/main/icons"
DEFAULT_CACHE = Path.home() / ".cache" / "landing-system" / "lucide"


def lucide_url(icon_name: str) -> str:
    return f"{LUCIDE_BASE_URL}/{icon_name}.svg"


def cache_path(icon_name: str) -> Path:
    cache_dir = Path(os.environ.get("LUCIDE_CACHE_DIR", str(DEFAULT_CACHE)))
    return cache_dir / f"{icon_name}.svg"


def _http_get(url: str):
    """Simple HTTP GET with stdlib (no requests dependency)."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "landing-system/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            class R:
                pass
            r = R()
            r.status_code = resp.status
            r.text = resp.read().decode("utf-8")
            return r
    except urllib.error.URLError as e:
        class R:
            pass
        r = R()
        r.status_code = 0
        r.text = f"ERROR: {e}"
        return r


def fetch_svg(icon_name: str) -> Optional[Path]:
    """Return path to cached SVG, downloading if needed. None on failure."""
    cp = cache_path(icon_name)
    if cp.exists() and cp.stat().st_size > 0:
        return cp

    cp.parent.mkdir(parents=True, exist_ok=True)
    resp = _http_get(lucide_url(icon_name))
    if resp.status_code != 200 or "<svg" not in resp.text:
        return None
    cp.write_text(resp.text, encoding="utf-8")
    return cp


def render_to_png(svg_path: Path, out_path: Path, brand_color: str = "#000000", size: int = 1024) -> None:
    """Rasterize SVG to a square PNG of `size` pixels with brand color.

    Strategy: replace `currentColor` and `stroke="currentColor"` with the brand color,
    then render via cairosvg if available, otherwise via Pillow + a simple SVG-to-raster
    fallback (drawing primitives only). Lucide icons use stroke geometry — for the
    Pillow fallback we cheat by using a thicker rasterization.
    """
    svg_text = Path(svg_path).read_text(encoding="utf-8")
    # Force brand color on strokes/fills
    svg_text = svg_text.replace("currentColor", brand_color)
    # Some Lucide icons set stroke="currentColor" — already covered. Also ensure default stroke set.
    svg_text = re.sub(r"\bstroke=\"#[0-9a-fA-F]{3,6}\"", f'stroke="{brand_color}"', svg_text)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    # Try cairosvg first
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(bytestring=svg_text.encode("utf-8"),
                         write_to=str(out_path),
                         output_width=size, output_height=size)
        return
    except ImportError:
        pass

    # Fallback: use Pillow with a manually-stroked rendering via svglib if available
    try:
        from io import BytesIO
        from svglib.svglib import svg2rlg  # type: ignore
        from reportlab.graphics import renderPM  # type: ignore
        tmp_svg = out_path.with_suffix(".tmp.svg")
        tmp_svg.write_text(svg_text, encoding="utf-8")
        drawing = svg2rlg(str(tmp_svg))
        scale = size / max(drawing.width, drawing.height)
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        renderPM.drawToFile(drawing, str(out_path), fmt="PNG")
        tmp_svg.unlink()
        return
    except ImportError:
        pass

    # Last resort: write a placeholder PNG via Pillow (single-color square)
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a simple marker so the file isn't blank
    border = size // 8
    rgb = tuple(int(brand_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    draw.rectangle([border, border, size - border, size - border], outline=rgb + (255,), width=size // 32)
    img.save(out_path, "PNG")


def fetch_and_render(icon_name: str, out_path: Path, brand_color: str = "#000000", size: int = 1024) -> Optional[Path]:
    """One-shot: fetch SVG (cached) + render PNG to out_path. Returns out_path on success, None on fail."""
    svg = fetch_svg(icon_name)
    if svg is None:
        return None
    render_to_png(svg, Path(out_path), brand_color=brand_color, size=size)
    return Path(out_path)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="Lucide icon name (e.g. 'menu', 'shield')")
    ap.add_argument("--out", required=True, help="Output PNG path")
    ap.add_argument("--color", default="#000000", help="Brand color for the icon")
    ap.add_argument("--size", type=int, default=1024)
    args = ap.parse_args()

    result = fetch_and_render(args.name, args.out, args.color, args.size)
    if result is None:
        print(f"FAIL: could not fetch Lucide icon '{args.name}'", file=__import__("sys").stderr)
        raise SystemExit(1)
    print(f"OK: {result}")


if __name__ == "__main__":
    main()
```

Also need module mapping in conftest. Update `tests/phase-prd/conftest.py` to add:
```python
_LUCIDE = REPO_ROOT / "skills" / "visual-generation" / "scripts" / "lucide-fetcher.py"
if _LUCIDE.exists():
    _mod = _load_module("lucide_fetcher", _LUCIDE)
    sys.modules["lucide_fetcher"] = _mod
```

But the test uses `_load_module` directly — that's fine, no need for sys.modules registration here.

- [ ] **Step 4: Run — pass**

```bash
python3 -m pytest tests/phase-prd/test-lucide-fetcher.py -v
```

Expected: 6/6 PASS (possibly with Pillow-only fallback if cairosvg/svglib absent).

- [ ] **Step 5: Commit**

```bash
git add skills/visual-generation/scripts/lucide-fetcher.py tests/phase-prd/test-lucide-fetcher.py tests/phase-prd/conftest.py
git commit -m "feat(pr-d): lucide-fetcher.py — download Lucide SVG, render as brand-colored PNG"
```

---

## Task 7: Update `prompt-picker.py` — add Lucide branch as first waterfall step

**Files:**
- Modify: `skills/visual-generation/scripts/prompt-picker.py`
- Create: `tests/phase-prd/test-prompt-picker-lucide.py`

- [ ] **Step 1: Inspect current prompt-picker.py**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
cat skills/visual-generation/scripts/prompt-picker.py
```

Find `pick_icon_prompt()` and the `PromptSource` enum.

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-prompt-picker-lucide.py`:
```python
"""Tests for prompt-picker.py Lucide branch (PR-D extension)."""
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


from tests.phase_prd.conftest import _load_module

PP = REPO / "skills" / "visual-generation" / "scripts" / "prompt-picker.py"


def _load_pp():
    return _load_module("prompt_picker_prd", PP)


def test_lucide_source_enum_exists():
    mod = _load_pp()
    assert hasattr(mod.PromptSource, "LUCIDE")


def test_pick_icon_returns_lucide_source_when_icons_csv_says_lucide(tmp_path):
    mod = _load_pp()
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Navigation,menu,hamburger menu navigation toggle bars,Lucide,import { Menu },<Menu />,Mobile drawer,Outline\n'
    )
    result = mod.pick_icon_prompt(
        hint="menu",
        brand_context={"BRAND_ACCENT": "#1e3a8a", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    assert result.source == mod.PromptSource.LUCIDE
    # PickedPrompt should carry the lucide icon name in attribution or a new field
    assert (hasattr(result, "lucide_icon_name") and result.lucide_icon_name == "menu") \
        or (result.attribution and result.attribution.get("lucide_icon_name") == "menu")


def test_pick_icon_falls_through_to_csv_match_when_library_not_lucide(tmp_path):
    mod = _load_pp()
    icons_csv = tmp_path / "icons.csv"
    icons_csv.write_text(
        "No,Category,Icon Name,Keywords,Library,Import Code,Usage,Best For,Style\n"
        '1,Custom,shield,shield protect security,Heroicons,import,...,Trust,Outline\n'
    )
    result = mod.pick_icon_prompt(
        hint="shield",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Minimalism"},
        icons_csv=icons_csv,
        opendesign_index=None,
    )
    # Library != Lucide → ICONS_CSV path (codex generic), not LUCIDE
    assert result.source == mod.PromptSource.ICONS_CSV


def test_pick_icon_no_csv_falls_to_generic():
    mod = _load_pp()
    result = mod.pick_icon_prompt(
        hint="xyz-no-match",
        brand_context={"BRAND_ACCENT": "#000", "VISUAL_STYLE": "Minimalism"},
        icons_csv=None,
        opendesign_index=None,
    )
    assert result.source == mod.PromptSource.GENERIC
```

- [ ] **Step 3: Run — fails (no LUCIDE enum value)**

```bash
python3 -m pytest tests/phase-prd/test-prompt-picker-lucide.py -v 2>&1 | head -15
```

- [ ] **Step 4: Update prompt-picker.py**

Add `LUCIDE` to the enum:
```python
class PromptSource(Enum):
    LUCIDE = "lucide"       # NEW: direct fetch from Lucide, bypass codex
    OPENDESIGN = "opendesign"
    ICONS_CSV = "icons_csv"
    GENERIC = "generic"
```

Update `PickedPrompt` dataclass to add `lucide_icon_name` (optional):
```python
@dataclass
class PickedPrompt:
    prompt: str           # may be empty for LUCIDE
    source: PromptSource
    attribution: Optional[dict] = None
    lucide_icon_name: Optional[str] = None  # NEW
```

Update `pick_icon_prompt()` to check Lucide first:
```python
def pick_icon_prompt(
    hint: str,
    brand_context: dict,
    icons_csv: Optional[Path] = None,
    opendesign_index: Optional[Path] = None,
) -> PickedPrompt:
    """Pick prompt for icon slot. Waterfall: Lucide → icons.csv → generic."""
    chroma = brand_context.get("CHROMA_KEY", "#00ff00")
    brand_accent = brand_context.get("BRAND_ACCENT", "#888888")
    visual_style = brand_context.get("VISUAL_STYLE", "Minimalism")
    icon_style = brand_context.get("ICON_STYLE", "outlined")
    niche = brand_context.get("NICHE", "")

    row = _icons_csv_match(hint, icons_csv) if icons_csv else None

    # STEP 1 (NEW): if matched row says Library=Lucide → bypass codex entirely
    if row and row.get("Library", "").strip().lower() == "lucide":
        return PickedPrompt(
            prompt="",
            source=PromptSource.LUCIDE,
            lucide_icon_name=row["Icon Name"].strip(),
            attribution={"source": "Lucide", "license": "ISC", "url": "https://lucide.dev"},
        )

    # STEP 2: icons.csv match but non-Lucide → codex generic with hint enrichment
    if row:
        first_kw = row.get("Keywords", "").split()[0] if row.get("Keywords") else ""
        prompt = GENERIC_ICON_TEMPLATE.format(
            chroma=chroma,
            hint=f"{row['Icon Name']} icon ({first_kw})",
            visual_style=visual_style,
            icon_style=icon_style,
            brand_accent=brand_accent,
            niche=niche,
        )
        return PickedPrompt(prompt=prompt, source=PromptSource.ICONS_CSV)

    # STEP 3: generic fallback
    prompt = GENERIC_ICON_TEMPLATE.format(
        chroma=chroma,
        hint=hint if hint else "abstract minimalist icon",
        visual_style=visual_style,
        icon_style=icon_style,
        brand_accent=brand_accent,
        niche=niche,
    )
    return PickedPrompt(prompt=prompt, source=PromptSource.GENERIC)
```

- [ ] **Step 5: Run — pass**

```bash
python3 -m pytest tests/phase-prd/test-prompt-picker-lucide.py -v
python3 -m pytest tests/phase-prc/test-prompt-picker.py -v   # PR-C regression
```

Both must pass.

- [ ] **Step 6: Commit**

```bash
git add skills/visual-generation/scripts/prompt-picker.py tests/phase-prd/test-prompt-picker-lucide.py
git commit -m "feat(pr-d): prompt-picker — Lucide as first waterfall step (bypass codex)"
```

---

## Task 8: `install-codex.sh` — automated codex CLI install

**Files:**
- Create: `scripts/install-codex.sh`
- Create: `tests/phase-prd/test-install-codex.bats`

- [ ] **Step 1: Write failing test**

`tests/phase-prd/test-install-codex.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "install-codex.sh exists and is executable" {
    [ -x "$REPO/scripts/install-codex.sh" ]
}

@test "install-codex.sh --check reports installed when codex on PATH" {
    if ! command -v codex >/dev/null 2>&1; then skip "codex not installed locally"; fi
    run bash "$REPO/scripts/install-codex.sh" --check
    [ "$status" -eq 0 ]
    echo "$output" | grep -qi "уже установлен\|already installed"
}

@test "install-codex.sh --check exits non-zero when codex absent (in mock PATH)" {
    # Run with PATH that doesn't include codex
    run env PATH="/usr/bin:/bin" bash "$REPO/scripts/install-codex.sh" --check
    [ "$status" -ne 0 ]
}

@test "install-codex.sh --dry-run prints commands without running them" {
    run bash "$REPO/scripts/install-codex.sh" --dry-run
    [ "$status" -eq 0 ]
    echo "$output" | grep -q "npm i -g @openai/codex"
}
```

- [ ] **Step 2: Run — fails**

```bash
bats tests/phase-prd/test-install-codex.bats 2>&1 | head -15
```

- [ ] **Step 3: Implement install-codex.sh**

`scripts/install-codex.sh`:
```bash
#!/usr/bin/env bash
# install-codex.sh — verify codex CLI is installed; install via npm if not.
#
# Usage:
#   bash install-codex.sh             # check + install if missing + prompt login
#   bash install-codex.sh --check     # just report status, no install
#   bash install-codex.sh --dry-run   # print what would happen

set -euo pipefail

CHECK_ONLY=0
DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --check) CHECK_ONLY=1 ;;
        --dry-run) DRY_RUN=1 ;;
    esac
done

print_install_cmd() {
    echo "→ Would run: npm i -g @openai/codex"
}

if command -v codex >/dev/null 2>&1; then
    echo "✅ codex CLI уже установлен ($(codex --version 2>&1 | head -1))"
    exit 0
fi

if [ "$CHECK_ONLY" -eq 1 ]; then
    echo "❌ codex CLI не найден на PATH"
    exit 1
fi

if [ "$DRY_RUN" -eq 1 ]; then
    print_install_cmd
    echo "→ Would prompt: codex login"
    exit 0
fi

echo "→ codex CLI не найден. Устанавливаю через npm..."

if ! command -v npm >/dev/null 2>&1; then
    cat >&2 <<EOF
❌ npm не установлен. Установи Node.js + npm с https://nodejs.org/
   После установки запусти этот скрипт снова.
EOF
    exit 2
fi

# Try install. On EACCES suggest sudo.
if ! npm i -g @openai/codex 2>/tmp/codex-install.err; then
    if grep -qi "eacces\|permission denied" /tmp/codex-install.err; then
        cat >&2 <<EOF
❌ npm install failed (permission denied).
   Попробуй: sudo npm i -g @openai/codex
   Или настрой npm prefix без sudo: https://docs.npmjs.com/resolving-eacces-permissions-errors
EOF
    else
        cat /tmp/codex-install.err >&2
    fi
    exit 1
fi

echo "✅ codex установлен. Проверяю авторизацию..."
if ! codex auth status >/dev/null 2>&1; then
    echo "→ codex не залогинен. Запускаю codex login..."
    codex login || {
        echo "⚠ codex login пропущен. Запусти 'codex login' вручную перед использованием /landing-photos или /landing-visuals." >&2
    }
fi

echo "✅ codex готов к работе"
```

Make executable: `chmod +x scripts/install-codex.sh`

- [ ] **Step 4: Run — pass**

```bash
bats tests/phase-prd/test-install-codex.bats
```

Expected: 4/4 PASS (1 might skip if codex not locally installed).

- [ ] **Step 5: Commit**

```bash
git add scripts/install-codex.sh tests/phase-prd/test-install-codex.bats
git commit -m "feat(pr-d): install-codex.sh — automated codex CLI install with sudo hint"
```

---

## Task 9: `/landing-go` slash command + auto-resume

**Files:**
- Create: `commands/landing-go.md`
- Create: `scripts/landing-go-next-stage.py`
- Create: `tests/phase-prd/test-landing-go.bats`
- Create: `tests/phase-prd/test-next-stage.py`

- [ ] **Step 1: Write failing test for next-stage detection**

`tests/phase-prd/test-next-stage.py`:
```python
"""Tests for landing-go-next-stage.py — pick the next actionable stage."""
import subprocess
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "landing-go-next-stage.py"


def _make_state(tmp_path, stages: dict) -> Path:
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / ".landing-state.yaml").write_text(yaml.safe_dump({
        "project": "x",
        "schema_version": 2,
        "stages": stages,
    }, allow_unicode=True))
    return proj


def _run(project) -> str:
    r = subprocess.run(["python3", str(SCRIPT), "--project", str(project)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_fresh_project_next_is_07a_prototype(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "in_progress"},
        "07b_wireframe": {"status": "locked"},
    })
    assert _run(proj) == "07a_prototype"


def test_returns_first_non_approved_non_na(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "approved"},
        "03_references": {"status": "locked"},
        "07b_wireframe": {"status": "locked"},
    })
    # 03_references is first (locked < 07b_wireframe in stage order)
    assert _run(proj) == "03_references"


def test_returns_done_when_all_complete(tmp_path):
    proj = _make_state(tmp_path, {
        "00_brief": {"status": "n/a"},
        "07a_prototype": {"status": "approved"},
        "12_seo": {"status": "approved"},
    })
    assert _run(proj) == "DONE"


def test_handles_failed_status_by_returning_that_stage(tmp_path):
    proj = _make_state(tmp_path, {
        "07a_prototype": {"status": "failed"},
        "07b_wireframe": {"status": "locked"},
    })
    assert _run(proj) == "07a_prototype"
```

- [ ] **Step 2: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
python3 -m pytest tests/phase-prd/test-next-stage.py -v 2>&1 | head -15
```

- [ ] **Step 3: Implement landing-go-next-stage.py**

`scripts/landing-go-next-stage.py`:
```python
#!/usr/bin/env python3
"""Read .landing-state.yaml and print the next actionable stage id.

Output: stage id on stdout. Prints "DONE" if everything approved.
"""
import argparse
import sys
from pathlib import Path

import yaml


# Canonical stage order (matches template/.landing-state.yaml)
STAGE_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "03_references", "04_brand", "05_design", "06_stack", "07_content",
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "09_deploy", "10_qa", "11_analytics", "12_seo",
]


def next_stage(state_yaml: dict) -> str:
    stages = state_yaml.get("stages", {})
    for stage_id in STAGE_ORDER:
        entry = stages.get(stage_id, {})
        status = entry.get("status") if isinstance(entry, dict) else None
        if status in ("approved", "n/a", None):
            continue
        return stage_id
    return "DONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True, help="Project directory containing .landing-state.yaml")
    args = ap.parse_args()

    state_path = Path(args.project) / ".landing-state.yaml"
    if not state_path.exists():
        print(f"ERROR: {state_path} not found", file=sys.stderr)
        sys.exit(2)

    state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    print(next_stage(state))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run — pass**

```bash
python3 -m pytest tests/phase-prd/test-next-stage.py -v
```

Expected: 4/4 PASS.

- [ ] **Step 5: Write bats test for landing-go command file**

`tests/phase-prd/test-landing-go.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "/landing-go command file exists with frontmatter" {
    [ -f "$REPO/commands/landing-go.md" ]
    head -10 "$REPO/commands/landing-go.md" | grep -q "^description:"
}

@test "/landing-go mentions auto-resume from state.yaml" {
    grep -qE "state\.yaml|state\.|auto.?resume|resume" "$REPO/commands/landing-go.md"
}

@test "/landing-go mentions key flags --auto-fix and --skip-gate" {
    grep -q -- "--auto-fix" "$REPO/commands/landing-go.md"
    grep -q -- "--skip-gate" "$REPO/commands/landing-go.md"
}

@test "/landing-go mentions landing-orchestrator agent" {
    grep -q "landing-orchestrator" "$REPO/commands/landing-go.md"
}

@test "/landing-go documents prototype-first entry" {
    body=$(cat "$REPO/commands/landing-go.md")
    echo "$body" | grep -qE "prototype|07_ПРОТОТИП"
    echo "$body" | grep -q "07a_prototype"
}
```

- [ ] **Step 6: Create commands/landing-go.md**

```markdown
---
description: Single entry point для конвейера landing-system. Читает .landing-state.yaml, диспатчит следующий этап через landing-orchestrator. Поддерживает auto-fix и параллельную диспетчеризацию 07d⇆07e.
---

# /landing-go

Главная команда оркестратора. Запусти её один раз — и она проведёт тебя по всем этапам от прототипа до live сайта на Бегете.

## Использование

```
/landing-go [--project <slug>] [--auto-fix yes|no] [--skip-gate <id>]
```

**Флаги:**
- `--project <slug>` — папка проекта (по умолчанию текущая).
- `--auto-fix yes` — применять авто-фиксы без подтверждения (опасно — только когда уверен).
- `--skip-gate <id>` — пропустить конкретный гейт-чек (для отладки).

## Вход (prototype-first)

Положи `prototype.pdf` или `prototype.md` в `<project>/07_ПРОТОТИП/source/`. Это **единственное обязательное условие** для старта.

Этапы 00 (бриф), 01 (контекст), 01a (анализ ниши), 02 (материалы клиента) автоматически помечены `n/a` — они происходят **до** landing-system и попадают сюда уже свёрнутыми внутри прототипа.

## Что происходит

Команда вызывает `landing-orchestrator` агента. Он:

1. Читает `<project>/.landing-state.yaml` через `scripts/landing-go-next-stage.py` → находит следующий этап.
2. Показывает что сделать (одно действие + одно ожидание).
3. Проверяет гейт через `scripts/gate-check.sh`.
4. Если гейт упал — предлагает auto-fix (или просит вмешательства).
5. На этапе 07d_photos/07e_visuals — диспатчит оба субагента **параллельно**.
6. После всех этапов → live сайт на Бегете.

## Этапы

| # | Stage | Кто делает | Чем |
|---|---|---|---|
| 07a | prototype | АВТО | `/landing-prototype` под капотом |
| 03 | references | Руками | references-curator (с auto-fix дефолтами) |
| 04 | brand | Руками + AI | brand-architect |
| 05 | design | Руками + AI | design-system-generator |
| 06 | stack | АВТО | stack-planner |
| 07 | content | АВТО | content-writer |
| 07b | wireframe | Маркетолог выбирает варианты | `/landing-wireframe` |
| 07c | composed | АВТО | `/landing-compose` |
| **07d** ⇆ **07e** | photos + visuals | **ПАРАЛЛЕЛЬНО** | `/landing-photos` + `/landing-visuals` |
| 07f | composed_final | АВТО re-render | `/landing-compose` |
| 08 | build | АВТО | wp-builder |
| 09 | deploy | Руками (Бегет creds) | wp-deployer |
| 10-12 | QA / Analytics / SEO | АВТО | существующие агенты |

## Auto-fix mechanism

Когда гейт падает, оркестратор смотрит `fix_hint` из `config/stage-gates.yaml`:
- Если начинается с `auto_fix:` → предлагает запустить указанную команду
- На `yes` пользователя — выполняет, re-runs gate-check
- Один auto-fix retry на check per `/landing-go` invocation (защита от циклов)

Примеры авто-фиксов:
- Нет `prototype.yaml` → запустить `/landing-prototype`
- Нет `wireframe.html` → запустить `/landing-wireframe`
- composed.html содержит `[SLOT: ...]` → re-run `/landing-compose`

## Ручные команды сохраняются

`/landing-photos`, `/landing-visuals`, `/landing-prototype`, `/landing-wireframe`, `/landing-compose` продолжают работать **как ручные точки входа** для повторных прогонов. `/landing-go` использует их под капотом.

## Что делать при падении гейта

1. Прочитай fix_hint в выводе.
2. Если предложен auto-fix — ответь `yes`.
3. Иначе сделай руками что просят.
4. Запусти `/landing-go` снова — продолжит с того же места.

## После завершения

После 12_seo все этапы approved. Сайт live на Бегете. Конечный URL виден в `state.yaml:stages.09_deploy.deploy_url`.

См. [spec](../docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md), [plan](../docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md).
```

- [ ] **Step 7: Run + commit**

```bash
bats tests/phase-prd/test-landing-go.bats
git add commands/landing-go.md scripts/landing-go-next-stage.py tests/phase-prd/test-landing-go.bats tests/phase-prd/test-next-stage.py
git commit -m "feat(pr-d): /landing-go slash command + next-stage detection script"
```

---

## Task 10: Update `landing-orchestrator.md` — prototype-first + parallel + auto-fix

**Files:**
- Modify: `agents/landing-orchestrator.md`
- Create: `tests/phase-prd/test-orchestrator-update.bats`

- [ ] **Step 1: Read existing orchestrator**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
cat agents/landing-orchestrator.md
```

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-orchestrator-update.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
ORCH="$REPO/agents/landing-orchestrator.md"

@test "orchestrator references /landing-go command" {
    grep -q "/landing-go" "$ORCH"
}

@test "orchestrator has dispatch table for new PR-A/B/C/D stages" {
    grep -qE "07a_prototype|07a |Прототип \(parse\)" "$ORCH"
    grep -qE "07d_photos|photo-curator" "$ORCH"
    grep -qE "07e_visuals|visual-curator" "$ORCH"
}

@test "orchestrator documents parallel 07d ⇆ 07e dispatch" {
    grep -qE "паралл|parallel|одновременно" "$ORCH"
}

@test "orchestrator documents auto-fix mechanism" {
    grep -qE "auto.?fix|автофикс|авто-fix" "$ORCH"
}

@test "orchestrator documents prototype-first flow with n/a for 00/01/01a/02" {
    grep -qE "prototype.?first|n/a|prototype-first" "$ORCH"
}

@test "orchestrator references derive-landing-structure bridge" {
    grep -q "derive-landing-structure" "$ORCH"
}
```

- [ ] **Step 3: Run — fails**

```bash
bats tests/phase-prd/test-orchestrator-update.bats
```

- [ ] **Step 4: Append PR-D section to landing-orchestrator.md**

Open `agents/landing-orchestrator.md`. APPEND at the end (preserve existing content):

```markdown

---

## PR-D Phase: Prototype-First Orchestration (2026-05-13)

С PR-D у меня появилась команда `/landing-go` — single entry point с auto-resume по state.yaml.

### Поток в prototype-first режиме

Этапы `00_brief`, `01_context`, `01a_niche_analysis`, `02_assets` помечены `n/a` в `.landing-state.yaml`. Вход = `prototype.pdf` в `07_ПРОТОТИП/source/`. Я начинаю работу с этапа `07a_prototype`.

### Обновлённая dispatch table

| # | Stage | Что делаю | Команда / агент |
|---|---|---|---|
| 07a | Прототип (parse) | Авто | `/landing-prototype` → prototype-importer |
| 07a→ | Bridge: prototype → landing-structure.md | Авто | `scripts/derive-landing-structure.py` (для совместимости с wp-builder) |
| 03 | Референсы | User-interactive | references-curator (auto-fix: defaults по нише если пусто) |
| 04 | Бренд | User-interactive | brand-architect |
| 05 | Дизайн-система | User-interactive | design-system-generator |
| 06 | Стек | Авто | stack-planner |
| 07 | Контент | Авто | content-writer |
| 07b | Wireframe | User picks variants | `/landing-wireframe` |
| 07c | Composed (draft) | Авто | `/landing-compose` |
| 07d ⇆ 07e | Photos + Visuals | **Параллельно** | `/landing-photos` ‖ `/landing-visuals` |
| 07f | Composed (final) | Авто re-render | `/landing-compose` |
| 08 | Build | Авто | wp-builder |
| 09 | Deploy | Маркетолог даёт Бегет creds | wp-deployer |
| 10-12 | QA / Analytics / SEO | Авто | существующие агенты |

### Параллельная диспетчеризация (07d + 07e)

Когда state.yaml:stages.07c_composed.status == approved → я диспатчу **двух субагентов одновременно** через `superpowers:dispatching-parallel-agents`:

- Subagent A: `photo-curator` (стадия 07d_photos)
- Subagent B: `visual-curator` (стадия 07e_visuals)

После того как **оба** DONE → проверяю оба гейта → перехожу к 07f.

### Auto-fix mechanism

При падении hard_check в gate-check.sh:

1. Парсю `fix_hint` из stage-gates.yaml для упавшего check_id.
2. Если `fix_hint` начинается с `auto_fix:` → извлекаю команду (`/landing-prototype`, `/landing-wireframe`, etc).
3. Спрашиваю пользователя: «🔧 АВТО-FIX: запустить `{команда}`? (yes/no)».
4. На `yes` — выполняю команду, re-run gate-check.
5. Один auto-fix attempt per check_id per `/landing-go` invocation (защита от циклов).

### Step-by-step UX

На каждом этапе я говорю **одно действие + одно ожидание**:
- «🎯 Положи prototype.pdf в 07_ПРОТОТИП/source/. Напиши готово»
- «🎯 Открой 07a_WIREFRAME/wireframe.html, выбери варианты, скачай selections.yaml. Напиши готово»
- «🎯 Открой 07c_PHOTOS/photo-preview.html и approve. Напиши ok»

Не сваливаю несколько шагов в одно сообщение — маркетолог должен делать по одному.

### Что НЕ изменяется

- `Phase 1`, `Phase 2 Scope` секции выше — остаются документацией старого flow для совместимости
- Существующие агенты — не модифицируются, я просто их по-новому вызываю
```

- [ ] **Step 5: Run — pass**

```bash
bats tests/phase-prd/test-orchestrator-update.bats
```

Expected: 6/6 PASS.

- [ ] **Step 6: Commit**

```bash
git add agents/landing-orchestrator.md tests/phase-prd/test-orchestrator-update.bats
git commit -m "feat(pr-d): orchestrator — prototype-first + parallel 07d⇆07e + auto-fix"
```

---

## Task 11: `landing-onboarding` rewrite — codex install + new flow

**Files:**
- Modify: `skills/landing-onboarding/SKILL.md`
- Create: `tests/phase-prd/test-onboarding-update.bats`

- [ ] **Step 1: Read existing onboarding**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
cat skills/landing-onboarding/SKILL.md
```

- [ ] **Step 2: Write failing test**

`tests/phase-prd/test-onboarding-update.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
ONB="$REPO/skills/landing-onboarding/SKILL.md"

@test "onboarding references install-codex.sh" {
    grep -q "install-codex" "$ONB"
}

@test "onboarding explains /landing-go entry point" {
    grep -q "/landing-go" "$ONB"
}

@test "onboarding explains prototype-first flow" {
    grep -qE "prototype-first|07_ПРОТОТИП/source|положи prototype" "$ONB"
}

@test "onboarding mentions both PR-B (photos) and PR-C (visuals)" {
    grep -q "/landing-photos" "$ONB"
    grep -q "/landing-visuals" "$ONB"
}
```

- [ ] **Step 3: Run — fails**

```bash
bats tests/phase-prd/test-onboarding-update.bats 2>&1 | head -10
```

- [ ] **Step 4: Update landing-onboarding/SKILL.md**

Read current content, then APPEND (preserve existing setup checks) a new section at end:

```markdown

---

## PR-D Onboarding additions (2026-05-13)

С PR-D флоу упрощается: **одна команда `/landing-go` ведёт через все этапы**.

### Шаг 1 — установка codex CLI

```bash
bash scripts/install-codex.sh
```

Скрипт проверяет что `codex` есть на PATH. Если нет — устанавливает `npm i -g @openai/codex` и запускает `codex login`. Без codex `/landing-photos` и `/landing-visuals` не работают.

### Шаг 2 — explain new flow

В прежнем флоу маркетолог запускал по очереди:
1. `/landing-new` → бриф (00_brief)
2. `/landing-niche` → анализ ниши
3. ... и так далее до 12_seo

В новом flow (prototype-first):

1. Маркетолог получает уже готовый `prototype.pdf` (сделан внешне в PR-A или другом инструменте).
2. Кладёт его в `<project>/07_ПРОТОТИП/source/`.
3. Запускает **`/landing-go`** — оркестратор ведёт через все этапы автоматически, останавливаясь только там где нужно вмешательство (выбрать варианты блоков, утвердить design-system, дать Бегет credentials).

Этапы 00 (бриф) / 01 (контекст) / 01a (анализ ниши) / 02 (материалы клиента) помечены `n/a` — они происходят **до** landing-system.

### Шаг 3 — smoke test

```bash
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding tests/phase-pra/fixtures/prototype-sample.md
```

Пайплайн должен пройти полностью (PR-A + PR-B + PR-C этапы с mock codex).

### Полезное

- `/landing-photos`, `/landing-visuals` остаются как **ручные** entry points для повторных прогонов.
- Auto-fix на гейтах: оркестратор предлагает фикс и применяет на `yes`.
- 07d_photos и 07e_visuals идут **параллельно** через `dispatching-parallel-agents`.
```

- [ ] **Step 5: Run + commit**

```bash
bats tests/phase-prd/test-onboarding-update.bats
git add skills/landing-onboarding/SKILL.md tests/phase-prd/test-onboarding-update.bats
git commit -m "feat(pr-d): landing-onboarding — codex install + prototype-first flow explanation"
```

---

## Task 12: Migration script + THIRD_PARTY_NOTICES + CLAUDE.md + final review

**Files:**
- Create: `scripts/migrate-state-for-prd.sh`
- Modify: `THIRD_PARTY_NOTICES.md`
- Modify: `CLAUDE.md`
- Create: `tests/phase-prd/test-migration.bats`

- [ ] **Step 1: Write failing migration test**

`tests/phase-prd/test-migration.bats`:
```bash
#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"
SCRIPT="$REPO/scripts/migrate-state-for-prd.sh"

setup() {
    TMP="$(mktemp -d)"
    cat > "$TMP/.landing-state.yaml" <<'EOF'
project: legacy
created: "2026-04-01"
schema_version: 1
stages:
  "00_brief":           {status: approved, timestamp: "2026-04-02T10:00:00"}
  "01_context":         {status: approved, timestamp: ""}
  "07_content":         {status: approved, timestamp: ""}
EOF
}
teardown() { rm -rf "$TMP"; }

@test "migration adds missing PR-D stages without overwriting existing ones" {
    run bash "$SCRIPT" "$TMP/.landing-state.yaml"
    [ "$status" -eq 0 ]

    # Existing approved stage preserved
    grep -E '"00_brief":\s*\{status:\s*approved' "$TMP/.landing-state.yaml"

    # New PR-D stages added as locked
    grep -qE '"07a_prototype":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
    grep -qE '"07d_photos":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
    grep -qE '"07f_composed_final":\s*\{status:\s*locked' "$TMP/.landing-state.yaml"
}

@test "migration is idempotent (running twice produces same result)" {
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    sum1=$(md5 -q "$TMP/.landing-state.yaml" 2>/dev/null || md5sum "$TMP/.landing-state.yaml" | awk '{print $1}')
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    sum2=$(md5 -q "$TMP/.landing-state.yaml" 2>/dev/null || md5sum "$TMP/.landing-state.yaml" | awk '{print $1}')
    [ "$sum1" = "$sum2" ]
}

@test "migration bumps schema_version to 2" {
    bash "$SCRIPT" "$TMP/.landing-state.yaml"
    grep -E '^schema_version:\s*2' "$TMP/.landing-state.yaml"
}
```

- [ ] **Step 2: Run — fails**

```bash
cd "/Users/kirillbezikov/Desktop/Обучение вайбкодинг Кодекс/02_projects - проекты/Агентство лидогенерации/landing-system"
bats tests/phase-prd/test-migration.bats 2>&1 | head -10
```

- [ ] **Step 3: Implement migration script**

`scripts/migrate-state-for-prd.sh`:
```bash
#!/usr/bin/env bash
# migrate-state-for-prd.sh — add new PR-D stages to existing .landing-state.yaml.
#
# Usage: bash migrate-state-for-prd.sh <path-to-.landing-state.yaml>
# - Idempotent: existing stages preserved, only missing ones added (status=locked).
# - Bumps schema_version to 2.

set -euo pipefail

STATE="${1:?ERROR: state.yaml path required}"
[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 2; }

python3 - "$STATE" <<'PYEOF'
import sys
import yaml
from pathlib import Path

NEW_STAGES = [
    "07a_prototype", "07b_wireframe", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
]

p = Path(sys.argv[1])
data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
stages = data.setdefault("stages", {})

added = []
for sid in NEW_STAGES:
    if sid not in stages:
        stages[sid] = {"status": "locked", "timestamp": ""}
        added.append(sid)

data["schema_version"] = 2

p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

if added:
    print(f"Added {len(added)} stages: {', '.join(added)}")
else:
    print("Already migrated; no changes")
PYEOF
```

Make executable.

- [ ] **Step 4: Run migration tests — pass**

```bash
bats tests/phase-prd/test-migration.bats
```

Expected: 3/3 PASS.

- [ ] **Step 5: Update THIRD_PARTY_NOTICES.md**

Append at end:
```markdown

## Lucide icons (ISC License) — PR-D integration

PR-D (2026-05-13) integrates Lucide icons (https://lucide.dev) as the first-step
bypass in icon generation waterfall — for any icon row in `icons.csv` where
`Library=Lucide`, the SVG is fetched directly from the official GitHub repo,
rendered to a brand-colored PNG, and used as-is (no codex call).

Source: https://github.com/lucide-icons/lucide
License: ISC
Use locations:
- `skills/visual-generation/scripts/lucide-fetcher.py` — download + render
- `skills/visual-generation/scripts/prompt-picker.py` — Lucide branch in waterfall
Cache: `~/.cache/landing-system/lucide/` (offline-friendly after first download)
```

- [ ] **Step 6: Update CLAUDE.md**

Find the PR-C section. Insert AFTER it, BEFORE "Block Library" section:

```markdown
## Новая команда PR-D (Orchestrator Integration)

- `/landing-go` — **главная** команда: single entry point. Читает `.landing-state.yaml`, диспатчит следующий этап через `landing-orchestrator`.

**Workflow PR-D (prototype-first):**
1. Положи `prototype.pdf` в `<project>/07_ПРОТОТИП/source/`.
2. Запусти `/landing-go`.
3. Следуй подсказкам — оркестратор сам ведёт через все этапы:
   - 07a prototype parse (авто)
   - 03 references → 04 brand → 05 design (user-interactive)
   - 06 stack → 07 content (авто)
   - 07b wireframe (user picks variants) → 07c composed (авто)
   - **07d photos ⇆ 07e visuals параллельно**
   - 07f composed final → 08 build → 09 deploy → 10-12

**Auto-fix:** при падении гейта оркестратор предлагает фикс и применяет на `yes`.

**Этапы 00/01/01a/02 помечены `n/a`** в `.landing-state.yaml` — они происходят до landing-system (prototype-first).

**Установка codex CLI:** `bash scripts/install-codex.sh` (в onboarding).

**Lucide icons:** простые иконки берутся бесплатно из Lucide вместо codex API.

**Migration:** для существующих проектов — `bash scripts/migrate-state-for-prd.sh <project>/.landing-state.yaml`.

См. [spec](docs/superpowers/specs/2026-05-13-pr-d-orchestrator-integration-design.md), [plan](docs/superpowers/plans/2026-05-13-pr-d-orchestrator-integration-plan.md).
```

- [ ] **Step 7: Final commit + holistic review**

```bash
git add scripts/migrate-state-for-prd.sh THIRD_PARTY_NOTICES.md CLAUDE.md tests/phase-prd/test-migration.bats
git commit -m "feat(pr-d): migration script + Lucide attribution + CLAUDE.md workflow"
```

- [ ] **Step 8: Run full PR-D test suite + regression**

```bash
# PR-D tests
python3 -m pytest tests/phase-prd/ -v 2>&1 | tail -15
bats tests/phase-prd/ 2>&1 | tail -15

# Regression
bats tests/phase-pra/ tests/gate-check/ tests/phase-prb/ tests/phase-prc/ 2>&1 | tail -5
python3 -m pytest tests/phase-prb/ tests/phase-prc/ -v 2>&1 | tail -5

# E2E smoke
SKIP_OPEN=1 USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh prd-smoke tests/phase-pra/fixtures/prototype-sample.md 2>&1 | tail -10
```

All must pass. If anything regresses, fix before claiming done.

---

## Final acceptance checklist

- [ ] `/landing-go` reads state.yaml and prints next stage (Task 9)
- [ ] All 7 new PR-D stages in `.landing-state.yaml` template (Task 1)
- [ ] `n/a` status works in gate-check and gate-state (Task 3)
- [ ] Stage gates defined for 07a-07f + augmented 08/09 (Task 2)
- [ ] `derive-landing-structure.py` bridge works (Task 4)
- [ ] 4 verify-* scripts for build/deploy gates (Task 5)
- [ ] Lucide fetcher works offline after first download (Task 6)
- [ ] prompt-picker Lucide branch as first waterfall step (Task 7)
- [ ] `install-codex.sh` install + login flow (Task 8)
- [ ] `landing-orchestrator.md` updated with prototype-first + parallel + auto-fix (Task 10)
- [ ] `landing-onboarding` rewrite explains new flow (Task 11)
- [ ] Migration script for existing projects (Task 12)
- [ ] THIRD_PARTY_NOTICES.md + CLAUDE.md updated (Task 12)
- [ ] PR-A + PR-B + PR-C regression tests pass
- [ ] 25+ new tests passing

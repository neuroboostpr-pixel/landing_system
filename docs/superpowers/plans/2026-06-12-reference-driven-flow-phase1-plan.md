# Reference-Driven Flow — Phase 1 (Zone E: архив + единый источник этапов)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Выполнить зону E спеки [2026-06-12-reference-driven-flow-spec.md](../specs/2026-06-12-reference-driven-flow-spec.md): перенести блочный трек в `archive/` (E2), не задев переиспользуемое (`_styles`, `_shapes`, `_patterns`, `_assets`, slot-формат, Lazy Blocks, фото-пайплайн), и свести список этапов к одному источнику истины `config/stages.yaml` (E1).

**Architecture:** Архив = `archive/` в корне репо, перенос через `git mv` (история сохраняется). Guard-тест запрещает живому коду ссылаться на архив. Единый источник этапов = `config/stages.yaml` + хелпер `scripts/stages.py`; bash-скрипты и python-диспетчер читают порядок оттуда, хардкод-массивы удаляются.

**Tech Stack:** Python 3 + pytest, bash, yq, git mv.

**Scope:** только зона E. Зоны A (прототип), B (декор/премиум), C (сборка WP), D (картинки) — отдельные планы (Phase 2+).

**Ключевые решения (зафиксированы исследованием кодовой базы):**

| Вопрос | Решение | Почему |
|---|---|---|
| `block-library/_patterns/` | СОХРАНИТЬ | читается `skills/wp-gutenberg-block-builder/scripts/generate-theme.py` (stage 08, живой) |
| `block-library/_assets/` | СОХРАНИТЬ | читается `skills/block-composition/scripts/inject-content.py:331` |
| `scripts/generate-wp-blocks.py` | СОХРАНИТЬ | живой stage 08 (landing-build, wp-builder, stage-gates) |
| `skills/block-composition/` | СОХРАНИТЬ (переходно) | `inject-tokens.py` нужен mood-переключателю (спека §2.5); переписывается в Zone C |
| `enrich-quiz-funnel.py` | ПЕРЕНЕСТИ в `skills/prototype-import/scripts/` | вызывается живым агентом prototype-importer, а лежит в архивируемом скилле |
| Этап `07b_wireframe` | УДАЛИТЬ из stage-gates/state/порядков | wireframe-этап целиком ВЫБРОСИТЬ (спека §6) |
| `03b_visual_concept` | ДОБАВИТЬ в канон | есть в stage-gates.yaml, но отсутствует в template-state и порядках — это и есть рассинхрон E1 |
| Порядок 09/10 | `09_deploy` → `10_qa` | qa-auditor проверяет живой сайт «during stage 10 after /landing-deploy»; gate-check.sh и render-pipeline-map.sh ставили 10 перед 09 ошибочно |

**Канонический порядок этапов (21):**
`00_brief, 01_context, 01a_niche_analysis, 02_assets, 03_references, 03b_visual_concept, 04_brand, 05_design, 06_stack, 07_content, 07a_prototype, 07c_composed, 07d_photos, 07e_visuals, 07f_composed_final, 08_build, 08b_style, 09_deploy, 10_qa, 11_analytics, 12_seo`

---

### Task 1: Каркас архива + pytest-изоляция

**Files:**
- Create: `archive/README.md`
- Modify: `pytest.ini`

- [ ] **Step 1: Создать archive/README.md**

```markdown
# Архив блочного трека

Сюда перенесено наследие «блочного» способа производства лендингов
(подбор готовых блоков из библиотеки + wireframe-выбор вариантов).

**Почему:** система переведена на reference-driven флоу — агент рисует макет
сам по прототипу и референсу клиента. Канон:
`docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md`, раздел 6.

**Что здесь лежит:**
- `block-library/` — ~178 готовых блоков, каталог, таксономия, галерея
- `skills/` — wireframe-rendering, landing-import-blocks, block-library-management
- `commands/` — /landing-wireframe, /landing-import-blocks
- `agents/` — ux-composer
- `scripts/` — генераторы каталога/галереи, нормализаторы блоков
- `tests/` — тесты блочного трека
- `template/` — папка 07a_WIREFRAME из шаблона проекта

**НЕ здесь (переиспользуется новым флоу, лежит на старых местах):**
`block-library/_styles/`, `_shapes/`, `_patterns/`, `_assets/`,
slot-формат `{{slot:name}}`, Lazy Blocks, плагин lp-preview-panel, фото-пайплайн.

Код в архиве не поддерживается и не запускается. Не импортировать из live-кода —
это проверяет `tests/archive/test_no_block_track_refs.py`.
```

- [ ] **Step 2: Изолировать архив от pytest** — в `pytest.ini` добавить строку:

```ini
[pytest]
# Support both test_*.py (pytest default) and test-*.py (our convention)
python_files = test_*.py test-*.py
testpaths = tests
pythonpath = .
norecursedirs = archive .claude node_modules
```

- [ ] **Step 3: Commit**

```bash
git add archive/README.md pytest.ini
git commit -m "chore(archive): scaffold archive/ for block-track retirement (E2)"
```

---

### Task 2: Guard-тест «живой код не ссылается на блочный трек» (failing)

**Files:**
- Create: `tests/archive/test_no_block_track_refs.py`

- [ ] **Step 1: Написать тест**

```python
"""E2: блочный трек в архиве — живой код не должен на него ссылаться.

Сканируются исполняемые/конфигурационные зоны. docs/, wiki/, archive/ —
вне скоупа (история легальна). skills/block-composition исключён осознанно:
переходный код, переписывается в Zone C (см. план Phase 1, решения).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ["agents", "skills", "scripts", "commands", ".claude/commands",
             "config", "template"]
SCAN_FILES = ["CLAUDE.md"]
EXCLUDE_PARTS = {"block-composition", "worktrees", "node_modules", "__pycache__"}

FORBIDDEN = [
    "skills/wireframe-rendering",
    "skills/landing-import-blocks",
    "skills/block-library-management",
    "render-wireframe.py",
    "match-candidates.py",
    "generate-gallery.py",
    "normalize-block-templates.py",
    "block-library/catalog.yaml",
    "block-library/taxonomy.yaml",
    "landing-wireframe",
    "landing-import-blocks",
    "ux-composer",
    "07b_wireframe",
    "07a_WIREFRAME",
]

EXTS = {".md", ".py", ".sh", ".yaml", ".yml", ".html", ".json", ".bats"}


def _iter_files():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in EXTS and not (EXCLUDE_PARTS & set(p.parts)):
                yield p
    for f in SCAN_FILES:
        p = ROOT / f
        if p.exists():
            yield p


def test_no_references_to_archived_block_track():
    violations = []
    for p in _iter_files():
        text = p.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN:
            if token in text:
                violations.append(f"{p.relative_to(ROOT)}: {token}")
    assert not violations, (
        "Живой код ссылается на архивированный блочный трек:\n" + "\n".join(violations)
    )
```

- [ ] **Step 2: Убедиться, что тест падает**

Run: `python3 -m pytest tests/archive/test_no_block_track_refs.py -v`
Expected: FAIL — десятки violations (skills/wireframe-rendering существует, команды, stage-gates и т.д.)

- [ ] **Step 3: Commit (red)**

```bash
git add tests/archive/test_no_block_track_refs.py
git commit -m "test(E2): guard — live code must not reference archived block track (red)"
```

---

### Task 3: Перенос block-library в архив (кроме `_styles`, `_shapes`, `_patterns`, `_assets`)

**Files:**
- Move: `block-library/<15 категорий>`, `catalog.yaml`, `taxonomy.yaml`, `gallery.html`, `dedup-report.html`, `keep-list.yaml`, `migration-map.yaml`, `migration-report-b34.md`, старый `README.md` → `archive/block-library/`
- Create: новый `block-library/README.md`

- [ ] **Step 1: git mv категорий и каталогов**

```bash
mkdir -p archive/block-library
cd block-library
git mv contacts faq features footer gallery header hero menu pricing process \
       quiz references social-proof team trust \
       catalog.yaml taxonomy.yaml gallery.html dedup-report.html \
       keep-list.yaml migration-map.yaml migration-report-b34.md README.md \
       ../archive/block-library/
cd ..
```

- [ ] **Step 2: Новый block-library/README.md**

```markdown
# block-library — переиспользуемые ресурсы дизайна

Библиотека готовых блоков выведена из эксплуатации и лежит в
`archive/block-library/` (см. спеку reference-driven flow, раздел 6).

Здесь остались только ресурсы, которые нужны новому флоу:

- `_styles/` — 6 цветовых наборов (mood). Работают как переключатель палитры
  уровня темы/сайта (спека §2.5). Читается `inject-tokens.py` и `generate-theme.py`.
- `_shapes/` — 18 фигур. ТОЛЬКО подсказка-палитра для генерации декора (§3.1):
  агент генерирует формы под проект, не вставляет файлы как есть.
- `_patterns/` — премиум-эффекты, читаются `generate-theme.py` (stage 08).
- `_assets/` — вспомогательные ассеты, читаются `inject-content.py`.
```

- [ ] **Step 3: Проверить, что сохранённые папки на месте**

Run: `ls block-library/`
Expected: `README.md _assets _patterns _shapes _styles` — и ничего больше.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore(E2): archive block-library catalog (keep _styles/_shapes/_patterns/_assets)"
```

---

### Task 4: Перенос enrich-quiz-funnel в prototype-import, затем архив скиллов

**Files:**
- Move: `skills/wireframe-rendering/scripts/enrich-quiz-funnel.py` → `skills/prototype-import/scripts/enrich-quiz-funnel.py`
- Modify: `agents/prototype-importer.md`, `scripts/test-pipeline.sh`, `tests/phase-pra/test-enrich-quiz-funnel.bats`, `tests/phase-pra/README.md`
- Move: `skills/wireframe-rendering/`, `skills/landing-import-blocks/`, `skills/block-library-management/` → `archive/skills/`

- [ ] **Step 1: Перенести enrich-quiz-funnel.py**

```bash
git mv skills/wireframe-rendering/scripts/enrich-quiz-funnel.py \
       skills/prototype-import/scripts/enrich-quiz-funnel.py
```

- [ ] **Step 2: Обновить все ссылки на старый путь**

```bash
grep -rln "wireframe-rendering/scripts/enrich-quiz-funnel" \
    agents/ scripts/ commands/ .claude/commands/ tests/ skills/ config/ \
  | xargs sed -i '' 's|skills/wireframe-rendering/scripts/enrich-quiz-funnel|skills/prototype-import/scripts/enrich-quiz-funnel|g'
```

- [ ] **Step 3: Прогнать bats-тест enrich**

Run: `bats tests/phase-pra/test-enrich-quiz-funnel.bats`
Expected: PASS (путь обновлён). Если bats не установлен — `python3 -m pytest tests/prototype-import/ -v` как smoke и пометить в логе.

- [ ] **Step 4: Архивировать три скилла**

```bash
mkdir -p archive/skills
git mv skills/wireframe-rendering archive/skills/
git mv skills/landing-import-blocks archive/skills/
git mv skills/block-library-management archive/skills/
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore(E2): archive wireframe/import-blocks/block-library-management skills; relocate enrich-quiz-funnel to prototype-import"
```

---

### Task 5: Архив команд, агента ux-composer, скриптов блочного трека

**Files:**
- Move: `commands/landing-wireframe.md`, `commands/landing-import-blocks.md`, `.claude/commands/landing-wireframe.md`, `.claude/commands/landing-import-blocks.md` → `archive/commands/`
- Move: `agents/ux-composer.md` → `archive/agents/`
- Move: скрипты блочного трека → `archive/scripts/`
- Move: `template/07a_WIREFRAME/` → `archive/template/07a_WIREFRAME/`

- [ ] **Step 1: Команды и агент**

```bash
mkdir -p archive/commands archive/agents archive/scripts archive/template
git mv commands/landing-wireframe.md archive/commands/landing-wireframe.md
git mv commands/landing-import-blocks.md archive/commands/landing-import-blocks.md
git mv .claude/commands/landing-wireframe.md archive/commands/dot-claude-landing-wireframe.md
git mv .claude/commands/landing-import-blocks.md archive/commands/dot-claude-landing-import-blocks.md
git mv agents/ux-composer.md archive/agents/ux-composer.md
```

- [ ] **Step 2: Скрипты блочного трека** (каждый перед переносом проверить grep'ом, что не используется живым кодом — `grep -rn "<имя>" agents/ skills/ commands/ .claude/commands/ config/ scripts/ --include="*.md" --include="*.py" --include="*.sh" --include="*.yaml" | grep -v archive`):

```bash
cd scripts
git mv apply-taxonomy.py block-loader.py block-loader.py.doc.md \
       fix-display-names.py generate-catalog.py generate-gallery.py \
       migrate-blocks-to-wireframe-format.py migrate-blocks-to-wireframe-format.py.doc.md \
       normalize-block-colors.py normalize-block-templates.py \
       preview-blocks-library.py preview-blocks-library.py.doc.md \
       rebuild-catalog.py reclassify-blocks-taxonomy.py \
       refresh-catalog.py refresh-catalog.py.doc.md \
       restore_block_templates.py import-blocks \
       ../archive/scripts/
cd ..
```

ВАЖНО: `generate-wp-blocks.py` НЕ переносить (живой stage 08).

- [ ] **Step 3: Шаблонная папка wireframe**

```bash
git mv template/07a_WIREFRAME archive/template/07a_WIREFRAME
```

- [ ] **Step 4: Обновить scripts/test-pipeline.sh** — удалить шаги, запускающие render-wireframe/match-candidates/галерею (найти: `grep -n "wireframe\|gallery\|catalog" scripts/test-pipeline.sh`), оставив остальной конвейер нетронутым.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore(E2): archive block-track commands, ux-composer agent, scripts, template wireframe dir"
```

---

### Task 6: Архив тестов блочного трека

**Files:**
- Move: `tests/block-library/` → `archive/tests/block-library/`
- Move: wireframe-тесты из `tests/phase-pra/` (те, что зовут render-wireframe/match-candidates) → `archive/tests/phase-pra/`

- [ ] **Step 1: Перенести tests/block-library целиком**

```bash
mkdir -p archive/tests
git mv tests/block-library archive/tests/block-library
```

- [ ] **Step 2: Найти и перенести wireframe-тесты в других папках**

```bash
grep -rln "render-wireframe\|match-candidates\|wireframe-shell\|generate-gallery" tests/ | sort -u
```

Каждый найденный файл → `git mv` в `archive/tests/<та же подпапка>/`. Файлы, где упоминание только в комментарии/фикстуре, не относящейся к запуску архивных скриптов, — почистить упоминание вместо переноса.

- [ ] **Step 3: Прогнать живые тесты**

Run: `python3 -m pytest tests/ -x -q`
Expected: без collection errors; падения, связанные с 07b_wireframe в stage-конфигах, чинятся в Task 7 (если есть — зафиксировать список).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore(E2): archive block-track tests"
```

---

### Task 7: Удалить этап 07b_wireframe из конфигов и состояния

**Files:**
- Modify: `config/stage-gates.yaml`
- Modify: `template/.landing-state.yaml`
- Modify: `scripts/migrate-state-for-prd.sh`
- Modify: `tests/phase-prd/test-next-stage.py` (если ссылается)

- [ ] **Step 1: config/stage-gates.yaml** — удалить целиком блок `"07b_wireframe":` (от `  "07b_wireframe":` до строки перед `  "07c_composed":`). В `"07c_composed"` заменить:

```yaml
    require_approved: ["05_design", "07a_prototype", "07b_wireframe"]
```
на:
```yaml
    require_approved: ["05_design", "07a_prototype"]
```

Проверить остальные require_approved: `grep -n "07b_wireframe" config/stage-gates.yaml` → должно быть пусто.

- [ ] **Step 2: template/.landing-state.yaml** — удалить строку `"07b_wireframe":        {status: locked, timestamp: ""}`, добавить `03b_visual_concept` после `03_references`:

```yaml
  # User-interactive design stages
  "03_references":        {status: locked, timestamp: ""}
  "03b_visual_concept":   {status: locked, timestamp: ""}
  "04_brand":             {status: locked, timestamp: ""}
  "05_design":            {status: locked, timestamp: ""}
```

И комментарий секции PR-A:

```yaml
  # PR-A artifacts (new in state tracking)
  "07a_prototype":        {status: in_progress, timestamp: ""}
  "07c_composed":         {status: locked, timestamp: ""}
```

- [ ] **Step 3: scripts/migrate-state-for-prd.sh** — из `NEW_STAGES` убрать `07b_wireframe` (миграция старых проектов больше не должна добавлять мёртвый этап; уже добавленные записи безвредны — диспетчер их игнорирует).

- [ ] **Step 4: Обновить tests/phase-prd/test-next-stage.py** — убрать `07b_wireframe` из фикстур/ожиданий (`grep -n "07b_wireframe" tests/`), ожидания перестроить под канонический порядок.

- [ ] **Step 5: Прогнать**

Run: `python3 -m pytest tests/phase-prd/ tests/gate-check/ -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(E2): remove 07b_wireframe stage from gates/state/migration; add 03b to state template"
```

---

### Task 8: Обновить CLAUDE.md, агентов и команды под новый флоу

**Files:**
- Modify: `CLAUDE.md`
- Modify: `agents/landing-orchestrator.md`, `commands/landing-go.md`, `.claude/commands/landing-go.md`, `commands/landing-help.md`/`.claude/commands/landing-help.md`, `commands/landing-compose.md` и прочие из grep

- [ ] **Step 1: Найти все живые упоминания**

```bash
grep -rn "landing-wireframe\|landing-import-blocks\|ux-composer\|07b_wireframe\|07a_WIREFRAME\|wireframe" \
  CLAUDE.md agents/ commands/ .claude/commands/ skills/ config/ template/ scripts/ \
  | grep -v archive | grep -v block-composition
```

- [ ] **Step 2: CLAUDE.md** — заменить секцию `## Block Library` на:

```markdown
## Архив блочного трека (reference-driven flow, 2026-06-12)

Библиотека готовых блоков и wireframe-этап выведены из эксплуатации и лежат в
`archive/` (история сохранена через git mv). Новый флоу: агент **рисует** макет
composed.html сам по прототипу и референсу клиента — канон:
[`docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md`](docs/superpowers/specs/2026-06-12-reference-driven-flow-spec.md).

Переиспользуемое (НЕ удалять): `block-library/_styles/` (палитры-moods),
`_shapes/` (подсказка для генерации декора), `_patterns/`, `_assets/`,
slot-формат `{{slot:name}}`, Lazy Blocks, плагин lp-preview-panel.

Guard: `tests/archive/test_no_block_track_refs.py` не даёт живому коду
ссылаться на архив.
```

В секции «Workflow PR-A» удалить шаги 4–5 про /landing-wireframe и mood-табы, заменив на: «Макет composed.html рисует агент по правилам спеки reference-driven (раздел 2–3); /landing-compose применяет токены и тексты». Секцию PR-S переписать: mood = только переключатель палитры уровня темы (lp-preview-panel + `_styles/`), mood-вкладки wireframe удалены. В списке wiki-источников строки про `block-library/*/*/meta.yaml` заменить на `block-library/_styles/**` + `_patterns/**`. В PR-D workflow строку «07b wireframe (user picks variants) → 07c composed (авто)» заменить на «07c composed (агент рисует макет)».

- [ ] **Step 3: agents/landing-orchestrator.md** — из mission-таблицы и диспатчей убрать wireframe/ux-composer; этап 07c composed диспатчится на block-composer.

- [ ] **Step 4: commands/landing-go.md + landing-help.md (+ зеркала в .claude/commands/)** — убрать /landing-wireframe и /landing-import-blocks из таблиц и подсказок.

- [ ] **Step 5: commands/landing-compose.md (+ зеркало)** — убрать требование selections.yaml (вход теперь prototype + design-tokens; машинная склейка блоков уходит в Zone C rework). Если команда жёстко зовёт compose-blocks.py с selections — пометить TODO ссылкой на Zone C план, но текст команды очистить от wireframe-шагов.

- [ ] **Step 6: Guard-тест должен стать зелёным**

Run: `python3 -m pytest tests/archive/test_no_block_track_refs.py -v`
Expected: PASS. Если остались violations — это точный список недочищенных файлов, дочистить.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "docs(E2): rewrite CLAUDE.md/orchestrator/commands for reference-driven flow; guard test green"
```

---

### Task 9: Тест единого источника этапов (E1, failing)

**Files:**
- Create: `tests/stages/test_stage_single_source.py`

- [ ] **Step 1: Написать тест**

```python
"""E1: единый источник истины списка этапов — config/stages.yaml.

Спека reference-driven flow, раздел 6 «список этапов рассинхронен»:
порядок этапов задан в одном месте, всё остальное читает оттуда.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
STAGES_YAML = ROOT / "config" / "stages.yaml"

EXPECTED_ORDER = [
    "00_brief", "01_context", "01a_niche_analysis", "02_assets",
    "03_references", "03b_visual_concept", "04_brand", "05_design",
    "06_stack", "07_content", "07a_prototype", "07c_composed",
    "07d_photos", "07e_visuals", "07f_composed_final",
    "08_build", "08b_style", "09_deploy", "10_qa", "11_analytics", "12_seo",
]


def canonical():
    return yaml.safe_load(STAGES_YAML.read_text(encoding="utf-8"))["stages"]


def test_canonical_file_well_formed():
    stages = canonical()
    ids = [s["id"] for s in stages]
    assert ids == EXPECTED_ORDER
    assert all(s.get("label") for s in stages), "у каждого этапа есть label"


def test_stages_py_prints_order():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "stages.py"), "--order"],
        capture_output=True, text=True, check=True,
    )
    assert out.stdout.split() == EXPECTED_ORDER


def test_stages_py_prints_labels():
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "stages.py"), "--labels"],
        capture_output=True, text=True, check=True,
    )
    lines = [l for l in out.stdout.splitlines() if l.strip()]
    assert len(lines) == len(EXPECTED_ORDER)
    assert all("\t" in l for l in lines)


def test_state_template_matches_canonical():
    state = yaml.safe_load(
        (ROOT / "template" / ".landing-state.yaml").read_text(encoding="utf-8")
    )
    assert list(state["stages"].keys()) == EXPECTED_ORDER


def test_stage_gates_keys_subset_of_canonical():
    gates = yaml.safe_load(
        (ROOT / "config" / "stage-gates.yaml").read_text(encoding="utf-8")
    )
    unknown = set(gates["stages"].keys()) - set(EXPECTED_ORDER)
    assert not unknown, f"stage-gates.yaml содержит этапы вне канона: {unknown}"


def test_no_hardcoded_order_in_bash_scripts():
    for script in ("gate-check.sh", "render-pipeline-map.sh"):
        text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
        assert "00_brief" not in text, f"{script} хардкодит список этапов"
        assert "stages.py" in text, f"{script} должен читать порядок из stages.py"


def test_next_stage_dispatcher_uses_canonical():
    text = (ROOT / "scripts" / "landing-go-next-stage.py").read_text(encoding="utf-8")
    assert "stages.yaml" in text
    assert "07b_wireframe" not in text
```

- [ ] **Step 2: Убедиться, что тест падает**

Run: `python3 -m pytest tests/stages/ -v`
Expected: FAIL — config/stages.yaml не существует, скрипты хардкодят порядок.

- [ ] **Step 3: Commit (red)**

```bash
git add tests/stages/test_stage_single_source.py
git commit -m "test(E1): single source of truth for stage list (red)"
```

---

### Task 10: config/stages.yaml + scripts/stages.py

**Files:**
- Create: `config/stages.yaml`
- Create: `scripts/stages.py`

- [ ] **Step 1: config/stages.yaml**

```yaml
# ЕДИНЫЙ ИСТОЧНИК ИСТИНЫ списка этапов пайплайна (E1, спека reference-driven flow §6).
#
# Все потребители обязаны читать порядок отсюда (через scripts/stages.py):
#   - scripts/gate-check.sh          (PIPELINE_ORDER)
#   - scripts/render-pipeline-map.sh (PIPELINE_ORDER + LABELS)
#   - scripts/landing-go-next-stage.py (STAGE_ORDER)
#   - template/.landing-state.yaml — генерится/сверяется тестом
# Добавляя этап: добавь его ЗДЕСЬ + в config/stage-gates.yaml (гейты) +
# в template/.landing-state.yaml. Тест: tests/stages/test_stage_single_source.py.
stages:
  - {id: 00_brief,            label: "Бриф"}
  - {id: 01_context,          label: "Контекст"}
  - {id: 01a_niche_analysis,  label: "Анализ ниши"}
  - {id: 02_assets,           label: "Материалы"}
  - {id: 03_references,       label: "Референсы"}
  - {id: 03b_visual_concept,  label: "Визуальная концепция"}
  - {id: 04_brand,            label: "Бренд"}
  - {id: 05_design,           label: "Дизайн-система"}
  - {id: 06_stack,            label: "Стек"}
  - {id: 07_content,          label: "Контент"}
  - {id: 07a_prototype,       label: "Прототип"}
  - {id: 07c_composed,        label: "Макет (composed)"}
  - {id: 07d_photos,          label: "Фото"}
  - {id: 07e_visuals,         label: "Иконки/чарты"}
  - {id: 07f_composed_final,  label: "Макет финальный"}
  - {id: 08_build,            label: "WP-сборка"}
  - {id: 08b_style,           label: "Style polish"}
  - {id: 09_deploy,           label: "Деплой"}
  - {id: 10_qa,               label: "QA"}
  - {id: 11_analytics,        label: "Аналитика"}
  - {id: 12_seo,              label: "SEO"}
```

- [ ] **Step 2: scripts/stages.py**

```python
#!/usr/bin/env python3
"""Единый источник списка этапов (E1). Читает config/stages.yaml.

Usage:
    python3 scripts/stages.py --order    # id по одному в строке
    python3 scripts/stages.py --labels   # id<TAB>label по одному в строке
"""
import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STAGES_YAML = ROOT / "config" / "stages.yaml"


def load_stages():
    data = yaml.safe_load(STAGES_YAML.read_text(encoding="utf-8"))
    return data["stages"]


def stage_ids():
    return [s["id"] for s in load_stages()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--order", action="store_true")
    group.add_argument("--labels", action="store_true")
    args = ap.parse_args()
    for s in load_stages():
        if args.labels:
            print(f"{s['id']}\t{s['label']}")
        else:
            print(s["id"])


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Частичная зелень**

Run: `python3 -m pytest tests/stages/ -v`
Expected: `test_canonical_file_well_formed`, `test_stages_py_prints_order`, `test_stages_py_prints_labels`, `test_stage_gates_keys_subset_of_canonical` — PASS; остальные ещё FAIL.

- [ ] **Step 4: Commit**

```bash
git add config/stages.yaml scripts/stages.py
git commit -m "feat(E1): canonical stage list config/stages.yaml + stages.py helper"
```

---

### Task 11: Переключить bash-скрипты на канон

**Files:**
- Modify: `scripts/gate-check.sh:124-129`
- Modify: `scripts/render-pipeline-map.sh:38-69`

- [ ] **Step 1: gate-check.sh** — заменить литеральный массив (строки 124–129):

```bash
# 1b. Soft-lock warning: для soft-этапов — если предыдущий по pipeline не approved
# Порядок этапов — из config/stages.yaml (E1, single source of truth)
PIPELINE_ORDER=()
while IFS= read -r _sid; do
    PIPELINE_ORDER+=("$_sid")
done < <(python3 "$SCRIPT_DIR/stages.py" --order)
```

Где `$SCRIPT_DIR` — существующая переменная скрипта с путём к scripts/ (проверить начало файла: `grep -n "SCRIPT_DIR\|dirname" scripts/gate-check.sh`; если её нет — добавить `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` рядом с инициализацией GATES_YAML).

- [ ] **Step 2: render-pipeline-map.sh** — заменить блок PIPELINE_ORDER + LABELS (строки 38–69):

```bash
# Pipeline order + labels — из config/stages.yaml (E1, single source of truth)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_ORDER=()
declare -A LABELS=()
while IFS=$'\t' read -r _sid _slabel; do
    PIPELINE_ORDER+=("$_sid")
    LABELS["$_sid"]="$_slabel"
done < <(python3 "$SCRIPT_DIR/stages.py" --labels)
```

- [ ] **Step 3: Smoke-тест на живом состоянии**

```bash
bash scripts/render-pipeline-map.sh template/.landing-state.yaml | head -40
```
Expected: Mermaid-карта с 21 этапом, без 07b_wireframe, лейблы русские.

- [ ] **Step 4: Тесты**

Run: `python3 -m pytest tests/stages/ tests/gate-check/ -v`
Expected: `test_no_hardcoded_order_in_bash_scripts` PASS; gate-check тесты PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/gate-check.sh scripts/render-pipeline-map.sh
git commit -m "feat(E1): gate-check + pipeline-map read stage order from config/stages.yaml"
```

---

### Task 12: Переключить диспетчер landing-go на канон

**Files:**
- Modify: `scripts/landing-go-next-stage.py:13-20`

- [ ] **Step 1: Заменить хардкод STAGE_ORDER**

```python
# Canonical stage order — single source of truth (E1): config/stages.yaml
_ROOT = Path(__file__).resolve().parent.parent
STAGE_ORDER = [
    s["id"]
    for s in yaml.safe_load(
        (_ROOT / "config" / "stages.yaml").read_text(encoding="utf-8")
    )["stages"]
]
```

(литерал из 7 строк удалить; импорты `Path`, `yaml` уже есть).

- [ ] **Step 2: Тесты**

Run: `python3 -m pytest tests/stages/ tests/phase-prd/ -v`
Expected: все PASS, включая `test_next_stage_dispatcher_uses_canonical` и `test_state_template_matches_canonical`.

- [ ] **Step 3: Commit**

```bash
git add scripts/landing-go-next-stage.py
git commit -m "feat(E1): landing-go dispatcher reads stage order from config/stages.yaml"
```

---

### Task 13: Документация порядка этапов + финальная верификация

**Files:**
- Modify: `commands/landing-go.md`, `.claude/commands/landing-go.md`, `agents/landing-orchestrator.md`, `template/CLAUDE.md`
- Verify: полный pytest, wiki sync

- [ ] **Step 1: В landing-go.md и landing-orchestrator.md** — таблицы этапов заменить ссылкой на канон: «Полный порядок этапов — `config/stages.yaml` (single source of truth); карта — `bash scripts/render-pipeline-map.sh <project>/.landing-state.yaml`», оставив только смысловые группировки без полного дубля списка. В `template/CLAUDE.md` таблицу из 13 этапов дополнить строкой-ссылкой на `config/stages.yaml` мастер-системы.

- [ ] **Step 2: Полный прогон тестов**

Run: `python3 -m pytest tests/ -q`
Expected: PASS (0 failed). Падения не из скоупа Phase 1 — зафиксировать и разобрать поштучно, не глушить.

- [ ] **Step 3: Wiki sync**

```bash
bash scripts/check-wiki-sync.sh || python3 -m scripts.wiki.compile --source-mode=system
git add wiki/ && git commit -m "chore(wiki): resync after block-track archive" || true
```

- [ ] **Step 4: Финальный commit + сводка**

```bash
git add -A
git commit -m "docs(E1): stage order docs point to config/stages.yaml"
git log --oneline main..HEAD
```

Сводка для пользователя: что в архиве, что сохранено, что стало каноном, какие зоны следующие (A → B → C, отдельные планы).

---

## Self-Review (выполнен)

- **Spec coverage (зона E):** E2 — Tasks 1–8 (архив + guard + конфиги + доки); E1 — Tasks 9–13 (канон + 4 потребителя + доки). «Убедиться что ПЕРЕИСПОЛЬЗУЕМОЕ не задето» — таблица решений + Step-проверки в Task 3/5 + сохранение block-composition.
- **Вне скоупа Phase 1 (осознанно):** зоны A/B/C/D; переработка landing-compose под «агент рисует» (Zone A4/C1); генерация .landing-state.yaml из канона (сейчас — сверка тестом, генерация в Zone C-плане при изменении списка этапов).
- **Type consistency:** `stages.py --order/--labels`, формат `id<TAB>label` — согласованы между Task 10, 11 и тестом Task 9. `EXPECTED_ORDER` совпадает с config/stages.yaml.
- **Риск:** `bats` может быть не установлен (Task 4 Step 3 имеет fallback). `declare -A` требует bash 4 — уже используется в текущем render-pipeline-map.sh, регресса нет.

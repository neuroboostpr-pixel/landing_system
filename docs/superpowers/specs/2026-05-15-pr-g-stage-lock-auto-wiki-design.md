# PR-G — Stage Lock + Auto-Wiki

**Дата:** 2026-05-15
**Источник:** ПЛАН-ДОРАБОТОК.md пункт №1 («Система идёт строго по шагам, без перепрыгиваний»)
**Статус:** draft на ревью
**Связанный PR:** PR-F (вики-разметка) — фундамент

---

## 1. Зачем (простым языком)

Сейчас агент иногда:
- Пропускает этапы (делает 07c, а 07a ещё не закрыт)
- Не помнит на каком этапе сейчас
- При провале молча идёт дальше вместо «стоп, что делать?»

**PR-F (вики)** дал агенту память о текущем этапе. **PR-G** — добавляет **жёсткий замок**: «нельзя на следующий этап пока зависимости не закрыты». Плюс автоматизирует обновление wiki при изменениях системы и закрытии этапов.

---

## 2. Главные решения (из брейншторма)

| Решение | Значение |
|---|---|
| Жёсткость лока | **Гибрид**: дизайн-этапы soft (можно итерировать), технические hard (требуют зависимости) |
| Триггер system wiki | После `git commit` (через post-commit hook) |
| Триггер project graph | После `gate-check.sh exit 0` (закрытие этапа) |
| Поведение hard-лока | exit 1 + список незакрытых зависимостей |
| Поведение soft-лока | Предупреждение + требование подтверждения от пользователя |

---

## 3. Stage Lock (гибрид)

### 3.1 Конфигурация в `config/stage-gates.yaml`

Каждому этапу добавляется поле `lock: soft | hard`. Hard-этапам — список `requires_approved: [stages]`.

```yaml
stages:
  # Дизайн-этапы — итеративные (soft)
  "03_references":  {lock: soft, ...}
  "04_brand":       {lock: soft, ...}
  "05_design":      {lock: soft, ...}
  "06_stack":       {lock: soft, ...}
  "07_content":     {lock: soft, ...}
  "07a_prototype":  {lock: soft, ...}
  
  # Технические — жёсткие (hard)
  "07b_wireframe":
    lock: hard
    requires_approved: ["04_brand", "05_design", "07a_prototype"]
  
  "07c_composed":
    lock: hard
    requires_approved: ["05_design", "07a_prototype", "07b_wireframe"]
  
  "07d_photos":     {lock: soft, ...}  # параллельный этап, не блокирует
  "07e_visuals":    {lock: soft, ...}  # параллельный
  "07f_composed_final": {lock: soft, ...}  # пересборка с фото
  
  "08_build":
    lock: hard
    requires_approved: ["07c_composed"]
  
  "10_qa":
    lock: hard
    requires_approved: ["08_build"]
  
  "09_deploy":
    lock: hard
    requires_approved: ["08_build", "10_qa"]
  
  "11_analytics":
    lock: hard
    requires_approved: ["09_deploy"]
  
  "12_seo":
    lock: hard
    requires_approved: ["09_deploy"]
```

### 3.2 Логика `gate-check.sh`

В начало добавляется новая проверка `check_lock_requires_approved`:

```bash
# В gate-check.sh, после парсинга stage
lock=$(yq ".stages.\"$stage\".lock // \"soft\"" "$GATES_YAML")
requires=$(yq ".stages.\"$stage\".requires_approved // []" "$GATES_YAML" -o=tsv)

if [ "$lock" = "hard" ] && [ -n "$requires" ]; then
    missing=()
    for req in $requires; do
        status=$(bash "$GATE_STATE" --get "$project" "$req")
        if [ "$status" != "approved" ]; then
            missing+=("$req ($status)")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "❌ Hard lock: нельзя зайти на этап '$stage'" >&2
        echo "   Сначала закрой:" >&2
        for m in "${missing[@]}"; do echo "   - $m" >&2; done
        exit 1
    fi
fi

# Для soft-лока — предупреждение если в предыдущем этапе in_progress/locked
if [ "$lock" = "soft" ]; then
    # Найти предыдущий этап в порядке pipeline
    prev_stage=$(yq ".pipeline_order // [] | .[index(\"$stage\") - 1]" "$GATES_YAML")
    if [ -n "$prev_stage" ] && [ "$prev_stage" != "null" ]; then
        prev_status=$(bash "$GATE_STATE" --get "$project" "$prev_stage")
        if [ "$prev_status" != "approved" ] && [ "$prev_status" != "n/a" ]; then
            echo "⚠️  Soft lock: предыдущий этап '$prev_stage' ($prev_status) не закрыт." >&2
            if [ "$auto" != "1" ]; then
                read -r -p "Точно зайти на '$stage'? [y/N] " ans
                [ "$ans" = "y" ] || exit 1
            fi
        fi
    fi
fi
```

### 3.3 Изменения в `landing-orchestrator`

В промпт `agents/landing-orchestrator.md` добавляется первой строкой:

```
ОБЯЗАТЕЛЬНО перед любым действием:
1. Прочитай `<project>/wiki/index.md` — узнай текущий этап.
2. Запусти `scripts/gate-check.sh --stage <следующий> --project <project>`.
3. Если exit != 0 — НЕ ПРОДОЛЖАЙ. Сообщи пользователю что говорит gate-check.
4. Никогда не действуй вне current_stage из .landing-state.yaml.
```

---

## 4. Auto-update системной wiki

### 4.1 Post-commit hook

Создаётся `.githooks/post-commit`:

```bash
#!/bin/bash
# Авто-обновление системной wiki при изменениях в источниках.

# Файлы которые влияют на wiki
SOURCE_PATTERN='^(agents/|skills/.*/SKILL\.md|commands/|template/.*/README\.md|docs/standards/)'

# Менялись ли источники в этом коммите?
CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD)
if echo "$CHANGED" | grep -qE "$SOURCE_PATTERN"; then
    echo "📚 Источники wiki изменились — пересобираю..."
    
    cd "$(git rev-parse --show-toplevel)"
    python3 -m scripts.wiki.compile --source-mode=system 2>&1 | tail -3
    
    # Если wiki/ обновилась — авто-коммит
    if [ -n "$(git status wiki/ --short)" ]; then
        git add wiki/
        git commit -m "chore(wiki): авто-обновление после изменений системы" --no-verify
        echo "✅ wiki/ авто-закоммичено"
    fi
fi

exit 0
```

### 4.2 Установка хука

Создаётся `scripts/install-git-hooks.sh`:

```bash
#!/bin/bash
# Идемпотентная установка git hooks для wiki + блокировок.
REPO_ROOT="$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
chmod +x "$REPO_ROOT/.githooks/"*
echo "✅ Git hooks подключены через core.hooksPath = .githooks"
```

Запускается:
- Одноразово вручную после клонирования репо
- Автоматически из `landing-onboarding` скилла при первой настройке системы

### 4.3 Поведение при коммите без изменений в источниках

Hook отрабатывает мгновенно (просто `grep -q`), wiki не пересобирается. Это нормальный случай — большинство коммитов не трогают agents/skills.

---

## 5. Auto-update графа проекта

### 5.1 Интеграция в `gate-check.sh`

В конец `scripts/gate-check.sh` добавляется блок:

```bash
# Auto-update project-graph после успешного gate-check
if [ "${exit_code:-1}" = "0" ] && [ -d "$project/wiki" ]; then
    project_slug=$(basename "$project")
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
    cd "$REPO_ROOT" && python3 -m scripts.wiki.compile \
        --source-mode=project-graph --project="$project_slug" \
        >/dev/null 2>&1 || true
fi
```

### 5.2 Условия

- `exit_code = 0` (gate-check прошёл) — обязательное условие
- `<project>/wiki/` существует — проект мигрирован
- `|| true` — если compile упал, не валим gate-check
- Без SDK — stub-индекс уже без SDK (project_graph_compiler._build_index)
- Время: <1 сек

---

## 6. Структура файлов

**Создаются:**
- `.githooks/post-commit`
- `scripts/install-git-hooks.sh`
- `tests/wiki/test_pr_g/` — папка для bats-тестов
- `tests/wiki/test_pr_g/test_stage_lock_hard.bats`
- `tests/wiki/test_pr_g/test_stage_lock_soft.bats`
- `tests/wiki/test_pr_g/test_post_commit_hook.bats`
- `tests/wiki/test_pr_g/test_gate_check_updates_graph.bats`

**Модифицируются:**
- `config/stage-gates.yaml` — добавление `lock` и `requires_approved` для всех этапов
- `scripts/gate-check.sh` — логика hard/soft + auto-compile project-graph
- `agents/landing-orchestrator.md` — добавление правила про gate-check
- `scripts/check-deps.sh` или `landing-onboarding` — упоминание `install-git-hooks.sh`

---

## 7. Тесты (4 bats-теста)

### Test 1: `test_stage_lock_hard.bats`
- Setup: `.landing-state.yaml` где `04_brand: locked`, остальные locked
- Action: `gate-check.sh --stage 07b_wireframe --project <fixture>`
- Expected: exit 1, stderr содержит «нельзя зайти», «04_brand»

### Test 2: `test_stage_lock_soft.bats`
- Setup: `.landing-state.yaml` где `03_references: locked`
- Action: `gate-check.sh --stage 04_brand --project <fixture> --auto` (auto=1 пропускает интерактив)
- Expected: exit 0 (soft не блокирует), stderr содержит «⚠️»
- Без `--auto`: возвращает 1 если ответ не `y`

### Test 3: `test_post_commit_hook.bats`
- Setup: tmpdir git repo, скопировать `.githooks/post-commit`, `git config core.hooksPath .githooks`
- Action 1: коммит трогающий только `docs/README.md` → hook отрабатывает мгновенно, wiki не пересобирается
- Action 2: коммит трогающий `agents/foo.md` → hook вызывает `compile.py` (мок)
- Expected: проверка через `mocker` что compile.py был вызван только во втором случае

### Test 4: `test_gate_check_updates_graph.bats`
- Setup: мок-проект с `wiki/`, `.landing-state.yaml`
- Action: gate-check.sh успешно проходит (мокаем hard_checks)
- Expected: `<project>/wiki/log.md` содержит новую запись

---

## 8. Связь с другими PR

- **PR-F** (вики-разметка) — фундамент, без него PR-G не имеет смысла. ✅ Сделано.
- **PR-D** (orchestrator integration) — уже сделано, оркестратор зовёт gate-check.sh. PR-G усиливает gate-check.
- Будущее: **PR-H** (если понадобится) — UI/чат для подтверждения soft-лока вместо stdin `read -r`. Сейчас не делаем (YAGNI).

---

## 9. Открытые вопросы для финального ревью

1. **Список hard-этапов** (раздел 3.1): согласен ли пользователь с выбором `07b/07c/08/09/10/11/12` как hard? Если хочет добавить/убрать — поправить yaml.
2. **`requires_approved` для 07c** — нужны ли `04_brand` и `07b_wireframe` оба? (сейчас да)
3. **Soft-лок на интерактив** — `read -r -p` в gate-check.sh работает в bash, но в окружении Claude Code (где gate-check вызывается из агента) может быть проблема. Альтернатива: всегда `--auto` для soft в неинтерактивном режиме, но тогда смысл soft теряется. Решение: в `--auto` режиме soft становится «логгируется, но проходит». Это норм для CI/агента, в ручном — спрашивает.

---

## 10. Объём работы

| Этап | Задач | SDK calls |
|---|---|---|
| Stage lock в `gate-check.sh` | 1 | 0 |
| Config update `stage-gates.yaml` | 1 | 0 |
| Orchestrator promt | 1 | 0 |
| Post-commit hook | 1 | 0 |
| Install script | 1 | 0 |
| Project-graph auto-update в gate-check | 1 | 0 |
| Тесты (4 bats) | 4 | 0 |

**Итого:** 10 задач, ~2 часа реальной работы, **0 SDK вызовов**.

---

## 11. Артефакты по правилу пользователя (MD + HTML)

PR-G не создаёт новых артефактов для пользователя — это инфраструктурный PR. Документация в README + примеры использования в `docs/SETUP.md`.

---

## 12. Что меняется для пользователя на практике

**До PR-G:**
- Агент мог взять и пойти делать `07b_wireframe` хотя `04_brand` ещё пустой
- Wiki/ устаревала между прогонами compile

**После PR-G:**
- Агент пытается на 07b → gate-check возвращает «❌ нельзя, закрой 04_brand, 05_design, 07a_prototype» → пользователь видит чёткий список что доделать
- После `git commit` правки агента → wiki автоматом пересобирается и коммитится
- Закрыл этап → `<project>/wiki/index.md` сразу актуальный

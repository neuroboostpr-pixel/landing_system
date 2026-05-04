# Phase 1 — Skeleton & Infrastructure (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить базовую папку `landing-system/` со всем каркасом + работающую команду `/landing-new`, которая создаёт пустой проект-лендинг со структурой 00–12 из шаблона.

**Architecture:** Bash-скрипты для скиллов (init.sh, from-context.sh), markdown для агентов и команд Claude Code. Bats-core для тестирования. Template-папка как канонический шаблон проекта-лендинга. Никаких placeholder-заглушек — каждый файл выполняет конкретную работу.

**Tech Stack:** Bash, bats-core, Node.js (для hooks базы), Markdown с frontmatter для скиллов/агентов/команд Claude Code.

**Spec:** [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](../specs/2026-05-03-landing-system-design.md) (разделы 4, 6, 10, 17, 18)

**Master plan:** [`2026-05-03-landing-system-master-plan.md`](2026-05-03-landing-system-master-plan.md)

---

## File Structure

После Phase 1 в `landing-system/` будут созданы:

```
landing-system/
├─ CLAUDE.md                              # NEW — инструкции для Claude
├─ README.md                              # MODIFY — обновляем существующий
├─ .env.local.example                     # NEW — глобальные секреты-шаблон
├─ package.json                           # NEW — для node-зависимостей
├─ .gitignore                             # EXISTS — уже создан
│
├─ agents/
│  └─ landing-orchestrator.md             # NEW — главный агент (Phase 1 stub)
│
├─ .claude/
│  ├─ settings.json                       # NEW — базовые hooks (пустые в Phase 1)
│  └─ commands/
│     ├─ landing-new.md                   # NEW
│     ├─ landing-from-context.md          # NEW
│     ├─ landing-help.md                  # NEW
│     └─ landing-status.md                # NEW
│
├─ skills/
│  ├─ landing-project-init/
│  │  ├─ SKILL.md                         # NEW
│  │  └─ scripts/init.sh                  # NEW
│  └─ landing-from-context/
│     ├─ SKILL.md                         # NEW
│     └─ scripts/from-context.sh          # NEW
│
├─ template/                              # NEW — шаблон проекта-лендинга
│  ├─ 00_БРИФ/.gitkeep
│  ├─ 01_КОНТЕКСТ/.gitkeep
│  ├─ 02_МАТЕРИАЛЫ_КЛИЕНТА/.gitkeep
│  ├─ 03_РЕФЕРЕНСЫ/.gitkeep
│  ├─ 04_БРЕНД/.gitkeep
│  ├─ 05_ДИЗАЙН-СИСТЕМА/.gitkeep
│  ├─ 06_СТЕК/.gitkeep
│  ├─ 07_КОНТЕНТ/.gitkeep
│  ├─ 08_КОД/.gitkeep
│  ├─ 09_ДЕПЛОЙ/.gitkeep
│  ├─ 10_QA/.gitkeep
│  ├─ 11_АНАЛИТИКА/.gitkeep
│  ├─ 12_SEO/.gitkeep
│  ├─ CLAUDE.md                           # шаблон для каждого проекта
│  ├─ README.md
│  ├─ .env.example                        # проектные секреты
│  └─ .gitignore
│
├─ tests/
│  ├─ helpers/
│  │  └─ test_helpers.bash                # вспомогательные функции для тестов
│  └─ phase-1/
│     ├─ test-deps.bats                   # проверка bats и зависимостей
│     ├─ test-template-structure.bats     # шаблон проекта корректен
│     ├─ test-skills-and-agents.bats      # скиллы и агенты валидны
│     ├─ test-commands.bats               # slash-команды валидны
│     ├─ test-project-init.bats           # init.sh работает
│     ├─ test-from-context.bats           # from-context.sh работает
│     └─ test-integration.bats            # end-to-end Phase 1
│
└─ scripts/
   └─ check-deps.sh                       # проверка установленных зависимостей
```

**Принцип организации:**
- `template/` — каноничный шаблон. Скрипты копируют его в новую папку проекта.
- `skills/<name>/` — каждый скилл = папка с `SKILL.md` + опциональные `scripts/`.
- `agents/<name>.md` — один файл на агента.
- `.claude/commands/<name>.md` — slash-команда = один markdown с frontmatter.
- `tests/phase-N/` — тесты группируются по фазам (для параллельных запусков).

---

## Prerequisites

Перед стартом Phase 1 на машине должны быть:

```bash
# Проверка
bash --version       # >= 5.0
git --version        # any recent
node --version       # >= 20
```

**Bats-core устанавливается в Task 0** (если нет).

---

## Task Breakdown

22 задачи, каждая ~3–5 минут. Группированы по логическим блокам.

| Block | Tasks | What |
|---|---|---|
| **A. Foundation** | 0–4 | bats, helpers, master CLAUDE.md, .env.local.example, package.json, deps-check |
| **B. Template** | 5–10 | template/ структура и базовые файлы |
| **C. Skills & Agents** | 11–15 | landing-project-init, landing-from-context, landing-orchestrator |
| **D. Slash Commands** | 16–19 | /landing-new, /landing-from-context, /landing-help, /landing-status |
| **E. Settings & Integration** | 20–22 | .claude/settings.json, integration test, README update |

---

## Block A — Foundation

### Task 0: Установить bats-core и проверить зависимости

**Files:**
- Create: `scripts/check-deps.sh`
- Test: `tests/phase-1/test-deps.bats`

**Зачем:** Без bats не запустим ни один тест. Без node — не работают hooks. Скрипт `check-deps.sh` проверяет окружение.

- [ ] **Step 0.1: Установить bats-core, если не установлен**

```bash
# macOS
brew install bats-core 2>/dev/null || brew upgrade bats-core
# или
npm install -g bats

# Проверка
bats --version
# Expected: Bats <something>
```

- [ ] **Step 0.2: Создать тест проверки зависимостей**

`tests/phase-1/test-deps.bats`:
```bash
#!/usr/bin/env bats

@test "bats-core installed" {
  run bats --version
  [ "$status" -eq 0 ]
}

@test "git installed" {
  run git --version
  [ "$status" -eq 0 ]
}

@test "node installed and version >= 20" {
  run node --version
  [ "$status" -eq 0 ]
  # node --version returns "v22.x.x" — strip "v" and compare major
  major=$(echo "$output" | sed 's/v//' | cut -d. -f1)
  [ "$major" -ge 20 ]
}

@test "bash version >= 5" {
  major=$(bash --version | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 | cut -d. -f1)
  [ "$major" -ge 5 ]
}

@test "check-deps.sh exists and executable" {
  [ -x "scripts/check-deps.sh" ]
}

@test "check-deps.sh exits 0 when all deps present" {
  run scripts/check-deps.sh
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 0.3: Запустить тест — должен FAIL**

```bash
cd landing-system
bats tests/phase-1/test-deps.bats
```

Expected: 4 проходят (bats/git/node/bash), 2 падают (`check-deps.sh` отсутствует).

- [ ] **Step 0.4: Создать `scripts/check-deps.sh`**

```bash
#!/usr/bin/env bash
# Phase 1 dependency checker
set -euo pipefail

errors=0

check() {
  local name="$1"
  local cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "✅ $name: $($cmd --version 2>&1 | head -1)"
  else
    echo "❌ $name not found"
    errors=$((errors + 1))
  fi
}

echo "=== Landing System: Dependency Check ==="
check "bats-core" bats
check "git" git
check "node" node
check "bash" bash

if [ "$errors" -gt 0 ]; then
  echo ""
  echo "⚠️  Missing $errors dependencies. Install them and re-run."
  echo "   macOS: brew install bats-core node git"
  echo "   Linux: apt-get install bats node git"
  exit 1
fi

echo ""
echo "✅ All dependencies OK."
exit 0
```

- [ ] **Step 0.5: chmod + run test — должен PASS**

```bash
chmod +x scripts/check-deps.sh
bats tests/phase-1/test-deps.bats
```

Expected: 6 passed.

- [ ] **Step 0.6: Commit**

```bash
git add scripts/check-deps.sh tests/phase-1/test-deps.bats
git commit -m "feat(phase-1): add dependency check script and tests"
```

---

### Task 1: Test helpers

**Files:**
- Create: `tests/helpers/test_helpers.bash`

**Зачем:** Общие функции для всех тестов Phase 1+ (создание временных папок, проверка структуры, etc).

- [ ] **Step 1.1: Создать helpers**

`tests/helpers/test_helpers.bash`:
```bash
#!/usr/bin/env bash
# Shared test helpers for landing-system

# Create a temp directory for test isolation
setup_temp_dir() {
  TEST_TEMP=$(mktemp -d -t "landing-test-XXXXXX")
  export TEST_TEMP
}

# Cleanup
teardown_temp_dir() {
  if [ -n "${TEST_TEMP:-}" ] && [ -d "$TEST_TEMP" ]; then
    rm -rf "$TEST_TEMP"
  fi
}

# Assert directory exists
assert_dir_exists() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    echo "Expected directory '$dir' to exist"
    return 1
  fi
}

# Assert file exists
assert_file_exists() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "Expected file '$file' to exist"
    return 1
  fi
}

# Assert file contains string
assert_file_contains() {
  local file="$1"
  local needle="$2"
  if ! grep -q "$needle" "$file"; then
    echo "Expected file '$file' to contain '$needle'"
    echo "Actual content:"
    cat "$file"
    return 1
  fi
}

# Path to landing-system root (for tests)
LANDING_SYSTEM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export LANDING_SYSTEM_ROOT
```

- [ ] **Step 1.2: Smoke-test helpers**

```bash
bash -n tests/helpers/test_helpers.bash
# Expected: no output (syntax OK)

# Source check
source tests/helpers/test_helpers.bash
echo "$LANDING_SYSTEM_ROOT"
# Expected: absolute path to landing-system
```

- [ ] **Step 1.3: Commit**

```bash
git add tests/helpers/test_helpers.bash
git commit -m "feat(phase-1): add shared test helpers"
```

---

### Task 2: Master CLAUDE.md

**Files:**
- Create: `CLAUDE.md` (master, не в template — его сделаем в Block B)
- Test: `tests/phase-1/test-master-claude-md.bats`

**Зачем:** CLAUDE.md в корне = инструкции для Claude Code, когда он запускается в папке `landing-system/`. Описывает что это за папка, как использовать команды, какие правила.

- [ ] **Step 2.1: Создать тест**

`tests/phase-1/test-master-claude-md.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "master CLAUDE.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/CLAUDE.md"
}

@test "master CLAUDE.md mentions landing-system" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "landing-system"
}

@test "master CLAUDE.md mentions /landing-new command" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "/landing-new"
}

@test "master CLAUDE.md mentions superpowers" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "superpowers"
}

@test "master CLAUDE.md mentions WordPress" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/CLAUDE.md" "WordPress"
}
```

- [ ] **Step 2.2: Run test, expect FAIL**

```bash
bats tests/phase-1/test-master-claude-md.bats
# Expected: 5 failures (file not found)
```

- [ ] **Step 2.3: Создать `CLAUDE.md`**

```markdown
# Landing System — CLAUDE Instructions

Это папка мастер-системы для производства WordPress-лендингов через Claude Code.

## Что это

Агентская система для построения production-grade лендингов на WordPress + Бегет.
Полный цикл: бриф → мудборд → бренд-кит → DESIGN.md → код → деплой → QA → SEO.

## Главные команды

- `/landing-new <slug>` — создать новый проект-лендинг с нуля
- `/landing-from-context <slug>` — создать проект из родительской папки агентства
- `/landing-status` — статус системы и текущих проектов
- `/landing-help` — справка по всем командам

## Зависимости

Эта система использует:
- **superpowers** plugin (brainstorming, writing-plans, executing-plans, subagent-driven-development)
- Скиллы из `skills/` (landing-project-init, landing-from-context)
- Агентов из `agents/` (landing-orchestrator)

Перед работой проверь: `scripts/check-deps.sh`.

## Структура

- `template/` — каноничный шаблон проекта-лендинга (13 папок 00–12)
- `skills/` — наши специализированные скиллы
- `agents/` — специализированные агенты
- `.claude/commands/` — slash-команды
- `docs/superpowers/` — спецификации и планы реализации

## Правила работы

1. **TDD строго:** каждое изменение в коде начинается с failing test (через `bats` для bash, `vitest` для JS, `pytest` для Python).
2. **YAGNI:** не реализуем то, чего нет в spec.
3. **Frequent commits:** один commit = одна логическая единица.
4. **HARD GATE между этапами проектов:** агент не идёт на следующий этап workflow без явного утверждения пользователем.

## Для нового проекта-лендинга

При запуске `/landing-new my-project` агенты:
1. Создают `~/Lendings/my-project/` со структурой template/.
2. Запускают `landing-orchestrator`, который ведёт через 12 этапов.
3. На каждом этапе генерируют HTML-preview, ждут подтверждения.
4. Финал — деплой на Бегет, готовый сайт.

## Поддержка

Spec-документ: [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](docs/superpowers/specs/2026-05-03-landing-system-design.md)
Master plan: [`docs/superpowers/plans/2026-05-03-landing-system-master-plan.md`](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)
```

- [ ] **Step 2.4: Run test, expect PASS**

```bash
bats tests/phase-1/test-master-claude-md.bats
# Expected: 5 passed
```

- [ ] **Step 2.5: Commit**

```bash
git add CLAUDE.md tests/phase-1/test-master-claude-md.bats
git commit -m "feat(phase-1): add master CLAUDE.md with system instructions"
```

---

### Task 3: .env.local.example (глобальные секреты)

**Files:**
- Create: `.env.local.example`
- Test: `tests/phase-1/test-env-template.bats`

- [ ] **Step 3.1: Создать тест**

`tests/phase-1/test-env-template.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test ".env.local.example exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.env.local.example"
}

@test ".env.local.example has BEGET_API_LOGIN" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "BEGET_API_LOGIN"
}

@test ".env.local.example has FIRECRAWL_API_KEY" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "FIRECRAWL_API_KEY"
}

@test ".env.local.example has YANDEX_OAUTH_TOKEN" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "YANDEX_OAUTH_TOKEN"
}

@test ".env.local.example has YANDEX_METRIKA_OAUTH" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "YANDEX_METRIKA_OAUTH"
}

@test ".env.local.example has TELEGRAM_BOT_TOKEN" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "TELEGRAM_BOT_TOKEN"
}

@test ".env.local.example has WHATTHEFONT_API_KEY" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.env.local.example" "WHATTHEFONT_API_KEY"
}

@test ".env.local NOT committed (in gitignore)" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.gitignore" ".env.local"
}
```

- [ ] **Step 3.2: Run test, expect FAIL**

```bash
bats tests/phase-1/test-env-template.bats
```

- [ ] **Step 3.3: Создать `.env.local.example`**

```bash
# Landing System — Global secrets
# COPY this file to .env.local and fill in. NEVER commit .env.local!
# See spec section 19 for where to obtain each key.

# === Hosting & DNS ===
# Бегет (https://beget.com → панель → API)
BEGET_API_LOGIN=
BEGET_API_PASSWORD=

# Reg.ru (https://www.reg.ru → партнёрский кабинет → API)
REGRU_API_USERNAME=
REGRU_API_PASSWORD=

# Cloudflare (https://dash.cloudflare.com → API tokens)
CLOUDFLARE_API_TOKEN=

# === Parsing ===
# Firecrawl (https://www.firecrawl.dev) — free 500/mo, paid $19/mo
FIRECRAWL_API_KEY=

# === Fonts ===
# WhatTheFont (https://www.myfonts.com/WhatTheFont) — free 25/day
WHATTHEFONT_API_KEY=

# === Yandex ===
# Wordstat (OAuth: https://oauth.yandex.ru/client/new, scope: direct:api,wordstat:use)
YANDEX_OAUTH_TOKEN=

# Metrika reading (OAuth scope: metrika:read)
YANDEX_METRIKA_OAUTH=

# === Telegram (notifications) ===
# Bot token from @BotFather
TELEGRAM_BOT_TOKEN=
# Chat ID for deploy notifications
TELEGRAM_NOTIFY_CHAT_ID=

# === Optional (Phase 2+) ===
# GitHub (for plugin marketplace, Phase 2)
GITHUB_TOKEN=
```

- [ ] **Step 3.4: Run test, expect PASS**

```bash
bats tests/phase-1/test-env-template.bats
# Expected: 8 passed
```

- [ ] **Step 3.5: Commit**

```bash
git add .env.local.example tests/phase-1/test-env-template.bats
git commit -m "feat(phase-1): add global secrets template (.env.local.example)"
```

---

### Task 4: package.json (заготовка для Node deps)

**Files:**
- Create: `package.json`
- Test: `tests/phase-1/test-package-json.bats`

**Зачем:** В будущих фазах появятся hooks на Node.js (vitest для тестов, простые скрипты). Сейчас создаём минимальный package.json как foundation.

- [ ] **Step 4.1: Создать тест**

`tests/phase-1/test-package-json.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "package.json exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/package.json"
}

@test "package.json is valid JSON" {
  run node -e "JSON.parse(require('fs').readFileSync('$LANDING_SYSTEM_ROOT/package.json', 'utf8'))"
  [ "$status" -eq 0 ]
}

@test "package.json has correct name" {
  run node -e "console.log(require('$LANDING_SYSTEM_ROOT/package.json').name)"
  [ "$output" = "landing-system" ]
}

@test "package.json has test script using bats" {
  run node -e "console.log(require('$LANDING_SYSTEM_ROOT/package.json').scripts.test)"
  [[ "$output" =~ "bats" ]]
}
```

- [ ] **Step 4.2: Run test, expect FAIL**

- [ ] **Step 4.3: Создать `package.json`**

```json
{
  "name": "landing-system",
  "version": "0.1.0-mvp",
  "description": "Agency landing system for Claude Code (WordPress + Бегет)",
  "private": true,
  "scripts": {
    "test": "bats tests/**/*.bats",
    "test:phase-1": "bats tests/phase-1/*.bats",
    "check-deps": "bash scripts/check-deps.sh"
  },
  "engines": {
    "node": ">=20"
  },
  "license": "UNLICENSED"
}
```

- [ ] **Step 4.4: Run test, expect PASS**

- [ ] **Step 4.5: Commit**

```bash
git add package.json tests/phase-1/test-package-json.bats
git commit -m "feat(phase-1): add minimal package.json with test scripts"
```

---

## Block B — Template (шаблон проекта-лендинга)

### Task 5: Структура папок 00–12 в template/

**Files:**
- Create: `template/00_БРИФ/.gitkeep` ... `template/12_SEO/.gitkeep` (13 папок)
- Test: `tests/phase-1/test-template-structure.bats`

- [ ] **Step 5.1: Создать тест**

`tests/phase-1/test-template-structure.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

# 13 expected folders (00 through 12)
EXPECTED_DIRS=(
  "00_БРИФ"
  "01_КОНТЕКСТ"
  "02_МАТЕРИАЛЫ_КЛИЕНТА"
  "03_РЕФЕРЕНСЫ"
  "04_БРЕНД"
  "05_ДИЗАЙН-СИСТЕМА"
  "06_СТЕК"
  "07_КОНТЕНТ"
  "08_КОД"
  "09_ДЕПЛОЙ"
  "10_QA"
  "11_АНАЛИТИКА"
  "12_SEO"
)

@test "template/ folder exists" {
  assert_dir_exists "$LANDING_SYSTEM_ROOT/template"
}

@test "all 13 numbered folders exist in template/" {
  for dir in "${EXPECTED_DIRS[@]}"; do
    assert_dir_exists "$LANDING_SYSTEM_ROOT/template/$dir" || return 1
  done
}

@test "each numbered folder has .gitkeep" {
  for dir in "${EXPECTED_DIRS[@]}"; do
    assert_file_exists "$LANDING_SYSTEM_ROOT/template/$dir/.gitkeep" || return 1
  done
}
```

- [ ] **Step 5.2: Run test, expect FAIL**

- [ ] **Step 5.3: Создать все 13 папок**

```bash
cd landing-system
DIRS=(
  "00_БРИФ" "01_КОНТЕКСТ" "02_МАТЕРИАЛЫ_КЛИЕНТА" "03_РЕФЕРЕНСЫ"
  "04_БРЕНД" "05_ДИЗАЙН-СИСТЕМА" "06_СТЕК" "07_КОНТЕНТ"
  "08_КОД" "09_ДЕПЛОЙ" "10_QA" "11_АНАЛИТИКА" "12_SEO"
)
for dir in "${DIRS[@]}"; do
  mkdir -p "template/$dir"
  touch "template/$dir/.gitkeep"
done
```

- [ ] **Step 5.4: Run test, expect PASS**

- [ ] **Step 5.5: Commit**

```bash
git add template/ tests/phase-1/test-template-structure.bats
git commit -m "feat(phase-1): scaffold template with 13 numbered project folders"
```

---

### Task 6: Template CLAUDE.md (для каждого проекта-лендинга)

**Files:**
- Create: `template/CLAUDE.md`
- Test: `tests/phase-1/test-template-claude-md.bats`

**Зачем:** Когда Claude открывается внутри папки проекта-лендинга, он должен прочитать project-level CLAUDE.md и понять «я внутри проекта-лендинга, мой workflow — 12 этапов».

- [ ] **Step 6.1: Создать тест**

`tests/phase-1/test-template-claude-md.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "template/CLAUDE.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/CLAUDE.md"
}

@test "template/CLAUDE.md mentions 12 этапов" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "12 этап"
}

@test "template/CLAUDE.md mentions landing-orchestrator" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "landing-orchestrator"
}

@test "template/CLAUDE.md mentions HARD GATE" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "HARD GATE"
}

@test "template/CLAUDE.md mentions WordPress" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/CLAUDE.md" "WordPress"
}
```

- [ ] **Step 6.2: Run test, expect FAIL**

- [ ] **Step 6.3: Создать `template/CLAUDE.md`**

```markdown
# Project Lending — CLAUDE Instructions

Это папка одного **проекта-лендинга**, созданная из template мастер-системой landing-system.

## Контекст

Ты находишься в проекте, который должен пройти **12 этапов workflow**:

| # | Папка | Этап |
|---|---|---|
| 00 | `00_БРИФ/` | Бриф проекта (ниша, KPI, ЦА) |
| 01 | `01_КОНТЕКСТ/` | Снепшот данных о нише, ЦА, конкурентах |
| 02 | `02_МАТЕРИАЛЫ_КЛИЕНТА/` | Фото, видео, отзывы клиента |
| 03 | `03_РЕФЕРЕНСЫ/` | Визуальные референсы + мудборд |
| 04 | `04_БРЕНД/` | Бренд-кит с трассировкой источников |
| 05 | `05_ДИЗАЙН-СИСТЕМА/` | DESIGN.md (единый источник истины токенов) |
| 06 | `06_СТЕК/` | Плагины, библиотеки, иконки, шрифты |
| 07 | `07_КОНТЕНТ/` | Финальные тексты под блоки лендинга |
| 08 | `08_КОД/` | WP-тема, Gutenberg-блоки, ACF |
| 09 | `09_ДЕПЛОЙ/` | Конфиг, скрипт, лог деплоев на Бегет |
| 10 | `10_QA/` | Чек-листы, скриншоты, отчёты |
| 11 | `11_АНАЛИТИКА/` | Я.Метрика, цели, события, UTM |
| 12 | `12_SEO/` | Ключи, мета, Schema.org, sitemap |

## Главный агент

`landing-orchestrator` ведёт через все 12 этапов. На каждом этапе:
1. Дёргает специализированных агентов (см. master-system `agents/`)
2. Генерирует визуальный артефакт (`.html` preview в соответствующей папке)
3. **HARD GATE**: ждёт явного утверждения от пользователя перед переходом на следующий этап

## Правила

1. **Никогда не пропускай HARD GATE.** Не идём на этап N+1 без утверждения этапа N.
2. **Все артефакты идут в свою номерную папку.** Никаких файлов в корне проекта (кроме CLAUDE.md, README.md, .env, deploy.sh).
3. **TDD при разработке кода темы:** тесты (PHPUnit/Pest) идут в `08_КОД/wp-theme/tests/`.
4. **Один проект = один WordPress = один поддомен.** Изоляция строгая.
5. **Я.Директ-копии** делаются через мастер-команду `/landing-clone`, не вручную.

## Полезные команды

В этой папке (если установлен мастер-плагин):
- `/landing-status` — на каком ты этапе
- `/landing-references` — перезапустить этап 03
- `/landing-deploy` — задеплоить на Бегет
- `/landing-rollback v1.0` — откат к версии

## Источник правды

Все системные правила и архитектура: [мастер-spec](../../landing-system/docs/superpowers/specs/2026-05-03-landing-system-design.md)
```

- [ ] **Step 6.4: Run test, expect PASS**

- [ ] **Step 6.5: Commit**

```bash
git add template/CLAUDE.md tests/phase-1/test-template-claude-md.bats
git commit -m "feat(phase-1): add template CLAUDE.md describing 12-stage workflow"
```

---

### Task 7: Template README.md

**Files:**
- Create: `template/README.md`
- Test: внутри `test-template-structure.bats` (расширяем)

- [ ] **Step 7.1: Расширить test-template-structure.bats**

Добавить:
```bash
@test "template/README.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/README.md"
}

@test "template/README.md has Quick Start section" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/README.md" "Quick Start"
}
```

- [ ] **Step 7.2: Run test, expect FAIL (2 new failures)**

- [ ] **Step 7.3: Создать `template/README.md`**

```markdown
# Landing Project — {{PROJECT_NAME}}

> Этот файл создаётся автоматически. После создания проекта замени `{{PROJECT_NAME}}` на имя своего лендинга.

## О проекте

- **Ниша:** _заполни в `00_БРИФ/brief.md`_
- **Клиент:** __
- **Целевой URL:** __
- **Стек:** WordPress + Gutenberg + GenerateBlocks + ACF
- **Хостинг:** Бегет

## Quick Start

1. Открой Claude Code в этой папке: `claude`
2. Запусти: `/landing-status`
3. Если ты только начал: `/landing-references` (этап 03 из 12)
4. Следуй инструкциям оркестратора

## Структура

См. `CLAUDE.md` — там описаны все 13 папок (00–12) и их назначение.

## Где живёт что

- **Бриф и контекст** → `00_БРИФ/`, `01_КОНТЕКСТ/`
- **Материалы клиента** (фото/видео/отзывы) → `02_МАТЕРИАЛЫ_КЛИЕНТА/`
- **Дизайн** → `03_РЕФЕРЕНСЫ/`, `04_БРЕНД/`, `05_ДИЗАЙН-СИСТЕМА/`
- **Код** → `08_КОД/`
- **Деплой** → `09_ДЕПЛОЙ/` (включая `versions/` для отката)
- **QA, аналитика, SEO** → `10_QA/`, `11_АНАЛИТИКА/`, `12_SEO/`

## Команды

```bash
/landing-status              # где сейчас
/landing-references          # этап 03
/landing-brand               # этап 04
/landing-design              # этап 05
/landing-build               # этап 08
/landing-deploy              # этап 09
/landing-qa                  # этап 10
/landing-rollback v1.0       # откат
```

## Секреты

См. `.env.example` — скопируй в `.env` и заполни.
```

- [ ] **Step 7.4: Run test, expect PASS**

- [ ] **Step 7.5: Commit**

```bash
git add template/README.md tests/phase-1/test-template-structure.bats
git commit -m "feat(phase-1): add template README for landing projects"
```

---

### Task 8: Template .env.example

**Files:**
- Create: `template/.env.example`
- Test: `tests/phase-1/test-template-env.bats`

- [ ] **Step 8.1: Создать тест**

`tests/phase-1/test-template-env.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "template/.env.example exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/.env.example"
}

@test "template/.env.example has BEGET_HOST" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.env.example" "BEGET_HOST"
}

@test "template/.env.example has DOMAIN" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.env.example" "DOMAIN"
}

@test "template/.env.example has YM_COUNTER_ID" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.env.example" "YM_COUNTER_ID"
}

@test "template/.env.example has DNS_PROVIDER" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.env.example" "DNS_PROVIDER"
}
```

- [ ] **Step 8.2: Run test, expect FAIL**

- [ ] **Step 8.3: Создать `template/.env.example`**

```bash
# Project-level secrets for {{PROJECT_NAME}}
# Copy this to .env and fill in. NEVER commit .env!

# === Бегет SSH access ===
BEGET_HOST=server123.beget.tech
BEGET_USER=neuroboost
SSH_KEY_PATH=~/.ssh/beget_neuroboost
WP_PATH=/home/n/neuroboost/landing.example.ru

# === WP Admin ===
WP_ADMIN_LOGIN=admin
WP_ADMIN_PASSWORD=
SITE_TITLE=Landing Title
THEME_SLUG=landing-theme

# === Domain ===
DOMAIN=landing.example.ru
DNS_PROVIDER=beget          # beget | regru | cloudflare | manual

# === Yandex Metrika ===
YM_COUNTER_ID=

# === Notifications ===
TELEGRAM_LEADS_CHAT_ID=     # лиды с форм
TELEGRAM_NOTIFY_CHAT_ID=    # уведомления о деплое (override global)

# === CRM Webhook ===
CRM_WEBHOOK_URL=

# === A/B Parent (auto-filled by /landing-clone) ===
PARENT_PROJECT=
```

- [ ] **Step 8.4: Run test, expect PASS**

- [ ] **Step 8.5: Commit**

```bash
git add template/.env.example tests/phase-1/test-template-env.bats
git commit -m "feat(phase-1): add template .env.example with project secrets"
```

---

### Task 9: Template .gitignore

**Files:**
- Create: `template/.gitignore`

- [ ] **Step 9.1: Расширить test-template-structure.bats**

Добавить:
```bash
@test "template/.gitignore exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/.gitignore"
}

@test "template/.gitignore ignores .env" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.gitignore" ".env"
}

@test "template/.gitignore ignores versions/" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.gitignore" "versions"
}
```

- [ ] **Step 9.2: Run test, expect FAIL (3 new)**

- [ ] **Step 9.3: Создать `template/.gitignore`**

```
# Secrets
.env
.env.local
.env.*.local

# Deploy snapshots (могут быть большими — храним внешне)
09_ДЕПЛОЙ/versions/

# Local
.DS_Store
node_modules/
__pycache__/
*.pyc

# WP local dev
wp-content/uploads/
wp-content/cache/

# Logs
*.log
```

- [ ] **Step 9.4: Run test, expect PASS**

- [ ] **Step 9.5: Commit**

```bash
git add template/.gitignore tests/phase-1/test-template-structure.bats
git commit -m "feat(phase-1): add template .gitignore"
```

---

### Task 10: README.md мастер-системы (обновляем существующий)

**Files:**
- Modify: `README.md` (root)

- [ ] **Step 10.1: Расширить test (мы уже создали test-master-claude-md, но README отдельный)**

Создать `tests/phase-1/test-master-readme.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "master README.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/README.md"
}

@test "master README.md mentions Quick Start" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "Quick Start"
}

@test "master README.md links to spec" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "2026-05-03-landing-system-design"
}

@test "master README.md mentions /landing-new" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/README.md" "/landing-new"
}
```

- [ ] **Step 10.2: Run test, expect partial FAIL**

- [ ] **Step 10.3: Обновить `README.md`**

```markdown
# Landing System (Neuroboost Agency)

Агентская система внутри Claude Code для производства production-grade лендингов на WordPress + Бегет. Полный цикл: от референсов до публикации.

## Quick Start

1. **Установить зависимости:**
   ```bash
   bash scripts/check-deps.sh
   ```

2. **Заполнить глобальные секреты:**
   ```bash
   cp .env.local.example .env.local
   # Отредактируй .env.local — см. spec раздел 19 для получения ключей
   ```

3. **Установить плагин superpowers (один раз):**
   ```bash
   claude
   > /plugin install superpowers@claude-plugins-official
   ```

4. **Создать первый лендинг:**
   ```bash
   claude
   > /landing-new my-first-landing
   ```

## Структура

```
landing-system/
├─ agents/              # 18 специализированных агентов (по фазам)
├─ skills/              # наши скиллы (landing-project-init и др.)
├─ .claude/commands/     # slash-команды
├─ template/             # каноничный шаблон проекта-лендинга
├─ docs/superpowers/     # spec и planы реализации
├─ tests/                # bats-тесты (по фазам)
├─ scripts/              # bash-утилиты
├─ CLAUDE.md             # инструкции для Claude в этой папке
├─ README.md             # этот файл
└─ .env.local.example    # шаблон глобальных секретов
```

## Команды

| Команда | Назначение |
|---|---|
| `/landing-new <slug>` | Новый проект с нуля |
| `/landing-from-context <slug>` | Из родительской папки агентства |
| `/landing-clone <src> --as <new>` | A/B-копия независимого лендинга |
| `/landing-status` | Состояние системы и проектов |
| `/landing-help` | Справка по всем командам |

## Документация

- **Полное ТЗ:** [docs/superpowers/specs/2026-05-03-landing-system-design.md](docs/superpowers/specs/2026-05-03-landing-system-design.md)
- **Master plan:** [docs/superpowers/plans/2026-05-03-landing-system-master-plan.md](docs/superpowers/plans/2026-05-03-landing-system-master-plan.md)

## Тестирование

```bash
npm test              # все тесты
npm run test:phase-1  # только Phase 1
```

## Статус

🟡 **Phase 1 — Skeleton & Infrastructure** (в разработке)

Полный roadmap см. в master plan.

## License

Internal use — Neuroboost Agency. Distribution to students under separate agreement.
```

- [ ] **Step 10.4: Run test, expect PASS**

- [ ] **Step 10.5: Commit**

```bash
git add README.md tests/phase-1/test-master-readme.bats
git commit -m "docs(phase-1): rewrite master README with Quick Start"
```

---

## Block C — Skills & Agents

### Task 11: Скилл `landing-project-init` — SKILL.md

**Files:**
- Create: `skills/landing-project-init/SKILL.md`
- Test: `tests/phase-1/test-skills-and-agents.bats`

- [ ] **Step 11.1: Создать тест**

`tests/phase-1/test-skills-and-agents.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-project-init SKILL.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/skills/landing-project-init/SKILL.md"
}

@test "landing-project-init has frontmatter with name" {
  run grep -E "^name: landing-project-init$" "$LANDING_SYSTEM_ROOT/skills/landing-project-init/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "landing-project-init has frontmatter with description" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/skills/landing-project-init/SKILL.md"
  [ "$status" -eq 0 ]
}

@test "landing-project-init mentions init.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/skills/landing-project-init/SKILL.md" "init.sh"
}
```

- [ ] **Step 11.2: Run test, expect FAIL**

- [ ] **Step 11.3: Создать `skills/landing-project-init/SKILL.md`**

```markdown
---
name: landing-project-init
description: Use when user wants to create a new landing project from scratch. Creates a project folder by copying the template and initializes it with metadata.
---

# landing-project-init

## Когда использовать

- Пользователь сказал «создай новый лендинг», `/landing-new <slug>`, или эквивалент.
- Нужна **чистая** папка проекта (не из существующего контекста — для этого есть `landing-from-context`).

## Что делаю

1. Принимаю slug проекта (например, `lp-курс-марафон`).
2. Запрашиваю базовые поля: ниша, клиент, желаемый домен (опционально на старте).
3. Запускаю `scripts/init.sh <slug>`:
   - Создаёт `~/Lendings/<slug>/` со структурой template/.
   - Инициализирует git-репо.
   - Заполняет placeholder в README.md и CLAUDE.md проекта.
4. Открываю в проекте файл `00_БРИФ/brief.md` для заполнения первого этапа.
5. Передаю управление `landing-orchestrator` для запуска workflow с этапа 00.

## Аргументы

- `<slug>` — имя папки и проекта (kebab-case рекомендуется)
- `--cinematic` (опционально) — флаг premium-режима

## Side effects

- Создаётся новая папка вне `landing-system/`. Папка проекта **не вкладывается** в мастер-систему.
- Инициализируется git-репо проекта.

## Что НЕ делаю

- Не создаю WordPress (это Phase 5: `wp-deployer`).
- Не запрашиваю домен жёстко (можно отложить до этапа 09).
- Не вызываю других агентов кроме передачи `landing-orchestrator`.

## Скрипт

См. [`scripts/init.sh`](scripts/init.sh).
```

- [ ] **Step 11.4: Run test, expect PASS**

- [ ] **Step 11.5: Commit**

```bash
git add skills/landing-project-init/SKILL.md tests/phase-1/test-skills-and-agents.bats
git commit -m "feat(phase-1): add landing-project-init skill"
```

---

### Task 12: Скрипт `init.sh`

**Files:**
- Create: `skills/landing-project-init/scripts/init.sh`
- Test: `tests/phase-1/test-project-init.bats`

- [ ] **Step 12.1: Создать тест**

`tests/phase-1/test-project-init.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
  export TARGET_DIR="$TEST_TEMP/test-project"
}

teardown() {
  teardown_temp_dir
}

@test "init.sh exists and executable" {
  [ -x "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" ]
}

@test "init.sh fails without arguments" {
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh"
  [ "$status" -ne 0 ]
}

@test "init.sh creates project from template" {
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_dir_exists "$TARGET_DIR"
  assert_dir_exists "$TARGET_DIR/00_БРИФ"
  assert_dir_exists "$TARGET_DIR/12_SEO"
  assert_file_exists "$TARGET_DIR/CLAUDE.md"
  assert_file_exists "$TARGET_DIR/README.md"
  assert_file_exists "$TARGET_DIR/.env.example"
  assert_file_exists "$TARGET_DIR/.gitignore"
}

@test "init.sh initializes git in new project" {
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_dir_exists "$TARGET_DIR/.git"
}

@test "init.sh refuses to overwrite existing project" {
  mkdir -p "$TARGET_DIR"
  touch "$TARGET_DIR/some-file"
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -ne 0 ]
  [[ "$output" =~ "exists" ]] || [[ "$output" =~ "уже" ]]
}

@test "init.sh substitutes PROJECT_NAME placeholder in README" {
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  run grep "{{PROJECT_NAME}}" "$TARGET_DIR/README.md"
  [ "$status" -ne 0 ]  # placeholder gone
}
```

- [ ] **Step 12.2: Run test, expect FAIL**

- [ ] **Step 12.3: Написать `init.sh`**

```bash
#!/usr/bin/env bash
# landing-project-init: creates a new landing project from template
set -euo pipefail

# --- Args ---
if [ $# -lt 1 ]; then
  echo "Usage: init.sh <target-path> [--cinematic]"
  echo "  target-path: absolute or relative path to new project folder"
  exit 1
fi

TARGET="$1"
CINEMATIC=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --cinematic) CINEMATIC="true"; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Resolve paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TEMPLATE_DIR="$SYSTEM_ROOT/template"

if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "❌ Template not found at $TEMPLATE_DIR"
  exit 2
fi

# --- Refuse overwrite ---
if [ -e "$TARGET" ]; then
  echo "❌ Path already exists: $TARGET"
  echo "   Choose another name or remove the existing folder."
  exit 3
fi

# --- Project name from path ---
PROJECT_NAME="$(basename "$TARGET")"

# --- Copy template ---
echo "📦 Copying template to $TARGET ..."
mkdir -p "$TARGET"
# Copy contents (including hidden files via .gitkeep, .env.example, .gitignore)
cp -R "$TEMPLATE_DIR/." "$TARGET/"

# --- Substitute placeholders ---
echo "✏️  Substituting placeholders..."
# README.md
if [ -f "$TARGET/README.md" ]; then
  # macOS sed needs '' after -i; Linux differs. Use a portable approach.
  sed -i.bak "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TARGET/README.md"
  rm -f "$TARGET/README.md.bak"
fi
# .env.example
if [ -f "$TARGET/.env.example" ]; then
  sed -i.bak "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$TARGET/.env.example"
  rm -f "$TARGET/.env.example.bak"
fi

# --- Initialize git ---
echo "🌱 Initializing git..."
git -C "$TARGET" init -b main >/dev/null
git -C "$TARGET" add -A >/dev/null
git -C "$TARGET" commit -m "chore: scaffold project from landing-system template" >/dev/null 2>&1 || true

# --- Optional: cinematic flag ---
if [ "$CINEMATIC" = "true" ]; then
  echo "CINEMATIC=true" >> "$TARGET/00_БРИФ/.flags"
  echo "🎬 Cinematic mode enabled"
fi

# --- Success ---
echo ""
echo "✅ Project created: $TARGET"
echo ""
echo "Next steps:"
echo "  cd $TARGET"
echo "  cp .env.example .env  # fill in secrets"
echo "  claude                # open Claude Code"
echo "  > /landing-status     # see what's next"
```

- [ ] **Step 12.4: chmod + run test, expect PASS**

```bash
chmod +x skills/landing-project-init/scripts/init.sh
bats tests/phase-1/test-project-init.bats
# Expected: 6 passed
```

- [ ] **Step 12.5: Commit**

```bash
git add skills/landing-project-init/scripts/init.sh tests/phase-1/test-project-init.bats
git commit -m "feat(phase-1): add init.sh that creates project from template"
```

---

### Task 13: Скилл `landing-from-context` — SKILL.md

**Files:**
- Create: `skills/landing-from-context/SKILL.md`

- [ ] **Step 13.1: Расширить test-skills-and-agents.bats**

Добавить:
```bash
@test "landing-from-context SKILL.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/skills/landing-from-context/SKILL.md"
}

@test "landing-from-context frontmatter ok" {
  run grep -E "^name: landing-from-context$" "$LANDING_SYSTEM_ROOT/skills/landing-from-context/SKILL.md"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 13.2: Run test, expect FAIL**

- [ ] **Step 13.3: Создать `skills/landing-from-context/SKILL.md`**

```markdown
---
name: landing-from-context
description: Use when starting a new landing project inside an existing parent agency project that already contains research, audience data, prototypes. Snapshots data into the new landing folder.
---

# landing-from-context

## Когда использовать

- Пользователь сказал «новый лендинг по этому курсу/проекту», `/landing-from-context <slug>`.
- Текущая рабочая папка — родительский проект агентства (есть подпапки `01_контекст`, `04_документы`, `05_исследования` и пр.).
- Нужно унаследовать данные о ЦА, отзывы, прототип текста.

## Что делаю

1. Принимаю slug нового лендинга.
2. Определяю родительскую папку (cwd должна быть структурой агентства).
3. Запускаю `scripts/from-context.sh <slug>`:
   - Создаёт лендинг через `landing-project-init` (вызывает `init.sh`).
   - **Копирует снепшотом** релевантные подпапки родителя:
     - `01_контекст/` → `<новый-лендинг>/01_КОНТЕКСТ/`
     - `05_исследования/` → `<новый-лендинг>/01_КОНТЕКСТ/исследования/`
     - `04_документы/прототип-*.md` → `<новый-лендинг>/07_КОНТЕНТ/prototype.md`
   - Записывает `01_КОНТЕКСТ/source-references.yaml` с информацией откуда копировалось.
4. Передаю управление `landing-orchestrator`, начиная с этапа 02 (материалы клиента) — этапы 00–01 уже частично заполнены.

## Аргументы

- `<slug>` — имя нового лендинга
- `--cinematic` (опционально)

## Изоляция

После копирования лендинг **не имеет связи** с родителем — он самодостаточен. Изменения в родителе не влияют на лендинг.

## Что НЕ делаю

- Symlink-и не создаю (только snapshot).
- Не модифицирую данные родительского проекта.
- Не угадываю прототип, если файлов нет — спрашиваю пользователя.

## Скрипт

См. [`scripts/from-context.sh`](scripts/from-context.sh).
```

- [ ] **Step 13.4: Run test, expect PASS**

- [ ] **Step 13.5: Commit**

```bash
git add skills/landing-from-context/SKILL.md tests/phase-1/test-skills-and-agents.bats
git commit -m "feat(phase-1): add landing-from-context skill"
```

---

### Task 14: Скрипт `from-context.sh`

**Files:**
- Create: `skills/landing-from-context/scripts/from-context.sh`
- Test: `tests/phase-1/test-from-context.bats`

- [ ] **Step 14.1: Создать тест**

`tests/phase-1/test-from-context.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
  # Simulate parent agency project structure
  export PARENT_DIR="$TEST_TEMP/parent-agency-project"
  mkdir -p "$PARENT_DIR/01_контекст"
  mkdir -p "$PARENT_DIR/05_исследования"
  mkdir -p "$PARENT_DIR/04_документы"
  echo "Niche info" > "$PARENT_DIR/01_контекст/niche.md"
  echo "Audience research" > "$PARENT_DIR/05_исследования/audience.md"
  echo "Prototype text" > "$PARENT_DIR/04_документы/прототип-марафон.md"

  export TARGET_DIR="$TEST_TEMP/lp-test-from-context"
}

teardown() {
  teardown_temp_dir
}

@test "from-context.sh exists and executable" {
  [ -x "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" ]
}

@test "from-context.sh creates project and copies parent context" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]

  # Project structure exists
  assert_dir_exists "$TARGET_DIR/00_БРИФ"

  # Context copied
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/niche.md"
  run grep "Niche info" "$TARGET_DIR/01_КОНТЕКСТ/niche.md"
  [ "$status" -eq 0 ]
}

@test "from-context.sh copies research subfolder" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/исследования/audience.md"
}

@test "from-context.sh copies prototype to 07_КОНТЕНТ" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/07_КОНТЕНТ/prototype.md"
}

@test "from-context.sh writes source-references.yaml" {
  cd "$PARENT_DIR"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET_DIR"
  [ "$status" -eq 0 ]
  assert_file_exists "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  run grep "parent_path" "$TARGET_DIR/01_КОНТЕКСТ/source-references.yaml"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 14.2: Run test, expect FAIL**

- [ ] **Step 14.3: Написать `from-context.sh`**

```bash
#!/usr/bin/env bash
# landing-from-context: create new landing inheriting context from parent agency project
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: from-context.sh <target-path> [--cinematic]"
  echo "  Run from inside a parent agency project folder."
  exit 1
fi

TARGET="$1"
CINEMATIC_FLAG=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --cinematic) CINEMATIC_FLAG="--cinematic"; shift ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

PARENT="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
INIT_SH="$SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh"

if [ ! -x "$INIT_SH" ]; then
  echo "❌ landing-project-init/init.sh not found or not executable"
  exit 2
fi

# --- Step 1: create blank project ---
echo "📦 Creating project skeleton..."
"$INIT_SH" "$TARGET" $CINEMATIC_FLAG

# --- Step 2: snapshot parent context ---
echo "📋 Snapshotting parent context from $PARENT ..."

# 01_контекст → 01_КОНТЕКСТ (copy contents)
if [ -d "$PARENT/01_контекст" ]; then
  cp -R "$PARENT/01_контекст/." "$TARGET/01_КОНТЕКСТ/"
  echo "  ✓ 01_контекст copied"
fi

# 05_исследования → 01_КОНТЕКСТ/исследования
if [ -d "$PARENT/05_исследования" ]; then
  mkdir -p "$TARGET/01_КОНТЕКСТ/исследования"
  cp -R "$PARENT/05_исследования/." "$TARGET/01_КОНТЕКСТ/исследования/"
  echo "  ✓ 05_исследования copied"
fi

# Prototype: look for files matching 'прототип-*.md' or 'prototype-*.md' in 04_документы
if [ -d "$PARENT/04_документы" ]; then
  mkdir -p "$TARGET/07_КОНТЕНТ"
  # First match wins
  for pattern in "прототип-*.md" "prototype-*.md" "прототип*.md"; do
    proto=$(find "$PARENT/04_документы" -maxdepth 1 -name "$pattern" -type f 2>/dev/null | head -1)
    if [ -n "$proto" ]; then
      cp "$proto" "$TARGET/07_КОНТЕНТ/prototype.md"
      echo "  ✓ Prototype copied: $(basename "$proto")"
      break
    fi
  done
fi

# --- Step 3: write source-references.yaml ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$TARGET/01_КОНТЕКСТ/source-references.yaml" <<EOF
# Snapshot manifest — created by landing-from-context
created: $TIMESTAMP
parent_path: $PARENT
parent_basename: $(basename "$PARENT")
copied:
  - source: 01_контекст
    target: 01_КОНТЕКСТ
  - source: 05_исследования
    target: 01_КОНТЕКСТ/исследования
  - source: 04_документы (prototype match)
    target: 07_КОНТЕНТ/prototype.md
note: |
  This is a snapshot. Changes in the parent project will NOT propagate here.
  To re-snapshot, delete 01_КОНТЕКСТ/* and run from-context.sh again.
EOF

# --- Step 4: extra commit in target ---
git -C "$TARGET" add -A >/dev/null
git -C "$TARGET" commit -m "chore: snapshot parent context" >/dev/null 2>&1 || true

echo ""
echo "✅ Project created with parent context: $TARGET"
echo ""
echo "Next:"
echo "  cd $TARGET"
echo "  claude"
echo "  > /landing-status"
```

- [ ] **Step 14.4: chmod + run test, expect PASS**

```bash
chmod +x skills/landing-from-context/scripts/from-context.sh
bats tests/phase-1/test-from-context.bats
# Expected: 5 passed
```

- [ ] **Step 14.5: Commit**

```bash
git add skills/landing-from-context/scripts/from-context.sh tests/phase-1/test-from-context.bats
git commit -m "feat(phase-1): add from-context.sh that snapshots parent context"
```

---

### Task 15: Агент `landing-orchestrator` (Phase 1 stub)

**Files:**
- Create: `agents/landing-orchestrator.md`

В Phase 1 это **stub** — он умеет принять контроль после init.sh и сказать «следующий этап будет в Phase 2». Полная функциональность придёт в Phase 2.

- [ ] **Step 15.1: Расширить test-skills-and-agents.bats**

```bash
@test "landing-orchestrator agent exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
}

@test "landing-orchestrator has frontmatter name" {
  run grep -E "^name: landing-orchestrator$" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
}

@test "landing-orchestrator has description" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md"
  [ "$status" -eq 0 ]
}

@test "landing-orchestrator mentions HARD GATE" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/agents/landing-orchestrator.md" "HARD GATE"
}
```

- [ ] **Step 15.2: Run test, expect FAIL**

- [ ] **Step 15.3: Создать `agents/landing-orchestrator.md`**

```markdown
---
name: landing-orchestrator
description: Master orchestrator for landing projects. Owns the 12-stage workflow, dispatches specialized agents, enforces HARD GATEs between stages. Use as the entry point after a project is initialized.
---

# landing-orchestrator (Главный дирижёр)

## Mission

Веди проект-лендинг через 12 этапов workflow:

| # | Stage | Agents (will be implemented in Phases 2–5) |
|---|---|---|
| 00 | Бриф | self |
| 01 | Контекст | self |
| 02 | Материалы клиента | client-assets-collector, photo-stylist |
| 03 | Референсы | references-curator, moodboard-composer, style-extractor |
| 04 | Бренд | brand-architect |
| 05 | Дизайн-система | design-system-generator, scene-director (cinematic) |
| 06 | Стек | stack-planner |
| 07 | Контент | content-writer |
| 08 | Код | wp-builder, integrations-engineer, analytics-engineer, seo-optimizer |
| 09 | Деплой | wp-deployer |
| 10 | QA | qa-auditor |
| 11 | Аналитика | analytics-engineer |
| 12 | SEO | seo-optimizer |

## Phase 1 Scope (текущая реализация)

В Phase 1 я умею **только**:
1. Принимать контроль после `landing-project-init` или `landing-from-context`.
2. Спрашивать пользователя: ниша / клиент / KPI / есть ли прототип / есть ли материалы клиента.
3. Заполнять `00_БРИФ/brief.md` на основе ответов.
4. Сообщать: «Phase 1 завершён. Этапы 02–12 будут доступны после Phase 2 implementation».

В Phase 2+ я расширюсь до полного дирижирования всех 12 этапов.

## HARD GATE правила

**Никогда** не идти на этап N+1 без явного утверждения этапа N. Утверждение = пользователь написал «утверждаю», «ok», «дальше», или эквивалент.

## Output template (Phase 1)

После сбора брифа я пишу в `00_БРИФ/brief.md`:

```markdown
# Бриф проекта {{PROJECT_NAME}}

**Дата:** YYYY-MM-DD
**Ниша:** ...
**Клиент:** ...
**Целевой URL:** ...
**KPI:** ...
**Дедлайн:** ...

## Цели лендинга

...

## Воронка

...

## Что есть на входе

- [ ] Прототип текста
- [ ] Фото клиента
- [ ] Видео-отзывы
- [ ] Доступ к Я.Метрике
- [ ] Доступ к Бегету
```

И вывожу пользователю:
> ✅ Бриф зафиксирован в `00_БРИФ/brief.md`. Этап 00 завершён.
>
> 🚧 Этапы 02–12 ещё не реализованы (Phase 2+). После реализации Phase 2 ты сможешь продолжить через `/landing-references`.

## Tools available

В Phase 1: Read, Write, Edit, Bash. В Phase 2+ — Task для дёргания специализированных агентов.
```

- [ ] **Step 15.4: Run test, expect PASS**

- [ ] **Step 15.5: Commit**

```bash
git add agents/landing-orchestrator.md tests/phase-1/test-skills-and-agents.bats
git commit -m "feat(phase-1): add landing-orchestrator agent (Phase 1 stub)"
```

---

## Block D — Slash Commands

### Task 16: Slash-команда `/landing-new`

**Files:**
- Create: `.claude/commands/landing-new.md`
- Test: `tests/phase-1/test-commands.bats`

- [ ] **Step 16.1: Создать тест**

`tests/phase-1/test-commands.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

@test "landing-new command file exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
}

@test "landing-new has description frontmatter" {
  run grep -E "^description:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
  [ "$status" -eq 0 ]
}

@test "landing-new references init.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md" "init.sh"
}

@test "landing-new mentions argument-hint" {
  run grep -E "^argument-hint:" "$LANDING_SYSTEM_ROOT/.claude/commands/landing-new.md"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 16.2: Run test, expect FAIL**

- [ ] **Step 16.3: Создать `.claude/commands/landing-new.md`**

```markdown
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
SCRIPT="${CLAUDE_PROJECT_DIR:-.}/skills/landing-project-init/scripts/init.sh"
bash "$SCRIPT" "$TARGET" "${@:2}"
```

After successful run, dispatch `landing-orchestrator` agent to lead the user through Stage 00 (brief).
```

- [ ] **Step 16.4: Run test, expect PASS**

- [ ] **Step 16.5: Commit**

```bash
git add .claude/commands/landing-new.md tests/phase-1/test-commands.bats
git commit -m "feat(phase-1): add /landing-new slash command"
```

---

### Task 17: Slash-команда `/landing-from-context`

**Files:**
- Create: `.claude/commands/landing-from-context.md`

- [ ] **Step 17.1: Расширить test-commands.bats**

```bash
@test "landing-from-context command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-from-context.md"
}

@test "landing-from-context references from-context.sh" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-from-context.md" "from-context.sh"
}
```

- [ ] **Step 17.2: Run test, expect FAIL**

- [ ] **Step 17.3: Создать `.claude/commands/landing-from-context.md`**

```markdown
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

SCRIPT="${CLAUDE_PROJECT_DIR:-.}/skills/landing-from-context/scripts/from-context.sh"
bash "$SCRIPT" "$TARGET" "${@:2}"
```

After project is created with parent snapshot, dispatch `landing-orchestrator` starting from Stage 02 (Materials) — Stages 00–01 are partially pre-filled from snapshot.
```

- [ ] **Step 17.4: Run test, expect PASS**

- [ ] **Step 17.5: Commit**

```bash
git add .claude/commands/landing-from-context.md tests/phase-1/test-commands.bats
git commit -m "feat(phase-1): add /landing-from-context slash command"
```

---

### Task 18: Slash-команда `/landing-help`

**Files:**
- Create: `.claude/commands/landing-help.md`

- [ ] **Step 18.1: Расширить test-commands.bats**

```bash
@test "landing-help command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md"
}

@test "landing-help lists landing-new" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md" "/landing-new"
}

@test "landing-help lists landing-status" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-help.md" "/landing-status"
}
```

- [ ] **Step 18.2: Run test, expect FAIL**

- [ ] **Step 18.3: Создать `.claude/commands/landing-help.md`**

```markdown
---
description: Show all landing-system slash commands and their usage
allowed-tools: Read
---

# /landing-help

Print a summary of all available landing-system commands.

## Output

Print exactly:

```
Landing System — Commands

ENTRY POINTS:
  /landing-new <slug>              — new project from scratch
  /landing-from-context <slug>     — new project from parent agency folder
  /landing-clone <src> --as <new>  — A/B copy of existing landing (Phase 5)

PER-STAGE (Phase 2+):
  /landing-references              — stage 03
  /landing-moodboard               — stage 03
  /landing-brand                   — stage 04
  /landing-design                  — stage 05
  /landing-stack                   — stage 06
  /landing-content                 — stage 07
  /landing-build                   — stage 08

OPERATIONS (Phase 5):
  /landing-deploy                  — deploy to Бегет
  /landing-redeploy                — redeploy after edits
  /landing-rollback <version>      — rollback
  /landing-qa                      — run QA audit

SERVICE:
  /landing-status                  — current state
  /landing-help                    — this help
  /landing-update                  — update master system

Phase 1 of MVP is in progress. Most stage commands return "not yet implemented".
See docs/superpowers/plans/ for roadmap.
```

End of help.
```

- [ ] **Step 18.4: Run test, expect PASS**

- [ ] **Step 18.5: Commit**

```bash
git add .claude/commands/landing-help.md tests/phase-1/test-commands.bats
git commit -m "feat(phase-1): add /landing-help slash command"
```

---

### Task 19: Slash-команда `/landing-status`

**Files:**
- Create: `.claude/commands/landing-status.md`

- [ ] **Step 19.1: Расширить test-commands.bats**

```bash
@test "landing-status command exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md"
}

@test "landing-status mentions Phase 1" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/.claude/commands/landing-status.md" "Phase 1"
}
```

- [ ] **Step 19.2: Run test, expect FAIL**

- [ ] **Step 19.3: Создать `.claude/commands/landing-status.md`**

```markdown
---
description: Show current state of the landing system and active projects
allowed-tools: Read, Bash
---

# /landing-status

Show the current state of the master system and any active project in the cwd.

## Algorithm

1. **Master system check** (cwd is `landing-system/` or contains `skills/landing-project-init/`):
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

# Master system?
if [ -d "$CWD/skills/landing-project-init" ]; then
  echo "📦 Landing System (master)"
  if [ -f "$CWD/package.json" ]; then
    VERSION=$(node -e "console.log(require('$CWD/package.json').version)" 2>/dev/null || echo "unknown")
    echo "   Version: $VERSION"
  fi
  echo "   Phase 1: Skeleton & Infrastructure"
  echo ""
  echo "   Skills:"
  for skill in "$CWD"/skills/*/SKILL.md; do
    name=$(basename "$(dirname "$skill")")
    echo "     - $name"
  done
  echo ""
  echo "   Agents:"
  for agent in "$CWD"/agents/*.md; do
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
  [ -d "$CWD/01_КОНТЕКСТ" ] && [ "$(ls -A "$CWD/01_КОНТЕКСТ" 2>/dev/null)" ] && STAGE=2
  [ -d "$CWD/02_МАТЕРИАЛЫ_КЛИЕНТА" ] && [ "$(ls -A "$CWD/02_МАТЕРИАЛЫ_КЛИЕНТА" 2>/dev/null | grep -v .gitkeep)" ] && STAGE=3
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
```

- [ ] **Step 19.4: Run test, expect PASS**

- [ ] **Step 19.5: Commit**

```bash
git add .claude/commands/landing-status.md tests/phase-1/test-commands.bats
git commit -m "feat(phase-1): add /landing-status slash command"
```

---

## Block E — Settings & Integration

### Task 20: `.claude/settings.json` (Phase 1 baseline)

**Files:**
- Create: `.claude/settings.json`

В Phase 1 hooks ещё не реализованы (это Phase 5). Сейчас просто валидный пустой settings.

- [ ] **Step 20.1: Расширить test-skills-and-agents.bats**

```bash
@test ".claude/settings.json exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/.claude/settings.json"
}

@test ".claude/settings.json is valid JSON" {
  run node -e "JSON.parse(require('fs').readFileSync('$LANDING_SYSTEM_ROOT/.claude/settings.json', 'utf8'))"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 20.2: Run test, expect FAIL**

- [ ] **Step 20.3: Создать `.claude/settings.json`**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(bash scripts/check-deps.sh)",
      "Bash(bash skills/landing-project-init/scripts/init.sh:*)",
      "Bash(bash skills/landing-from-context/scripts/from-context.sh:*)",
      "Bash(bats tests/**/*.bats)",
      "Bash(bats tests/phase-1/*.bats)",
      "Bash(npm test)",
      "Bash(npm run test:phase-1)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ]
  },
  "hooks": {}
}
```

- [ ] **Step 20.4: Run test, expect PASS**

- [ ] **Step 20.5: Commit**

```bash
git add .claude/settings.json tests/phase-1/test-skills-and-agents.bats
git commit -m "feat(phase-1): add baseline .claude/settings.json with permissions"
```

---

### Task 21: Integration test — end-to-end Phase 1

**Files:**
- Create: `tests/phase-1/test-integration.bats`

Этот тест проверяет всё Phase 1 в связке: «возьми чистую папку, запусти init.sh, проверь что всё на месте».

- [ ] **Step 21.1: Создать тест**

`tests/phase-1/test-integration.bats`:
```bash
#!/usr/bin/env bats

load '../helpers/test_helpers'

setup() {
  setup_temp_dir
}

teardown() {
  teardown_temp_dir
}

@test "INTEGRATION: full Phase 1 — create project from scratch" {
  TARGET="$TEST_TEMP/integration-project"

  # 1. Run init.sh
  run "$LANDING_SYSTEM_ROOT/skills/landing-project-init/scripts/init.sh" "$TARGET"
  [ "$status" -eq 0 ]

  # 2. All 13 stage folders exist
  for n in 00_БРИФ 01_КОНТЕКСТ 02_МАТЕРИАЛЫ_КЛИЕНТА 03_РЕФЕРЕНСЫ 04_БРЕНД 05_ДИЗАЙН-СИСТЕМА 06_СТЕК 07_КОНТЕНТ 08_КОД 09_ДЕПЛОЙ 10_QA 11_АНАЛИТИКА 12_SEO; do
    [ -d "$TARGET/$n" ] || { echo "missing: $n"; return 1; }
  done

  # 3. Project files exist
  [ -f "$TARGET/CLAUDE.md" ]
  [ -f "$TARGET/README.md" ]
  [ -f "$TARGET/.env.example" ]
  [ -f "$TARGET/.gitignore" ]

  # 4. Git initialized with commit
  [ -d "$TARGET/.git" ]
  run git -C "$TARGET" log --oneline
  [ "$status" -eq 0 ]
  [ -n "$output" ]
}

@test "INTEGRATION: from-context with parent" {
  PARENT="$TEST_TEMP/parent"
  mkdir -p "$PARENT/01_контекст" "$PARENT/04_документы"
  echo "niche stuff" > "$PARENT/01_контекст/niche.md"
  echo "proto" > "$PARENT/04_документы/прототип-test.md"

  TARGET="$TEST_TEMP/from-ctx-project"
  cd "$PARENT"
  run "$LANDING_SYSTEM_ROOT/skills/landing-from-context/scripts/from-context.sh" "$TARGET"
  [ "$status" -eq 0 ]

  # Project skeleton intact
  [ -d "$TARGET/00_БРИФ" ]
  # Context copied
  [ -f "$TARGET/01_КОНТЕКСТ/niche.md" ]
  [ -f "$TARGET/07_КОНТЕНТ/prototype.md" ]
  [ -f "$TARGET/01_КОНТЕКСТ/source-references.yaml" ]
}

@test "INTEGRATION: dependency check passes" {
  run "$LANDING_SYSTEM_ROOT/scripts/check-deps.sh"
  [ "$status" -eq 0 ]
}

@test "INTEGRATION: all skills have valid SKILL.md" {
  for skill_dir in "$LANDING_SYSTEM_ROOT"/skills/*/; do
    skill_md="$skill_dir/SKILL.md"
    [ -f "$skill_md" ] || { echo "missing SKILL.md in $skill_dir"; return 1; }
    grep -qE "^name:" "$skill_md" || { echo "no name in $skill_md"; return 1; }
    grep -qE "^description:" "$skill_md" || { echo "no description in $skill_md"; return 1; }
  done
}

@test "INTEGRATION: all agents have valid frontmatter" {
  for agent_md in "$LANDING_SYSTEM_ROOT"/agents/*.md; do
    grep -qE "^name:" "$agent_md" || { echo "no name in $agent_md"; return 1; }
    grep -qE "^description:" "$agent_md" || { echo "no description in $agent_md"; return 1; }
  done
}

@test "INTEGRATION: all commands have description" {
  for cmd_md in "$LANDING_SYSTEM_ROOT"/.claude/commands/*.md; do
    grep -qE "^description:" "$cmd_md" || { echo "no description in $cmd_md"; return 1; }
  done
}

@test "INTEGRATION: npm test runs all phase-1 tests successfully" {
  cd "$LANDING_SYSTEM_ROOT"
  run npm run test:phase-1
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 21.2: Run test (initial state)**

```bash
bats tests/phase-1/test-integration.bats
# Last test (npm run test:phase-1) may recurse — guard against this in CI later
```

Some sub-tests may pass already; the goal is the entire suite green.

- [ ] **Step 21.3: Если что-то сломалось — исправить и перезапустить**

(Этот таск может выявить regressions в предыдущих задачах. Если выявил — фиксим в отдельном коммите `fix:` перед continuation.)

- [ ] **Step 21.4: Commit когда зелёное**

```bash
git add tests/phase-1/test-integration.bats
git commit -m "test(phase-1): add end-to-end integration tests"
```

---

### Task 22: Финальный self-review + обновление master plan статуса

**Files:**
- Modify: `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` (статус Phase 1 → 🟢 complete)

- [ ] **Step 22.1: Прогнать все Phase 1 тесты ещё раз**

```bash
cd landing-system
bash scripts/check-deps.sh
npm run test:phase-1
```

Expected: ALL PASS.

- [ ] **Step 22.2: Self-review против spec разделов 4, 6, 10, 17, 18**

Открыть spec и проверить:
- Spec § 4 (структура папки проекта 00–12) — есть ли в template? ✅
- Spec § 6 (карта 18 агентов) — landing-orchestrator stub есть? ✅
- Spec § 10 (slash-команды) — Phase 1 команды реализованы? ✅
- Spec § 17 (упаковка MVP — ZIP) — структура для ZIP готова? ✅
- Spec § 18 (установка пошагово) — README отражает Quick Start? ✅

Любые расхождения — исправить inline.

- [ ] **Step 22.3: Обновить master plan**

В `docs/superpowers/plans/2026-05-03-landing-system-master-plan.md` строку Phase 1 поменять с `🟡 Plan ready` на `🟢 Complete (YYYY-MM-DD)`.

- [ ] **Step 22.4: Commit финальный**

```bash
git add docs/superpowers/plans/2026-05-03-landing-system-master-plan.md
git commit -m "docs(phase-1): mark Phase 1 as complete in master plan

Phase 1 — Skeleton & Infrastructure delivers:
- 13-folder template/ for project scaffolding
- Skills: landing-project-init, landing-from-context
- Agent: landing-orchestrator (stub for stages 00-01)
- Slash commands: /landing-new, /landing-from-context, /landing-help, /landing-status
- 7 bats test suites, all green
- README + CLAUDE.md + .env templates

Ready to proceed to Phase 2 plan."
```

- [ ] **Step 22.5: Tag the milestone**

```bash
git tag -a phase-1-complete -m "Phase 1: Skeleton & Infrastructure complete"
```

---

## Self-Review (по методике writing-plans)

**1. Spec coverage:**
- ✅ Spec § 4 (структура папок) → Tasks 5–10
- ✅ Spec § 6 агент `landing-orchestrator` → Task 15
- ✅ Spec § 10 (slash-команды Phase 1) → Tasks 16–19
- ✅ Spec § 17 (MVP ZIP) — структура мастер-системы готова → Tasks 0–4 + master CLAUDE/README
- ✅ Spec § 18 (Quick Start в README) → Task 10
- ⚠️ Hooks (раздел 15 spec) — заглушка в settings.json (Task 20). Полная реализация — Phase 5.
- ⚠️ Скиллы из anthropic/skills и tapestry — устанавливаются ученикам отдельно (см. §18 spec). В Phase 1 не упаковываем.

**2. Placeholder scan:**
- Нет TBD / TODO в задачах.
- Все шаги содержат конкретный код.
- Нет «similar to Task N» — код повторяется в каждой задаче.

**3. Type consistency:**
- Имя скиллов: `landing-project-init`, `landing-from-context` — единое везде ✅
- Имена скриптов: `init.sh`, `from-context.sh` — единое везде ✅
- Имена slash-команд начинаются с `landing-` ✅
- Bats-тесты пути относительно `$LANDING_SYSTEM_ROOT` ✅

**4. Ambiguity check:**
- Все пути к файлам абсолютные или относительные от `$LANDING_SYSTEM_ROOT`.
- Команды одинаково на macOS и Linux (sed -i.bak — портабельно).
- Есть guard против Windows (нужен WSL).

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-03-phase-1-skeleton.md`.

**Two execution options:**

**1. Subagent-Driven (рекомендую)** — я диспатчирую свежий субагент на каждую из 22 задач, между задачами провожу двухступенчатое ревью (spec compliance + code quality), быстрая итерация. Идеально для длинных планов.

**2. Inline Execution** — задачи выполняются в текущей сессии через `executing-plans`, batch с чекпоинтами на пользовательское ревью.

**Which approach?**

После завершения Phase 1 — запишу план Phase 2 (Brainstorming Pipeline: этапы 00–04) и продолжим.

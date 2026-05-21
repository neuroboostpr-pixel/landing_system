# S2-CD Phase CD1: Multisite Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Дать маркетологу команду `/landing-segment <name>` которая создаёт новый сегмент целевой аудитории (поддомен + WordPress subsite + skeleton в файловой системе проекта) внутри multisite-сети. Включает автоматическую миграцию single-site → multisite при первом сегменте, а также скрипт `clone-subsite.sh` для byte-by-byte копирования между сегментами.

**Architecture:** Скилл `wp-multisite` оборачивает Beget API + wp-cli в идемпотентные bash-скрипты. Все вызовы Beget API инкапсулированы в `lib/beget-api.sh` (валидированы POC). State синхронизирован через `.landing-state.yaml::audience_segments[]`. Каждый шаг каждого скрипта пишет в `<project>/.landing-state.yaml` сразу после успеха — рестарт после фейла продолжает с того же места.

**Tech Stack:**
- bash 5+ (Git Bash на Windows, обычный bash на Linux)
- Python 3.8+ с PyYAML (для чтения/записи `.landing-state.yaml`)
- wp-cli (на Бегете доступен через `/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar`)
- bats-core (для тестов скриптов) — `npm install -g bats` или `apt install bats`
- curl для Beget API запросов

**Validated на POC:** см. [docs/beget-cookbook.md](../../beget-cookbook.md) и [tests/poc/](../../../tests/poc/).

---

## Терминология

**«Сегмент ЦА» (segment, audience segment)** — отдельная версия лендинга одного клиента под конкретный сегмент его целевой аудитории. Пример для клиента LiAuto в Дубае: `russian` (русскоязычные в Дубае), `family` (семьи с детьми), `business` (бизнес-туристы). Каждый сегмент = отдельный поддомен (`russian.liauto.dubai`) = отдельный WordPress subsite в multisite-сети одного клиентского домена.

**«Multisite migration»** — одноразовая операция превращения single-site WordPress проекта в multisite-сеть (subdomain mode). Запускается автоматически перед созданием первого сегмента ЦА.

---

## Pre-requisites (validated before plan starts)

- `.env` файл проекта содержит `BEGET_USER`, `BEGET_HOST`, `BEGET_API_PASSWORD`, `BEGET_DOMAIN_ID` (последнее — нужно для `addSubdomainVirtual`)
- Проект уже задеплоен в single-site режиме (есть валидный wp-config.php, БД, тема активна)
- SSH-ключ доступен по `BEGET_SSH_KEY` (default `~/.ssh/id_rsa` или из `.env`)
- bats-core установлен локально (для запуска тестов)

---

## File Structure

### Создаём

| Путь | Ответственность |
|------|------|
| `skills/wp-multisite/SKILL.md` | Описание скилла, точка входа, ссылки на скрипты |
| `skills/wp-multisite/scripts/lib/beget-api.sh` | Production-ready обёртка Beget API: `beget_api`, `beget_ok`, `beget_subdomain_add`, `beget_site_link`, `beget_set_php` |
| `skills/wp-multisite/scripts/lib/ssh-helpers.sh` | `ssh_beget`, `wp_remote` обёртки + `REMOTE_WP` constant (`/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar`) |
| `skills/wp-multisite/scripts/lib/state.sh` | `state_get_field`, `state_add_segment`, `state_set_multisite_true` через python+yaml |
| `skills/wp-multisite/scripts/migrate-to-multisite.sh` | Одноразовая миграция single→multisite |
| `skills/wp-multisite/scripts/landing-segment.sh` | Создание нового сегмента ЦА |
| `skills/wp-multisite/scripts/clone-subsite.sh` | Копирование контента source-subsite → dest-subsite |
| `skills/wp-multisite/tests/test_beget_api_lib.bats` | Unit-тесты обёртки (мок curl) |
| `skills/wp-multisite/tests/test_state_lib.bats` | Unit-тесты state-обёртки |
| `skills/wp-multisite/tests/test_migrate_to_multisite.bats` | Integration-тест миграции (на fixture-проекте) |
| `skills/wp-multisite/tests/test_landing_segment.bats` | Integration-тест создания сегмента |
| `skills/wp-multisite/tests/test_clone_subsite.bats` | Integration-тест клонирования |
| `skills/wp-multisite/tests/fixtures/.env.example` | Шаблон .env для тестов |
| `skills/wp-multisite/tests/fixtures/landing-state.single.yaml` | State до миграции |
| `skills/wp-multisite/tests/fixtures/landing-state.multisite.yaml` | State после миграции |
| `.claude/commands/landing-segment.md` | Slash-команда `/landing-segment <slug>` |
| `template/13_СЕГМЕНТЫ_ЦА/README.md` | Документация для маркетолога |
| `template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md` | Что внутри одного сегмента |
| `template/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example` | Пример subbrief.yaml |

### Изменяем

| Путь | Что меняем |
|------|------|
| `template/.landing-state.yaml` | Добавляем `multisite: false` и `audience_segments: []` |
| `.claude/commands/landing-clone.md` | Переписан под multisite-модель (был filesystem copy, стал subsite copy) |
| `skills/landing-versioning-and-cloning/SKILL.md` | Добавлен deprecation-notice о `clone-landing.sh` (используется только для legacy single-site) |
| `CLAUDE.md` | Добавлен раздел «Multisite режим и сегменты ЦА» |
| `docs/SETUP.md` | Добавлен раздел «Когда нужна миграция в multisite» |

---

## Task 1: Setup skill skeleton + lib/beget-api.sh

**Files:**
- Create: `skills/wp-multisite/SKILL.md`
- Create: `skills/wp-multisite/scripts/lib/beget-api.sh`
- Test: `skills/wp-multisite/tests/test_beget_api_lib.bats`
- Create: `skills/wp-multisite/tests/fixtures/.env.example`

- [ ] **Step 1: Write the failing test for beget_api function**

Create `skills/wp-multisite/tests/test_beget_api_lib.bats`:

```bash
#!/usr/bin/env bats
# Unit tests for lib/beget-api.sh — beget_api wrapper

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    # Mock curl: write expected stub responses
    MOCK_DIR="$(mktemp -d)"
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Mock curl that prints fixture based on method in URL
url=""
for arg in "$@"; do
    case "$arg" in
        https://*) url="$arg" ;;
    esac
done
case "$url" in
    *getAccountInfo*)
        echo '{"status":"success","answer":{"status":"success","result":{"plan_name":"Blog"}}}'
        ;;
    *getList*)
        echo '{"status":"success","answer":{"status":"success","result":[{"id":12513532,"fqdn":"example.ru"}]}}'
        ;;
    *)
        echo '{"status":"success","answer":{"status":"error","errors":[{"error_code":"UNEXPECTED","error_text":"mock fallthrough"}]}}'
        ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    PATH="$MOCK_DIR:$PATH"
    export PATH
    export BEGET_API="https://api.beget.com/api"
    export BEGET_LOGIN="testuser"
    export BEGET_PASSWD="testpass"
    source "$HERE/beget-api.sh"
}

teardown() {
    rm -rf "$MOCK_DIR"
}

@test "beget_api wraps a successful call and returns the JSON body" {
    run beget_api "user/getAccountInfo"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"plan_name":"Blog"'* ]]
}

@test "beget_ok returns 0 when both outer and inner status are success" {
    resp='{"status":"success","answer":{"status":"success","result":true}}'
    run beget_ok "$resp"
    [ "$status" -eq 0 ]
}

@test "beget_ok returns 1 when inner status is error" {
    resp='{"status":"success","answer":{"status":"error","errors":[{"error_text":"x"}]}}'
    run beget_ok "$resp"
    [ "$status" -eq 1 ]
}

@test "beget_ok returns 1 when outer status is error" {
    resp='{"status":"error","error_text":"auth"}'
    run beget_ok "$resp"
    [ "$status" -eq 1 ]
}
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `bats skills/wp-multisite/tests/test_beget_api_lib.bats`
Expected: ERROR (file `scripts/lib/beget-api.sh` does not exist)

- [ ] **Step 3: Create lib/beget-api.sh with minimal implementation**

Create `skills/wp-multisite/scripts/lib/beget-api.sh`:

```bash
#!/usr/bin/env bash
# Production-ready Beget API wrapper.
# Required env: BEGET_API, BEGET_LOGIN, BEGET_PASSWD
# Validated on POC against ailexi.ru / esper21 account 2026-05-18.

beget_api() {
    # beget_api <category/method> [input_data_json]
    local method="$1"
    local input_data="${2:-{}}"
    curl -s -X POST "${BEGET_API}/${method}" \
        --data-urlencode "login=${BEGET_LOGIN}" \
        --data-urlencode "passwd=${BEGET_PASSWD}" \
        --data-urlencode "input_format=json" \
        --data-urlencode "output_format=json" \
        --data-urlencode "input_data=${input_data}"
}

beget_ok() {
    # beget_ok <json_response> — exit 0 if both outer.status and answer.status == "success"
    local resp="$1"
    local outer inner
    outer=$(printf '%s' "$resp" | python -c 'import sys,json
try: print(json.load(sys.stdin).get("status",""))
except: print("")' 2>/dev/null)
    inner=$(printf '%s' "$resp" | python -c 'import sys,json
try: print(json.load(sys.stdin).get("answer",{}).get("status",""))
except: print("")' 2>/dev/null)
    [ "$outer" = "success" ] && [ "$inner" = "success" ]
}

beget_error_text() {
    # beget_error_text <json_response> — extract first error_text for diagnostics
    printf '%s' "$1" | python -c 'import sys,json
try:
    d=json.load(sys.stdin)
    errs=d.get("answer",{}).get("errors") or [{"error_text": d.get("error_text","unknown")}]
    print(errs[0].get("error_text","unknown"))
except: print("parse_error")' 2>/dev/null
}
```

- [ ] **Step 4: Run the test and verify it passes**

Run: `bats skills/wp-multisite/tests/test_beget_api_lib.bats`
Expected: 4 tests pass, 0 failures

- [ ] **Step 5: Create SKILL.md skeleton**

Create `skills/wp-multisite/SKILL.md`:

```markdown
---
name: wp-multisite
description: Manage WordPress Multisite networks on Beget shared hosting — migration from single-site, segment creation, subsite cloning. Use when a project needs more than one landing under one client domain.
---

# wp-multisite

Скилл управляет WordPress Multisite-сетями на Beget shared hosting:
миграция single-site → multisite, создание сегментов ЦА (поддоменов),
клонирование контента между сегментами.

Все скрипты валидированы POC на ailexi.ru — см. [tests/poc/RESULTS.md](../../tests/poc/RESULTS.md).

## Скрипты

### migrate-to-multisite.sh
```bash
bash skills/wp-multisite/scripts/migrate-to-multisite.sh <project-dir>
```
Превращает single-site WordPress проект в multisite (subdomain mode).
Идемпотентен. Read `.landing-state.yaml::multisite` — если уже `true`, no-op.

### landing-segment.sh
```bash
bash skills/wp-multisite/scripts/landing-segment.sh <project-dir> <segment-slug>
```
Создаёт новый сегмент ЦА: Beget subdomain + WP subsite + skeleton директории
`<project>/13_СЕГМЕНТЫ_ЦА/<slug>/`. Если проект ещё single-site —
автоматически запускает миграцию.

### clone-subsite.sh
```bash
bash skills/wp-multisite/scripts/clone-subsite.sh <project-dir> <source-slug> <dest-slug>
```
Копирует все страницы из source-сегмента в новый dest-сегмент.
Byte-by-byte: текст, фото-ссылки, опции (siteurl/home переписываются).

## Lib

- `lib/beget-api.sh` — обёртка Beget API
- `lib/ssh-helpers.sh` — SSH + wp-cli обёртки
- `lib/state.sh` — read/write `.landing-state.yaml`
```

- [ ] **Step 6: Create test .env fixture**

Create `skills/wp-multisite/tests/fixtures/.env.example`:

```bash
# Test environment for skills/wp-multisite/tests/
# Copy to .env and fill real values to run integration tests against live Beget.
BEGET_USER="esper21"
BEGET_HOST="esper21.beget.tech"
BEGET_LOGIN="esper21"
BEGET_PASSWD="YOUR_BEGET_API_PASSWORD"
BEGET_API="https://api.beget.com/api"
BEGET_SSH_KEY="$HOME/.ssh/beget_poc"
BEGET_DOMAIN_ID=12513532  # ailexi.ru — get yours via beget_api domain/getList
TEST_ROOT_DOMAIN="ailexi.ru"
```

- [ ] **Step 7: Commit**

```bash
git add skills/wp-multisite/SKILL.md \
        skills/wp-multisite/scripts/lib/beget-api.sh \
        skills/wp-multisite/tests/test_beget_api_lib.bats \
        skills/wp-multisite/tests/fixtures/.env.example
git commit -m "feat(wp-multisite): skill skeleton + lib/beget-api.sh

Wraps Beget API for multisite operations. Unit tests with mocked curl
verify beget_api/beget_ok contract. SKILL.md documents future scripts.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: lib/beget-api.sh — domain/subdomain/site/php helpers

**Files:**
- Modify: `skills/wp-multisite/scripts/lib/beget-api.sh`
- Modify: `skills/wp-multisite/tests/test_beget_api_lib.bats`

- [ ] **Step 1: Write failing tests for the 4 helper functions**

Append to `skills/wp-multisite/tests/test_beget_api_lib.bats`:

```bash
@test "beget_subdomain_exists returns 0 when subdomain present in list" {
    # Override mock to return one subdomain
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[{"id":42,"fqdn":"alpha.example.ru","domain_id":1}]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_exists "alpha.example.ru"
    [ "$status" -eq 0 ]
}

@test "beget_subdomain_exists returns 1 when subdomain absent" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_exists "alpha.example.ru"
    [ "$status" -eq 1 ]
}

@test "beget_subdomain_add returns the new subdomain id on success" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":99}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_add "alpha" 12513532
    [ "$status" -eq 0 ]
    [ "$output" = "99" ]
}

@test "beget_subdomain_id returns id of named subdomain when present" {
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo '{"status":"success","answer":{"status":"success","result":[{"id":77,"fqdn":"beta.example.ru"}]}}'
MOCK
    chmod +x "$MOCK_DIR/curl"
    run beget_subdomain_id "beta.example.ru"
    [ "$status" -eq 0 ]
    [ "$output" = "77" ]
}
```

- [ ] **Step 2: Run tests — verify the 4 new tests fail**

Run: `bats skills/wp-multisite/tests/test_beget_api_lib.bats`
Expected: 4 of 8 fail with "function not found"

- [ ] **Step 3: Implement helpers in lib/beget-api.sh**

Append to `skills/wp-multisite/scripts/lib/beget-api.sh`:

```bash
# --- Subdomain helpers ----------------------------------------------------

beget_subdomain_exists() {
    # beget_subdomain_exists <fqdn> — exit 0 if subdomain found in account
    local fqdn="$1"
    local resp
    resp=$(beget_api "domain/getSubdomainList")
    printf '%s' "$resp" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    found = any(x.get('fqdn') == '$fqdn' for x in d.get('answer', {}).get('result', []))
    sys.exit(0 if found else 1)
except Exception:
    sys.exit(1)
"
}

beget_subdomain_id() {
    # beget_subdomain_id <fqdn> — print numeric id; exit 1 if not found
    local fqdn="$1"
    local resp
    resp=$(beget_api "domain/getSubdomainList")
    printf '%s' "$resp" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for x in d.get('answer', {}).get('result', []):
        if x.get('fqdn') == '$fqdn':
            print(x['id']); sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
"
}

beget_subdomain_add() {
    # beget_subdomain_add <subdomain> <root_domain_id> — print new subdomain id
    local sub="$1" root_id="$2"
    local resp
    resp=$(beget_api "domain/addSubdomainVirtual" "{\"subdomain\":\"$sub\",\"domain_id\":$root_id}")
    if beget_ok "$resp"; then
        printf '%s' "$resp" | python -c "
import sys, json
print(json.load(sys.stdin)['answer']['result'])
"
        return 0
    fi
    echo "beget_subdomain_add failed: $(beget_error_text "$resp")" >&2
    return 1
}

# --- Site/domain linking --------------------------------------------------

beget_site_link() {
    # beget_site_link <domain_id> <site_id> — exit 0 on success
    local dom_id="$1" site_id="$2"
    local resp
    resp=$(beget_api "site/linkDomain" "{\"domain_id\":$dom_id,\"site_id\":$site_id}")
    beget_ok "$resp" || {
        echo "beget_site_link failed: $(beget_error_text "$resp")" >&2
        return 1
    }
}

# --- PHP version ---------------------------------------------------------

beget_set_php() {
    # beget_set_php <full_fqdn> <version> — e.g. "alpha.ailexi.ru" "8.3"
    local fqdn="$1" version="$2"
    local resp
    resp=$(beget_api "domain/changePhpVersion" "{\"full_fqdn\":\"$fqdn\",\"php_version\":\"$version\"}")
    beget_ok "$resp" || {
        echo "beget_set_php failed: $(beget_error_text "$resp")" >&2
        return 1
    }
}
```

- [ ] **Step 4: Run all tests — verify 8/8 pass**

Run: `bats skills/wp-multisite/tests/test_beget_api_lib.bats`
Expected: 8 tests pass, 0 failures

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/lib/beget-api.sh \
        skills/wp-multisite/tests/test_beget_api_lib.bats
git commit -m "feat(wp-multisite): add subdomain/site/php helpers to beget-api lib

beget_subdomain_exists/add/id, beget_site_link, beget_set_php — these
are the 5 Beget API operations needed for migration + segment creation,
all validated on POC. Unit tests with mocked curl cover happy and error paths.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: lib/ssh-helpers.sh

**Files:**
- Create: `skills/wp-multisite/scripts/lib/ssh-helpers.sh`
- Create: `skills/wp-multisite/tests/test_ssh_helpers.bats`

- [ ] **Step 1: Write the failing test for ssh-helpers**

Create `skills/wp-multisite/tests/test_ssh_helpers.bats`:

```bash
#!/usr/bin/env bats
# Unit tests for lib/ssh-helpers.sh — uses mock ssh

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    MOCK_DIR="$(mktemp -d)"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "MOCK_SSH_CALLED $*"
MOCK
    chmod +x "$MOCK_DIR/ssh"
    PATH="$MOCK_DIR:$PATH"
    export PATH
    export BEGET_USER="testuser"
    export BEGET_HOST="example.beget.tech"
    export BEGET_SSH_KEY="/tmp/fake_key"
    source "$HERE/ssh-helpers.sh"
}

teardown() { rm -rf "$MOCK_DIR"; }

@test "ssh_beget runs ssh with -i key and user@host" {
    run ssh_beget "echo hello"
    [ "$status" -eq 0 ]
    [[ "$output" == *"MOCK_SSH_CALLED"* ]]
    [[ "$output" == *"-i /tmp/fake_key"* ]]
    [[ "$output" == *"testuser@example.beget.tech"* ]]
    [[ "$output" == *"echo hello"* ]]
}

@test "wp_remote prepends REMOTE_WP path to args and quotes them" {
    run wp_remote "/wp/path" "option get siteurl"
    [ "$status" -eq 0 ]
    [[ "$output" == *"cd /wp/path"* ]]
    [[ "$output" == *"/usr/local/bin/php8.3"* ]]
    [[ "$output" == *"option get siteurl"* ]]
}

@test "wp_remote_url prepends --url flag" {
    run wp_remote_url "/wp/path" "http://alpha.example.ru" "post list"
    [ "$status" -eq 0 ]
    [[ "$output" == *"--url=http://alpha.example.ru"* ]]
    [[ "$output" == *"post list"* ]]
}
```

- [ ] **Step 2: Run the test — verify it fails**

Run: `bats skills/wp-multisite/tests/test_ssh_helpers.bats`
Expected: ERROR (file does not exist)

- [ ] **Step 3: Implement ssh-helpers.sh**

Create `skills/wp-multisite/scripts/lib/ssh-helpers.sh`:

```bash
#!/usr/bin/env bash
# SSH + wp-cli wrappers for Beget shared.
# Required env: BEGET_USER, BEGET_HOST, BEGET_SSH_KEY

# wp-cli on Beget: default /usr/local/bin/wp shim runs PHP 7.4. We need 8.3,
# so always call wp-cli.phar directly with php8.3 binary.
REMOTE_WP_BIN="/usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar"

ssh_opts() {
    echo "-i $BEGET_SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
}

ssh_beget() {
    # ssh_beget "<remote-command>"
    local opts; opts=$(ssh_opts)
    ssh $opts "${BEGET_USER}@${BEGET_HOST}" "$1"
}

wp_remote() {
    # wp_remote <wp-path> <wp-cli-args> — run wp-cli inside wp directory
    local wp_path="$1"; shift
    ssh_beget "cd $wp_path && $REMOTE_WP_BIN $*"
}

wp_remote_url() {
    # wp_remote_url <wp-path> <url> <wp-cli-args> — adds --url for multisite
    local wp_path="$1" url="$2"; shift 2
    ssh_beget "cd $wp_path && $REMOTE_WP_BIN --url=$url $*"
}
```

- [ ] **Step 4: Run tests — verify all pass**

Run: `bats skills/wp-multisite/tests/test_ssh_helpers.bats`
Expected: 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/lib/ssh-helpers.sh \
        skills/wp-multisite/tests/test_ssh_helpers.bats
git commit -m "feat(wp-multisite): lib/ssh-helpers.sh — ssh_beget + wp_remote(_url)

REMOTE_WP_BIN forces php8.3 invocation (Beget default wp shim uses 7.4).
wp_remote_url adds --url for multisite-aware wp-cli calls. Unit tests
verify command construction via mock ssh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: lib/state.sh — read/write .landing-state.yaml

**Files:**
- Create: `skills/wp-multisite/scripts/lib/state.sh`
- Create: `skills/wp-multisite/tests/test_state_lib.bats`
- Create: `skills/wp-multisite/tests/fixtures/landing-state.single.yaml`
- Create: `skills/wp-multisite/tests/fixtures/landing-state.multisite.yaml`

- [ ] **Step 1: Create fixtures**

Create `skills/wp-multisite/tests/fixtures/landing-state.single.yaml`:

```yaml
project: "test-project"
created: "2026-05-18T10:00:00Z"
schema_version: 2
multisite: false
audience_segments: []
stages:
  "09_deploy": {status: approved, timestamp: "2026-05-18T11:00:00Z"}
```

Create `skills/wp-multisite/tests/fixtures/landing-state.multisite.yaml`:

```yaml
project: "test-project"
created: "2026-05-18T10:00:00Z"
schema_version: 2
multisite: true
audience_segments:
  - slug: russian
    host: russian.example.ru
    blog_id: 2
    created: "2026-05-18T12:00:00Z"
stages:
  "09_deploy": {status: approved, timestamp: "2026-05-18T11:00:00Z"}
```

- [ ] **Step 2: Write failing tests**

Create `skills/wp-multisite/tests/test_state_lib.bats`:

```bash
#!/usr/bin/env bats
# Unit tests for lib/state.sh

setup() {
    HERE="$(cd "$BATS_TEST_DIRNAME/../scripts/lib" && pwd)"
    source "$HERE/state.sh"
    TMPDIR_T="$(mktemp -d)"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.single.yaml" "$TMPDIR_T/.landing-state.yaml"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$TMPDIR_T/multisite.yaml"
}

teardown() { rm -rf "$TMPDIR_T"; }

@test "state_get_field reads top-level field" {
    run state_get_field "$TMPDIR_T/.landing-state.yaml" "multisite"
    [ "$status" -eq 0 ]
    [ "$output" = "False" ] || [ "$output" = "false" ]
}

@test "state_is_multisite returns 1 for single, 0 for multisite" {
    run state_is_multisite "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 1 ]
    run state_is_multisite "$TMPDIR_T/multisite.yaml"
    [ "$status" -eq 0 ]
}

@test "state_set_multisite_true flips the flag" {
    state_set_multisite_true "$TMPDIR_T/.landing-state.yaml"
    run state_is_multisite "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 0 ]
}

@test "state_add_segment appends a new segment entry" {
    state_add_segment "$TMPDIR_T/.landing-state.yaml" "family" "family.example.ru" 3
    run state_segment_count "$TMPDIR_T/.landing-state.yaml"
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
}

@test "state_segment_exists returns 0 if found" {
    run state_segment_exists "$TMPDIR_T/multisite.yaml" "russian"
    [ "$status" -eq 0 ]
    run state_segment_exists "$TMPDIR_T/multisite.yaml" "nonexistent"
    [ "$status" -eq 1 ]
}
```

- [ ] **Step 3: Run tests — verify they fail**

Run: `bats skills/wp-multisite/tests/test_state_lib.bats`
Expected: ERROR (file does not exist)

- [ ] **Step 4: Implement state.sh**

Create `skills/wp-multisite/scripts/lib/state.sh`:

```bash
#!/usr/bin/env bash
# Read/write helpers for <project>/.landing-state.yaml
# Uses python+PyYAML (assumed installed; same as rest of landing-system).

# Python helper invocation — handle Windows/Linux python binary name.
_state_py() {
    if command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi
}

state_get_field() {
    # state_get_field <state.yaml> <field-name> — print top-level field value
    local state="$1" field="$2"
    "$(_state_py)" -c "
import yaml, sys
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f)
print(d.get('$field', ''))
"
}

state_is_multisite() {
    # state_is_multisite <state.yaml> — exit 0 if multisite==true
    local state="$1"
    local result
    result=$("$(_state_py)" -c "
import yaml
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f)
print('yes' if d.get('multisite') is True else 'no')
")
    [ "$result" = "yes" ]
}

state_set_multisite_true() {
    # state_set_multisite_true <state.yaml> — flip flag, preserve other fields
    local state="$1"
    "$(_state_py)" -c "
import yaml
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f) or {}
d['multisite'] = True
if 'audience_segments' not in d:
    d['audience_segments'] = []
with open('$state', 'w', encoding='utf-8') as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
"
}

state_add_segment() {
    # state_add_segment <state.yaml> <slug> <host> <blog_id>
    local state="$1" slug="$2" host="$3" blog_id="$4"
    "$(_state_py)" -c "
import yaml, datetime
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f) or {}
d.setdefault('audience_segments', [])
d['audience_segments'].append({
    'slug': '$slug',
    'host': '$host',
    'blog_id': int('$blog_id'),
    'created': datetime.datetime.utcnow().isoformat() + 'Z',
})
with open('$state', 'w', encoding='utf-8') as f:
    yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False)
"
}

state_segment_count() {
    # state_segment_count <state.yaml>
    local state="$1"
    "$(_state_py)" -c "
import yaml
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f) or {}
print(len(d.get('audience_segments', [])))
"
}

state_segment_exists() {
    # state_segment_exists <state.yaml> <slug> — exit 0 if found
    local state="$1" slug="$2"
    local found
    found=$("$(_state_py)" -c "
import yaml
with open('$state', encoding='utf-8') as f:
    d = yaml.safe_load(f) or {}
print('yes' if any(s.get('slug') == '$slug' for s in d.get('audience_segments', [])) else 'no')
")
    [ "$found" = "yes" ]
}
```

- [ ] **Step 5: Run tests — verify 5/5 pass**

Run: `bats skills/wp-multisite/tests/test_state_lib.bats`
Expected: 5 tests pass

- [ ] **Step 6: Commit**

```bash
git add skills/wp-multisite/scripts/lib/state.sh \
        skills/wp-multisite/tests/test_state_lib.bats \
        skills/wp-multisite/tests/fixtures/landing-state.single.yaml \
        skills/wp-multisite/tests/fixtures/landing-state.multisite.yaml
git commit -m "feat(wp-multisite): lib/state.sh — read/write .landing-state.yaml

Helpers state_is_multisite/set_multisite_true/add_segment/segment_exists.
All operations preserve other state fields. Python+PyYAML implementation
matches the rest of landing-system tooling.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: template/.landing-state.yaml — add multisite fields

**Files:**
- Modify: `template/.landing-state.yaml`

- [ ] **Step 1: Show current state**

Run: `head -15 template/.landing-state.yaml`
Expected: existing skeleton (project, created, schema_version, stages)

- [ ] **Step 2: Add multisite + audience_segments fields**

Edit `template/.landing-state.yaml`. After line `schema_version: 2`, before `stages:`, add:

```yaml
# Multisite mode (set true by migrate-to-multisite.sh on first segment creation).
# Existing projects stay false — single-site deploy continues to work.
multisite: false

# List of audience segments (subsites in the multisite network).
# Each entry: {slug, host, blog_id, created}. Added by landing-segment.sh.
audience_segments: []
```

- [ ] **Step 3: Verify YAML validity**

Run: `python -c "import yaml; print(yaml.safe_load(open('template/.landing-state.yaml')))"`
Expected: dict prints with both new keys present (`multisite: False`, `audience_segments: []`)

- [ ] **Step 4: Commit**

```bash
git add template/.landing-state.yaml
git commit -m "feat(template): add multisite + audience_segments fields to state

Both default to single-site behavior (multisite: false, empty list).
landing-segment.sh flips multisite to true on first run and appends
to audience_segments.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: template/13_СЕГМЕНТЫ_ЦА/ skeleton

**Files:**
- Create: `template/13_СЕГМЕНТЫ_ЦА/README.md`
- Create: `template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md`
- Create: `template/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example`

- [ ] **Step 1: Create the top-level README**

Create `template/13_СЕГМЕНТЫ_ЦА/README.md`:

```markdown
# 13_СЕГМЕНТЫ_ЦА — Сегменты целевой аудитории

Сегмент ЦА — отдельная версия лендинга под конкретную часть аудитории клиента.

**Пример:** клиент по аренде премиум-авто в Дубае хочет ещё лендинги:
- `russian` — для русскоязычных в Дубае
- `family` — для семей с детьми
- `business` — для бизнес-туристов

Каждый сегмент = свой поддомен (`russian.liauto.dubai`) = свой WordPress subsite.

## Как создать

```
/landing-segment russian
```

Команда автоматически:
1. Мигрирует проект в multisite (если ещё не мигрирован)
2. Создаёт Beget subdomain `<slug>.<корневой-домен>`
3. Создаёт WordPress subsite внутри сети
4. Создаёт здесь папку `<slug>/` со скелетом для маркетолога

## Структура сегмента

```
<slug>/
  subbrief.yaml          # описание сегмента ЦА (заполняет маркетолог)
  prototype/             # будущий прототип под этот сегмент (пусто)
  photos/                # будущие фото под этот сегмент (пусто)
  .subsite-meta.yaml     # машинные метаданные (blog_id, host) — НЕ редактировать
```

Дальнейший pipeline (генерация контента под сегмент, деплой контента
в subsite) — отдельные команды, см. фазы CD2+.
```

- [ ] **Step 2: Create skeleton README and example**

Create `template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md`:

```markdown
# Скелет одного сегмента

Эта папка копируется landing-segment.sh при создании нового сегмента.
НЕ редактируйте файлы внутри `_skeleton/` напрямую — они служат шаблоном.

Структура копии:
- `subbrief.yaml` — заполняет маркетолог сразу после `/landing-segment`
- `prototype/` — сюда положить прототип под этот сегмент (если другой)
- `photos/` — фото специфичные для этого сегмента
- `.subsite-meta.yaml` — заполняется автоматически, не трогать
```

Create `template/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example`:

```yaml
# subbrief.yaml — бриф сегмента ЦА
# Заполняется маркетологом после создания сегмента командой /landing-segment.
# Описывает что отличает этот сегмент от основного лендинга.

audience:
  description: ""               # "русскоязычные туристы в Дубае"
  demographics: ""              # "30-50 лет, средний+ доход"
  pain_points: []               # ["языковой барьер", "недоверие к местным агентствам"]
  motivations: []               # ["комфорт", "знакомый сервис"]

offer:
  positioning: ""               # "Аренда с русскоговорящим менеджером"
  unique_value: ""              # "Поддержка 24/7 на русском"
  price_range: ""               # "от 800 AED/день" (если отличается от основного)

content_overrides:
  # Какие тексты заменяем относительно основного лендинга.
  # Если пусто — landing-content генерит с нуля под этот сегмент.
  hero_headline: ""
  cta_primary: ""
  testimonials_filter: ""       # "russian" — показывать только русские отзывы

photo_overrides:
  # Если нужны другие фото — описать тут.
  hero_image: ""                # путь к фото в photos/ или slot-name из 07c_PHOTOS/
  team_filter: ""               # "russian-speakers" — фильтр для team photos
```

- [ ] **Step 3: Verify directory created with all three files**

Run: `find template/13_СЕГМЕНТЫ_ЦА/ -type f`
Expected output (3 lines):
```
template/13_СЕГМЕНТЫ_ЦА/README.md
template/13_СЕГМЕНТЫ_ЦА/_skeleton/README.md
template/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example
```

- [ ] **Step 4: Commit**

```bash
git add template/13_СЕГМЕНТЫ_ЦА/
git commit -m "feat(template): добавить директорию 13_СЕГМЕНТЫ_ЦА/

README объясняет маркетологу что такое сегмент ЦА и как его создать.
_skeleton/ копируется landing-segment.sh при создании нового сегмента,
содержит subbrief.yaml.example с гайдом по заполнению.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: migrate-to-multisite.sh — Phase 1 (DNS + state check)

**Files:**
- Create: `skills/wp-multisite/scripts/migrate-to-multisite.sh`
- Create: `skills/wp-multisite/tests/test_migrate_to_multisite.bats`

- [ ] **Step 1: Write failing tests for early-exit and wildcard creation**

Create `skills/wp-multisite/tests/test_migrate_to_multisite.bats`:

```bash
#!/usr/bin/env bats
# Integration-ish tests for migrate-to-multisite.sh
# Uses mock curl + mock ssh for all Beget/SSH calls.

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/migrate-to-multisite.sh"
    LIB_DIR="$BATS_TEST_DIRNAME/../scripts/lib"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"
    # Minimal .landing-state.yaml + .env for project
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.single.yaml" "$PROJECT_DIR/.landing-state.yaml"
    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_LOGIN=testuser
BEGET_PASSWD=testpass
BEGET_API=https://api.beget.com/api
BEGET_SSH_KEY=/tmp/fake_key
BEGET_DOMAIN_ID=12345
BEGET_PATH=/home/t/testuser/example.ru/public_html
ROOT_DOMAIN=example.ru
EOF

    # Mock curl returns success-shape JSON for all calls
    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
# Track each call by writing to log
echo "CURL $*" >> /tmp/curl_calls.log
# Default success response
echo '{"status":"success","answer":{"status":"success","result":true}}'
MOCK
    chmod +x "$MOCK_DIR/curl"

    # Mock ssh prints commands instead of running them
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> /tmp/ssh_calls.log
echo "MOCK_OK"
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f /tmp/curl_calls.log /tmp/ssh_calls.log
    PATH="$MOCK_DIR:$PATH"
    export PATH
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "migrate exits early when state.multisite already true" {
    # Replace single state with multisite state
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$PROJECT_DIR/.landing-state.yaml"
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    [[ "$output" == *"already multisite"* ]]
}

@test "migrate creates wildcard subdomain via Beget API" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "addSubdomainVirtual" /tmp/curl_calls.log
}
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `bats skills/wp-multisite/tests/test_migrate_to_multisite.bats`
Expected: ERROR (script does not exist)

- [ ] **Step 3: Implement Phase 1 of migrate-to-multisite.sh (early exit + wildcard DNS)**

Create `skills/wp-multisite/scripts/migrate-to-multisite.sh`:

```bash
#!/usr/bin/env bash
# migrate-to-multisite.sh — convert single-site WP on Beget to subdomain multisite.
# Usage: bash migrate-to-multisite.sh <project-dir>
# Idempotent: re-running on already-multisite project is a no-op.
#
# Required env (from <project>/.env):
#   BEGET_USER, BEGET_HOST, BEGET_LOGIN, BEGET_PASSWD, BEGET_API,
#   BEGET_SSH_KEY, BEGET_DOMAIN_ID, BEGET_PATH, ROOT_DOMAIN

set -euo pipefail

PROJECT="${1:?Usage: migrate-to-multisite.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

# Load .env
set -a
source "$PROJECT/.env"
set +a

: "${BEGET_USER:?missing in .env}"; : "${BEGET_HOST:?}"; : "${BEGET_LOGIN:?}"
: "${BEGET_PASSWD:?}"; : "${BEGET_API:?}"; : "${BEGET_SSH_KEY:?}"
: "${BEGET_DOMAIN_ID:?}"; : "${BEGET_PATH:?}"; : "${ROOT_DOMAIN:?}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/beget-api.sh"
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
source "$SCRIPT_DIR/lib/state.sh"

# Phase 0: idempotency check
if state_is_multisite "$STATE"; then
    echo "OK: project is already multisite — nothing to do"
    exit 0
fi

# Phase 1: wildcard DNS
echo "▶ Phase 1: ensure *.${ROOT_DOMAIN} wildcard subdomain exists"
WILDCARD_FQDN="*.${ROOT_DOMAIN}"
if ! beget_subdomain_exists "$WILDCARD_FQDN"; then
    WC_ID=$(beget_subdomain_add "*" "$BEGET_DOMAIN_ID")
    echo "  created wildcard subdomain id=$WC_ID"
else
    echo "  wildcard already exists"
fi
```

- [ ] **Step 4: Run tests — verify pass**

Run: `bats skills/wp-multisite/tests/test_migrate_to_multisite.bats`
Expected: 2 tests pass

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/migrate-to-multisite.sh \
        skills/wp-multisite/tests/test_migrate_to_multisite.bats
git commit -m "feat(wp-multisite): migrate-to-multisite.sh Phase 1 — wildcard DNS

Reads <project>/.env + .landing-state.yaml. Early-exits if multisite already
true. Otherwise creates *.<root> wildcard subdomain via Beget API
(addSubdomainVirtual). Tests use mocked curl/ssh.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: migrate-to-multisite.sh — Phase 2-4 (WP convert + plugins + state)

**Files:**
- Modify: `skills/wp-multisite/scripts/migrate-to-multisite.sh`
- Modify: `skills/wp-multisite/tests/test_migrate_to_multisite.bats`

- [ ] **Step 1: Add failing tests for the new phases**

Append to `skills/wp-multisite/tests/test_migrate_to_multisite.bats`:

```bash
@test "migrate calls WP_ALLOW_MULTISITE config set" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "config set WP_ALLOW_MULTISITE" /tmp/ssh_calls.log
}

@test "migrate calls core multisite-convert" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "core multisite-convert" /tmp/ssh_calls.log
}

@test "migrate writes .htaccess" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q ".htaccess" /tmp/ssh_calls.log
}

@test "migrate network-activates lazy-blocks + seo-by-rank-math" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "plugin install lazy-blocks" /tmp/ssh_calls.log
    grep -q "plugin install seo-by-rank-math" /tmp/ssh_calls.log
    grep -q "activate-network" /tmp/ssh_calls.log
}

@test "migrate sets multisite=true in state after success" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "^multisite: true" "$PROJECT_DIR/.landing-state.yaml"
}

@test "migrate sets PHP 8.3 for root + wildcard FQDNs" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 0 ]
    grep -q "changePhpVersion" /tmp/curl_calls.log
}
```

- [ ] **Step 2: Run — verify 6 new tests fail**

Run: `bats skills/wp-multisite/tests/test_migrate_to_multisite.bats`
Expected: 6 of 8 tests fail

- [ ] **Step 3: Implement Phase 2-4**

Append to `skills/wp-multisite/scripts/migrate-to-multisite.sh`:

```bash

# Phase 2: ensure linkDomain + PHP 8.3 for root and wildcard
echo "▶ Phase 2: link domain + PHP 8.3"
SITE_ID="${BEGET_SITE_ID:-}"
if [ -z "$SITE_ID" ]; then
    echo "  ERROR: BEGET_SITE_ID not in .env. Run beget_api site/getList to find it." >&2
    echo "  Add BEGET_SITE_ID=<id> to <project>/.env and re-run." >&2
    exit 2
fi
beget_site_link "$BEGET_DOMAIN_ID" "$SITE_ID" || echo "  (already linked)"
WC_ID=$(beget_subdomain_id "$WILDCARD_FQDN")
beget_site_link "$WC_ID" "$SITE_ID" || echo "  (already linked)"
beget_set_php "$ROOT_DOMAIN" "8.3"
beget_set_php "$WILDCARD_FQDN" "8.3"

# Phase 3: WP multisite convert
echo "▶ Phase 3: WordPress multisite-convert"
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN config set WP_ALLOW_MULTISITE true --raw" || true
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN core multisite-convert --subdomains" || \
    { echo "ERROR: multisite-convert failed" >&2; exit 3; }

# Phase 4: rewrite .htaccess
echo "▶ Phase 4: write multisite .htaccess"
ssh_beget "cat > $BEGET_PATH/.htaccess <<'HTACCESS'
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php\$ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?wp-admin\$ \$1wp-admin/ [R=301,L]
RewriteCond %{REQUEST_FILENAME} -f [OR]
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^ - [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) \$2 [L]
RewriteRule ^([_0-9a-zA-Z-]+/)?(.*\\.php)\$ \$2 [L]
RewriteRule . index.php [L]
HTACCESS"

# Phase 5: network-activate plugins
echo "▶ Phase 5: network-activate lazy-blocks + seo-by-rank-math"
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN plugin install lazy-blocks --activate-network" || true
ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN plugin install seo-by-rank-math --activate-network" || true

# Phase 6: state — flip multisite flag
echo "▶ Phase 6: update state"
state_set_multisite_true "$STATE"

echo "✅ Migration complete. Project is now multisite."
```

- [ ] **Step 4: Update test — add `BEGET_SITE_ID` to fixture .env**

Edit `setup()` in `skills/wp-multisite/tests/test_migrate_to_multisite.bats`. In the `cat > "$PROJECT_DIR/.env"` heredoc, add this line before EOF:

```
BEGET_SITE_ID=99999
```

- [ ] **Step 5: Run all tests — verify 8/8 pass**

Run: `bats skills/wp-multisite/tests/test_migrate_to_multisite.bats`
Expected: 8 tests pass

- [ ] **Step 6: Commit**

```bash
git add skills/wp-multisite/scripts/migrate-to-multisite.sh \
        skills/wp-multisite/tests/test_migrate_to_multisite.bats
git commit -m "feat(wp-multisite): migrate-to-multisite Phase 2-6 — convert + plugins

Phase 2: site/linkDomain + PHP 8.3 for root and wildcard FQDNs.
Phase 3: WP_ALLOW_MULTISITE constant + core multisite-convert --subdomains.
Phase 4: write subdomain-mode .htaccess.
Phase 5: network-activate lazy-blocks + seo-by-rank-math.
Phase 6: flip multisite=true in .landing-state.yaml.

Requires BEGET_SITE_ID in <project>/.env (fail-fast with instruction if missing).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: landing-segment.sh — Phase 1 (validate + auto-migrate)

**Files:**
- Create: `skills/wp-multisite/scripts/landing-segment.sh`
- Create: `skills/wp-multisite/tests/test_landing_segment.bats`

- [ ] **Step 1: Write failing tests**

Create `skills/wp-multisite/tests/test_landing_segment.bats`:

```bash
#!/usr/bin/env bats
# Tests for landing-segment.sh — uses mock curl + ssh.

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/landing-segment.sh"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$PROJECT_DIR/.landing-state.yaml"
    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_LOGIN=testuser
BEGET_PASSWD=testpass
BEGET_API=https://api.beget.com/api
BEGET_SSH_KEY=/tmp/fake_key
BEGET_DOMAIN_ID=12345
BEGET_SITE_ID=99999
BEGET_PATH=/home/t/testuser/example.ru/public_html
ROOT_DOMAIN=example.ru
EOF
    # Skeleton dir for template copy
    mkdir -p "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/_skeleton"
    cat > "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example" <<'YAML'
audience:
  description: ""
YAML

    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo "CURL $*" >> /tmp/curl_calls.log
case "$*" in
    *getSubdomainList*) echo '{"status":"success","answer":{"status":"success","result":[]}}' ;;
    *addSubdomainVirtual*) echo '{"status":"success","answer":{"status":"success","result":777}}' ;;
    *) echo '{"status":"success","answer":{"status":"success","result":true}}' ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> /tmp/ssh_calls.log
# wp site create returns a numeric blog_id (--porcelain)
if [[ "$*" == *"site create"* ]] && [[ "$*" == *"--porcelain"* ]]; then
    echo "5"
else
    echo "OK"
fi
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f /tmp/curl_calls.log /tmp/ssh_calls.log
    PATH="$MOCK_DIR:$PATH"; export PATH
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "landing-segment exits 2 when slug missing" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 2 ]
    [[ "$output" == *"Usage:"* ]]
}

@test "landing-segment exits 2 when slug already exists in state" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian"
    [ "$status" -eq 2 ]
    [[ "$output" == *"already exists"* ]]
}

@test "landing-segment creates beget subdomain via API" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    grep -q "addSubdomainVirtual" /tmp/curl_calls.log
}
```

- [ ] **Step 2: Run — verify fail**

Run: `bats skills/wp-multisite/tests/test_landing_segment.bats`
Expected: ERROR (script does not exist)

- [ ] **Step 3: Implement Phase 1**

Create `skills/wp-multisite/scripts/landing-segment.sh`:

```bash
#!/usr/bin/env bash
# landing-segment.sh — create a new audience segment subsite in multisite.
# Usage: bash landing-segment.sh <project-dir> <segment-slug>

set -euo pipefail

PROJECT="${1:-}"; SLUG="${2:-}"
if [ -z "$PROJECT" ] || [ -z "$SLUG" ]; then
    echo "Usage: landing-segment.sh <project-dir> <segment-slug>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

# Validate slug — only lowercase letters, digits, hyphens.
if ! [[ "$SLUG" =~ ^[a-z][a-z0-9-]*$ ]]; then
    echo "ERROR: slug must match ^[a-z][a-z0-9-]*$, got: $SLUG" >&2
    exit 2
fi

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?missing in .env}"; : "${BEGET_HOST:?}"; : "${BEGET_LOGIN:?}"
: "${BEGET_PASSWD:?}"; : "${BEGET_API:?}"; : "${BEGET_SSH_KEY:?}"
: "${BEGET_DOMAIN_ID:?}"; : "${BEGET_SITE_ID:?}"; : "${BEGET_PATH:?}"; : "${ROOT_DOMAIN:?}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/beget-api.sh"
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
source "$SCRIPT_DIR/lib/state.sh"

# Phase 0: idempotency — fail-fast if slug already exists
if state_segment_exists "$STATE" "$SLUG"; then
    echo "ERROR: segment '$SLUG' already exists in $STATE" >&2
    exit 2
fi

# Phase 1: auto-migrate to multisite if needed
if ! state_is_multisite "$STATE"; then
    echo "▶ Project is single-site — running migrate-to-multisite.sh first"
    bash "$SCRIPT_DIR/migrate-to-multisite.sh" "$PROJECT"
fi

HOST="${SLUG}.${ROOT_DOMAIN}"
echo "▶ Creating segment '$SLUG' at $HOST"

# Phase 2: Beget subdomain (idempotent — skip if exists)
if ! beget_subdomain_exists "$HOST"; then
    NEW_SUB_ID=$(beget_subdomain_add "$SLUG" "$BEGET_DOMAIN_ID")
    echo "  Beget subdomain created (id=$NEW_SUB_ID)"
else
    NEW_SUB_ID=$(beget_subdomain_id "$HOST")
    echo "  Beget subdomain already exists (id=$NEW_SUB_ID)"
fi
beget_site_link "$NEW_SUB_ID" "$BEGET_SITE_ID"
beget_set_php "$HOST" "8.3"

echo "  (Phase 3: WP subsite — implemented in next Task)"
```

- [ ] **Step 4: Run tests — verify 3/3 pass**

Run: `bats skills/wp-multisite/tests/test_landing_segment.bats`
Expected: 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/landing-segment.sh \
        skills/wp-multisite/tests/test_landing_segment.bats
git commit -m "feat(wp-multisite): landing-segment.sh Phase 1 — slug validation + DNS

Validates slug against regex ^[a-z][a-z0-9-]*$, fail-fast if already
in state. Auto-runs migrate-to-multisite.sh if project still single.
Creates Beget subdomain + linkDomain + PHP 8.3. WP subsite creation
and skeleton copy come in next Task.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: landing-segment.sh — Phase 3-5 (WP subsite + skeleton + state)

**Files:**
- Modify: `skills/wp-multisite/scripts/landing-segment.sh`
- Modify: `skills/wp-multisite/tests/test_landing_segment.bats`

- [ ] **Step 1: Write failing tests**

Append to `skills/wp-multisite/tests/test_landing_segment.bats`:

```bash
@test "landing-segment runs wp site create" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    grep -q "site create --slug=family" /tmp/ssh_calls.log
}

@test "landing-segment creates project segment directory" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    [ -d "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/family" ]
    [ -f "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/family/subbrief.yaml" ]
    [ -f "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/family/.subsite-meta.yaml" ]
}

@test "landing-segment appends segment to state" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    grep -q "slug: family" "$PROJECT_DIR/.landing-state.yaml"
    grep -q "host: family.example.ru" "$PROJECT_DIR/.landing-state.yaml"
}

@test "landing-segment subsite-meta contains blog_id" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    grep -q "blog_id: 5" "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/family/.subsite-meta.yaml"
}
```

- [ ] **Step 2: Run — 4 new tests fail**

Run: `bats skills/wp-multisite/tests/test_landing_segment.bats`
Expected: 4 of 7 fail

- [ ] **Step 3: Implement Phase 3-5**

Replace the last `echo` line in `skills/wp-multisite/scripts/landing-segment.sh` with:

```bash

# Phase 3: WP subsite
echo "▶ Phase 3: wp site create --slug=$SLUG"
BLOG_ID=$(ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN site create --slug=$SLUG --title='$SLUG' --porcelain" | tail -1 | tr -d '\r')
if ! [[ "$BLOG_ID" =~ ^[0-9]+$ ]]; then
    echo "ERROR: wp site create did not return a numeric blog_id, got: $BLOG_ID" >&2
    exit 4
fi
echo "  subsite created blog_id=$BLOG_ID"

# Phase 4: create project segment directory from skeleton
SEG_DIR="$PROJECT/13_СЕГМЕНТЫ_ЦА/$SLUG"
SKELETON="$PROJECT/13_СЕГМЕНТЫ_ЦА/_skeleton"
echo "▶ Phase 4: create $SEG_DIR from skeleton"
mkdir -p "$SEG_DIR/prototype" "$SEG_DIR/photos"
if [ -f "$SKELETON/subbrief.yaml.example" ]; then
    cp "$SKELETON/subbrief.yaml.example" "$SEG_DIR/subbrief.yaml"
fi

# .subsite-meta.yaml — machine-readable, NOT to be edited by humans
cat > "$SEG_DIR/.subsite-meta.yaml" <<META
# Machine metadata for segment '$SLUG' — DO NOT edit manually.
slug: $SLUG
host: $HOST
blog_id: $BLOG_ID
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
META

# Phase 5: state update
echo "▶ Phase 5: append to .landing-state.yaml::audience_segments"
state_add_segment "$STATE" "$SLUG" "$HOST" "$BLOG_ID"

echo "✅ Segment '$SLUG' created → http://$HOST/"
echo "   Next: fill in $SEG_DIR/subbrief.yaml, then run pipeline for this segment (CD2+)."
```

- [ ] **Step 4: Run all tests — verify 7/7 pass**

Run: `bats skills/wp-multisite/tests/test_landing_segment.bats`
Expected: 7 tests pass

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/landing-segment.sh \
        skills/wp-multisite/tests/test_landing_segment.bats
git commit -m "feat(wp-multisite): landing-segment Phase 3-5 — WP subsite + skeleton

Phase 3: wp site create --slug=<X> --porcelain returns numeric blog_id;
fail-fast if non-numeric.
Phase 4: copy _skeleton/ → 13_СЕГМЕНТЫ_ЦА/<slug>/, write .subsite-meta.yaml
with machine-readable blog_id+host+created.
Phase 5: state_add_segment appends to audience_segments[].

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 11: clone-subsite.sh

**Files:**
- Create: `skills/wp-multisite/scripts/clone-subsite.sh`
- Create: `skills/wp-multisite/tests/test_clone_subsite.bats`

- [ ] **Step 1: Write failing tests**

Create `skills/wp-multisite/tests/test_clone_subsite.bats`:

```bash
#!/usr/bin/env bats
# Tests for clone-subsite.sh

setup() {
    SCRIPT="$BATS_TEST_DIRNAME/../scripts/clone-subsite.sh"
    MOCK_DIR="$(mktemp -d)"
    PROJECT_DIR="$(mktemp -d)"
    cp "$BATS_TEST_DIRNAME/fixtures/landing-state.multisite.yaml" "$PROJECT_DIR/.landing-state.yaml"
    cat > "$PROJECT_DIR/.env" <<EOF
BEGET_USER=testuser
BEGET_HOST=test.beget.tech
BEGET_LOGIN=testuser
BEGET_PASSWD=testpass
BEGET_API=https://api.beget.com/api
BEGET_SSH_KEY=/tmp/fake_key
BEGET_DOMAIN_ID=12345
BEGET_SITE_ID=99999
BEGET_PATH=/home/t/testuser/example.ru/public_html
ROOT_DOMAIN=example.ru
EOF
    mkdir -p "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/_skeleton"
    cat > "$PROJECT_DIR/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example" <<'YAML'
audience:
  description: ""
YAML

    cat > "$MOCK_DIR/curl" <<'MOCK'
#!/bin/bash
echo "CURL $*" >> /tmp/curl_calls.log
case "$*" in
    *getSubdomainList*) echo '{"status":"success","answer":{"status":"success","result":[]}}' ;;
    *addSubdomainVirtual*) echo '{"status":"success","answer":{"status":"success","result":888}}' ;;
    *) echo '{"status":"success","answer":{"status":"success","result":true}}' ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> /tmp/ssh_calls.log
case "$*" in
    *"site create"*"--porcelain"*) echo "7" ;;
    *"post list"*"--field=ID"*) echo "10"; echo "11" ;;
    *"post get 10"*"--field=post_title"*) echo "Home" ;;
    *"post get 10"*"--field=post_content"*) echo "<!-- wp:paragraph --><p>Hello russian</p><!-- /wp:paragraph -->" ;;
    *"post get 11"*) echo "MOCK_DATA" ;;
    *"post create"*"--porcelain"*) echo "20" ;;
    *) echo "OK" ;;
esac
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f /tmp/curl_calls.log /tmp/ssh_calls.log
    PATH="$MOCK_DIR:$PATH"; export PATH
}

teardown() { rm -rf "$MOCK_DIR" "$PROJECT_DIR"; }

@test "clone-subsite exits 2 when args missing" {
    run bash "$SCRIPT" "$PROJECT_DIR"
    [ "$status" -eq 2 ]
    [[ "$output" == *"Usage:"* ]]
}

@test "clone-subsite exits 2 when source segment doesn't exist" {
    run bash "$SCRIPT" "$PROJECT_DIR" "nonexistent" "newcopy"
    [ "$status" -eq 2 ]
    [[ "$output" == *"source segment"* ]]
}

@test "clone-subsite exits 2 when dest segment already exists" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian"
    [ "$status" -eq 2 ]
    [[ "$output" == *"already exists"* ]]
}

@test "clone-subsite creates destination subsite first" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian-test"
    [ "$status" -eq 0 ]
    grep -q "site create --slug=russian-test" /tmp/ssh_calls.log
}

@test "clone-subsite copies pages from source to dest" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian-test"
    [ "$status" -eq 0 ]
    # Each page from source -> post get + post create on dest
    grep -q "post list --post_type=page" /tmp/ssh_calls.log
    grep -q "post create --post_type=page" /tmp/ssh_calls.log
}

@test "clone-subsite appends new segment to state" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian-test"
    [ "$status" -eq 0 ]
    grep -q "slug: russian-test" "$PROJECT_DIR/.landing-state.yaml"
}
```

- [ ] **Step 2: Run — verify fail**

Run: `bats skills/wp-multisite/tests/test_clone_subsite.bats`
Expected: ERROR (script does not exist)

- [ ] **Step 3: Implement clone-subsite.sh**

Create `skills/wp-multisite/scripts/clone-subsite.sh`:

```bash
#!/usr/bin/env bash
# clone-subsite.sh — copy content from one multisite subsite to a new one.
# Usage: bash clone-subsite.sh <project-dir> <source-slug> <dest-slug>
# Byte-for-byte: copies all pages (title + content). siteurl/home are
# auto-managed by wp site create.

set -euo pipefail

PROJECT="${1:-}"; SOURCE_SLUG="${2:-}"; DEST_SLUG="${3:-}"
if [ -z "$PROJECT" ] || [ -z "$SOURCE_SLUG" ] || [ -z "$DEST_SLUG" ]; then
    echo "Usage: clone-subsite.sh <project-dir> <source-slug> <dest-slug>" >&2
    exit 2
fi
PROJECT="$(cd "$PROJECT" && pwd)"
STATE="$PROJECT/.landing-state.yaml"

[ -f "$STATE" ] || { echo "ERROR: $STATE not found" >&2; exit 1; }
[ -f "$PROJECT/.env" ] || { echo "ERROR: $PROJECT/.env not found" >&2; exit 1; }

set -a; source "$PROJECT/.env"; set +a
: "${BEGET_USER:?}"; : "${BEGET_HOST:?}"; : "${BEGET_LOGIN:?}"
: "${BEGET_PASSWD:?}"; : "${BEGET_API:?}"; : "${BEGET_SSH_KEY:?}"
: "${BEGET_DOMAIN_ID:?}"; : "${BEGET_SITE_ID:?}"; : "${BEGET_PATH:?}"; : "${ROOT_DOMAIN:?}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/beget-api.sh"
source "$SCRIPT_DIR/lib/ssh-helpers.sh"
source "$SCRIPT_DIR/lib/state.sh"

# Validation
if ! state_segment_exists "$STATE" "$SOURCE_SLUG"; then
    echo "ERROR: source segment '$SOURCE_SLUG' does not exist in state" >&2
    exit 2
fi
if state_segment_exists "$STATE" "$DEST_SLUG"; then
    echo "ERROR: destination segment '$DEST_SLUG' already exists" >&2
    exit 2
fi

SOURCE_URL="http://${SOURCE_SLUG}.${ROOT_DOMAIN}"
DEST_URL="http://${DEST_SLUG}.${ROOT_DOMAIN}"

# Step 1: create dest segment (subdomain + WP site + skeleton)
echo "▶ Step 1: create destination segment '$DEST_SLUG'"
bash "$SCRIPT_DIR/landing-segment.sh" "$PROJECT" "$DEST_SLUG"

# Step 2: copy all pages from source to dest
echo "▶ Step 2: copy pages $SOURCE_URL → $DEST_URL"
PAGE_IDS=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post list --post_type=page --post_status=publish --field=ID")
for src_id in $PAGE_IDS; do
    [ -z "$src_id" ] && continue
    TITLE=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_title" | tr -d '\r')
    CONTENT=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_content")
    NAME=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $src_id --field=post_name" | tr -d '\r')

    # Write content to temp remote file to avoid shell-escape issues
    REMOTE_TMP="/tmp/clone-$DEST_SLUG-$src_id.html"
    ssh_beget "cat > $REMOTE_TMP <<'CLONE_EOF'
$CONTENT
CLONE_EOF"
    NEW_ID=$(ssh_beget "cd $BEGET_PATH && $REMOTE_WP_BIN --url=$DEST_URL post create --post_type=page --post_status=publish --post_title=\"$TITLE\" --post_name=\"$NAME\" --post_content=\"\$(cat $REMOTE_TMP)\" --porcelain" | tail -1 | tr -d '\r')
    ssh_beget "rm -f $REMOTE_TMP"
    echo "  page $src_id → $NEW_ID"
done

# Step 3: copy show_on_front + page_on_front (homepage continuity)
ON_FRONT=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "option get show_on_front" | tr -d '\r')
PAGE_FRONT_ID=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "option get page_on_front" | tr -d '\r')
if [ "$ON_FRONT" = "page" ] && [ -n "$PAGE_FRONT_ID" ]; then
    # The new page IDs differ; for now copy front-page by post_name match.
    FRONT_NAME=$(wp_remote_url "$BEGET_PATH" "$SOURCE_URL" "post get $PAGE_FRONT_ID --field=post_name" | tr -d '\r')
    NEW_FRONT_ID=$(wp_remote_url "$BEGET_PATH" "$DEST_URL" "post list --post_type=page --name=$FRONT_NAME --field=ID" | head -1 | tr -d '\r')
    if [ -n "$NEW_FRONT_ID" ]; then
        wp_remote_url "$BEGET_PATH" "$DEST_URL" "option update show_on_front page" > /dev/null
        wp_remote_url "$BEGET_PATH" "$DEST_URL" "option update page_on_front $NEW_FRONT_ID" > /dev/null
        echo "  page_on_front → $NEW_FRONT_ID"
    fi
fi

echo "✅ Clone complete → $DEST_URL"
```

- [ ] **Step 4: Run tests — verify 6/6 pass**

Run: `bats skills/wp-multisite/tests/test_clone_subsite.bats`
Expected: 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add skills/wp-multisite/scripts/clone-subsite.sh \
        skills/wp-multisite/tests/test_clone_subsite.bats
git commit -m "feat(wp-multisite): clone-subsite.sh — byte-for-byte segment copy

Delegates segment creation to landing-segment.sh, then iterates pages
on source subsite and creates duplicates on dest via wp post create.
Preserves show_on_front + page_on_front by post_name lookup.
Content piped through remote tempfile to avoid shell-escape issues.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: .claude/commands/landing-segment.md slash command

**Files:**
- Create: `.claude/commands/landing-segment.md`

- [ ] **Step 1: Create the slash command**

Create `.claude/commands/landing-segment.md`:

```markdown
---
description: Создать новый сегмент целевой аудитории — поддомен + WordPress subsite + skeleton директории. Если проект ещё single-site, автоматически мигрирует в multisite.
allowed-tools: Bash, Read
---

# /landing-segment

Создаёт новый сегмент ЦА (subsite в multisite-сети WordPress) для текущего
landing-проекта.

## Использование

```
/landing-segment <slug>
```

Пример: `/landing-segment russian`

`<slug>` — имя сегмента, регекс `^[a-z][a-z0-9-]*$` (только нижний регистр,
цифры, дефисы; начинается с буквы).

## Что делаю

1. Проверяю что есть `.landing-state.yaml` + `.env` в текущей папке проекта.
2. Если `state.multisite=false` — запускаю `migrate-to-multisite.sh` (одноразово).
3. Создаю Beget subdomain `<slug>.<корневой-домен>` через API.
4. Создаю WordPress subsite (`wp site create --slug=<slug>`).
5. Копирую `13_СЕГМЕНТЫ_ЦА/_skeleton/` → `13_СЕГМЕНТЫ_ЦА/<slug>/`.
6. Записываю сегмент в `.landing-state.yaml::audience_segments[]`.
7. Сообщаю URL нового сегмента + следующий шаг для маркетолога.

## После выполнения

1. Открой `13_СЕГМЕНТЫ_ЦА/<slug>/subbrief.yaml` — заполни описание ЦА.
2. (Будущая фаза CD2) запусти pipeline генерации контента под сегмент.
3. (Будущая фаза CD2) задеплой контент в новый subsite.

## Скрипт

`skills/wp-multisite/scripts/landing-segment.sh <project-dir> <slug>`
```

- [ ] **Step 2: Verify the command renders**

Run: `cat .claude/commands/landing-segment.md | head -5`
Expected: prints frontmatter with `description:`

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/landing-segment.md
git commit -m "feat(commands): add /landing-segment slash command

Wrapper for skills/wp-multisite/scripts/landing-segment.sh — describes
the workflow + the slug regex + what marketolog should do next.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 13: Update /landing-clone to point at multisite implementation

**Files:**
- Modify: `.claude/commands/landing-clone.md`
- Modify: `skills/landing-versioning-and-cloning/SKILL.md`

- [ ] **Step 1: Show current /landing-clone**

Run: `cat .claude/commands/landing-clone.md`
Expected: existing 20-line file describing filesystem clone

- [ ] **Step 2: Rewrite /landing-clone under multisite model**

Replace entire `.claude/commands/landing-clone.md` content with:

```markdown
---
description: Клонировать существующий сегмент в новый — byte-by-byte копия страниц с одного поддомена на другой внутри одной multisite-сети. Использует skills/wp-multisite/scripts/clone-subsite.sh.
allowed-tools: Bash, Read
---

# /landing-clone

Клонирует контент существующего сегмента ЦА в новый сегмент.
Использует multisite-модель: оба сегмента — subsites одной WordPress-сети.

## Использование

```
/landing-clone <source-slug> <dest-slug>
```

Пример: `/landing-clone russian russian-experiment`

## Что делаю

1. Проверяю что source-сегмент существует в `.landing-state.yaml`.
2. Создаю dest-сегмент (через `/landing-segment` под капотом).
3. Копирую все страницы source → dest (по одной через `wp post get` + `wp post create`).
4. Переношу `show_on_front` / `page_on_front` если они стояли.

## Когда использовать

- Тестирование изменений на копии без риска основному сегменту.
- Создание варианта существующего сегмента для A/B-сплита.

## Когда НЕ использовать

- Для создания **нового** сегмента ЦА (с другим брифом и контентом) →
  используйте `/landing-segment` (он создаёт пустой skeleton под новый контент).

## Скрипт

`skills/wp-multisite/scripts/clone-subsite.sh <project-dir> <source-slug> <dest-slug>`

## Legacy

Старая команда `/landing-clone <new-slug>` для filesystem-клонирования проекта
(модель «N независимых WP инстансов») переехала в
`skills/landing-versioning-and-cloning/scripts/clone-landing.sh`
и помечена deprecated. Использовать только для legacy single-site проектов
без multisite-миграции.
```

- [ ] **Step 3: Add deprecation notice to landing-versioning-and-cloning SKILL**

Replace `skills/landing-versioning-and-cloning/SKILL.md` content with:

```markdown
---
name: landing-versioning-and-cloning
description: Create version snapshots, rollback to previous versions, and create A/B clones of landing projects (LEGACY single-site model only — for multisite, use skills/wp-multisite).
---

# landing-versioning-and-cloning

> ⚠️ **DEPRECATED для модели multisite.** Этот скилл клонирует проект целиком
> как **отдельный WP-инстанс** (filesystem copy + новый .env). Для новой
> модели «один клиентский домен = WP Multisite сеть с сегментами ЦА»
> используйте `skills/wp-multisite/scripts/clone-subsite.sh`.
>
> Этот скилл оставлен для legacy single-site проектов без multisite-миграции.

## Scripts

### create-version.sh
```bash
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> [version-label]
```
Saves snapshot to `09_ВЕРСИИ/<version>/`. Не зависит от multisite — работает
для любого проекта.

### clone-landing.sh (legacy)
```bash
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```
Создаёт полную filesystem-копию проекта. **Только для single-site проектов.**
Для multisite сегментов используйте `clone-subsite.sh`.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/commands/landing-clone.md \
        skills/landing-versioning-and-cloning/SKILL.md
git commit -m "refactor(commands): rewrite /landing-clone under multisite model

/landing-clone теперь delegates to skills/wp-multisite/clone-subsite.sh
для multisite-сегментов. Старый clone-landing.sh (filesystem copy +
отдельный WP инстанс) помечен deprecated, оставлен для legacy single-site.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 14: Update CLAUDE.md + docs/SETUP.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/SETUP.md`

- [ ] **Step 1: Read current CLAUDE.md to find insertion point**

Run: `grep -n "Главные команды" CLAUDE.md | head -3`
Expected: line number where the commands section starts

- [ ] **Step 2: Add multisite section to CLAUDE.md**

Append a new section to `CLAUDE.md` after the existing "Главные команды" section. Add this block:

```markdown
## Multisite режим и сегменты ЦА (S2-CD CD1)

С 2026-05-18 landing-system поддерживает multisite-режим: один клиентский
корневой домен (`liauto.dubai`) может содержать N сегментов целевой
аудитории (`russian.liauto.dubai`, `family.liauto.dubai`, ...),
каждый — отдельный WordPress subsite в одной multisite-сети.

### Команды

- `/landing-segment <slug>` — создать новый сегмент ЦА (subdomain + WP subsite).
  При первом сегменте автоматически мигрирует проект single-site → multisite.
- `/landing-clone <source> <dest>` — byte-by-byte копия сегмента в новый сегмент.

### Артефакты

- `.landing-state.yaml::multisite` (bool) — флаг режима.
- `.landing-state.yaml::audience_segments[]` — список сегментов с blog_id и host.
- `13_СЕГМЕНТЫ_ЦА/<slug>/subbrief.yaml` — бриф сегмента (заполняет маркетолог).
- `13_СЕГМЕНТЫ_ЦА/<slug>/.subsite-meta.yaml` — машинные метаданные.

### Скилл

`skills/wp-multisite/` — содержит migrate-to-multisite, landing-segment,
clone-subsite + lib (beget-api, ssh-helpers, state).

### Required .env

Помимо стандартных BEGET_*, для multisite требуется `BEGET_SITE_ID`
(integer id «site-entity» на Бегете — получить через
`beget_api site/getList` для соответствующего public_html).

См. также [docs/beget-cookbook.md](docs/beget-cookbook.md),
[docs/superpowers/specs/2026-05-18-s2cd-multisite-cloning-design.md](docs/superpowers/specs/2026-05-18-s2cd-multisite-cloning-design.md).
```

- [ ] **Step 3: Add multisite section to docs/SETUP.md**

Append to `docs/SETUP.md`:

```markdown
## Когда нужен multisite-режим

Single-site (по умолчанию):
- У клиента **один лендинг** под одну аудиторию.
- Домен — один без поддоменов.

Multisite (через `/landing-segment`):
- У клиента **несколько лендингов** под разные сегменты ЦА.
- Используются поддомены одного клиентского домена.
- Один wp-admin управляет всеми сегментами.

### Миграция single → multisite

Автоматическая. При первом запуске `/landing-segment <slug>` для проекта,
у которого `state.multisite=false`, запускается
`skills/wp-multisite/scripts/migrate-to-multisite.sh`. Он:
1. Создаёт wildcard subdomain в DNS через Beget API.
2. Активирует `WP_ALLOW_MULTISITE` в `wp-config.php`.
3. Запускает `wp core multisite-convert --subdomains`.
4. Переписывает `.htaccess` под multisite (subdomain mode).
5. Сетевая активация Lazy Blocks + RankMath SEO.
6. Флипает `state.multisite=true`.

После миграции существующий лендинг становится `blog_id=1` (главным сайтом
сети). Контент не теряется.

### Pre-requisites

Помимо стандартных переменных `.env`, нужно:
- `BEGET_SITE_ID` — числовой id «сайт-сущности» на Бегете (из `site/getList`).
- `BEGET_DOMAIN_ID` — числовой id корневого домена (из `domain/getList`).
- `ROOT_DOMAIN` — fqdn корневого клиентского домена.

### SSL после миграции

**Manual one-click через панель Beget** (Домены → SSL → бесплатный wildcard
Let's Encrypt). Покрывает все existing и future subdomains.
Beget сам обновляет каждые 60 дней. Скрейп-автоматизация — следующая фаза.

См. [docs/beget-cookbook.md §SSL](beget-cookbook.md).
```

- [ ] **Step 4: Verify both files are valid markdown**

Run: `head -5 CLAUDE.md && echo --- && head -5 docs/SETUP.md`
Expected: both files print without errors

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md docs/SETUP.md
git commit -m "docs: добавить разделы про multisite режим и сегменты ЦА

CLAUDE.md: новый раздел 'Multisite режим и сегменты ЦА (S2-CD CD1)' —
команды /landing-segment + /landing-clone, артефакты, required .env.
docs/SETUP.md: раздел 'Когда нужен multisite-режим' — single vs multisite,
автоматическая миграция, pre-requisites, SSL через панель.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 15: End-to-end manual smoke test on Beget

**Files:** none new

This is a **manual** verification on the live POC environment (`ailexi.ru`).
No bats — это финальный sanity check что всё реально работает в боевых условиях.

- [ ] **Step 1: Prepare project fixture on Beget**

Use the existing POC multisite at `ailexi.ru`. State on the Beget server:
- `ailexi.ru` (blog_id=1), `alpha.ailexi.ru` (2), `bravo.ailexi.ru` (3), `clone.ailexi.ru` (4)

Create a fake local project directory:

```bash
mkdir -p /tmp/poc-multisite-project
cat > /tmp/poc-multisite-project/.landing-state.yaml <<'YAML'
project: "ailexi-poc"
created: "2026-05-18T10:00:00Z"
schema_version: 2
multisite: true
audience_segments:
  - {slug: alpha, host: alpha.ailexi.ru, blog_id: 2, created: "2026-05-18T12:00:00Z"}
  - {slug: bravo, host: bravo.ailexi.ru, blog_id: 3, created: "2026-05-18T12:01:00Z"}
  - {slug: clone, host: clone.ailexi.ru, blog_id: 4, created: "2026-05-18T12:02:00Z"}
YAML

cat > /tmp/poc-multisite-project/.env <<'EOF'
BEGET_USER=esper21
BEGET_HOST=esper21.beget.tech
BEGET_LOGIN=esper21
BEGET_PASSWD=FP63zwOF%41*
BEGET_API=https://api.beget.com/api
BEGET_SSH_KEY=/c/Users/esper21/.ssh/beget_poc
BEGET_DOMAIN_ID=12513532
BEGET_SITE_ID=9192816
BEGET_PATH=/home/e/esper21/ailexi.ru/public_html
ROOT_DOMAIN=ailexi.ru
EOF

mkdir -p /tmp/poc-multisite-project/13_СЕГМЕНТЫ_ЦА/_skeleton
cp template/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example \
   /tmp/poc-multisite-project/13_СЕГМЕНТЫ_ЦА/_skeleton/subbrief.yaml.example
```

- [ ] **Step 2: Create a new segment via landing-segment.sh**

Run:
```bash
bash skills/wp-multisite/scripts/landing-segment.sh /tmp/poc-multisite-project smoke-test
```

Expected output:
- `▶ Creating segment 'smoke-test' at smoke-test.ailexi.ru`
- `▶ Phase 3: wp site create --slug=smoke-test`
- `  subsite created blog_id=<N>` where N ≥ 5
- `▶ Phase 4: create /tmp/poc-multisite-project/13_СЕГМЕНТЫ_ЦА/smoke-test from skeleton`
- `▶ Phase 5: append to .landing-state.yaml::audience_segments`
- `✅ Segment 'smoke-test' created → http://smoke-test.ailexi.ru/`

Verify locally:
- `[ -f /tmp/poc-multisite-project/13_СЕГМЕНТЫ_ЦА/smoke-test/subbrief.yaml ]`
- `grep "slug: smoke-test" /tmp/poc-multisite-project/.landing-state.yaml`

- [ ] **Step 3: curl the new subsite**

Run: `curl -s -L --max-time 15 http://smoke-test.ailexi.ru/ | grep -iE '<title|smoke-test' | head -5`
Expected: HTML response with `<title>` mentioning the new subsite

- [ ] **Step 4: Clone the new subsite**

Run:
```bash
bash skills/wp-multisite/scripts/clone-subsite.sh /tmp/poc-multisite-project alpha smoke-clone
```

Expected:
- `▶ Step 1: create destination segment 'smoke-clone'`
- `▶ Step 2: copy pages http://alpha.ailexi.ru → http://smoke-clone.ailexi.ru`
- `  page <id> → <new_id>` for each page in alpha
- `✅ Clone complete → http://smoke-clone.ailexi.ru`

- [ ] **Step 5: curl the cloned subsite, check it contains the same block as alpha**

Run: `curl -s -L --max-time 15 http://smoke-clone.ailexi.ru/ | grep -c 'lazyblock-poc-hero'`
Expected: ≥ 1 (block from alpha was copied)

- [ ] **Step 6: Clean up smoke artifacts on Beget**

Run:
```bash
# Delete WP subsites
ssh esper21@esper21.beget.tech "cd /home/e/esper21/ailexi.ru/public_html && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar site delete --slug=smoke-test --yes"
ssh esper21@esper21.beget.tech "cd /home/e/esper21/ailexi.ru/public_html && /usr/local/bin/php8.3 /usr/local/bin/wp-cli.phar site delete --slug=smoke-clone --yes"

# Delete Beget subdomains
SMOKE_TEST_ID=$(curl -s -X POST "https://api.beget.com/api/domain/getSubdomainList" \
  --data-urlencode "login=esper21" --data-urlencode "passwd=FP63zwOF%41*" \
  --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(x['id']) for x in d['answer']['result'] if x['fqdn'] in ('smoke-test.ailexi.ru','smoke-clone.ailexi.ru')]")
for id in $SMOKE_TEST_ID; do
    curl -s -X POST "https://api.beget.com/api/domain/deleteSubdomain" \
      --data-urlencode "login=esper21" --data-urlencode "passwd=FP63zwOF%41*" \
      --data-urlencode "input_format=json" --data-urlencode "output_format=json" \
      --data-urlencode "input_data={\"id\":$id}"
done

rm -rf /tmp/poc-multisite-project
```

- [ ] **Step 7: Record smoke test results in cookbook**

Add to `docs/beget-cookbook.md` under the «Validated рецепты» section a one-paragraph note:

```markdown
### CD1 end-to-end smoke (2026-MM-DD)

`landing-segment.sh` создал новый segment `smoke-test.ailexi.ru` за <N>
секунд: subdomain через API + linkDomain + PHP 8.3 + `wp site create`
вернуло blog_id=<X>. curl на новый поддомен показал валидный HTML с
правильным `<title>`. `clone-subsite.sh` скопировал страницы с alpha на
smoke-clone, curl на копию содержит `lazyblock-poc-hero` маркер. Cleanup
прошёл чисто. **CD1 готов к merge в main.**
```

- [ ] **Step 8: Commit smoke test result**

```bash
git add docs/beget-cookbook.md
git commit -m "docs(beget): CD1 end-to-end smoke test passed

Verified landing-segment.sh + clone-subsite.sh against live POC env
(ailexi.ru multisite). New segment created and cloned successfully,
artifacts cleaned. CD1 ready for merge.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

### 1. Spec coverage

S2-CD spec §3.1 «migrate-to-multisite.sh» → Tasks 7-8 ✓
S2-CD spec §3.1 «landing-segment.sh» → Tasks 9-10 ✓
S2-CD spec §3.1 «clone-subsite.sh» → Task 11 ✓
S2-CD spec §3.1 «`.landing-state.yaml::audience_segments`» → Tasks 4, 5 ✓
S2-CD spec §3.1 «`13_СЕГМЕНТЫ_ЦА/<name>/` skeleton» → Task 6 ✓
S2-CD spec §3.1 «`/landing-segment` slash command» → Task 12 ✓
S2-CD spec §3.1 «`/landing-clone` updated under multisite» → Task 13 ✓
S2-CD spec §9 «smoke-gate after each Task» → каждый Task имеет bats-тесты + Task 15 end-to-end ✓
S2-CD spec §6 «Lazy Blocks safety gate» — пока что не интегрирован в migrate-to-multisite. Это **намеренно** отложено в CD3 (когда переписываем генератор) — smoke `lazyblock/X` slug требует переделки stage-08, а в CD1 мы инфраструктуру создаём, не блоки. Существующая тема (после миграции) сохраняет старый `lzb/init` хук и старые slugs — это работает (см. lixiang-dubai2 анализ).

### 2. Placeholder scan

Search the plan for: TBD, TODO, implement later, fill in details, similar to Task. **None found.** Every code block is complete and runnable.

One soft-spot: Task 15 manual smoke test has `<N>`, `<X>` placeholders in the **cookbook entry text** — these are intentional, they'll be filled with actual numbers at run time. Не plan failure, а legitimate template для recording results.

### 3. Type / API consistency

- `state_is_multisite`, `state_segment_exists`, `state_add_segment`, `state_set_multisite_true` — все объявлены в Task 4, используются в Tasks 7-11 одинаково.
- `beget_subdomain_exists`, `beget_subdomain_add`, `beget_subdomain_id`, `beget_site_link`, `beget_set_php` — объявлены в Tasks 1-2, используются в Tasks 7-11 одинаково.
- `ssh_beget`, `wp_remote`, `wp_remote_url`, `REMOTE_WP_BIN` — объявлены в Task 3, используются всеми.
- Регекс slug `^[a-z][a-z0-9-]*$` — последовательно в Task 9 и frontmatter Task 12.
- `.subsite-meta.yaml` поля (`slug`, `host`, `blog_id`, `created`) — одинаково в Task 6 (template) и Task 10 (генерация).

Всё consistent.

---

## Что НЕ покрыто CD1 (отложено в CD2+)

| Что | Куда отложено | Почему |
|---|---|---|
| Multisite-aware deploy (генерация контента в subsite) | CD2 | Требует переработки `deploy-wordpress.sh` под `--url=<subsite>`. |
| Pipeline генерации контента под сегмент (брейф → прототип → composed) | CD2 | Отдельный pipeline, читает `subbrief.yaml`. |
| Lazy Blocks generator fixes (slug namespace) | CD3 | Не нужно для CD1, который только инфраструктуру создаёт. |
| SEO/AI mu-plugins из POC | CD4 | Не нужно для CD1. |
| Скрейпер панели Бегета для авто-SSL | CD6 | Manual SSL в CD1 достаточно. |

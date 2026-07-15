# HybridAutos Backup, Staging, Deploy, and Rollback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put the exact HybridAutos production source under verified GitHub control, create a free encrypted current-state file/database backup, rehearse restore and rollback on staging, and deploy the lead-reliability release to production in backward-compatible allow-listed phases.

**Architecture:** `neuroboostpr-pixel/landing_system` owns the generic WordPress lead plugin, while a new private `neuroboostpr-pixel/hybridautos-ae` repository owns the captured production theme, deployment tooling, release manifests, and the pinned `landing_system` submodule. A current encrypted local archive is the normal recovery point; production is updated backend-first and frontend-second using only manifest-listed files, with the previous immutable release used for normal rollback. Full database restore is reserved for corruption and merges post-snapshot lead tables plus integration/options state back afterwards.

**Tech Stack:** Git/GitHub CLI, Bash 3.2-compatible scripts, Bats, SSH, rsync, scp, WP-CLI, PHP 8.x on Beget, OpenSSL AES-256-CBC with PBKDF2, macOS Keychain, jq, SHA-256.

## Global Constraints

- Production site: `https://hybridautos.ae`.
- Production WordPress path: `/home/c/cmoevexs/hybridautos.ae/public_html` on `cmoevexs@cmoevexs.beget.tech`.
- Staging WordPress path: `/home/e/esper21/esper21.ru/public_html` on `esper21@esper21.beget.tech`; staging is disposable and must remain outbound-blocked while production data is present.
- System worktree: `/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15`.
- Site repository path: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae`.
- Backup output path: `/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current`.
- Release ID: `20260715-lead-reliability-v1`; previous release ID: `20260715-pre-reliability-v1`.
- The system baseline is commit `1c3372cacd41efc21be038fef13d5a12919e2769` on `backup/hybridautos-prod-before-reliability-2026-07-15`.
- GitHub is not considered a backup until the remote API returns the expected commit SHA. Current write access is unproven, so the first task is a hard gate.
- The site repository must be private. Neither repository may contain `Секреты.txt`, `.env`, `wp-config.php`, database dumps, logs, uploads, tokens, passwords, or customer data.
- Do not create a second Beget permanent backup with the observed `2 ₽/day` recurring charge. This plan uses a complete encrypted local export and verifies it by restore rehearsal.
- Database migration is additive only. No dropped/renamed columns and no required column without a safe default.
- Never run site-wide `rsync --delete`, never replace all of `public_html`, and never deploy an uncommitted working tree.
- Backend must accept both old cached requests without `submission_id` and new requests with it before frontend deployment begins.
- Upload new backend files before `landing-config.php`; upload new frontend assets before `functions.php`. Entry points are always replaced last.
- Paid traffic remains stopped until both contact-preservation and advertising-analytics gates pass.
- Any failed hard gate stops execution. Do not “continue and check later.”

---

### Task 1: Prove GitHub Write Access and Publish the System Safety Branch

**Files:**
- No file changes.

**Interfaces:**
- Consumes: local system branch `backup/hybridautos-prod-before-reliability-2026-07-15` at `1c3372cacd41efc21be038fef13d5a12919e2769`.
- Produces: verified remote backup branch and authenticated GitHub CLI with push permission.

- [ ] **Step 1: Authenticate GitHub CLI through the browser without reading the PAT from `Секреты.txt`**

Run:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
```

Expected: `Logged in to github.com account neuroboostpr-pixel` and no `token is invalid` message. If the active account is different, stop.

- [ ] **Step 2: Verify write permission to the system repository**

Run:

```bash
test "$(gh api repos/neuroboostpr-pixel/landing_system --jq '.permissions.push')" = "true"
printf 'GITHUB_SYSTEM_PUSH_OK\n'
```

Expected:

```text
GITHUB_SYSTEM_PUSH_OK
```

- [ ] **Step 3: Push the immutable production-hotfix backup branch**

Run:

```bash
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" push origin \
  1c3372cacd41efc21be038fef13d5a12919e2769:refs/heads/backup/hybridautos-prod-before-reliability-2026-07-15
```

Expected: a new or up-to-date remote branch, with no rejected update.

- [ ] **Step 4: Verify the remote SHA through GitHub, not the local remote-tracking cache**

Run:

```bash
test "$(gh api repos/neuroboostpr-pixel/landing_system/git/ref/heads/backup/hybridautos-prod-before-reliability-2026-07-15 --jq '.object.sha')" = \
  "1c3372cacd41efc21be038fef13d5a12919e2769"
printf 'REMOTE_SYSTEM_BACKUP_OK\n'
```

Expected:

```text
REMOTE_SYSTEM_BACKUP_OK
```

- [ ] **Step 5: Publish the current feature branch and verify its remote SHA**

Run:

```bash
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" push -u origin fix/lead-reliability-observability
LOCAL_SHA="$(git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" rev-parse HEAD)"
REMOTE_SHA="$(gh api repos/neuroboostpr-pixel/landing_system/git/ref/heads/fix/lead-reliability-observability --jq '.object.sha')"
test "$LOCAL_SHA" = "$REMOTE_SHA"
printf 'REMOTE_SYSTEM_FEATURE_OK %s\n' "$REMOTE_SHA"
```

Expected: `REMOTE_SYSTEM_FEATURE_OK` followed by one 40-character SHA.

---

### Task 2: Create the Private Site Repository and Capture the Exact Production Theme

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/.gitignore`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/README.md`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/08_КОД/wp-theme/**`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/baseline-theme.sha256`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/.gitmodules`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/landing_system` as a Git submodule.

**Interfaces:**
- Consumes: production theme `/home/c/cmoevexs/hybridautos.ae/public_html/wp-content/themes/lp-hibridcars-uae` and system baseline commit `1c3372c`.
- Produces: private remote repository, baseline tag `prod-before-reliability-2026-07-15`, and an exact Git copy of the live custom theme.

- [ ] **Step 1: Add this Mac’s existing public SSH key to both Beget accounts**

Run locally to display the public key and fingerprint:

```bash
cat "$HOME/.ssh/id_ed25519.pub"
ssh-keygen -lf "$HOME/.ssh/id_ed25519.pub"
```

Expected fingerprint:

```text
256 SHA256:oubwS5FdFXFcnVllv66ve4OEpk5nxJoLGGRCpImtiEQ kirill@mac (ED25519)
```

In each Beget account, open `SSH → SSH keys → Add key`, add the displayed public key, and do not upload the private file `~/.ssh/id_ed25519`.

- [ ] **Step 2: Verify non-interactive SSH, WP-CLI, PHP, and SHA-256 on production and staging**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" -o BatchMode=yes cmoevexs@cmoevexs.beget.tech \
  'printf "PROD_SSH_OK\n"; command -v wp; command -v php; command -v sha256sum'
ssh -i "$HOME/.ssh/id_ed25519" -o BatchMode=yes esper21@esper21.beget.tech \
  'printf "STAGING_SSH_OK\n"; command -v wp; command -v php; command -v sha256sum'
```

Expected: both markers plus three non-empty executable paths. If either account still says `Permission denied`, stop before touching production.

- [ ] **Step 3: Initialize the site repository and write the exclusion boundary before copying files**

Run:

```bash
mkdir -p "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy"
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" init -b main
```

Create `.gitignore` with exactly:

```gitignore
.env
.env.*
Секреты.txt
*.sql
*.sql.gz
*.dump
*.log
*.tar
*.tar.gz
*.enc
backups/
dist/
wp-config.php
wp-content/uploads/
wp-content/cache/
.DS_Store
```

Create `README.md` with exactly:

```markdown
# HybridAutos UAE

Private source repository for `https://hybridautos.ae`.

- `08_КОД/wp-theme/` is the custom production theme.
- `landing_system/` pins the reviewed shared deployment/plugin source.
- `deploy/` contains non-secret manifests and controlled deployment tooling.

Secrets, databases, logs, uploads, backups, and customer data are forbidden in Git.
```

- [ ] **Step 4: Create and verify the private GitHub repository**

Run:

```bash
if gh repo view neuroboostpr-pixel/hybridautos-ae >/dev/null 2>&1; then
  test "$(gh repo view neuroboostpr-pixel/hybridautos-ae --json visibility --jq '.visibility')" = "PRIVATE"
else
  gh repo create neuroboostpr-pixel/hybridautos-ae --private \
    --description "Private production source for hybridautos.ae" \
    --disable-issues --disable-wiki
fi
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" remote add origin \
  https://github.com/neuroboostpr-pixel/hybridautos-ae.git
test "$(gh repo view neuroboostpr-pixel/hybridautos-ae --json visibility --jq '.visibility')" = "PRIVATE"
printf 'PRIVATE_SITE_REPO_OK\n'
```

Expected:

```text
PRIVATE_SITE_REPO_OK
```

- [ ] **Step 5: Pull the complete current custom theme from production without copying WordPress core, uploads, or configuration**

Run:

```bash
mkdir -p "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/08_КОД/wp-theme"
rsync -a --safe-links -e "ssh -i $HOME/.ssh/id_ed25519" \
  cmoevexs@cmoevexs.beget.tech:/home/c/cmoevexs/hybridautos.ae/public_html/wp-content/themes/lp-hibridcars-uae/ \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/08_КОД/wp-theme/"
```

Expected: `functions.php`, `index.php`, all six page variants, `assets/`, and `blocks/` exist locally.

- [ ] **Step 6: Verify the current fixed form file is exactly the public production file**

Run:

```bash
REMOTE_HASH="$(ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  'sha256sum /home/c/cmoevexs/hybridautos.ae/public_html/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js' | awk '{print $1}')"
LOCAL_HASH="$(shasum -a 256 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/08_КОД/wp-theme/assets/js/lead-form.js" | awk '{print $1}')"
test "$REMOTE_HASH" = "34410806e241b51e576bc8d0e21fc4005e5250d967eab73d9905322e4b2c4522"
test "$LOCAL_HASH" = "$REMOTE_HASH"
printf 'PRODUCTION_FORM_BASELINE_OK %s\n' "$LOCAL_HASH"
```

Expected: `PRODUCTION_FORM_BASELINE_OK 34410806e241b51e576bc8d0e21fc4005e5250d967eab73d9905322e4b2c4522`.

- [ ] **Step 7: Pin the system baseline as a submodule and generate a theme manifest**

Run:

```bash
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" submodule add \
  https://github.com/neuroboostpr-pixel/landing_system.git landing_system
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/landing_system" checkout \
  1c3372cacd41efc21be038fef13d5a12919e2769
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/08_КОД/wp-theme"
find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 \
  > "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/baseline-theme.sha256"
```

Expected: the submodule is detached at `1c3372c`, and `baseline-theme.sha256` contains one row per theme file.

- [ ] **Step 8: Scan the staged source boundary for forbidden artifacts**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
test -z "$(find . -path './.git' -prune -o -type f \( -name 'wp-config.php' -o -name '*.sql' -o -name '*.log' -o -name 'Секреты.txt' \) -print)"
test -z "$(find . -path './.git' -prune -o -type d \( -path '*/wp-content/uploads' -o -path '*/wp-content/cache' \) -print)"
printf 'SOURCE_BOUNDARY_OK\n'
```

Expected:

```text
SOURCE_BOUNDARY_OK
```

- [ ] **Step 9: Commit, tag, push, and verify the remote baseline**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add .gitignore README.md .gitmodules landing_system 08_КОД/wp-theme deploy/baseline-theme.sha256
git commit -m "chore: capture HybridAutos production source baseline"
git tag -a prod-before-reliability-2026-07-15 -m "Production source before lead reliability release"
git push -u origin main --follow-tags
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(gh api repos/neuroboostpr-pixel/hybridautos-ae/commits/main --jq '.sha')"
test "$LOCAL_SHA" = "$REMOTE_SHA"
test "$(gh api repos/neuroboostpr-pixel/hybridautos-ae/git/ref/tags/prod-before-reliability-2026-07-15 --jq '.object.type')" = "tag"
printf 'REMOTE_SITE_BASELINE_OK %s\n' "$REMOTE_SHA"
```

Expected: `REMOTE_SITE_BASELINE_OK` followed by the site baseline SHA.

- [ ] **Step 10: Create and publish the isolated site feature branch**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git switch -c fix/lead-reliability-2026-07-15
git push -u origin fix/lead-reliability-2026-07-15
LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(gh api repos/neuroboostpr-pixel/hybridautos-ae/git/ref/heads/fix/lead-reliability-2026-07-15 --jq '.object.sha')"
test "$LOCAL_SHA" = "$REMOTE_SHA"
printf 'REMOTE_SITE_FEATURE_OK %s\n' "$REMOTE_SHA"
```

Expected: `REMOTE_SITE_FEATURE_OK` followed by the same baseline SHA. All later site-repository commits in this plan stay on this feature branch; `main` remains the production-source baseline until the release is reviewed.

---

### Task 3: Implement a Free Encrypted Full Backup Command

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/tests/deploy/test_backup_current.bats`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/backup-current.sh`

**Interfaces:**
- Consumes: working production SSH access and macOS Keychain service `hybridautos-backup-20260715`.
- Produces: `hybridautos-pre-reliability-20260715.tar.gz.enc` plus non-sensitive `summary.json`; no plaintext database or site tree remains.

- [ ] **Step 1: Write the failing Bats contract test**

Create `tests/deploy/test_backup_current.bats` with exactly:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  SCRIPT="$REPO/deploy/backup-current.sh"
}

@test "backup script has valid bash syntax" {
  run bash -n "$SCRIPT"
  [ "$status" -eq 0 ]
}

@test "backup includes complete public_html and a WP-CLI database export" {
  run grep -F 'public_html/' "$SCRIPT"
  [ "$status" -eq 0 ]
  run grep -F 'wp db export' "$SCRIPT"
  [ "$status" -eq 0 ]
}

@test "backup is encrypted and never invokes a paid Beget snapshot API" {
  run grep -F 'openssl enc -aes-256-cbc' "$SCRIPT"
  [ "$status" -eq 0 ]
  run grep -E 'backup/save|backup/create|permanent.backup' "$SCRIPT"
  [ "$status" -ne 0 ]
}

@test "backup validates WordPress and lead tables before success" {
  run grep -F 'wp_options' "$SCRIPT"
  [ "$status" -eq 0 ]
  run grep -F 'wp_landing_leads' "$SCRIPT"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: Run the test and verify it fails because the script does not exist**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_backup_current.bats
```

Expected: four failed tests referencing missing `deploy/backup-current.sh`.

- [ ] **Step 3: Implement the complete backup command**

Create `deploy/backup-current.sh` with exactly:

```bash
#!/usr/bin/env bash
set -euo pipefail

REMOTE="cmoevexs@cmoevexs.beget.tech"
REMOTE_WP="/home/c/cmoevexs/hybridautos.ae/public_html"
SSH_KEY="$HOME/.ssh/id_ed25519"
OUTPUT_DIR="/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current"
ARCHIVE_NAME="hybridautos-pre-reliability-20260715.tar.gz.enc"
KEYCHAIN_SERVICE="hybridautos-backup-20260715"
REMOTE_SQL="/tmp/hybridautos-pre-reliability-20260715.sql"

for command_name in ssh rsync scp tar openssl jq shasum security; do
  command -v "$command_name" >/dev/null || {
    printf 'ERROR missing command: %s\n' "$command_name" >&2
    exit 1
  }
done

test -f "$SSH_KEY" || { printf 'ERROR SSH key missing\n' >&2; exit 1; }
mkdir -p "$OUTPUT_DIR"
chmod 700 "$OUTPUT_DIR"
WORK="$(mktemp -d /private/tmp/hybridautos-backup.XXXXXX)"

cleanup() {
  ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "rm -f '$REMOTE_SQL'" >/dev/null 2>&1 || true
  rm -rf "$WORK"
  unset BACKUP_PASS || true
}
trap cleanup EXIT INT TERM

if ! security find-generic-password -a "$USER" -s "$KEYCHAIN_SERVICE" -w >/dev/null 2>&1; then
  security add-generic-password -a "$USER" -s "$KEYCHAIN_SERVICE" \
    -w "$(openssl rand -base64 48)" >/dev/null
fi
BACKUP_PASS="$(security find-generic-password -a "$USER" -s "$KEYCHAIN_SERVICE" -w)"
export BACKUP_PASS

ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" \
  "test -d '$REMOTE_WP' && wp --path='$REMOTE_WP' core is-installed && printf 'REMOTE_READY\\n'"

mkdir -p "$WORK/public_html" "$WORK/database"
rsync -a --safe-links -e "ssh -i $SSH_KEY -o BatchMode=yes" \
  "$REMOTE:$REMOTE_WP/" "$WORK/public_html/"

ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" \
  "wp --path='$REMOTE_WP' db export '$REMOTE_SQL' --add-drop-table"
scp -i "$SSH_KEY" -o BatchMode=yes "$REMOTE:$REMOTE_SQL" \
  "$WORK/database/cmoevexs_wp_1.sql"
ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "rm -f '$REMOTE_SQL'"

grep -Eq 'CREATE TABLE [`]?wp_options' "$WORK/database/cmoevexs_wp_1.sql"
grep -Eq 'CREATE TABLE [`]?wp_landing_leads' "$WORK/database/cmoevexs_wp_1.sql"
grep -Eq 'CREATE TABLE [`]?wp_landing_lead_audit' "$WORK/database/cmoevexs_wp_1.sql"

(
  cd "$WORK"
  find public_html -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > files.sha256
  shasum -a 256 database/cmoevexs_wp_1.sql > database.sha256
)

FILE_COUNT="$(find "$WORK/public_html" -type f | wc -l | tr -d ' ')"
FILE_BYTES="$(du -sk "$WORK/public_html" | awk '{print $1 * 1024}')"
DB_BYTES="$(stat -f '%z' "$WORK/database/cmoevexs_wp_1.sql")"
CAPTURED_AT="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

jq -n \
  --arg captured_at "$CAPTURED_AT" \
  --arg domain "hybridautos.ae" \
  --arg database "cmoevexs_wp_1" \
  --argjson file_count "$FILE_COUNT" \
  --argjson file_bytes "$FILE_BYTES" \
  --argjson database_bytes "$DB_BYTES" \
  '{schema:1,captured_at_utc:$captured_at,domain:$domain,database:$database,file_count:$file_count,file_bytes:$file_bytes,database_bytes:$database_bytes}' \
  > "$WORK/manifest.json"

tar -C "$WORK" -czf - manifest.json files.sha256 database.sha256 public_html database \
  | openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 \
      -pass env:BACKUP_PASS -out "$OUTPUT_DIR/$ARCHIVE_NAME"

ARCHIVE_SHA="$(shasum -a 256 "$OUTPUT_DIR/$ARCHIVE_NAME" | awk '{print $1}')"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -pass env:BACKUP_PASS -in "$OUTPUT_DIR/$ARCHIVE_NAME" \
  | tar -tzf - | grep -qx 'database/cmoevexs_wp_1.sql'

jq -n \
  --arg archive "$ARCHIVE_NAME" \
  --arg sha256 "$ARCHIVE_SHA" \
  --arg captured_at "$CAPTURED_AT" \
  --argjson file_count "$FILE_COUNT" \
  '{schema:1,archive:$archive,sha256:$sha256,captured_at_utc:$captured_at,file_count:$file_count,encrypted:true,recurring_charge:false}' \
  > "$OUTPUT_DIR/summary.json"
chmod 600 "$OUTPUT_DIR/$ARCHIVE_NAME" "$OUTPUT_DIR/summary.json"

printf 'BACKUP_OK archive=%s sha256=%s files=%s\n' "$ARCHIVE_NAME" "$ARCHIVE_SHA" "$FILE_COUNT"
```

- [ ] **Step 4: Make the command executable and run the tests**

Run:

```bash
chmod 755 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/backup-current.sh"
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_backup_current.bats
```

Expected: `4 tests, 0 failures`.

- [ ] **Step 5: Commit the backup tooling**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/backup-current.sh tests/deploy/test_backup_current.bats
git commit -m "feat(deploy): add encrypted production backup command"
git push origin fix/lead-reliability-2026-07-15
```

Expected: one new commit pushed to the private site repository.

---

### Task 4: Create and Verify the Fresh Full Current-State Backup

**Files:**
- Create outside Git: `/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/hybridautos-pre-reliability-20260715.tar.gz.enc`
- Create outside Git: `/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/summary.json`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/release-inputs/predeploy-backup-summary.json`

**Interfaces:**
- Consumes: `deploy/backup-current.sh` and production SSH.
- Produces: fresh encrypted files+database recovery point and a non-sensitive release evidence record.

- [ ] **Step 1: Execute the backup command**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/backup-current.sh
```

Expected: one final line beginning `BACKUP_OK`, file count greater than `1500`, and no Beget paid-backup action.

- [ ] **Step 2: Verify the encrypted archive hash and contents independently**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current"
test "$(shasum -a 256 hybridautos-pre-reliability-20260715.tar.gz.enc | awk '{print $1}')" = \
  "$(jq -r '.sha256' summary.json)"
BACKUP_PASS="$(security find-generic-password -a "$USER" -s hybridautos-backup-20260715 -w)"
export BACKUP_PASS
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_PASS \
  -in hybridautos-pre-reliability-20260715.tar.gz.enc \
  | tar -tzf - \
  | grep -E '^(public_html/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js|public_html/wp-content/mu-plugins/landing-config/includes/rest-lead.php|database/cmoevexs_wp_1.sql)$'
unset BACKUP_PASS
```

Expected: exactly the three required paths are printed.

- [ ] **Step 3: Prove no plaintext backup remains in the persistent backup directory**

Run:

```bash
test -z "$(find "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current" \
  -type f ! -name '*.enc' ! -name 'summary.json' -print)"
printf 'NO_PLAINTEXT_BACKUP_OK\n'
```

Expected:

```text
NO_PLAINTEXT_BACKUP_OK
```

- [ ] **Step 4: Store only the non-sensitive evidence summary in the private site repository**

Run:

```bash
mkdir -p "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/release-inputs"
cp "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/summary.json" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/release-inputs/predeploy-backup-summary.json"
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/release-inputs/predeploy-backup-summary.json
git commit -m "chore(release): record encrypted predeploy backup evidence"
git push origin fix/lead-reliability-2026-07-15
```

Expected: the committed JSON contains only archive name, hash, UTC time, file count, encryption flag, and `recurring_charge:false`.

---

### Task 5: Add a Staging Outbound Guard and Recovery-State Utilities

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/staging-safety.php`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/export-recovery-state.php`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/import-recovery-state.php`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/tests/deploy/test_recovery_files.bats`

**Interfaces:**
- Consumes: a WordPress installation with `lp_integration` records.
- Produces: staging that cannot send Email/Telegram/Roistat, and an encrypted-bundle-ready JSON exporter/importer for integration records plus `lp_*`/`landing_*` options.

- [ ] **Step 1: Write the failing safety and syntax contract**

Create `tests/deploy/test_recovery_files.bats` with exactly:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
}

@test "staging guard blocks both email and external HTTP" {
  run grep -F "pre_wp_mail" "$REPO/deploy/staging-safety.php"
  [ "$status" -eq 0 ]
  run grep -F "pre_http_request" "$REPO/deploy/staging-safety.php"
  [ "$status" -eq 0 ]
}

@test "recovery exporter includes integrations and scoped options" {
  run grep -F "lp_integration" "$REPO/deploy/wp-cli/export-recovery-state.php"
  [ "$status" -eq 0 ]
  run grep -F "landing\\_%" "$REPO/deploy/wp-cli/export-recovery-state.php"
  [ "$status" -eq 0 ]
}

@test "recovery importer refuses a post ID collision with another post type" {
  run grep -F "integration_post_id_collision" "$REPO/deploy/wp-cli/import-recovery-state.php"
  [ "$status" -eq 0 ]
  run grep -F "wp_delete_post" "$REPO/deploy/wp-cli/import-recovery-state.php"
  [ "$status" -eq 0 ]
  run grep -F "delete_option" "$REPO/deploy/wp-cli/import-recovery-state.php"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: Run the test and verify all three tests fail**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_recovery_files.bats
```

Expected: `3 tests, 3 failures` because the files do not exist.

- [ ] **Step 3: Implement the staging outbound guard**

Create `deploy/staging-safety.php` with exactly:

```php
<?php
/**
 * Plugin Name: HybridAutos Staging Safety
 * Description: Prevents restored production data from contacting real external services.
 */
if (!defined('ABSPATH')) { exit; }

add_filter('pre_wp_mail', static function ($return, array $atts) {
    error_log('[hybridautos-staging] blocked wp_mail subject=' . sanitize_text_field((string)($atts['subject'] ?? '')));
    return true;
}, PHP_INT_MAX, 2);

add_filter('pre_http_request', static function ($preempt, array $args, string $url) {
    return new WP_Error('hybridautos_staging_external_http_blocked', 'External HTTP is blocked on staging.');
}, PHP_INT_MAX, 3);
```

- [ ] **Step 4: Implement recovery-state export**

Create `deploy/wp-cli/export-recovery-state.php` with exactly:

```php
<?php
if (!defined('WP_CLI') || !WP_CLI) { exit(1); }
if (count($args) !== 1) { WP_CLI::error('usage: wp eval-file export-recovery-state.php /tmp/hybridautos-recovery-state.json'); }

$output = (string)$args[0];
$posts = get_posts([
    'post_type' => 'lp_integration',
    'post_status' => 'any',
    'posts_per_page' => -1,
    'orderby' => 'ID',
    'order' => 'ASC',
]);

$integrations = [];
foreach ($posts as $post) {
    $meta = [];
    foreach (get_post_meta((int)$post->ID) as $key => $values) {
        $meta[$key] = array_map('maybe_unserialize', $values);
    }
    $integrations[] = [
        'ID' => (int)$post->ID,
        'post_title' => (string)$post->post_title,
        'post_status' => (string)$post->post_status,
        'meta' => $meta,
    ];
}

global $wpdb;
$option_names = $wpdb->get_col(
    "SELECT option_name FROM {$wpdb->options}
     WHERE option_name LIKE 'lp\\_%'
        OR option_name LIKE 'landing\\_%'
        OR option_name = 'admin_email'
     ORDER BY option_name ASC"
);
$options = [];
foreach ($option_names as $name) {
    $options[$name] = get_option($name);
}

$payload = [
    'schema' => 1,
    'captured_at_utc' => gmdate('c'),
    'site_url' => home_url('/'),
    'integrations' => $integrations,
    'options' => $options,
];

$json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if ($json === false || file_put_contents($output, $json) === false) {
    WP_CLI::error('recovery_state_write_failed');
}
chmod($output, 0600);
WP_CLI::success('RECOVERY_STATE_EXPORTED integrations=' . count($integrations) . ' options=' . count($options));
```

- [ ] **Step 5: Implement recovery-state import**

Create `deploy/wp-cli/import-recovery-state.php` with exactly:

```php
<?php
if (!defined('WP_CLI') || !WP_CLI) { exit(1); }
if (count($args) !== 1) { WP_CLI::error('usage: wp eval-file import-recovery-state.php /tmp/hybridautos-recovery-state.json'); }

$input = (string)$args[0];
$payload = json_decode((string)file_get_contents($input), true);
if (!is_array($payload) || ($payload['schema'] ?? null) !== 1) {
    WP_CLI::error('invalid_recovery_state_schema');
}

$payload_integrations = (array)($payload['integrations'] ?? []);
$payload_options = (array)($payload['options'] ?? []);
foreach ($payload_integrations as $record) {
    if (!is_array($record)) { WP_CLI::error('invalid_integration_record'); }
    $id = (int)($record['ID'] ?? 0);
    if ($id <= 0) { WP_CLI::error('invalid_integration_post_id'); }
    $existing = get_post($id);
    if ($existing && $existing->post_type !== 'lp_integration') {
        WP_CLI::error('integration_post_id_collision:' . $id);
    }
}
foreach (array_keys($payload_options) as $name) {
    if ($name !== 'admin_email' && !str_starts_with((string)$name, 'lp_') && !str_starts_with((string)$name, 'landing_')) {
        WP_CLI::error('option_outside_allowlist:' . $name);
    }
}
$payload_ids = array_values(array_map(
    static fn(array $record): int => (int)($record['ID'] ?? 0),
    $payload_integrations
));
$existing_ids = get_posts([
    'post_type' => 'lp_integration',
    'post_status' => 'any',
    'posts_per_page' => -1,
    'fields' => 'ids',
]);
foreach (array_diff(array_map('intval', $existing_ids), $payload_ids) as $stale_id) {
    wp_delete_post((int)$stale_id, true);
}

foreach ($payload_integrations as $record) {
    $id = (int)($record['ID'] ?? 0);
    if ($id <= 0) { WP_CLI::error('invalid_integration_post_id'); }
    $existing = get_post($id);
    if ($existing && $existing->post_type !== 'lp_integration') {
        WP_CLI::error('integration_post_id_collision:' . $id);
    }
    $post_data = [
        'ID' => $id,
        'post_type' => 'lp_integration',
        'post_title' => sanitize_text_field((string)($record['post_title'] ?? 'Integration')),
        'post_status' => sanitize_key((string)($record['post_status'] ?? 'publish')),
    ];
    $result = $existing ? wp_update_post($post_data, true) : wp_insert_post($post_data, true);
    if (is_wp_error($result)) { WP_CLI::error($result->get_error_message()); }
    foreach (($record['meta'] ?? []) as $key => $values) {
        delete_post_meta($id, (string)$key);
        foreach ((array)$values as $value) {
            add_post_meta($id, (string)$key, $value, false);
        }
    }
}

global $wpdb;
$current_option_names = $wpdb->get_col(
    "SELECT option_name FROM {$wpdb->options}
     WHERE option_name LIKE 'lp\\_%'
        OR option_name LIKE 'landing\\_%'"
);
foreach ($current_option_names as $current_name) {
    if (!array_key_exists((string)$current_name, $payload_options)) {
        delete_option((string)$current_name);
    }
}

foreach ($payload_options as $name => $value) {
    if ($name !== 'admin_email' && !str_starts_with((string)$name, 'lp_') && !str_starts_with((string)$name, 'landing_')) {
        WP_CLI::error('option_outside_allowlist:' . $name);
    }
    update_option((string)$name, $value, false);
}

WP_CLI::success('RECOVERY_STATE_IMPORTED integrations=' . count($payload['integrations'] ?? []) . ' options=' . count($payload['options'] ?? []));
```

- [ ] **Step 6: Run the contract tests**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_recovery_files.bats
```

Expected: `3 tests, 0 failures`.

- [ ] **Step 7: Commit and push the recovery utilities**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/staging-safety.php deploy/wp-cli/export-recovery-state.php \
  deploy/wp-cli/import-recovery-state.php tests/deploy/test_recovery_files.bats
git commit -m "feat(deploy): add staging guard and recovery state tools"
git push origin fix/lead-reliability-2026-07-15
```

Expected: recovery tooling is stored only in the private repository.

---

### Task 6: Restore the Fresh Backup to Staging and Sanitize Production Data

**Files:**
- Temporary local restore directory: `/private/tmp/hybridautos-restore-20260715`.
- Temporary staging backups: `/tmp/esper21-before-hybridautos-rehearsal.sql` and `/tmp/wp-config.before-hybridautos-rehearsal.php`.
- Staging guard target: `/home/e/esper21/esper21.ru/public_html/wp-content/mu-plugins/hybridautos-staging-safety.php`.

**Interfaces:**
- Consumes: encrypted archive from Task 4 and staging guard from Task 5.
- Produces: a working, anonymized, outbound-blocked staging copy whose database and custom code came from the fresh production backup.

- [ ] **Step 1: Decrypt and verify the archive into the fixed temporary restore directory**

Run:

```bash
rm -rf /private/tmp/hybridautos-restore-20260715
mkdir -p /private/tmp/hybridautos-restore-20260715
BACKUP_PASS="$(security find-generic-password -a "$USER" -s hybridautos-backup-20260715 -w)"
export BACKUP_PASS
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_PASS \
  -in "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/hybridautos-pre-reliability-20260715.tar.gz.enc" \
  | tar -xzf - -C /private/tmp/hybridautos-restore-20260715
unset BACKUP_PASS
cd /private/tmp/hybridautos-restore-20260715
shasum -a 256 -c database.sha256
shasum -a 256 -c files.sha256
```

Expected: every checksum reports `OK`; any failure stops the rehearsal.

- [ ] **Step 2: Preserve the current staging database and configuration before overwriting staging**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html db export /tmp/esper21-before-hybridautos-rehearsal.sql --add-drop-table && \
   cp /home/e/esper21/esper21.ru/public_html/wp-config.php /tmp/wp-config.before-hybridautos-rehearsal.php && \
   chmod 600 /tmp/esper21-before-hybridautos-rehearsal.sql /tmp/wp-config.before-hybridautos-rehearsal.php"
```

Expected: WP-CLI reports a successful staging database export.

- [ ] **Step 3: Install the outbound guard before importing production data**

Run:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/staging-safety.php" \
  esper21@esper21.beget.tech:/home/e/esper21/esper21.ru/public_html/wp-content/mu-plugins/hybridautos-staging-safety.php
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "php -l /home/e/esper21/esper21.ru/public_html/wp-content/mu-plugins/hybridautos-staging-safety.php"
```

Expected: `No syntax errors detected`.

- [ ] **Step 4: Upload the production database export and prepare the staging WordPress config**

Run:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  /private/tmp/hybridautos-restore-20260715/database/cmoevexs_wp_1.sql \
  esper21@esper21.beget.tech:/tmp/hybridautos-production-copy-20260715.sql
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html config set WP_ENVIRONMENT_TYPE staging --type=constant && \
   wp --path=/home/e/esper21/esper21.ru/public_html config set DISABLE_WP_CRON true --raw --type=constant && \
   wp --path=/home/e/esper21/esper21.ru/public_html db reset --yes && \
   wp --path=/home/e/esper21/esper21.ru/public_html config set table_prefix wp_ --raw --type=variable && \
   wp --path=/home/e/esper21/esper21.ru/public_html db import /tmp/hybridautos-production-copy-20260715.sql"
```

Expected: config updates succeed, the staging database is reset, and the production-copy SQL import succeeds.

- [ ] **Step 5: Replace only the custom theme and lead plugin on staging**

Run:

```bash
rsync -a -e "ssh -i $HOME/.ssh/id_ed25519" \
  /private/tmp/hybridautos-restore-20260715/public_html/wp-content/themes/lp-hibridcars-uae/ \
  esper21@esper21.beget.tech:/home/e/esper21/esper21.ru/public_html/wp-content/themes/lp-hibridcars-uae/
rsync -a -e "ssh -i $HOME/.ssh/id_ed25519" \
  /private/tmp/hybridautos-restore-20260715/public_html/wp-content/mu-plugins/landing-config/ \
  esper21@esper21.beget.tech:/home/e/esper21/esper21.ru/public_html/wp-content/mu-plugins/landing-config/
scp -i "$HOME/.ssh/id_ed25519" \
  /private/tmp/hybridautos-restore-20260715/public_html/wp-content/mu-plugins/landing-config-loader.php \
  esper21@esper21.beget.tech:/home/e/esper21/esper21.ru/public_html/wp-content/mu-plugins/landing-config-loader.php
```

Expected: only the two custom directories and loader are synchronized; staging `wp-config.php`, uploads, and WordPress core are untouched.

- [ ] **Step 6: Rewrite URLs, disable integrations, and anonymize contact data before opening staging**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html search-replace 'https://hybridautos.ae' 'https://esper21.ru' --all-tables-with-prefix --skip-columns=guid && \
   wp --path=/home/e/esper21/esper21.ru/public_html option update home 'https://esper21.ru' && \
   wp --path=/home/e/esper21/esper21.ru/public_html option update siteurl 'https://esper21.ru' && \
   wp --path=/home/e/esper21/esper21.ru/public_html option update blog_public 0 && \
   wp --path=/home/e/esper21/esper21.ru/public_html eval '\$ids=get_posts([\"post_type\"=>\"lp_integration\",\"post_status\"=>\"any\",\"posts_per_page\"=>-1,\"fields\"=>\"ids\"]); foreach(\$ids as \$id){update_post_meta(\$id,\"_lp_int_enabled\",\"0\");} echo \"INTEGRATIONS_DISABLED=\".count(\$ids).PHP_EOL;' && \
   wp --path=/home/e/esper21/esper21.ru/public_html eval 'global \$wpdb; foreach([\$wpdb->prefix.\"landing_leads\",\$wpdb->prefix.\"landing_lead_audit\"] as \$table){if(\$wpdb->get_var(\$wpdb->prepare(\"SHOW TABLES LIKE %s\",\$table))===\$table){\$wpdb->query(\"UPDATE `\$table` SET name=CONCAT(\\\"TEST Lead \\\",id), phone=CONCAT(\\\"+971500\\\",LPAD(MOD(id,1000000),6,\\\"0\\\")), email=CONCAT(\\\"lead+\\\",id,\\\"@example.invalid\\\"), message=\\\"[redacted]\\\", ip=\\\"0.0.0.0\\\", user_agent=\\\"[redacted]\\\"\");}} echo \"PII_SANITIZED\\n\";' && \
   wp --path=/home/e/esper21/esper21.ru/public_html cache flush"
```

Expected: search-replace reports replacements, `INTEGRATIONS_DISABLED` is printed, then `PII_SANITIZED` and cache flush success.

- [ ] **Step 7: Verify staging is installed, non-indexable, outbound-blocked, and on the restored baseline**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html core is-installed && \
   test \"\$(wp --path=/home/e/esper21/esper21.ru/public_html option get blog_public)\" = 0 && \
   test \"\$(sha256sum /home/e/esper21/esper21.ru/public_html/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js | awk '{print \\$1}')\" = 34410806e241b51e576bc8d0e21fc4005e5250d967eab73d9905322e4b2c4522 && \
   wp --path=/home/e/esper21/esper21.ru/public_html eval '\$r=wp_remote_get(\"https://example.com\"); echo is_wp_error(\$r)?\$r->get_error_code():\"NOT_BLOCKED\";'"
curl -fsSI https://esper21.ru | head -n 1
```

Expected: WordPress is installed, the baseline JS hash matches, external HTTP returns `hybridautos_staging_external_http_blocked`, and staging responds with HTTP 200 or 301/302 to its canonical HTTPS URL.

- [ ] **Step 8: Record restore-rehearsal evidence without customer data**

Create `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/release-inputs/restore-rehearsal.json` with:

```json
{
  "schema": 1,
  "environment": "https://esper21.ru",
  "source_backup": "hybridautos-pre-reliability-20260715.tar.gz.enc",
  "files_checksum": "passed",
  "database_import": "passed",
  "custom_theme_restore": "passed",
  "lead_plugin_restore": "passed",
  "outbound_guard": "passed",
  "pii_sanitized": true,
  "recurring_charge": false
}
```

Commit:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/release-inputs/restore-rehearsal.json
git commit -m "test(deploy): record full backup restore rehearsal"
git push origin fix/lead-reliability-2026-07-15
```

Expected: evidence is in the private repository; the encrypted backup itself remains outside Git.

- [ ] **Step 9: Remove decrypted production data after the restore evidence is recorded**

Run:

```bash
rm -rf /private/tmp/hybridautos-restore-20260715
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "rm -f /tmp/hybridautos-production-copy-20260715.sql && test ! -e /tmp/hybridautos-production-copy-20260715.sql"
test ! -e /private/tmp/hybridautos-restore-20260715
printf 'STAGING_RESTORE_PLAINTEXT_REMOVED\n'
```

Expected:

```text
STAGING_RESTORE_PLAINTEXT_REMOVED
```

The encrypted local backup remains; the decrypted database and file tree do not.

---

### Task 7: Build Immutable New and Previous Release Archives with Generated Allow-Lists

**Files:**
- Create locally, ignored by Git: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1/**`
- Create locally, ignored by Git: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1/**`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases/20260715-lead-reliability-v1.json`

**Interfaces:**
- Consumes: final committed system feature branch, final committed site feature branch, system baseline `1c3372c`, and site baseline tag `prod-before-reliability-2026-07-15`.
- Produces: code-only new/previous release archives, strict backend/frontend allow-lists, SHA-256 manifests, and GitHub release assets.

- [ ] **Step 1: Verify both implementation worktrees are clean and pushed**

Run:

```bash
SYSTEM_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15"
SITE_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
test -z "$(git -C "$SYSTEM_REPO" status --porcelain)"
test -z "$(git -C "$SITE_REPO" status --porcelain)"
SYSTEM_SHA="$(git -C "$SYSTEM_REPO" rev-parse HEAD)"
SITE_SHA="$(git -C "$SITE_REPO" rev-parse HEAD)"
test "$SYSTEM_SHA" = "$(gh api repos/neuroboostpr-pixel/landing_system/git/ref/heads/fix/lead-reliability-observability --jq '.object.sha')"
test "$SITE_SHA" = "$(gh api repos/neuroboostpr-pixel/hybridautos-ae/git/ref/heads/fix/lead-reliability-2026-07-15 --jq '.object.sha')"
grep -F "const DB_VERSION = '1.1.0';" "$SYSTEM_REPO/skills/wp-landing-config/mu-plugin/landing-config/includes/db.php"
printf 'RELEASE_SOURCE_OK system=%s site=%s\n' "$SYSTEM_SHA" "$SITE_SHA"
```

Expected: clean repositories, matching remote SHAs, and DB version `1.1.0`.

- [ ] **Step 2: Reject destructive source changes before constructing the release**

Run:

```bash
SYSTEM_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15"
SITE_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
test -z "$(git -C "$SYSTEM_REPO" diff --name-only --diff-filter=D 1c3372cacd41efc21be038fef13d5a12919e2769..HEAD -- skills/wp-landing-config/mu-plugin/landing-config)"
test -z "$(git -C "$SITE_REPO" diff --name-only --diff-filter=D prod-before-reliability-2026-07-15..HEAD -- 08_КОД/wp-theme)"
printf 'NO_RELEASE_DELETIONS_OK\n'
```

Expected:

```text
NO_RELEASE_DELETIONS_OK
```

- [ ] **Step 3: Construct the new release payload and allow-lists from Git diffs**

Run this block exactly:

```bash
set -euo pipefail
SYSTEM_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15"
SITE_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
RELEASE_DIR="$SITE_REPO/dist/20260715-lead-reliability-v1"
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR/payload" "$RELEASE_DIR/meta"

git -C "$SYSTEM_REPO" diff --name-only --diff-filter=AM \
  1c3372cacd41efc21be038fef13d5a12919e2769..HEAD -- \
  skills/wp-landing-config/mu-plugin/landing-config \
  | sed 's#^skills/wp-landing-config/mu-plugin/landing-config/#wp-content/mu-plugins/landing-config/#' \
  | LC_ALL=C sort > "$RELEASE_DIR/meta/allowlist-backend.unsorted.txt"

git -C "$SITE_REPO" diff --name-only --diff-filter=AM \
  prod-before-reliability-2026-07-15..HEAD -- 08_КОД/wp-theme \
  | sed 's#^08_КОД/wp-theme/#wp-content/themes/lp-hibridcars-uae/#' \
  | LC_ALL=C sort > "$RELEASE_DIR/meta/allowlist-frontend.unsorted.txt"

grep -v 'wp-content/mu-plugins/landing-config/landing-config.php$' \
  "$RELEASE_DIR/meta/allowlist-backend.unsorted.txt" > "$RELEASE_DIR/meta/allowlist-backend.txt" || true
grep 'wp-content/mu-plugins/landing-config/landing-config.php$' \
  "$RELEASE_DIR/meta/allowlist-backend.unsorted.txt" >> "$RELEASE_DIR/meta/allowlist-backend.txt" || true
grep -v 'wp-content/themes/lp-hibridcars-uae/functions.php$' \
  "$RELEASE_DIR/meta/allowlist-frontend.unsorted.txt" > "$RELEASE_DIR/meta/allowlist-frontend.txt" || true
grep 'wp-content/themes/lp-hibridcars-uae/functions.php$' \
  "$RELEASE_DIR/meta/allowlist-frontend.unsorted.txt" >> "$RELEASE_DIR/meta/allowlist-frontend.txt" || true

test -s "$RELEASE_DIR/meta/allowlist-backend.txt"
test -s "$RELEASE_DIR/meta/allowlist-frontend.txt"

while IFS= read -r remote_path; do
  source_path="skills/wp-landing-config/mu-plugin/landing-config/${remote_path#wp-content/mu-plugins/landing-config/}"
  mkdir -p "$RELEASE_DIR/payload/$(dirname "$remote_path")"
  cp "$SYSTEM_REPO/$source_path" "$RELEASE_DIR/payload/$remote_path"
done < "$RELEASE_DIR/meta/allowlist-backend.txt"

while IFS= read -r remote_path; do
  source_path="08_КОД/wp-theme/${remote_path#wp-content/themes/lp-hibridcars-uae/}"
  mkdir -p "$RELEASE_DIR/payload/$(dirname "$remote_path")"
  cp "$SITE_REPO/$source_path" "$RELEASE_DIR/payload/$remote_path"
done < "$RELEASE_DIR/meta/allowlist-frontend.txt"

(
  cd "$RELEASE_DIR/payload"
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "$RELEASE_DIR/meta/files.sha256"
)

SYSTEM_SHA="$(git -C "$SYSTEM_REPO" rev-parse HEAD)"
SITE_SHA="$(git -C "$SITE_REPO" rev-parse HEAD)"
jq -n --arg release_id "20260715-lead-reliability-v1" --arg system_sha "$SYSTEM_SHA" --arg site_sha "$SITE_SHA" \
  '{schema:1,release_id:$release_id,landing_system_commit:$system_sha,site_commit:$site_sha,database_version:"1.1.0",backend_first:true,site_wide_delete:false}' \
  > "$RELEASE_DIR/meta/release.json"
tar -C "$RELEASE_DIR" -czf "$SITE_REPO/dist/20260715-lead-reliability-v1.tar.gz" payload meta
shasum -a 256 "$SITE_REPO/dist/20260715-lead-reliability-v1.tar.gz" \
  > "$SITE_REPO/dist/20260715-lead-reliability-v1.tar.gz.sha256"
printf 'NEW_RELEASE_OK backend=%s frontend=%s\n' \
  "$(wc -l < "$RELEASE_DIR/meta/allowlist-backend.txt" | tr -d ' ')" \
  "$(wc -l < "$RELEASE_DIR/meta/allowlist-frontend.txt" | tr -d ' ')"
```

Expected: `NEW_RELEASE_OK` with both counts greater than zero.

- [ ] **Step 4: Construct the previous release using the same target list and baseline Git objects**

Run this block exactly:

```bash
set -euo pipefail
SYSTEM_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15"
SITE_REPO="/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
NEW_DIR="$SITE_REPO/dist/20260715-lead-reliability-v1"
OLD_DIR="$SITE_REPO/dist/20260715-pre-reliability-v1"
rm -rf "$OLD_DIR"
mkdir -p "$OLD_DIR/payload" "$OLD_DIR/meta"

: > "$OLD_DIR/meta/allowlist-backend.txt"
while IFS= read -r remote_path; do
  source_path="skills/wp-landing-config/mu-plugin/landing-config/${remote_path#wp-content/mu-plugins/landing-config/}"
  if git -C "$SYSTEM_REPO" cat-file -e "1c3372cacd41efc21be038fef13d5a12919e2769:$source_path" 2>/dev/null; then
    mkdir -p "$OLD_DIR/payload/$(dirname "$remote_path")"
    git -C "$SYSTEM_REPO" show "1c3372cacd41efc21be038fef13d5a12919e2769:$source_path" > "$OLD_DIR/payload/$remote_path"
    printf '%s\n' "$remote_path" >> "$OLD_DIR/meta/allowlist-backend.txt"
  fi
done < "$NEW_DIR/meta/allowlist-backend.txt"

: > "$OLD_DIR/meta/allowlist-frontend.txt"
while IFS= read -r remote_path; do
  source_path="08_КОД/wp-theme/${remote_path#wp-content/themes/lp-hibridcars-uae/}"
  if git -C "$SITE_REPO" cat-file -e "prod-before-reliability-2026-07-15:$source_path" 2>/dev/null; then
    mkdir -p "$OLD_DIR/payload/$(dirname "$remote_path")"
    git -C "$SITE_REPO" show "prod-before-reliability-2026-07-15:$source_path" > "$OLD_DIR/payload/$remote_path"
    printf '%s\n' "$remote_path" >> "$OLD_DIR/meta/allowlist-frontend.txt"
  fi
done < "$NEW_DIR/meta/allowlist-frontend.txt"

(
  cd "$OLD_DIR/payload"
  find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > "$OLD_DIR/meta/files.sha256"
)
jq -n --arg release_id "20260715-pre-reliability-v1" \
  '{schema:1,release_id:$release_id,landing_system_commit:"1c3372cacd41efc21be038fef13d5a12919e2769",site_ref:"prod-before-reliability-2026-07-15",database_rollback:false}' \
  > "$OLD_DIR/meta/release.json"
tar -C "$OLD_DIR" -czf "$SITE_REPO/dist/20260715-pre-reliability-v1.tar.gz" payload meta
shasum -a 256 "$SITE_REPO/dist/20260715-pre-reliability-v1.tar.gz" \
  > "$SITE_REPO/dist/20260715-pre-reliability-v1.tar.gz.sha256"
printf 'PREVIOUS_RELEASE_OK\n'
```

Expected:

```text
PREVIOUS_RELEASE_OK
```

New files absent from the previous release remain inert after the previous `landing-config.php` is restored; rollback does not delete them.

- [ ] **Step 5: Publish immutable archives as assets of a private GitHub release**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
SITE_SHA="$(jq -r '.site_commit' dist/20260715-lead-reliability-v1/meta/release.json)"
gh release create lead-reliability-v1 \
  dist/20260715-lead-reliability-v1.tar.gz \
  dist/20260715-lead-reliability-v1.tar.gz.sha256 \
  dist/20260715-pre-reliability-v1.tar.gz \
  dist/20260715-pre-reliability-v1.tar.gz.sha256 \
  --repo neuroboostpr-pixel/hybridautos-ae \
  --target "$SITE_SHA" \
  --title "HybridAutos lead reliability v1" \
  --notes "Backend-first compatible release with immutable previous-version rollback archive. No database, uploads, logs, secrets, or customer data."
gh release view lead-reliability-v1 --repo neuroboostpr-pixel/hybridautos-ae --json assets --jq '.assets[].name'
```

Expected: exactly the four archive/hash asset names are printed.

- [ ] **Step 6: Commit the non-secret release record**

Create `deploy/releases/20260715-lead-reliability-v1.json` from the generated metadata:

```bash
mkdir -p "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases"
jq -s '.[0] + {archive_sha256:.[1].sha256,previous_archive_sha256:.[2].sha256}' \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1/meta/release.json" \
  <(jq -Rn --arg sha256 "$(awk '{print $1}' "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1.tar.gz.sha256")" '{sha256:$sha256}') \
  <(jq -Rn --arg sha256 "$(awk '{print $1}' "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1.tar.gz.sha256")" '{sha256:$sha256}') \
  > "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases/20260715-lead-reliability-v1.json"
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/releases/20260715-lead-reliability-v1.json
git commit -m "chore(release): bind HybridAutos lead reliability artifacts"
git push origin fix/lead-reliability-2026-07-15
```

Expected: the record contains exact system/site commits, DB version `1.1.0`, and both archive hashes.

---

### Task 8: Implement the Allow-Listed Phase Deployer

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/tests/deploy/test_deploy_allowlist.bats`
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/deploy-allowlist.sh`

**Interfaces:**
- Consumes: an extracted release directory with `payload/`, `meta/files.sha256`, and phase allow-lists.
- Produces: one backend or frontend phase deployed per-file through temporary files, with entry points last and no deletions.

- [ ] **Step 1: Write the failing deploy safety tests**

Create `tests/deploy/test_deploy_allowlist.bats` with exactly:

```bash
#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  SCRIPT="$REPO/deploy/deploy-allowlist.sh"
}

@test "deployer has valid bash syntax" {
  run bash -n "$SCRIPT"
  [ "$status" -eq 0 ]
}

@test "deployer contains no delete sync" {
  run grep -F -- '--delete' "$SCRIPT"
  [ "$status" -ne 0 ]
}

@test "deployer restricts backend and frontend roots" {
  run grep -F 'wp-content/mu-plugins/landing-config/' "$SCRIPT"
  [ "$status" -eq 0 ]
  run grep -F 'wp-content/themes/lp-hibridcars-uae/' "$SCRIPT"
  [ "$status" -eq 0 ]
}

@test "production requires the exact confirmation token" {
  run grep -F 'deploy-20260715-lead-reliability-v1' "$SCRIPT"
  [ "$status" -eq 0 ]
}
```

- [ ] **Step 2: Run the tests and verify they fail because the deployer is absent**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_deploy_allowlist.bats
```

Expected: four failed tests.

- [ ] **Step 3: Implement the complete allow-listed deployer**

Create `deploy/deploy-allowlist.sh` with exactly:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  printf 'usage: deploy-allowlist.sh test|prod backend|frontend RELEASE_DIR\n' >&2
  exit 2
fi

ENVIRONMENT="$1"
PHASE="$2"
RELEASE_DIR="$(cd "$3" && pwd)"
SSH_KEY="$HOME/.ssh/id_ed25519"

case "$ENVIRONMENT" in
  test)
    REMOTE="esper21@esper21.beget.tech"
    REMOTE_WP="/home/e/esper21/esper21.ru/public_html"
    ;;
  prod)
    test "${HYBRIDAUTOS_PROD_CONFIRM:-}" = "deploy-20260715-lead-reliability-v1" || {
      printf 'ERROR production confirmation token missing\n' >&2
      exit 1
    }
    REMOTE="cmoevexs@cmoevexs.beget.tech"
    REMOTE_WP="/home/c/cmoevexs/hybridautos.ae/public_html"
    ;;
  *) printf 'ERROR invalid environment\n' >&2; exit 2 ;;
esac

case "$PHASE" in
  backend)
    ALLOWLIST="$RELEASE_DIR/meta/allowlist-backend.txt"
    SAFE_PREFIX="wp-content/mu-plugins/landing-config/"
    ;;
  frontend)
    ALLOWLIST="$RELEASE_DIR/meta/allowlist-frontend.txt"
    SAFE_PREFIX="wp-content/themes/lp-hibridcars-uae/"
    ;;
  *) printf 'ERROR invalid phase\n' >&2; exit 2 ;;
esac

test -s "$ALLOWLIST" || { printf 'ERROR empty allowlist\n' >&2; exit 1; }
test -f "$RELEASE_DIR/meta/files.sha256" || { printf 'ERROR missing files manifest\n' >&2; exit 1; }
(
  cd "$RELEASE_DIR/payload"
  shasum -a 256 -c "$RELEASE_DIR/meta/files.sha256"
)

RELEASE_ID="$(jq -r '.release_id' "$RELEASE_DIR/meta/release.json")"
REMOTE_STAGE="$(dirname "$REMOTE_WP")/.hybridautos-releases/$RELEASE_ID/$PHASE"
ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "mkdir -p '$REMOTE_STAGE'"

while IFS= read -r relative_path; do
  [ -n "$relative_path" ] || continue
  case "$relative_path" in
    "$SAFE_PREFIX"*) ;;
    *) printf 'ERROR path outside phase allowlist: %s\n' "$relative_path" >&2; exit 1 ;;
  esac
  case "$relative_path" in
    *'..'*|/*) printf 'ERROR unsafe relative path: %s\n' "$relative_path" >&2; exit 1 ;;
  esac

  local_file="$RELEASE_DIR/payload/$relative_path"
  test -f "$local_file" || { printf 'ERROR payload missing: %s\n' "$relative_path" >&2; exit 1; }
  expected_hash="$(shasum -a 256 "$local_file" | awk '{print $1}')"
  stage_file="$REMOTE_STAGE/$(basename "$relative_path").new"
  target_file="$REMOTE_WP/$relative_path"

  scp -i "$SSH_KEY" -o BatchMode=yes "$local_file" "$REMOTE:$stage_file"
  if [[ "$relative_path" == *.php ]]; then
    ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "php -l '$stage_file'"
  fi
  remote_hash="$(ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "sha256sum '$stage_file'" | awk '{print $1}')"
  test "$remote_hash" = "$expected_hash"
  ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" \
    "mkdir -p '$(dirname "$target_file")' && mv -f '$stage_file' '$target_file'"
  installed_hash="$(ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" "sha256sum '$target_file'" | awk '{print $1}')"
  test "$installed_hash" = "$expected_hash"
  printf 'INSTALLED %s %s\n' "$expected_hash" "$relative_path"
done < "$ALLOWLIST"

ssh -i "$SSH_KEY" -o BatchMode=yes "$REMOTE" \
  "wp --path='$REMOTE_WP' cache flush >/dev/null && wp --path='$REMOTE_WP' eval 'if(function_exists(\"opcache_reset\")){opcache_reset();} echo \"CACHE_PURGED\\n\";'"
printf 'DEPLOY_PHASE_OK environment=%s phase=%s release=%s\n' "$ENVIRONMENT" "$PHASE" "$RELEASE_ID"
```

- [ ] **Step 4: Run the deployer tests**

Run:

```bash
chmod 755 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/deploy-allowlist.sh"
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
bats tests/deploy/test_deploy_allowlist.bats
```

Expected: `4 tests, 0 failures`.

- [ ] **Step 5: Commit and push the deployer before using it**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/deploy-allowlist.sh tests/deploy/test_deploy_allowlist.bats
git commit -m "feat(deploy): add strict phased allow-list deployer"
git push origin fix/lead-reliability-2026-07-15
```

Expected: deploy tooling is reproducible from the private remote repository.

---

### Task 9: Rehearse Compatible Migration, Cache Cutover, Cron, and Normal Rollback on Staging

**Files:**
- Modify staging only through the allow-listed release payload.
- Create outside Git: `/tmp/esper21-crontab-before-lead-worker.txt` on staging.

**Interfaces:**
- Consumes: new and previous release directories plus restored staging from Task 6.
- Produces: proof that old requests survive the migration, new frontend uses cache-busted JavaScript, Beget cron advances the worker heartbeat, and previous code runs on DB schema `1.1.0`.

- [ ] **Step 1: Deploy the new backend to staging before any frontend file**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh test backend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
```

Expected: PHP syntax passes for every PHP file and the final line is `DEPLOY_PHASE_OK environment=test phase=backend release=20260715-lead-reliability-v1`.

- [ ] **Step 2: Trigger the additive migration and verify version `1.1.0`**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html eval 'do_action(\"init\"); echo get_site_option(\"landing_config_db_version\");'"
```

Expected:

```text
1.1.0
```

- [ ] **Step 3: Prove an old cached browser request without `submission_id` still saves**

Run:

```bash
curl -fsS -X POST 'https://esper21.ru/wp-json/landing/v1/lead' \
  --data-urlencode 'name=TEST OLD FORMAT AFTER MIGRATION' \
  --data-urlencode 'phone=+971500009801' \
  --data-urlencode 'pd_consent=1' \
  --data-urlencode 'source_block=https://esper21.ru/' \
  | tee /private/tmp/hybridautos-old-format-response.json
jq -e '.ok == true and (.lead_id | type == "number")' /private/tmp/hybridautos-old-format-response.json
```

Expected: jq exits 0 and response contains a positive numeric `lead_id`.

- [ ] **Step 4: Deploy the cache-busted frontend phase**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh test frontend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
```

Expected: frontend assets install before `functions.php`, followed by `DEPLOY_PHASE_OK environment=test phase=frontend`.

- [ ] **Step 5: Verify a new-format request and idempotent repeat**

Run:

```bash
for attempt in 1 2; do
  curl -fsS -X POST 'https://esper21.ru/wp-json/landing/v1/lead' \
    --data-urlencode 'submission_id=6f1e7a54-3e49-4a7a-93b8-202607150001' \
    --data-urlencode 'name=TEST NEW FORMAT IDEMPOTENT' \
    --data-urlencode 'phone=+971500009802' \
    --data-urlencode 'pd_consent=1' \
    --data-urlencode 'utm_source=google' \
    --data-urlencode 'utm_medium=cpc' \
    --data-urlencode 'gclid=STAGING_DEPLOY_AUDIT' \
    --data-urlencode 'source_block=https://esper21.ru/' \
    > "/private/tmp/hybridautos-new-format-$attempt.json"
done
test "$(jq -r '.lead_id' /private/tmp/hybridautos-new-format-1.json)" = \
  "$(jq -r '.lead_id' /private/tmp/hybridautos-new-format-2.json)"
printf 'STAGING_IDEMPOTENCY_OK lead_id=%s\n' "$(jq -r '.lead_id' /private/tmp/hybridautos-new-format-1.json)"
```

Expected: both requests return the same positive lead ID.

- [ ] **Step 6: Verify every public staging page references a versioned form script whose bytes match the release manifest**

Run:

```bash
for path in / /li-auto/ /zeekr/ /xiaomi/ /lynk-co/ /rox/; do
  html="$(curl -fsS "https://esper21.ru$path")"
  printf '%s' "$html" | grep -Eq 'lead-form\.js\?ver=[0-9a-f]{12,64}'
done
EXPECTED_JS_HASH="$(shasum -a 256 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1/payload/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js" | awk '{print $1}')"
PUBLIC_JS_URL="$(curl -fsS https://esper21.ru/ | grep -Eo "https?://[^\"' ]+/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form\.js\?ver=[0-9a-f]+" | head -n 1)"
test -n "$PUBLIC_JS_URL"
test "$(curl -fsS "$PUBLIC_JS_URL" | shasum -a 256 | awk '{print $1}')" = "$EXPECTED_JS_HASH"
printf 'STAGING_PUBLIC_JS_HASH_OK %s\n' "$EXPECTED_JS_HASH"
```

Expected: all six pages contain a versioned URL and the fetched bytes match the release hash.

- [ ] **Step 7: Install the staging system cron with a marker and preserve the old crontab**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech '
  crontab -l 2>/dev/null > /tmp/esper21-crontab-before-lead-worker.txt || :
  WP_BIN="$(command -v wp)"
  (crontab -l 2>/dev/null | grep -v "# hybridautos-lead-worker" || :; \
   printf "* * * * * /usr/bin/flock -n /tmp/hybridautos-lead-worker.lock %s --path=/home/e/esper21/esper21.ru/public_html landing queue run --quiet # hybridautos-lead-worker\n" "$WP_BIN") | crontab -
  crontab -l | grep "# hybridautos-lead-worker"
'
```

Expected: exactly one cron row with marker `# hybridautos-lead-worker`.

- [ ] **Step 8: Verify heartbeat advance and the queue integration test**

Run:

```bash
BEFORE="$(ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html option get landing_last_worker_run 2>/dev/null || printf 0")"
for poll in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do
  AFTER="$(ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
    "wp --path=/home/e/esper21/esper21.ru/public_html option get landing_last_worker_run 2>/dev/null || printf 0")"
  [ "$AFTER" != "$BEFORE" ] && break
  sleep 5
done
test "$AFTER" != "$BEFORE"
cd "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15"
bash skills/wp-landing-config/tests/integration/test_queue_cron.sh \
  esper21@esper21.beget.tech /home/e/esper21/esper21.ru/public_html
```

Expected: heartbeat changes within 90 seconds; integration test reports delayed retry executed, due queue empty, and two workers produced no duplicate send.

- [ ] **Step 9: Rehearse normal code rollback while leaving DB version `1.1.0` in place**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh test frontend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1"
./deploy/deploy-allowlist.sh test backend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1"
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "test \"\$(wp --path=/home/e/esper21/esper21.ru/public_html option get landing_config_db_version)\" = 1.1.0"
curl -fsS -X POST 'https://esper21.ru/wp-json/landing/v1/lead' \
  --data-urlencode 'name=TEST OLD CODE NEW SCHEMA' \
  --data-urlencode 'phone=+971500009803' \
  --data-urlencode 'pd_consent=1' \
  | jq -e '.ok == true and (.lead_id | type == "number")'
```

Expected: previous code saves a lead on schema `1.1.0`.

- [ ] **Step 10: Restore the new release to staging after rollback rehearsal**

Run:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh test backend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
./deploy/deploy-allowlist.sh test frontend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
```

Expected: staging returns to the new release and all Task 9 checks remain green.

---

### Task 10: Rehearse Full Database Restore with Post-Snapshot Lead and Configuration Merge

**Files:**
- Temporary staging files: `/tmp/hybridautos-rollback-baseline.sql`, `/tmp/hybridautos-post-snapshot-leads.sql`, `/tmp/hybridautos-recovery-state.json`, `/tmp/hybridautos-lead-table-counts-before.tsv`.
- Uses committed utilities: `deploy/wp-cli/export-recovery-state.php` and `deploy/wp-cli/import-recovery-state.php`.

**Interfaces:**
- Consumes: staging schema `1.1.0`, restored production-copy database, and staging outbound guard.
- Produces: proof that a full DB restore can preserve later leads/audit/outbox/status tables and reapply the active Email integration/options without ID drift.

- [ ] **Step 1: Disable staging cron and classify active locks before the rehearsal**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech '
  (crontab -l 2>/dev/null | grep -v "# hybridautos-lead-worker" || :) | crontab -
  wp --path=/home/e/esper21/esper21.ru/public_html landing queue health --format=json
'
```

Expected: no cron marker remains; health output shows zero active `sending` locks or explicitly lists only `unknown` rows that will not be retried.

- [ ] **Step 2: Create a rollback baseline with a deliberately old Email recipient**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html eval '\$ids=get_posts([\"post_type\"=>\"lp_integration\",\"post_status\"=>\"any\",\"posts_per_page\"=>-1,\"fields\"=>\"ids\",\"meta_key\"=>\"_lp_int_adapter_type\",\"meta_value\"=>\"email\"]); if(count(\$ids)!==1){WP_CLI::error(\"expected_one_email_integration\");} \$s=get_post_meta(\$ids[0],\"_lp_int_settings\",true); \$s[\"to\"]=\"pre-restore@example.invalid\"; update_post_meta(\$ids[0],\"_lp_int_settings\",\$s); echo \"BASELINE_EMAIL_SET\\n\";' && \
   wp --path=/home/e/esper21/esper21.ru/public_html db export /tmp/hybridautos-rollback-baseline.sql --add-drop-table"
```

Expected: `BASELINE_EMAIL_SET` and successful database export.

- [ ] **Step 3: Create post-snapshot business data and restore the required live Email recipient**

Run:

```bash
curl -fsS -X POST 'https://esper21.ru/wp-json/landing/v1/lead' \
  --data-urlencode 'submission_id=6f1e7a54-3e49-4a7a-93b8-202607150010' \
  --data-urlencode 'name=TEST POST SNAPSHOT RECOVERY' \
  --data-urlencode 'phone=+971500009810' \
  --data-urlencode 'pd_consent=1' \
  > /private/tmp/hybridautos-post-snapshot.json
POST_SNAPSHOT_LEAD_ID="$(jq -r '.lead_id' /private/tmp/hybridautos-post-snapshot.json)"
test "$POST_SNAPSHOT_LEAD_ID" -gt 0
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html eval '\$ids=get_posts([\"post_type\"=>\"lp_integration\",\"post_status\"=>\"any\",\"posts_per_page\"=>-1,\"fields\"=>\"ids\",\"meta_key\"=>\"_lp_int_adapter_type\",\"meta_value\"=>\"email\"]); \$s=get_post_meta(\$ids[0],\"_lp_int_settings\",true); \$s[\"to\"]=\"elapova00@gmail.com\"; update_post_meta(\$ids[0],\"_lp_int_settings\",\$s); update_option(\"lp_recovery_rehearsal_marker\",\"post-snapshot\"); echo \"CURRENT_EMAIL_SET\\n\";'"
printf 'POST_SNAPSHOT_LEAD_ID=%s\n' "$POST_SNAPSHOT_LEAD_ID"
```

Expected: a positive synthetic lead ID and `CURRENT_EMAIL_SET`.

- [ ] **Step 4: Export the four complete lead-related tables and scoped configuration state**

Run:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/export-recovery-state.php" \
  esper21@esper21.beget.tech:/tmp/export-recovery-state.php
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html db export /tmp/hybridautos-post-snapshot-leads.sql \
     --tables=wp_landing_leads,wp_landing_lead_audit,wp_landing_lead_log,wp_landing_lead_status_log --add-drop-table && \
   wp --path=/home/e/esper21/esper21.ru/public_html eval-file /tmp/export-recovery-state.php /tmp/hybridautos-recovery-state.json && \
   wp --path=/home/e/esper21/esper21.ru/public_html db query --skip-column-names \
     \"SELECT (SELECT COUNT(*) FROM wp_landing_leads),(SELECT COUNT(*) FROM wp_landing_lead_audit),(SELECT COUNT(*) FROM wp_landing_lead_log),(SELECT COUNT(*) FROM wp_landing_lead_status_log)\" \
     > /tmp/hybridautos-lead-table-counts-before.tsv && \
   chmod 600 /tmp/hybridautos-post-snapshot-leads.sql /tmp/hybridautos-recovery-state.json /tmp/hybridautos-lead-table-counts-before.tsv"
```

Expected: lead table export succeeds and WP-CLI prints `RECOVERY_STATE_EXPORTED`.

- [ ] **Step 5: Restore the older baseline, then merge later lead tables and configuration**

Run:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/import-recovery-state.php" \
  esper21@esper21.beget.tech:/tmp/import-recovery-state.php
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html db import /tmp/hybridautos-rollback-baseline.sql && \
   wp --path=/home/e/esper21/esper21.ru/public_html db import /tmp/hybridautos-post-snapshot-leads.sql && \
   wp --path=/home/e/esper21/esper21.ru/public_html eval-file /tmp/import-recovery-state.php /tmp/hybridautos-recovery-state.json && \
   wp --path=/home/e/esper21/esper21.ru/public_html cache flush"
```

Expected: both imports succeed and WP-CLI prints `RECOVERY_STATE_IMPORTED`.

- [ ] **Step 6: Verify the later lead, audit link, queue rows, option marker, and Email recipient survived**

Run:

```bash
POST_SNAPSHOT_LEAD_ID="$(jq -r '.lead_id' /private/tmp/hybridautos-post-snapshot.json)"
BEFORE_COUNTS="$(ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  'cat /tmp/hybridautos-lead-table-counts-before.tsv')"
AFTER_COUNTS="$(ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  'wp --path=/home/e/esper21/esper21.ru/public_html db query --skip-column-names \
  "SELECT (SELECT COUNT(*) FROM wp_landing_leads),(SELECT COUNT(*) FROM wp_landing_lead_audit),(SELECT COUNT(*) FROM wp_landing_lead_log),(SELECT COUNT(*) FROM wp_landing_lead_status_log)"')"
test "$BEFORE_COUNTS" = "$AFTER_COUNTS"
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "wp --path=/home/e/esper21/esper21.ru/public_html eval 'global \$wpdb; \$id=(int)$POST_SNAPSHOT_LEAD_ID; \$leads=\$wpdb->prefix.\"landing_leads\"; \$audit=\$wpdb->prefix.\"landing_lead_audit\"; if((int)\$wpdb->get_var(\$wpdb->prepare(\"SELECT COUNT(*) FROM \".\$leads.\" WHERE id=%d\",\$id))!==1){WP_CLI::error(\"lead_missing\");} if((int)\$wpdb->get_var(\$wpdb->prepare(\"SELECT COUNT(*) FROM \".\$audit.\" WHERE lead_id=%d\",\$id))<1){WP_CLI::error(\"audit_missing\");} if(get_option(\"lp_recovery_rehearsal_marker\")!==\"post-snapshot\"){WP_CLI::error(\"option_missing\");} \$ids=get_posts([\"post_type\"=>\"lp_integration\",\"post_status\"=>\"any\",\"posts_per_page\"=>-1,\"fields\"=>\"ids\",\"meta_key\"=>\"_lp_int_adapter_type\",\"meta_value\"=>\"email\"]); \$s=get_post_meta(\$ids[0],\"_lp_int_settings\",true); if((\$s[\"to\"]??\"\")!==\"elapova00@gmail.com\"){WP_CLI::error(\"email_recipient_wrong\");} echo \"DB_MERGE_REHEARSAL_OK\\n\";'"
```

Expected:

```text
DB_MERGE_REHEARSAL_OK
```

- [ ] **Step 7: Re-enable only the staging cron and leave integrations disabled**

Run the Task 9 Step 7 cron installation command again. Expected: one staging cron marker and no enabled real integration.

- [ ] **Step 8: Remove temporary staging recovery exports after the rehearsal passes**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" esper21@esper21.beget.tech \
  "rm -f /tmp/hybridautos-rollback-baseline.sql \
    /tmp/hybridautos-post-snapshot-leads.sql \
    /tmp/hybridautos-recovery-state.json \
    /tmp/hybridautos-lead-table-counts-before.tsv \
    /tmp/export-recovery-state.php \
    /tmp/import-recovery-state.php \
    /tmp/esper21-before-hybridautos-rehearsal.sql \
    /tmp/wp-config.before-hybridautos-rehearsal.php"
rm -f /private/tmp/hybridautos-post-snapshot.json
printf 'STAGING_RECOVERY_PLAINTEXT_REMOVED\n'
```

Expected:

```text
STAGING_RECOVERY_PLAINTEXT_REMOVED
```

---

### Task 11: Run the Production Preflight and Compatible Two-Phase Deployment

**Files:**
- Create: `/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases/20260715-lead-reliability-v1-production-evidence.json`
- Create outside Git on production: `/tmp/cmoevexs-crontab-before-lead-worker.txt`.

**Interfaces:**
- Consumes: verified remote commits, encrypted backup, restore/rollback rehearsal, immutable GitHub release, and green staging acceptance.
- Produces: production backend and frontend at exact release commits, public cache hash evidence, active system cron, and control leads.

- [ ] **Step 1: Re-run every non-negotiable production gate immediately before deployment**

Run:

```bash
SYSTEM_SHA="$(jq -r '.landing_system_commit' "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases/20260715-lead-reliability-v1.json")"
SITE_SHA="$(jq -r '.site_commit' "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/releases/20260715-lead-reliability-v1.json")"
test "$SYSTEM_SHA" = "$(gh api "repos/neuroboostpr-pixel/landing_system/git/commits/$SYSTEM_SHA" --jq '.sha')"
test "$SITE_SHA" = "$(gh api "repos/neuroboostpr-pixel/hybridautos-ae/git/commits/$SITE_SHA" --jq '.sha')"
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" fetch origin fix/lead-reliability-observability
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /landing_system/.worktrees/lead-reliability-2026-07-15" merge-base --is-ancestor "$SYSTEM_SHA" origin/fix/lead-reliability-observability
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" fetch origin fix/lead-reliability-2026-07-15
git -C "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae" merge-base --is-ancestor "$SITE_SHA" origin/fix/lead-reliability-2026-07-15
test "$(gh repo view neuroboostpr-pixel/hybridautos-ae --json visibility --jq '.visibility')" = PRIVATE
test "$(shasum -a 256 "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/hybridautos-pre-reliability-20260715.tar.gz.enc" | awk '{print $1}')" = \
  "$(jq -r '.sha256' "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/summary.json")"
jq -e '.files_checksum=="passed" and .database_import=="passed" and .outbound_guard=="passed"' \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/release-inputs/restore-rehearsal.json"
printf 'PRODUCTION_PREFLIGHT_OK\n'
```

Expected:

```text
PRODUCTION_PREFLIGHT_OK
```

- [ ] **Step 2: Save the existing production crontab before adding the worker**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  'crontab -l 2>/dev/null > /tmp/cmoevexs-crontab-before-lead-worker.txt || :; chmod 600 /tmp/cmoevexs-crontab-before-lead-worker.txt'
```

Expected: command exits 0 and does not change cron.

- [ ] **Step 3: Deploy the backward-compatible backend only**

Run:

```bash
export HYBRIDAUTOS_PROD_CONFIRM=deploy-20260715-lead-reliability-v1
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh prod backend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
unset HYBRIDAUTOS_PROD_CONFIRM
```

Expected: every installed file hash is printed and final status is `DEPLOY_PHASE_OK environment=prod phase=backend`.

- [ ] **Step 4: Prove an old-format production request saves before frontend cutover**

Run:

```bash
curl -fsS -X POST 'https://hybridautos.ae/wp-json/landing/v1/lead' \
  --data-urlencode 'name=TEST PROD OLD FORMAT CUTOVER' \
  --data-urlencode 'phone=+971500009901' \
  --data-urlencode 'pd_consent=1' \
  --data-urlencode 'utm_source=google' \
  --data-urlencode 'utm_medium=cpc' \
  --data-urlencode 'gclid=PROD_BACKEND_CUTOVER' \
  --data-urlencode 'source_block=https://hybridautos.ae/' \
  > /private/tmp/hybridautos-prod-old-format.json
jq -e '.ok == true and (.lead_id | type == "number")' /private/tmp/hybridautos-prod-old-format.json
```

Expected: a positive production test lead ID. Confirm it is labelled `TEST` before continuing.

- [ ] **Step 5: Deploy the versioned/cache-busted frontend phase**

Run:

```bash
export HYBRIDAUTOS_PROD_CONFIRM=deploy-20260715-lead-reliability-v1
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh prod frontend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1"
unset HYBRIDAUTOS_PROD_CONFIRM
```

Expected: JavaScript/assets install first, `functions.php` last, and final status is `DEPLOY_PHASE_OK environment=prod phase=frontend`.

- [ ] **Step 6: Purge caches and verify anonymous public JS hashes on all six pages**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html cache flush && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html eval 'if(function_exists(\"opcache_reset\")){opcache_reset();} echo \"OPCACHE_RESET_REQUESTED\\n\";'"
EXPECTED_JS_HASH="$(shasum -a 256 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-lead-reliability-v1/payload/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js" | awk '{print $1}')"
for path in / /li-auto/ /zeekr/ /xiaomi/ /lynk-co/ /rox/; do
  html="$(curl -fsS -H 'Cache-Control: no-cache' "https://hybridautos.ae$path")"
  js_url="$(printf '%s' "$html" | grep -Eo "https?://[^\"' ]+/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form\.js\?ver=[0-9a-f]+" | head -n 1)"
  test -n "$js_url"
  test "$(curl -fsS -H 'Cache-Control: no-cache' "$js_url" | shasum -a 256 | awk '{print $1}')" = "$EXPECTED_JS_HASH"
  printf 'PUBLIC_PAGE_JS_OK %s %s\n' "$path" "$EXPECTED_JS_HASH"
done
```

Expected: six `PUBLIC_PAGE_JS_OK` lines with the same release hash.

- [ ] **Step 7: Submit and repeat a new-format production request**

Run:

```bash
for attempt in 1 2; do
  curl -fsS -X POST 'https://hybridautos.ae/wp-json/landing/v1/lead' \
    --data-urlencode 'submission_id=6f1e7a54-3e49-4a7a-93b8-202607150101' \
    --data-urlencode 'name=TEST PROD NEW FORMAT IDEMPOTENT' \
    --data-urlencode 'phone=+971500009902' \
    --data-urlencode 'pd_consent=1' \
    --data-urlencode 'utm_source=google' \
    --data-urlencode 'utm_medium=cpc' \
    --data-urlencode 'gclid=PROD_FRONTEND_CUTOVER' \
    --data-urlencode 'source_block=https://hybridautos.ae/' \
    > "/private/tmp/hybridautos-prod-new-format-$attempt.json"
done
test "$(jq -r '.lead_id' /private/tmp/hybridautos-prod-new-format-1.json)" = \
  "$(jq -r '.lead_id' /private/tmp/hybridautos-prod-new-format-2.json)"
printf 'PRODUCTION_IDEMPOTENCY_OK lead_id=%s\n' "$(jq -r '.lead_id' /private/tmp/hybridautos-prod-new-format-1.json)"
```

Expected: both responses have the same positive lead ID.

- [ ] **Step 8: Install production cron and verify heartbeat**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech '
  WP_BIN="$(command -v wp)"
  (crontab -l 2>/dev/null | grep -v "# hybridautos-lead-worker" || :; \
   printf "* * * * * /usr/bin/flock -n /tmp/hybridautos-lead-worker.lock %s --path=/home/c/cmoevexs/hybridautos.ae/public_html landing queue run --quiet # hybridautos-lead-worker\n" "$WP_BIN") | crontab -
  crontab -l | grep "# hybridautos-lead-worker"
'
BEFORE="$(ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html option get landing_last_worker_run 2>/dev/null || printf 0")"
for poll in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do
  AFTER="$(ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
    "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html option get landing_last_worker_run 2>/dev/null || printf 0")"
  [ "$AFTER" != "$BEFORE" ] && break
  sleep 5
done
test "$AFTER" != "$BEFORE"
printf 'PRODUCTION_CRON_OK heartbeat=%s\n' "$AFTER"
```

Expected: one production cron marker and heartbeat changes within 90 seconds.

- [ ] **Step 9: Run the complete CTA registry/browser acceptance and channel checks**

Run the browser acceptance from the lead-reliability implementation plan for Home, Li Auto, Zeekr, Xiaomi, Lynk & Co, ROX, and every generic/model-specific CTA registry row. Every synthetic lead must show:

```text
WordPress saved: yes
Audit linked: yes
Telegram: success with message_id
Email: accepted; elapova00@gmail.com inbox manually confirmed
Roistat: success
PHP errors: none
Due pending: 0
Stale sending: 0
```

Expected: all rows meet the exact checklist. A single missing channel status blocks completion.

- [ ] **Step 10: Record production evidence without PII**

Create `deploy/releases/20260715-lead-reliability-v1-production-evidence.json` with exact keys and observed non-sensitive values:

```json
{
  "schema": 1,
  "release_id": "20260715-lead-reliability-v1",
  "github_remote_commits_verified": true,
  "fresh_encrypted_backup_verified": true,
  "staging_restore_rehearsal": "passed",
  "staging_code_rollback": "passed",
  "staging_database_merge": "passed",
  "production_old_format_post": "passed",
  "production_new_format_idempotency": "passed",
  "six_page_public_js_hash": "passed",
  "production_cron_heartbeat": "passed",
  "php_errors": "none",
  "paid_traffic_restarted": false
}
```

Commit and push it only after all values are true/passed:

```bash
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
git add deploy/releases/20260715-lead-reliability-v1-production-evidence.json
git commit -m "chore(release): record HybridAutos production deployment evidence"
git push origin fix/lead-reliability-2026-07-15
```

Expected: production evidence is in the private remote repository and contains no names, phones, emails, tokens, or database content.

---

### Task 12: Execute the Tested Rollback Procedure if Any Production Gate Fails

**Files:**
- Uses immutable private GitHub asset: `20260715-pre-reliability-v1.tar.gz`.
- Uses encrypted local current-state backup: `hybridautos-pre-reliability-20260715.tar.gz.enc`.
- Temporary production recovery files: `/tmp/hybridautos-emergency-current.sql`, `/tmp/hybridautos-post-snapshot-leads.sql`, `/tmp/hybridautos-recovery-state.json`.

**Interfaces:**
- Consumes: previous code release, current encrypted backup, recovery-state utilities, and current production database while it is still readable.
- Produces: old compatible code with new additive columns left in place, or a full DB restore followed by post-snapshot data/config merge. Cron remains disabled until manual verification.

- [ ] **Step 1: Stop paid traffic, disable worker cron, and classify active deliveries**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech '
  (crontab -l 2>/dev/null | grep -v "# hybridautos-lead-worker" || :) | crontab -
  wp --path=/home/c/cmoevexs/hybridautos.ae/public_html landing queue health --format=json
'
```

Expected: cron marker absent. Do not continue until all active locks are finished or explicitly classified `unknown`; never reset an ambiguous send to `pending`.

- [ ] **Step 2: Perform normal code rollback in compatible reverse order**

Run:

```bash
export HYBRIDAUTOS_PROD_CONFIRM=deploy-20260715-lead-reliability-v1
cd "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae"
./deploy/deploy-allowlist.sh prod frontend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1"
./deploy/deploy-allowlist.sh prod backend \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1"
unset HYBRIDAUTOS_PROD_CONFIRM
```

Expected: previous frontend and backend hashes are installed; no database import occurs.

- [ ] **Step 3: Verify cache, old public JS hash, additive schema, and one control submission**

Run:

```bash
OLD_JS_HASH="$(shasum -a 256 "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/dist/20260715-pre-reliability-v1/payload/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form.js" | awk '{print $1}')"
PUBLIC_JS_URL="$(curl -fsS -H 'Cache-Control: no-cache' https://hybridautos.ae/ | grep -Eo "https?://[^\"' ]+/wp-content/themes/lp-hibridcars-uae/assets/js/lead-form\.js[^\"' ]*" | head -n 1)"
test "$(curl -fsS -H 'Cache-Control: no-cache' "$PUBLIC_JS_URL" | shasum -a 256 | awk '{print $1}')" = "$OLD_JS_HASH"
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "test \"\$(wp --path=/home/c/cmoevexs/hybridautos.ae/public_html option get landing_config_db_version)\" = 1.1.0"
curl -fsS -X POST 'https://hybridautos.ae/wp-json/landing/v1/lead' \
  --data-urlencode 'name=TEST PROD AFTER CODE ROLLBACK' \
  --data-urlencode 'phone=+971500009999' \
  --data-urlencode 'pd_consent=1' \
  | jq -e '.ok == true and (.lead_id | type == "number")'
```

Expected: old JS hash is public, DB remains `1.1.0`, and the control lead saves. Keep cron disabled until the external channels are reviewed.

- [ ] **Step 4: Before a full DB restore, export the entire current DB, four lead tables, and integration/options state**

Run only when the current DB is readable:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/export-recovery-state.php" \
  cmoevexs@cmoevexs.beget.tech:/tmp/export-recovery-state.php
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html db export /tmp/hybridautos-emergency-current.sql --add-drop-table && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html db export /tmp/hybridautos-post-snapshot-leads.sql \
     --tables=wp_landing_leads,wp_landing_lead_audit,wp_landing_lead_log,wp_landing_lead_status_log --add-drop-table && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html eval-file /tmp/export-recovery-state.php /tmp/hybridautos-recovery-state.json && \
   chmod 600 /tmp/hybridautos-emergency-current.sql /tmp/hybridautos-post-snapshot-leads.sql /tmp/hybridautos-recovery-state.json"
```

Expected: all three exports succeed before any destructive DB action. If the DB is unreadable, stop and escalate; do not pretend post-snapshot contacts are recoverable.

- [ ] **Step 5: Decrypt the fresh backup SQL and upload it for full restore**

Run:

```bash
rm -rf /private/tmp/hybridautos-prod-db-restore-20260715
mkdir -p /private/tmp/hybridautos-prod-db-restore-20260715
BACKUP_PASS="$(security find-generic-password -a "$USER" -s hybridautos-backup-20260715 -w)"
export BACKUP_PASS
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_PASS \
  -in "/Users/kirillbezikov/Documents/Сайт Дубай /backups/2026-07-15_pre_reliability_current/hybridautos-pre-reliability-20260715.tar.gz.enc" \
  | tar -xzf - -C /private/tmp/hybridautos-prod-db-restore-20260715 database/cmoevexs_wp_1.sql database.sha256
unset BACKUP_PASS
cd /private/tmp/hybridautos-prod-db-restore-20260715
shasum -a 256 -c database.sha256
scp -i "$HOME/.ssh/id_ed25519" database/cmoevexs_wp_1.sql \
  cmoevexs@cmoevexs.beget.tech:/tmp/hybridautos-fresh-backup.sql
```

Expected: database checksum reports `OK` before upload.

- [ ] **Step 6: Restore the fresh DB, then replace lead tables with current versions and reapply configuration**

Run:

```bash
scp -i "$HOME/.ssh/id_ed25519" \
  "/Users/kirillbezikov/Documents/Сайт Дубай /hybridautos-ae/deploy/wp-cli/import-recovery-state.php" \
  cmoevexs@cmoevexs.beget.tech:/tmp/import-recovery-state.php
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html db import /tmp/hybridautos-fresh-backup.sql && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html db import /tmp/hybridautos-post-snapshot-leads.sql && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html eval-file /tmp/import-recovery-state.php /tmp/hybridautos-recovery-state.json && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html cache flush"
```

Expected: backup DB import, lead-table merge, and recovery-state import all succeed.

- [ ] **Step 7: Verify the active recipient and manually reconcile ambiguous deliveries before cron restart**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "wp --path=/home/c/cmoevexs/hybridautos.ae/public_html eval '\$ids=get_posts([\"post_type\"=>\"lp_integration\",\"post_status\"=>\"any\",\"posts_per_page\"=>-1,\"fields\"=>\"ids\",\"meta_key\"=>\"_lp_int_adapter_type\",\"meta_value\"=>\"email\"]); if(count(\$ids)!==1){WP_CLI::error(\"expected_one_email_integration\");} \$s=get_post_meta(\$ids[0],\"_lp_int_settings\",true); if((\$s[\"to\"]??\"\")!==\"elapova00@gmail.com\"){WP_CLI::error(\"email_recipient_wrong\");} echo \"EMAIL_RECIPIENT_OK\\n\";' && \
   wp --path=/home/c/cmoevexs/hybridautos.ae/public_html landing queue health --format=json"
```

Expected: `EMAIL_RECIPIENT_OK`; every `sending`/`unknown` row is reviewed. Reinstall cron only after a human confirms no ambiguous external duplicate will be created.

- [ ] **Step 8: Remove plaintext recovery files after the full restore is verified**

Run:

```bash
ssh -i "$HOME/.ssh/id_ed25519" cmoevexs@cmoevexs.beget.tech \
  "rm -f /tmp/hybridautos-emergency-current.sql \
    /tmp/hybridautos-post-snapshot-leads.sql \
    /tmp/hybridautos-recovery-state.json \
    /tmp/hybridautos-fresh-backup.sql \
    /tmp/export-recovery-state.php \
    /tmp/import-recovery-state.php"
rm -rf /private/tmp/hybridautos-prod-db-restore-20260715
test ! -e /private/tmp/hybridautos-prod-db-restore-20260715
printf 'PRODUCTION_RECOVERY_PLAINTEXT_REMOVED\n'
```

Expected:

```text
PRODUCTION_RECOVERY_PLAINTEXT_REMOVED
```

---

## Final Verification

- [ ] Both GitHub repositories report the exact remote SHAs used by the release.
- [ ] `neuroboostpr-pixel/hybridautos-ae` is private.
- [ ] The encrypted backup contains complete files and DB, creates no recurring charge, and leaves no plaintext persistent copy.
- [ ] The backup restored successfully to staging with outbound traffic blocked and PII anonymized.
- [ ] Old code ran against DB version `1.1.0` during rollback rehearsal.
- [ ] New backend accepted an old-format POST before frontend cutover.
- [ ] Public anonymous JS bytes matched the release SHA on all six pages after cache purge.
- [ ] Staging and production cron heartbeats advanced, delayed retry passed, and concurrent workers did not duplicate a send.
- [ ] Full DB rollback rehearsal preserved post-snapshot lead/audit/outbox/status tables and restored `elapova00@gmail.com`.
- [ ] Production evidence contains no PII or secrets.
- [ ] Paid traffic remains stopped until the separately verified analytics gate passes.

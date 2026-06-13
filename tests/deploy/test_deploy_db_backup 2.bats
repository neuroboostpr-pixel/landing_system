#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  DEPLOY="$REPO/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
}

@test "backup happens before rsync" {
  # 'Backup DB' line must appear before 'Sync theme' line
  backup_line=$(grep -n "Backup DB" "$DEPLOY" | head -n1 | cut -d: -f1)
  sync_line=$(grep -n "Sync theme" "$DEPLOY" | head -n1 | cut -d: -f1)
  [ -n "$backup_line" ]
  [ -n "$sync_line" ]
  [ "$backup_line" -lt "$sync_line" ]
}

@test "backup uses wp db export" {
  run grep -q "db export" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "backup is downloaded via scp" {
  run grep -qE "scp.*backup.*\.sql" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "backup saved to 09_ДЕПЛОЙ/backups dir" {
  run grep -q "09_ДЕПЛОЙ/backups" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "remote backup file is removed after download" {
  run grep -qE "rm -f.*backup.*\.sql" "$DEPLOY"
  [ "$status" -eq 0 ]
}

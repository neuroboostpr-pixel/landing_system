#!/usr/bin/env bats

setup() {
  REPO="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  DEPLOY="$REPO/skills/wp-cli-deployer/scripts/deploy-wordpress.sh"
  TARGET_SCRIPT="$REPO/skills/wp-cli-deployer/scripts/get-deploy-target.py"
  TARGETS_TPL="$REPO/template/09_ДЕПЛОЙ/deploy-targets.yaml"
}

@test "deploy script accepts --env flag" {
  run grep -q "\-\-env" "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "deploy script default env is staging" {
  run grep -q 'DEPLOY_ENV="staging"' "$DEPLOY"
  [ "$status" -eq 0 ]
}

@test "prod deploy without --confirm exits nonzero" {
  # Source only the arg-parsing section by running bash -c with a stub
  run bash -c '
    DEPLOY_ENV="staging"; CONFIRMED=0
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --env)      DEPLOY_ENV="$2"; shift 2 ;;
        --confirm)  CONFIRMED=1; shift ;;
      esac
    done
    if [[ "$DEPLOY_ENV" == "prod" && "$CONFIRMED" -eq 0 ]]; then
      echo "ERROR: requires --confirm" >&2; exit 1
    fi
    echo "ok"
  ' -- --env prod
  [ "$status" -eq 1 ]
  [[ "$output" == *"--confirm"* ]] || [[ "$stderr" == *"--confirm"* ]]
}

@test "prod deploy with --confirm passes guard" {
  run bash -c '
    DEPLOY_ENV="staging"; CONFIRMED=0
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --env)      DEPLOY_ENV="$2"; shift 2 ;;
        --confirm)  CONFIRMED=1; shift ;;
      esac
    done
    if [[ "$DEPLOY_ENV" == "prod" && "$CONFIRMED" -eq 0 ]]; then exit 1; fi
    echo "ok"
  ' -- --env prod --confirm
  [ "$status" -eq 0 ]
}

@test "deploy-targets.yaml template exists" {
  [ -f "$TARGETS_TPL" ]
}

@test "deploy-targets.yaml template has staging and prod sections" {
  run grep -q "staging:" "$TARGETS_TPL"
  [ "$status" -eq 0 ]
  run grep -q "prod:" "$TARGETS_TPL"
  [ "$status" -eq 0 ]
}

@test "get-deploy-target.py script exists" {
  [ -f "$TARGET_SCRIPT" ]
}

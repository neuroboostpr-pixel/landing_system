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

@test "template/README.md exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/README.md"
}

@test "template/README.md has Quick Start section" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/README.md" "Quick Start"
}

@test "template/.gitignore exists" {
  assert_file_exists "$LANDING_SYSTEM_ROOT/template/.gitignore"
}

@test "template/.gitignore ignores .env" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.gitignore" ".env"
}

@test "template/.gitignore ignores versions/" {
  assert_file_contains "$LANDING_SYSTEM_ROOT/template/.gitignore" "versions"
}

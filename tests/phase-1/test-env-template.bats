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

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

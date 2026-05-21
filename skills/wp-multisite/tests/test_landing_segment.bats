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
echo "CURL $*" >> "$BATS_TMPDIR/curl_calls.log"
case "$*" in
    *getSubdomainList*) echo '{"status":"success","answer":{"status":"success","result":[]}}' ;;
    *addSubdomainVirtual*) echo '{"status":"success","answer":{"status":"success","result":777}}' ;;
    *) echo '{"status":"success","answer":{"status":"success","result":true}}' ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
# wp site create returns a numeric blog_id (--porcelain)
if [[ "$*" == *"site create"* ]] && [[ "$*" == *"--porcelain"* ]]; then
    echo "5"
else
    echo "OK"
fi
MOCK
    chmod +x "$MOCK_DIR/ssh"

    rm -f "$BATS_TMPDIR/curl_calls.log" "$BATS_TMPDIR/ssh_calls.log"
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
    grep -q "addSubdomainVirtual" "$BATS_TMPDIR/curl_calls.log"
}

@test "landing-segment runs wp site create" {
    run bash "$SCRIPT" "$PROJECT_DIR" "family"
    [ "$status" -eq 0 ]
    grep -q "site create --slug=family" "$BATS_TMPDIR/ssh_calls.log"
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

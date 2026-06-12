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
echo "CURL $*" >> "$BATS_TMPDIR/curl_calls.log"
case "$*" in
    *getSubdomainList*) echo '{"status":"success","answer":{"status":"success","result":[]}}' ;;
    *addSubdomainVirtual*) echo '{"status":"success","answer":{"status":"success","result":888}}' ;;
    *) echo '{"status":"success","answer":{"status":"success","result":true}}' ;;
esac
MOCK
    chmod +x "$MOCK_DIR/curl"
    cat > "$MOCK_DIR/ssh" <<'MOCK'
#!/bin/bash
echo "SSH $*" >> "$BATS_TMPDIR/ssh_calls.log"
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

    rm -f "$BATS_TMPDIR/curl_calls.log" "$BATS_TMPDIR/ssh_calls.log"
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
    grep -q "site create --slug=russian-test" "$BATS_TMPDIR/ssh_calls.log"
}

@test "clone-subsite copies pages from source to dest" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian-test"
    [ "$status" -eq 0 ]
    # Each page from source -> post get + post create on dest
    grep -q "post list --post_type=page" "$BATS_TMPDIR/ssh_calls.log"
    # post create reads content via stdin (`-` as positional arg, before flags)
    grep -q "post create - --post_type=page" "$BATS_TMPDIR/ssh_calls.log"
}

@test "clone-subsite appends new segment to state" {
    run bash "$SCRIPT" "$PROJECT_DIR" "russian" "russian-test"
    [ "$status" -eq 0 ]
    grep -q "slug: russian-test" "$PROJECT_DIR/.landing-state.yaml"
}

#!/usr/bin/env bats

# Tests for content extraction from prototype.yaml (BUG-001 fix)

load test_helper

@test "validate-content-extraction.py script exists and is executable" {
    [ -x "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" ]
}

@test "check-no-lorem: passes when content has real text" {
    # Create a temp content.md with real text (no Lorem)
    temp_file=$(mktemp)
    cat > "$temp_file" <<'EOF'
# Текстовый контент

## 1. Hero Section

### Заголовок (h1)
"The Skills You Need, The Success You Deserve"

### Описание
"Join thousands of professionals mastering new skills..."
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$temp_file" --check-no-lorem
    status=$?
    rm -f "$temp_file"
    [ $status -eq 0 ]
}

@test "check-no-lorem: fails when content has Lorem ipsum" {
    temp_file=$(mktemp)
    cat > "$temp_file" <<'EOF'
# Test Content

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$temp_file" --check-no-lorem
    status=$?
    rm -f "$temp_file"
    [ $status -ne 0 ]
}

@test "check-no-lorem: fails when content has 'description goes here'" {
    temp_file=$(mktemp)
    cat > "$temp_file" <<'EOF'
# Test Content

Section 1
description goes here
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$temp_file" --check-no-lorem
    status=$?
    rm -f "$temp_file"
    [ $status -ne 0 ]
}

@test "check-sections-match: passes when section counts match" {
    # Create temp prototype.yaml
    proto_file=$(mktemp)
    cat > "$proto_file" <<'EOF'
sections:
  - id: "header"
    name: "Header"
  - id: "hero"
    name: "Hero"
  - id: "footer"
    name: "Footer"
EOF

    # Create temp content.md with 3 H2 headers
    content_file=$(mktemp)
    cat > "$content_file" <<'EOF'
# Content

## 1. Header
Text

## 2. Hero
Text

## 3. Footer
Text
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$content_file" "$proto_file" --check-sections-match
    status=$?
    rm -f "$proto_file" "$content_file"
    [ $status -eq 0 ]
}

@test "check-sections-match: fails when section counts don't match" {
    proto_file=$(mktemp)
    cat > "$proto_file" <<'EOF'
sections:
  - id: "header"
    name: "Header"
  - id: "hero"
    name: "Hero"
EOF

    content_file=$(mktemp)
    cat > "$content_file" <<'EOF'
# Content

## 1. Header
Text

## 2. Hero
Text

## 3. Footer
Text
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$content_file" "$proto_file" --check-sections-match
    status=$?
    rm -f "$proto_file" "$content_file"
    [ $status -ne 0 ]
}

@test "check-log-passed: passes when log has ✅ SUCCESS marker" {
    log_file=$(mktemp)
    cat > "$log_file" <<'EOF'
# Extraction Log

**Status:** ✅ SUCCESS

All blocks extracted successfully.
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$log_file" --check-log-passed
    status=$?
    rm -f "$log_file"
    [ $status -eq 0 ]
}

@test "check-log-passed: fails when log doesn't have SUCCESS marker" {
    log_file=$(mktemp)
    cat > "$log_file" <<'EOF'
# Extraction Log

Some extraction happened but failed.
EOF

    python3 "$PROJECT_ROOT/skills/landing-system/scripts/validate-content-extraction.py" \
        "$log_file" --check-log-passed
    status=$?
    rm -f "$log_file"
    [ $status -ne 0 ]
}

@test "gate-check passes for stage 07_content when all files valid" {
    # Use neurokreator project which should have valid content extraction
    project="$HOME/Lendings/neurokreator"
    if [ ! -d "$project" ]; then
        skip "neurokreator project not found"
    fi

    bash "$PROJECT_ROOT/scripts/gate-check.sh" --stage 07_content --project "$project"
    [ $? -eq 0 ]
}

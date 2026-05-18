#!/usr/bin/env bats

load 'helpers.bash'

@test "post-commit hook: НЕ запускает compile если не менялись источники" {
    tmpdir=$(mktemp -d)
    cd "$tmpdir"
    git init -q
    git config user.email "test@test.local"
    git config user.name "Test"

    # Создать .githooks/post-commit (копия с моком compile)
    mkdir -p .githooks
    cat > .githooks/post-commit <<'HOOK'
#!/bin/bash
SOURCE_PATTERN='^(agents/|skills/.*/SKILL\.md|commands/|template/.*/README\.md|docs/standards/)'
CHANGED="$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null || true)"
if ! echo "$CHANGED" | grep -qE "$SOURCE_PATTERN"; then
    exit 0
fi
echo "COMPILE_WOULD_RUN" > "/tmp/wiki-hook-test-$$.flag"
HOOK
    chmod +x .githooks/post-commit

    # Сначала корневой коммит без хука, потом включаем хук
    echo "seed" > seed.txt
    git add seed.txt
    git commit -q -m "seed" 2>/dev/null
    git config core.hooksPath .githooks

    # Коммит файла НЕ из источников
    echo "x" > unrelated.txt
    git add unrelated.txt
    rm -f /tmp/wiki-hook-test-*.flag
    git commit -q -m "noise" 2>/dev/null
    [ ! -f /tmp/wiki-hook-test-*.flag ]
}

@test "post-commit hook: ЗАПУСКАЕТ compile если меняется agents/" {
    tmpdir=$(mktemp -d)
    cd "$tmpdir"
    git init -q
    git config user.email "test@test.local"
    git config user.name "Test"

    mkdir -p .githooks agents
    cat > .githooks/post-commit <<'HOOK'
#!/bin/bash
SOURCE_PATTERN='^(agents/|skills/.*/SKILL\.md|commands/|template/.*/README\.md|docs/standards/)'
CHANGED="$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null || true)"
if ! echo "$CHANGED" | grep -qE "$SOURCE_PATTERN"; then
    exit 0
fi
echo "COMPILE_WOULD_RUN" > /tmp/wiki-hook-test.flag
HOOK
    chmod +x .githooks/post-commit

    # Корневой коммит без хука (чтобы diff-tree HEAD работал на следующем коммите)
    echo "seed" > seed.txt
    git add seed.txt
    git commit -q -m "seed" 2>/dev/null
    git config core.hooksPath .githooks

    rm -f /tmp/wiki-hook-test.flag
    echo "test agent" > agents/test.md
    git add agents/test.md
    git commit -q -m "feat: add agent" 2>/dev/null
    [ -f /tmp/wiki-hook-test.flag ]
    [ "$(cat /tmp/wiki-hook-test.flag)" = "COMPILE_WOULD_RUN" ]
    rm -f /tmp/wiki-hook-test.flag
}

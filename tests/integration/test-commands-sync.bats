#!/usr/bin/env bats

setup() {
    REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    export REPO_ROOT
}

@test "every commands/*.md has a matching .claude/commands/*.md with same content" {
    cd "$REPO_ROOT"
    for f in commands/*.md; do
        base=$(basename "$f")
        runtime=".claude/commands/$base"
        [ -f "$runtime" ] || {
            echo "MISSING runtime copy: $base" >&2
            false
        }
        diff -q "$f" "$runtime" > /dev/null 2>&1 || {
            echo "DIVERGED: $base" >&2
            diff -u "$f" "$runtime" | head -30 >&2
            false
        }
    done
}

@test "no orphan files in .claude/commands/ that aren't in commands/" {
    cd "$REPO_ROOT"
    for f in .claude/commands/*.md; do
        base=$(basename "$f")
        # Ignore files that are intentionally runtime-only (document them)
        case "$base" in
            # add legitimate runtime-only exceptions here, e.g.:
            # local-only-command.md) continue ;;
            *) ;;
        esac
        [ -f "commands/$base" ] || {
            echo "ORPHAN runtime file: $base (no source in commands/)" >&2
            false
        }
    done
}

@test "scripts/sync-commands.sh exists and is executable" {
    [ -x "$REPO_ROOT/scripts/sync-commands.sh" ]
}

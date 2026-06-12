#!/usr/bin/env bash
# Sync commands/*.md (source of truth) → .claude/commands/*.md (Claude Code runtime).
# Source: commands/ — the version humans edit, lives in git, in wiki sources.
# Target: .claude/commands/ — what Claude Code actually executes at runtime.
#
# Run automatically by .githooks/post-commit (after wiki sync).
# Can also be invoked manually: bash scripts/sync-commands.sh [--check]
#
# Modes:
#   default     : copy all source → runtime, report changes
#   --check     : exit 1 if any divergence (CI mode)

set -Eeuo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

SRC_DIR="commands"
DST_DIR=".claude/commands"
MODE="${1:-sync}"

if [ ! -d "$SRC_DIR" ]; then
    echo "❌ Source $SRC_DIR/ missing" >&2
    exit 2
fi

mkdir -p "$DST_DIR"

changed=0
missing=0
orphans=0

# Step 1: For each source file, ensure runtime mirror exists with same content
for src in "$SRC_DIR"/*.md; do
    [ -f "$src" ] || continue
    base=$(basename "$src")
    dst="$DST_DIR/$base"

    if [ ! -f "$dst" ]; then
        if [ "$MODE" = "--check" ]; then
            echo "❌ MISSING runtime: $base" >&2
            missing=$((missing+1))
        else
            cp "$src" "$dst"
            echo "✅ Created: $dst"
            changed=$((changed+1))
        fi
    elif ! diff -q "$src" "$dst" > /dev/null 2>&1; then
        if [ "$MODE" = "--check" ]; then
            echo "❌ DIVERGED: $base" >&2
            missing=$((missing+1))
        else
            cp "$src" "$dst"
            echo "🔄 Updated: $dst"
            changed=$((changed+1))
        fi
    fi
done

# Step 2: Report orphans (files in runtime with no source) — warn but don't auto-delete
for dst in "$DST_DIR"/*.md; do
    [ -f "$dst" ] || continue
    base=$(basename "$dst")
    src="$SRC_DIR/$base"
    if [ ! -f "$src" ]; then
        echo "⚠️  ORPHAN runtime (no source): $base — consider deleting or moving to commands/" >&2
        orphans=$((orphans+1))
    fi
done

if [ "$MODE" = "--check" ]; then
    if [ "$missing" -gt 0 ]; then
        echo "❌ $missing divergence(s) found. Run 'bash scripts/sync-commands.sh' to fix." >&2
        exit 1
    fi
    if [ "$orphans" -gt 0 ]; then
        echo "⚠️  $orphans orphan(s) — manual action required." >&2
        # don't exit 1 on orphans — they may be intentional
    fi
    echo "✅ commands/ and .claude/commands/ in sync"
    exit 0
fi

if [ "$changed" -gt 0 ]; then
    echo "Synced $changed file(s) from $SRC_DIR/ to $DST_DIR/"
fi
exit 0

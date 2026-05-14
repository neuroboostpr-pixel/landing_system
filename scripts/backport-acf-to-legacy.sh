#!/usr/bin/env bash
# Backport stage-08 ACF/Gutenberg artifacts onto a legacy project.
# Usage: backport-acf-to-legacy.sh <project> [--dry-run] [--force]
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:?usage: backport-acf-to-legacy.sh <project> [--dry-run] [--force]}"
shift || true

DRY_RUN=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        --force)   FORCE=1 ;;
    esac
done

[ -d "$PROJECT" ] || { echo "❌ project dir not found: $PROJECT" >&2; exit 1; }

# 1. Refuse without --force if acf-fields.json exists
ACF="$PROJECT/08_КОД/acf-fields.json"
if [ "$DRY_RUN" = "0" ] && [ "$FORCE" = "0" ] && [ -f "$ACF" ]; then
    echo "❌ $ACF already exists. Use --force to regenerate." >&2
    exit 1
fi

# 2. Validate content can be parsed (fail fast)
python "$REPO_ROOT/scripts/lib/content_parser.py" "$PROJECT/07_КОНТЕНТ/final-copy.md" >/dev/null || {
    echo "❌ content_parser failed — fix final-copy.md first" >&2
    exit 1
}

# 3. Dry-run mode
if [ "$DRY_RUN" = "1" ]; then
    python "$REPO_ROOT/scripts/generate-wp-blocks.py" --project "$PROJECT" --dry-run
    exit 0
fi

# 4. Backup
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="$PROJECT/.backport-backup-$TS"
mkdir -p "$BACKUP"
for f in "$PROJECT/08_КОД/wp-theme/functions.php" "$ACF"; do
    [ -f "$f" ] && cp "$f" "$BACKUP/" || true
done
echo "  backup → $BACKUP"

# 5. Run the orchestrator
python "$REPO_ROOT/scripts/generate-wp-blocks.py" --project "$PROJECT" || {
    echo "❌ generate-wp-blocks failed" >&2
    exit 1
}

# 6. Verify gate passes (skip on --force; caller already accepts responsibility)
if [ "$FORCE" = "0" ]; then
    bash "$REPO_ROOT/scripts/gate-check.sh" --stage 08_build --project "$PROJECT" --auto || {
        echo "❌ Generated artifacts but gate still fails — investigate $BACKUP for rollback" >&2
        exit 1
    }
fi

# 7. Remove legacy marker
STATE="$PROJECT/.landing-state.yaml"
if [ -f "$STATE" ] && grep -q "^legacy: true" "$STATE"; then
    grep -v "^legacy: true" "$STATE" > "$STATE.tmp" && mv "$STATE.tmp" "$STATE"
fi

echo "✓ Backport complete for $(basename "$PROJECT"). Review generated files, then deploy."

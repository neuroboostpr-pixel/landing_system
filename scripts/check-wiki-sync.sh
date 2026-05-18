#!/bin/bash
# scripts/check-wiki-sync.sh
# Проверяет что hash источников совпадает с записями в wiki/.cache.json.
# Exit 0 — синхрон, exit 1 — есть desync.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

CACHE="wiki/.cache.json"
if [ ! -f "$CACHE" ]; then
    echo "❌ wiki/.cache.json не найден — wiki не была собрана."
    echo "   Запусти: python3 -m scripts.wiki.compile --source-mode=system"
    exit 1
fi

# Получить список источников (те же что в config.py)
SOURCES=(
    "agents/*.md"
    "skills/*/SKILL.md"
    "commands/*.md"
    "template/*/README.md"
    "docs/standards/*.md"
    "block-library/*/*/meta.yaml"
    "block-library/_patterns/*/meta.yaml"
    "block-library/_styles/*/README.md"
    "config/*.yaml"
    "docs/SETUP.md"
    "docs/ПЛАН-ДОРАБОТОК.md"
    "docs/BACKLOG.md"
    "docs/photo-selection-guide.md"
    "docs/superpowers/specs/*.md"
    "docs/superpowers/plans/*.md"
    "docs/superpowers/DOKRUTKA-system.md"
    "tests/*/README.md"
    "presets/*.md"
    "presets/*.yaml"
    "scripts/*.doc.md"
    "scripts/*/*.doc.md"
    "scripts/*/*/*.doc.md"
)

DESYNC=0
DESYNC_FILES=()
for pattern in "${SOURCES[@]}"; do
    for f in $pattern; do
        [ -f "$f" ] || continue
        rel="$f"
        current_hash=$(shasum -a 256 "$f" | cut -d' ' -f1)
        cached_hash=$(python3 -c "import json,sys; c=json.load(open('$CACHE')); print(c.get('$rel',''))" 2>/dev/null)
        if [ "$current_hash" != "$cached_hash" ]; then
            DESYNC=1
            DESYNC_FILES+=("$rel")
        fi
    done
done

if [ "$DESYNC" = "1" ]; then
    echo "❌ Wiki НЕ В СИНХРОНЕ. Источники изменились но wiki не пересобрана:"
    for f in "${DESYNC_FILES[@]}"; do echo "   - $f"; done
    echo ""
    echo "Фикс: python3 -m scripts.wiki.compile --source-mode=system"
    echo "      git add wiki/ && git commit -m 'chore(wiki): manual resync'"
    exit 1
fi

echo "✅ Wiki в синхроне с источниками."
exit 0

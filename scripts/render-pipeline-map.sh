#!/usr/bin/env bash
# render-pipeline-map.sh — Render Mermaid pipeline map from .landing-state.yaml.
#
# Inspired by Tencent Agent-Memory paper finding #2 (Mermaid task map reduces
# agent drift in 30+ step workflows). We use it as a visible carto for both
# agent and user — single source of truth for "where are we, what's left".
#
# Usage:
#   render-pipeline-map.sh <project>/.landing-state.yaml [--write-wiki]
#
# Default: outputs Mermaid + status to stdout.
# With --write-wiki: ALSO writes the same output to <project>/wiki/pipeline-map.md
# so the latest map becomes part of the project's wiki index.

set -uo pipefail

STATE_FILE=""
WRITE_WIKI=0

while [ $# -gt 0 ]; do
    case "$1" in
        --write-wiki) WRITE_WIKI=1; shift ;;
        -*) echo "ERROR: unknown flag $1" >&2; exit 2 ;;
        *) STATE_FILE="$1"; shift ;;
    esac
done

if [ -z "$STATE_FILE" ] || [ ! -f "$STATE_FILE" ]; then
    echo "ERROR: usage: render-pipeline-map.sh <path-to-.landing-state.yaml> [--write-wiki]" >&2
    exit 2
fi

if ! command -v yq >/dev/null 2>&1; then
    echo "❌ yq not installed (need mikefarah/yq). brew install yq" >&2
    exit 3
fi

# Pipeline order — must match gate-check.sh
PIPELINE_ORDER=(
    "00_brief" "01_context" "01a_niche_analysis" "02_assets" "03_references"
    "04_brand" "05_design" "06_stack" "07_content" "07a_prototype"
    "07b_wireframe" "07c_composed" "07d_photos" "07e_visuals" "07f_composed_final"
    "08_build" "08b_style" "10_qa" "09_deploy" "11_analytics" "12_seo"
)

# Short human-readable labels
declare -A LABELS=(
    ["00_brief"]="Бриф"
    ["01_context"]="Контекст"
    ["01a_niche_analysis"]="Анализ ниши"
    ["02_assets"]="Материалы"
    ["03_references"]="Референсы"
    ["04_brand"]="Бренд"
    ["05_design"]="Дизайн-система"
    ["06_stack"]="Стек"
    ["07_content"]="Контент"
    ["07a_prototype"]="Прототип"
    ["07b_wireframe"]="Wireframe"
    ["07c_composed"]="Compose v1"
    ["07d_photos"]="Фото"
    ["07e_visuals"]="Иконки/чарты"
    ["07f_composed_final"]="Compose final"
    ["08_build"]="WP-сборка"
    ["08b_style"]="Style polish"
    ["10_qa"]="QA"
    ["09_deploy"]="Деплой"
    ["11_analytics"]="Аналитика"
    ["12_seo"]="SEO"
)

render_map() {
# Mermaid class definitions (visual states)
echo '```mermaid'
echo 'flowchart LR'
echo '  classDef approved fill:#22c55e,stroke:#15803d,color:#fff;'
echo '  classDef inprogress fill:#f59e0b,stroke:#b45309,color:#fff;'
echo '  classDef failed fill:#ef4444,stroke:#b91c1c,color:#fff;'
echo '  classDef locked fill:#e5e7eb,stroke:#9ca3af,color:#374151;'
echo '  classDef na fill:#f3f4f6,stroke:#d1d5db,color:#9ca3af,stroke-dasharray: 3 3;'
echo ''

# Render nodes
prev=""
for stage in "${PIPELINE_ORDER[@]}"; do
    status="$(yq -r ".stages.\"$stage\".status // \"locked\"" "$STATE_FILE" 2>/dev/null)"
    label="${LABELS[$stage]:-$stage}"
    node_id="${stage//[^a-zA-Z0-9_]/_}"

    # Visual marker by status
    case "$status" in
        approved)    icon="✓" ; class="approved" ;;
        in_progress) icon="▶" ; class="inprogress" ;;
        failed)      icon="✗" ; class="failed" ;;
        n/a)         icon="—" ; class="na" ;;
        *)           icon="○" ; class="locked" ;;
    esac

    echo "  ${node_id}[\"${icon} ${label}<br/><small>${stage}</small>\"]:::${class}"

    if [ -n "$prev" ]; then
        echo "  ${prev} --> ${node_id}"
    fi
    prev="$node_id"
done

echo '```'
echo ''

# Plain-text summary
echo '## Статус этапов'
echo ''
approved_count=0
inprogress_count=0
locked_count=0
na_count=0
failed_count=0

for stage in "${PIPELINE_ORDER[@]}"; do
    status="$(yq -r ".stages.\"$stage\".status // \"locked\"" "$STATE_FILE" 2>/dev/null)"
    case "$status" in
        approved)    approved_count=$((approved_count+1)) ;;
        in_progress) inprogress_count=$((inprogress_count+1)) ;;
        failed)      failed_count=$((failed_count+1)) ;;
        n/a)         na_count=$((na_count+1)) ;;
        *)           locked_count=$((locked_count+1)) ;;
    esac
done

total=${#PIPELINE_ORDER[@]}
actionable=$((total - na_count))

echo "- ✅ Approved: ${approved_count} / ${actionable}"
echo "- ▶ In progress: ${inprogress_count}"
echo "- ✗ Failed: ${failed_count}"
echo "- ○ Locked: ${locked_count}"
echo "- — Not applicable: ${na_count}"
echo ''

# Next actionable stage
echo '## Следующий шаг'
echo ''
next=""
for stage in "${PIPELINE_ORDER[@]}"; do
    status="$(yq -r ".stages.\"$stage\".status // \"locked\"" "$STATE_FILE" 2>/dev/null)"
    if [ "$status" = "in_progress" ]; then
        next="$stage"
        echo "Текущий этап: **${stage}** — ${LABELS[$stage]:-$stage} (in_progress, нужно довести до approved)"
        break
    fi
done

if [ -z "$next" ]; then
    for stage in "${PIPELINE_ORDER[@]}"; do
        status="$(yq -r ".stages.\"$stage\".status // \"locked\"" "$STATE_FILE" 2>/dev/null)"
        if [ "$status" = "locked" ]; then
            next="$stage"
            echo "Следующий этап: **${stage}** — ${LABELS[$stage]:-$stage} (locked, запусти gate-check)"
            break
        fi
    done
fi

if [ -z "$next" ]; then
    echo "Все actionable-этапы закрыты. Проект готов."
fi
}

# Always print to stdout
render_map

# Optionally also write to project wiki
if [ "$WRITE_WIKI" = "1" ]; then
    PROJECT_DIR="$(cd "$(dirname "$STATE_FILE")" && pwd)"
    WIKI_DIR="$PROJECT_DIR/wiki"
    mkdir -p "$WIKI_DIR"
    WIKI_FILE="$WIKI_DIR/pipeline-map.md"
    {
        echo "<!-- AUTO-GENERATED by scripts/render-pipeline-map.sh — DO NOT EDIT BY HAND -->"
        echo "<!-- Source: $(basename "$STATE_FILE") | Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ) -->"
        echo ""
        echo "# Pipeline Map — $(basename "$PROJECT_DIR")"
        echo ""
        echo "Карта прогресса проекта. Обновляется каждым прогоном orchestrator-а"
        echo "(см. \`docs/standards/stage-execution-protocol.md\`)."
        echo ""
        render_map
    } > "$WIKI_FILE"
    echo "" >&2
    echo "📝 Wiki map updated: $WIKI_FILE" >&2
fi

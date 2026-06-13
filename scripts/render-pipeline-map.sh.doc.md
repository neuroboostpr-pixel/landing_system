---
type: script
name: render-pipeline-map
language: bash
sources: ["scripts/render-pipeline-map.sh"]
updated: 2026-05-18
---

# render-pipeline-map.sh

render-pipeline-map.sh — Render Mermaid pipeline map from .landing-state.yaml.

Inspired by Tencent Agent-Memory paper finding #2 (Mermaid task map reduces
agent drift in 30+ step workflows). We use it as a visible carto for both
agent and user — single source of truth for "where are we, what's left".

Usage:
render-pipeline-map.sh <project>/.landing-state.yaml [--write-wiki]

Default: outputs Mermaid + status to stdout.
With --write-wiki: ALSO writes the same output to <project>/wiki/pipeline-map.md
so the latest map becomes part of the project's wiki index.

## Источник

- `scripts/render-pipeline-map.sh`

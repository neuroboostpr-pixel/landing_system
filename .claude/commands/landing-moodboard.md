---
description: Generate or regenerate the visual moodboard for a landing project (stage 03). Run within a landing project folder after references are approved.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-moodboard

Run within a landing project after references are approved in `03_РЕФЕРЕНСЫ/index.yaml`.

## What I do

1. Invoke `moodboard-composer` agent.
2. Render `03_РЕФЕРЕНСЫ/moodboard.html` from approved references in `index.yaml`.
3. **HARD GATE**: show the preview path, wait for user approval before proceeding to style extraction.

## Output

- `03_РЕФЕРЕНСЫ/moodboard.html` — visual moodboard HTML preview

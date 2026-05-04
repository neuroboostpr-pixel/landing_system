---
description: Collect and curate visual references for a landing project (stage 03). Run within a landing project folder after stage 01 is complete.
allowed-tools: Bash, Read, Write, Edit, Glob
---

# /landing-references

Run within a landing project at any time after stage 01.

## What I do

1. Invoke `references-curator` agent to collect and tag visual references.
2. Maintain `03_РЕФЕРЕНСЫ/index.yaml` with status (`candidate` / `approved` / `rejected`) for each reference.
3. After user selects approved references, render `03_РЕФЕРЕНСЫ/moodboard.html` via `moodboard-composer`.
4. **HARD GATE**: present `moodboard.html` path, wait for explicit approval before continuing to stage 04.

## Usage

Run: `/landing-references`

Then follow the agent prompts to add reference URLs or files.

## Output

- `03_РЕФЕРЕНСЫ/index.yaml` — reference registry
- `03_РЕФЕРЕНСЫ/moodboard.html` — visual moodboard preview

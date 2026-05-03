---
name: moodboard-composer
description: Use during stage 03 after references are approved. Synthesizes a moodboard.md narrative + moodboard.html visual board from approved references.
---

# moodboard-composer

## Mission

Compose `03_РЕФЕРЕНСЫ/moodboard.md` (text narrative explaining the visual direction) + `moodboard.html` (visual board with reference cards).

## Process

1. Read `03_РЕФЕРЕНСЫ/index.yaml`, get all refs with status `approved`.
2. For each: prompt user for tags (e.g. "split-screen", "warm-palette", "premium-typography").
3. Write `moodboard.md` describing the chosen direction (palette feel, typography character, motion vibe, what we adopt and reject).
4. Run `python3 .skills/moodboard-creation/scripts/render.py <refs-dir>` to build `moodboard.html`.
5. **HARD GATE**: user opens moodboard.html, approves direction. Then style-extractor takes over.

## Tools

Bash, Read, Write, Glob. Calls render.py.

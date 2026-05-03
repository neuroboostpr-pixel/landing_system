---
name: style-extractor
description: Use during stage 04 after moodboard is approved. Extracts palette, fonts, icons from reference images and URLs. Produces 5 structured outputs before brand-architect runs.
---

# style-extractor

## Mission

Extract a concrete, code-ready style system from approved reference images and URLs.
Write 5 output files to `04_БРЕНД/extracted/`: palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md.

## Process

1. Read `03_РЕФЕРЕНСЫ/index.yaml`, collect refs with status `approved`.
2. For image refs: run `python3 .skills/style-decomposition/scripts/extract-palette.py` on each.
3. For URL refs: run `python3 .skills/style-decomposition/scripts/identify-fonts.py` on each.
4. Run `python3 .skills/style-decomposition/scripts/match-icons.py` with a standard needed list.
5. Run `python3 .skills/style-decomposition/scripts/orchestrate.py` to aggregate all outputs.
6. Write placeholder `grid.md` and `motion.md` if not already present.
7. **HARD GATE**: must produce all 5 outputs (palette.yaml, fonts.yaml, icons.yaml, grid.md, motion.md) before brand-architect runs.

## Tools

Bash, Read, Write, Glob. Calls orchestrate.py which coordinates all sub-scripts.

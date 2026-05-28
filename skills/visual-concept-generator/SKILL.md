---
name: visual-concept-generator
description: Stage 03b — generate 2-3 visual concept proposals from brief + prototype + reference palettes. Manager picks one concept; result saved to 03b_КОНЦЕПТ/visual-concept.yaml.
---

# visual-concept-generator

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill visual-concept-generator --stage 03b
```

## What it does

1. Reads `00_БРИФ/brief.md` — goal, audience, positioning
2. Reads `07_ПРОТОТИП/prototype.yaml` — block types (reveals pains/needs/CTAs)
3. Reads `03_РЕФЕРЕНСЫ/index.yaml` + extracts palette context if `refs-palette.html` exists
4. Runs `generate-concept.py` to produce 2-3 concept proposals
5. Presents concepts to manager in chat — name, emotional goal, palette hex, rationale
6. Manager picks (or requests adjustments)
7. Saves approved concept to `03b_КОНЦЕПТ/visual-concept.yaml`

## CLI

```bash
python skills/visual-concept-generator/scripts/generate-concept.py \
  --brief <project>/00_БРИФ/brief.md \
  --prototype <project>/07_ПРОТОТИП/prototype.yaml \
  --palette-json '<extracted_palette_json>' \
  --output <project>/03b_КОНЦЕПТ/visual-concept.yaml \
  --index <chosen_index>
```

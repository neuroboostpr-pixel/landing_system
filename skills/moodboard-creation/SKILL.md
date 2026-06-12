---
name: moodboard-creation
description: Render moodboard.html from approved references in 03_РЕФЕРЕНСЫ/index.yaml. Owned by moodboard-composer.
---

# moodboard-creation

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill moodboard-creation --stage 03
```

## What I do

- Read `index.yaml`, split refs into approved / rejected.
- Render `moodboard.html` via Jinja2 (`moodboard.html.j2`).
- Optionally embed a narrative from `moodboard.md` into the HTML preview.

See [scripts/render.py](scripts/render.py).

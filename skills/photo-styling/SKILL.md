---
name: photo-styling
description: Use during stage 02 to apply identity-safe photo transformations (cutout, edge cleanup, compositing). Owned by photo-stylist agent.
---

# photo-styling

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill photo-styling --stage 02
```

## Allowed modes

- `cutout` — remove background (rembg if available, else Pillow alpha-mask heuristic)
- `cleanup` — edge smoothing on existing alpha
- `crop` — to specified aspect ratio
- `resize` — to specified max dimension

See [scripts/style.py](scripts/style.py).

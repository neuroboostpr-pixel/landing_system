# Atlas prompt template — fill placeholders, paste into generate-atlas.sh

## How to use

1. Replace every `[PLACEHOLDER]` with project-specific text.
2. Choose CHROMA_KEY: `#00ff00` (default) or `#ff00ff` if subject is green.
3. Pass the filled prompt to `generate-atlas.sh` as `--prompt "..."` or via prompt-file.

## Placeholders

- `[THEME]` — short theme/topic (1 line)
- `[VISUAL_STYLE]` — Studio Photography / Cinematic Matte Painting / 3D Render / Editorial / Cyberpunk Vector
- `[LIGHTING]` — Soft studio box / Cinematic dramatic rim / Natural daylight / Moody neon / Golden hour
- `[COLOR_GRADING]` — overall palette / tone aligned to brand (e.g. "deep teal + emerald accent, low saturation")
- `[BG_DESCRIPTION]` — environment for the background quadrant (top-left)
- `[FAR_LIST]` — 4–7 medium-large objects with crisp edges (top-right; will become an alpha overlay)
- `[NEAR_LIST]` — bottom-frame objects only (bottom-left; alpha overlay; NEVER the main subject)
- `[SUBJECT]` — main object/character (bottom-right; alpha overlay)
- `[CONTACT_SURFACE]` — what supports the subject in the final scene (table, ground, podium, chair…)
- `[CHROMA_KEY]` — `#00ff00` default; `#ff00ff` if subject is predominantly green

---

## Prompt body (copy from here)

```
Use the built-in image_gen tool. Generate ONE single PNG, size 2048x1152 (2K, 16:9), as a clean 2x2 parallax hero atlas for: [THEME].

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: [VISUAL_STYLE]
LIGHTING: [LIGHTING]
COLOR GRADING: [COLOR_GRADING]

IMPORTANT COMPOSITION CONTRACT:
All 4 quadrants will be cropped and overlaid into ONE final hero scene.
They must share the same camera angle, horizon line, perspective, object scale, lighting direction and color grading.
The final assembled scene must look logical.
The main subject is [SUBJECT] and will sit in the bottom-right quadrant.
The subject contacts the environment via: [CONTACT_SURFACE]. It must NOT look suspended in air unless the theme explicitly requires floating.
Do not create a full standing body if the final scene needs a seated or cropped subject.

CHROMA-KEY RULES (critical):
Three of the four quadrants must use a perfectly flat solid [CHROMA_KEY] background — exactly that color, no shadows, no gradients, no texture, no reflections, no lighting variation.
The chroma color must NOT appear anywhere on the foreground objects of those quadrants.
Crisp edges around all foreground objects. No cast shadows, no contact shadows, no rim glow that bleeds into the chroma area.
Each quadrant occupies exactly one quarter of the 2048x1152 atlas (each quadrant is 1024x576).

QUADRANTS:

TOP LEFT — BACKGROUND (opaque, no chroma-key):
Full opaque background only.
[BG_DESCRIPTION]
No main subject. No foreground overlay objects. No transparency, no chroma color.
Render the full intended scene background that will sit behind everything else.

TOP RIGHT — FAR (chroma-key [CHROMA_KEY]):
Distant overlay layer on a perfectly flat solid [CHROMA_KEY] background.
Medium and large thematic cutout objects with clear, crisp edges. NOT tiny particles, NOT vague bokeh, NOT dust.
[FAR_LIST]
Objects only — the rest of the quadrant is pure flat [CHROMA_KEY].

BOTTOM LEFT — NEAR (chroma-key [CHROMA_KEY]):
Foreground frame layer on a perfectly flat solid [CHROMA_KEY] background.
Depth-framing objects ONLY, with crisp edges. This layer is NOT the main subject.
[NEAR_LIST]
Objects occupy mainly the lower 20-35 % of the quadrant, OR side edges only — the center area must remain pure flat [CHROMA_KEY].
This layer must create foreground depth without stealing the composition.
It may overlap only the very bottom of the main subject silhouette in the assembled scene, NEVER the face, torso, product body, or key silhouette.
Do not fill the quadrant with one huge object.

BOTTOM RIGHT — SUBJECT (chroma-key [CHROMA_KEY]):
Main subject on a perfectly flat solid [CHROMA_KEY] background.
[SUBJECT]
Subject occupies approximately two-thirds of the quadrant height. Not tiny. Not awkwardly cropped.
Generous transparent padding around the subject (the padding will become the chroma area).
No cast shadow, no contact shadow, no reflection on the chroma plane.

[VISUAL_STYLE] | [LIGHTING] | Premium editorial/commercial digital art.
The subject in the bottom-right and the foreground in the bottom-left and the far details in the top-right must all be cleanly separable from [CHROMA_KEY] for chroma-key removal.
```

---

## Filled example (NeuroUpgrade hero)

```
Use the built-in image_gen tool. Generate ONE single PNG, size 2048x1152 (2K, 16:9), as a clean 2x2 parallax hero atlas for: AI assistants working alongside an entrepreneur.

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: Cinematic editorial photography, photorealistic
LIGHTING: Cinematic dramatic rim light from upper-left, deep falloff into shadow
COLOR GRADING: Deep graphite + electric emerald accents (#10B981), low saturation, premium tech-editorial mood

IMPORTANT COMPOSITION CONTRACT:
All 4 quadrants will be cropped and overlaid into ONE final hero scene.
They must share the same camera angle, horizon line, perspective, object scale, lighting direction and color grading.
The final assembled scene must look logical.
The main subject is a 35-year-old male entrepreneur sitting at a dark wooden desk, three-quarter turn, calm composed gaze, wearing a charcoal-grey crewneck. He sits in the bottom-right quadrant.
The subject contacts the environment via: a dark walnut desk surface in front of him. He must NOT look suspended in air.

CHROMA-KEY RULES (critical):
Three of the four quadrants must use a perfectly flat solid #00ff00 background — exactly that color, no shadows, no gradients, no texture, no reflections, no lighting variation.
The chroma color must NOT appear anywhere on the foreground objects of those quadrants.
Crisp edges around all foreground objects. No cast shadows, no contact shadows, no rim glow that bleeds into the chroma area.
Each quadrant occupies exactly one quarter of the 2048x1152 atlas (each quadrant is 1024x576).

QUADRANTS:

TOP LEFT — BACKGROUND (opaque, no chroma-key):
A dim modern home office at night, deep graphite walls, faint emerald accent light strip behind a shelf in the upper right, soft window light from the upper-left, warm desk lamp pool of light spreading into the lower right area. Atmospheric, slightly hazy. No people, no objects in foreground.

TOP RIGHT — FAR (chroma-key #00ff00):
Distant overlay objects on flat #00ff00:
- a tall slim bookshelf with 5-6 hardcover books and one closed laptop
- a wall-mounted analog clock
- a framed minimalist abstract print
- a hanging pendant lamp with warm bulb visible
Crisp edges, clearly cut against pure green. No green on any object.

BOTTOM LEFT — NEAR (chroma-key #00ff00):
Foreground frame on flat #00ff00, lower 30 % only:
- foreground edge of a dark walnut desk surface seen from camera POV
- a half-open notebook with pen lying on it (left side)
- a ceramic coffee mug with subtle steam (right side)
- the corner of a closed laptop just barely visible in the lower-right corner
Center area must remain pure #00ff00. No green on any object. Lower 30 % only.

BOTTOM RIGHT — SUBJECT (chroma-key #00ff00):
A 35-year-old male entrepreneur on flat #00ff00:
- short dark hair, calm composed direct gaze toward camera, slight three-quarter turn
- wearing a charcoal-grey crewneck, no logos
- sitting upright, visible from chest up plus hands resting on the desk surface (the desk plane is implied by his arm contact, but desk itself is in the BL quadrant)
- soft single-source rim light from upper-left, gentle highlight on cheekbone, deep falloff into shadow on right
- skin texture preserved (subtle pores, no glossy retouch)
- subject occupies about two-thirds of quadrant height, generous green padding around him
- no cast shadow, no contact shadow on the green
- intellectual confidence, no smile, no salesman expression

Cinematic editorial photography | Cinematic dramatic rim light | Premium editorial/commercial digital art.
The subject in the bottom-right and the foreground in the bottom-left and the far details in the top-right must all be cleanly separable from #00ff00 for chroma-key removal.
```

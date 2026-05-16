# Atlas prompt template — fill placeholders, paste into generate-atlas.sh

## How to use

1. Replace every `[PLACEHOLDER]` with project-specific text.
2. Choose CHROMA_KEY: `#00ff00` (default) or `#ff00ff` if subject is predominantly green.
3. Pass the filled prompt to `generate-atlas.sh` as `--prompt "..."` or via prompt-file.

## Placeholders

- `[THEME]` — short theme/topic (1 line)
- `[VISUAL_STYLE]` — Studio Photography / Cinematic Matte Painting / 3D Render / Editorial / Cyberpunk Vector
- `[LIGHTING]` — Soft studio box / Cinematic dramatic rim / Natural daylight / Moody neon / Golden hour
- `[COLOR_GRADING]` — palette/tone aligned to brand (e.g. "deep teal + emerald accent, low saturation")
- `[BG_DESCRIPTION]` — environment for the background quadrant (top-left)
- `[FAR_LIST]` — 4–7 medium-large objects with crisp edges (top-right; will become an alpha overlay)
- `[NEAR_LIST]` — bottom-frame objects only (bottom-left; alpha overlay; NEVER the main subject)
- `[SUBJECT]` — main object/character (bottom-right; alpha overlay)
- `[CONTACT_SURFACE]` — what supports the subject in the final scene (table, ground, podium, chair…)
- `[CHROMA_KEY]` — `#00ff00` default; `#ff00ff` if subject is predominantly green

---

## Prompt body (copy from here)

```
GOAL
Generate ONE single PNG, exactly 2048x1152 px (2K, 16:9), as a clean 2x2 parallax hero atlas for: [THEME]. The atlas will be sliced into 4 layers (background + 3 chroma-keyed overlays) and reassembled into a single parallax hero scene by an automated pipeline.

ROLE
You are an editorial 3D/photography art director producing a production asset. Output must be deterministic, technically clean, and immediately pipeline-ready — no compositional ambiguity, no decorative noise.

WORKFLOW
1. Use the built-in image_gen tool. Save the result locally (personal prototype).
2. Render a single 2048x1152 image split into 4 equal quadrants of 1024x576 each.
3. Lock one shared camera angle, horizon line, perspective, object scale, lighting direction, and color grading across all 4 quadrants — they are pieces of ONE assembled scene.
4. Apply the QUADRANT SPEC below exactly. Treat the CHROMA-KEY rules as hard constraints.
5. Self-check before returning: every chroma-key quadrant has flat solid [CHROMA_KEY], crisp object edges, no shadow bleed, no chroma contamination on foreground objects.

HARD CONSTRAINTS (priority order — top rule wins on conflict)

1. SIZE: exactly 2048x1152 px. 16:9. Single PNG output.
2. NO TEXT: no letters, no logos, no watermarks, no numbers, no UI anywhere.
3. CHROMA INTEGRITY (TR, BL, BR quadrants only):
   - Background is perfectly flat solid [CHROMA_KEY] — exact hex, no gradient, no texture, no shadow, no reflection, no light variation.
   - The chroma hex MUST NOT appear anywhere on the foreground objects of those quadrants.
   - Crisp edges around every foreground object. No cast shadow, no contact shadow, no rim glow bleeding into the chroma area.
4. QUADRANT LAYOUT: each quadrant is exactly 1024x576, positioned TL / TR / BL / BR within the 2x2 atlas.
5. SCENE CONSISTENCY: same camera, same lighting direction, same color grading, same horizon across all 4 quadrants. They must reassemble into one logical scene.
6. SUBJECT GROUNDING: the main subject sits in BR and contacts the environment via [CONTACT_SURFACE]. Subject must NOT appear suspended in air unless [THEME] explicitly requires floating. If the final scene implies a seated or cropped subject, do NOT render a full standing body.
7. NEAR LAYER DISCIPLINE (BL): foreground frame objects only — never the main subject, never one giant object filling the quadrant. Objects occupy the lower 20–35% of the quadrant OR side edges only; the center area stays pure flat [CHROMA_KEY]. NEAR may overlap only the very bottom of the subject silhouette in the final assembled scene, NEVER the face, torso, product body, or key silhouette.
8. FAR LAYER DISCIPLINE (TR): medium and large thematic cutout objects with clear silhouettes. NOT tiny particles, NOT vague bokeh, NOT dust, NOT atmospheric haze.

QUADRANT SPEC

TL — BACKGROUND (opaque, NO chroma-key):
Full opaque environment that will sit behind everything else in the final scene.
Content: [BG_DESCRIPTION]
No main subject. No foreground overlay objects. No transparency, no [CHROMA_KEY] color anywhere.

TR — FAR (chroma-key [CHROMA_KEY]):
Distant overlay layer on flat solid [CHROMA_KEY].
Objects: [FAR_LIST]
Crisp edges. The remaining quadrant area is pure flat [CHROMA_KEY].

BL — NEAR (chroma-key [CHROMA_KEY]):
Foreground frame layer on flat solid [CHROMA_KEY], lower 20–35% only.
Objects: [NEAR_LIST]
Center area stays pure flat [CHROMA_KEY]. Depth-framing only — this layer is NOT the main subject.

BR — SUBJECT (chroma-key [CHROMA_KEY]):
Main subject on flat solid [CHROMA_KEY].
Subject: [SUBJECT]
Subject occupies approximately two-thirds of quadrant height. Generous chroma padding around the subject. No cast shadow, no contact shadow, no reflection on the chroma plane.

STYLE LOCK
Visual style: [VISUAL_STYLE].
Lighting: [LIGHTING].
Color grading: [COLOR_GRADING].
Tone: premium editorial / commercial digital art.

OUTPUT FORMAT
- Single PNG, 2048x1152 px.
- 2x2 atlas layout (TL background, TR far, BL near, BR subject).
- TR / BL / BR backgrounds = exact flat [CHROMA_KEY].
- TL = fully opaque.

COMPLETION CRITERIA (the asset is done when ALL are true)
- Dimensions are exactly 2048x1152.
- TR, BL, BR show flat solid [CHROMA_KEY] backgrounds with no contamination.
- All foreground objects have crisp, chroma-removable edges.
- Subject in BR is grounded via [CONTACT_SURFACE] logic for the assembled scene.
- The four quadrants share one consistent camera, lighting, and grade — they would reassemble into a coherent hero scene.
- No text, logos, watermarks, or UI anywhere.

DO NOT
- Do not output multiple images or variations.
- Do not add captions, labels, or annotations.
- Do not let [CHROMA_KEY] appear on any foreground object.
- Do not add shadows or reflections on the chroma plane.
- Do not place the main subject in TR or BL.
- Do not fill the NEAR quadrant with one giant object.
```

---

## Filled example (NeuroUpgrade hero)

```
GOAL
Generate ONE single PNG, exactly 2048x1152 px (2K, 16:9), as a clean 2x2 parallax hero atlas for: AI assistants working alongside an entrepreneur. The atlas will be sliced into 4 layers (background + 3 chroma-keyed overlays) and reassembled into a single parallax hero scene by an automated pipeline.

ROLE
You are an editorial 3D/photography art director producing a production asset. Output must be deterministic, technically clean, and immediately pipeline-ready — no compositional ambiguity, no decorative noise.

WORKFLOW
1. Use the built-in image_gen tool. Save the result locally (personal prototype).
2. Render a single 2048x1152 image split into 4 equal quadrants of 1024x576 each.
3. Lock one shared camera angle, horizon line, perspective, object scale, lighting direction, and color grading across all 4 quadrants — they are pieces of ONE assembled scene.
4. Apply the QUADRANT SPEC below exactly. Treat the CHROMA-KEY rules as hard constraints.
5. Self-check before returning: every chroma-key quadrant has flat solid #00ff00, crisp object edges, no shadow bleed, no chroma contamination on foreground objects.

HARD CONSTRAINTS (priority order — top rule wins on conflict)

1. SIZE: exactly 2048x1152 px. 16:9. Single PNG output.
2. NO TEXT: no letters, no logos, no watermarks, no numbers, no UI anywhere.
3. CHROMA INTEGRITY (TR, BL, BR quadrants only):
   - Background is perfectly flat solid #00ff00 — exact hex, no gradient, no texture, no shadow, no reflection, no light variation.
   - The chroma hex MUST NOT appear anywhere on the foreground objects of those quadrants.
   - Crisp edges around every foreground object. No cast shadow, no contact shadow, no rim glow bleeding into the chroma area.
4. QUADRANT LAYOUT: each quadrant is exactly 1024x576, positioned TL / TR / BL / BR within the 2x2 atlas.
5. SCENE CONSISTENCY: same camera, same lighting direction, same color grading, same horizon across all 4 quadrants.
6. SUBJECT GROUNDING: the entrepreneur sits in BR and contacts the environment via a dark walnut desk surface in front of him. He must NOT appear suspended in air.
7. NEAR LAYER DISCIPLINE (BL): foreground frame objects only — never the subject, never one giant object filling the quadrant. Objects occupy the lower 20–35% only.
8. FAR LAYER DISCIPLINE (TR): medium/large cutout objects with clear silhouettes. NOT particles, NOT bokeh.

QUADRANT SPEC

TL — BACKGROUND (opaque, NO chroma-key):
A dim modern home office at night. Deep graphite walls. Faint emerald accent light strip behind a shelf in the upper right. Soft window light from the upper-left. Warm desk lamp pool spreading into the lower right. Atmospheric, slightly hazy. No people, no foreground objects.

TR — FAR (chroma-key #00ff00):
Distant overlay objects on flat #00ff00:
- a tall slim bookshelf with 5–6 hardcover books and one closed laptop
- a wall-mounted analog clock
- a framed minimalist abstract print
- a hanging pendant lamp with a warm bulb visible
Crisp edges. No green on any object.

BL — NEAR (chroma-key #00ff00):
Foreground frame on flat #00ff00, lower 30% only:
- foreground edge of a dark walnut desk surface seen from camera POV
- a half-open notebook with pen on it (left side)
- a ceramic coffee mug with subtle steam (right side)
- corner of a closed laptop barely visible in the lower-right
Center stays pure #00ff00. No green on any object.

BR — SUBJECT (chroma-key #00ff00):
A 35-year-old male entrepreneur on flat #00ff00:
- short dark hair, calm composed direct gaze toward camera, slight three-quarter turn
- charcoal-grey crewneck, no logos
- visible from chest up plus hands resting on the (implied) desk surface
- soft single-source rim light from upper-left, gentle cheekbone highlight, deep falloff on right
- skin texture preserved (subtle pores, no glossy retouch)
- occupies about two-thirds of quadrant height, generous green padding
- no cast shadow, no contact shadow on the green
- intellectual confidence, no smile, no salesman expression

STYLE LOCK
Visual style: Cinematic editorial photography, photorealistic.
Lighting: Cinematic dramatic rim light from upper-left, deep falloff into shadow.
Color grading: Deep graphite + electric emerald accents (#10B981), low saturation, premium tech-editorial mood.
Tone: premium editorial / commercial digital art.

OUTPUT FORMAT
- Single PNG, 2048x1152 px.
- 2x2 atlas (TL background, TR far, BL near, BR subject).
- TR / BL / BR backgrounds = exact flat #00ff00.
- TL = fully opaque.

COMPLETION CRITERIA
- Dimensions are exactly 2048x1152.
- TR, BL, BR show flat solid #00ff00 with no contamination.
- All foreground objects have crisp, chroma-removable edges.
- Subject in BR is grounded via the implied desk surface.
- The four quadrants share one consistent camera, lighting, and grade.
- No text, logos, watermarks, or UI anywhere.

DO NOT
- Do not output multiple images or variations.
- Do not add captions, labels, or annotations.
- Do not let #00ff00 appear on any foreground object.
- Do not add shadows or reflections on the chroma plane.
- Do not place the subject in TR or BL.
- Do not fill the NEAR quadrant with one giant object.
```

# PR-S: Style Moods System Design Spec

**Date:** 2026-06-02  
**Status:** 📋 SPEC IN REVIEW  
**Related Plan:** [`2026-06-02-pr-s-style-moods-system-plan.md`](../plans/2026-06-02-pr-s-style-moods-system-plan.md)

---

## 1. Problem Statement

### Current State

The landing-system has **complete mood infrastructure** already built:

- **6 style moods:** brutalist, editorial-warm, swiss-modernist, retro-windows, coral-soft, monochrome-precision
- **Each mood includes:**
  - `palette.css` — semantic CSS variables (primary, secondary, accents, text hierarchy)
  - `typography.css` — font stack, type scale, line heights
  - `motion.css` — animation timing, easing, intensity
  - Design guide documenting when to apply the mood
- **38 reusable patterns:** scroll-reveal, ambient-mesh, paper-texture, marquee-fade, etc.
  - Each pattern: CSS snippet + vanilla JS + attribution

**Mood metadata:** Blocks register their style_mood in `meta.yaml` (e.g., `style_mood: brutalist`).

### The Gap

**Users cannot:**
- **See mood variants** — when choosing a layout, they don't see how the same block looks in different moods
- **Select mood** — mood is hardcoded in block metadata, not a user-selectable dimension
- **Preview mood combinations** — the wireframe UI has no mood tabs/selection

**Result:** Block selection is 1-dimensional (layout type + variant), not 2-dimensional (layout + mood).

---

## 2. Goals

### Primary

1. **Add mood as a user-selectable dimension** in wireframe UI (alongside layout type + block variant)
2. **Let users preview mood variants side-by-side** (5-8 mood tabs per block)
3. **Persist mood selection** in selections.yaml
4. **Apply mood CSS + patterns** automatically during compose phase

### Secondary

1. **Flexible across all projects** — not neurokreator-specific
2. **Backward compatible** — old selections without mood still work (default to block's hardcoded mood)
3. **Extensible** — foundation for future PR-S.2 (mood auto-detection)

---

## 3. User Experience

### Wireframe Stage (07a)

**Before PR-S:**
- User sees 3–5 layout variants for each block
- Selects preferred layout
- Downloads `selections.yaml` with block ID only

**After PR-S:**
- User sees 3–5 layout variants **AND** 5–8 mood tabs below each layout
- Clicks layout → renders preview
- Clicks mood tab → same layout, different colors/typography/patterns
- Selects both layout AND mood
- Downloads `selections.yaml` with layout + mood per block

**UI wireframe:**
```
┌─────────────────────────────────────┐
│  HERO SECTION                       │
├─────────────────────────────────────┤
│  [Layout Variant 1] [V2] [V3] [V4]  │  ← Layout tabs (existing)
├─────────────────────────────────────┤
│  [Brutalist] [Editorial] [Swiss]    │  ← Mood tabs (NEW)
│  [Retro] [Coral] [Monochrome]       │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │  PREVIEW IFRAME               │  │
│  │  (renders selected layout      │  │
│  │   + selected mood colors)      │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Compose Stage (07b)

**Before PR-S:**
- compose-blocks.py reads selections.yaml (block IDs only)
- Looks up block, injects content
- Final HTML uses block's hardcoded mood

**After PR-S:**
- compose-blocks.py reads selections.yaml (block IDs + mood)
- Looks up block, injects content
- Loads mood CSS: `block-library/_styles/{mood}/palette.css` + `typography.css` + `motion.css`
- Injects mood patterns based on mood→pattern mapping
- Final HTML uses selected mood CSS + patterns

---

## 4. Data Schema

### selections.yaml

**Before:**
```yaml
project: neurokreator
selections:
  - block_position: 1
    chosen_variant: hero-brutalist-split
  - block_position: 2
    chosen_variant: features-grid-4col
```

**After:**
```yaml
project: neurokreator
selections:
  - block_position: 1
    chosen_variant: hero-brutalist-split
    style_mood: brutalist           # NEW
  - block_position: 2
    chosen_variant: features-grid-4col
    style_mood: editorial-warm      # NEW
```

### Mood Values

Valid moods (enum):
- `brutalist` — geometric, high-contrast, minimal
- `editorial-warm` — warm colors, serif typography, soft gradients
- `swiss-modernist` — grid-based, sans-serif, precise spacing
- `retro-windows` — nostalgic, pastel, playful
- `coral-soft` — beauty/wellness aesthetic, rounded, soft
- `monochrome-precision` — luxury, symmetrical, minimal chromatic

### Backward Compatibility

If `style_mood` is missing in selections.yaml:
- Default to block's hardcoded `style_mood` from `meta.yaml`
- Compose runs without errors
- Mood CSS is still applied (from block's default mood)

---

## 5. Technical Implementation

### 5.1 Wireframe Rendering

**File:** `skills/wireframe-rendering/templates/wireframe-shell.html`

**Changes:**
- Add mood tabs DOM structure below layout variant tabs
- Use CSS `:has(:checked[data-mood=brutalist])` to toggle mood preview visibility
- Mood tabs are radio buttons: `<input type="radio" data-mood="brutalist" name="mood-{position}">`
- JavaScript `confirmSelections()` captures mood selection from checked mood radios

**Result:** User clicks mood tab → CSS selector matches → different mood preview renders

### 5.2 Wireframe Variant Generation

**File:** `skills/wireframe-rendering/scripts/render-wireframe.py`

**Changes:**
- For each candidate block, generate **6 mood variants** (one for each mood)
- Load mood CSS from `block-library/_styles/{mood}/palette.css`
- Inject mood CSS vars into iframe `<style>` tag before block HTML
- Group mood previews via `data-mood` attribute (CSS `:has()` hides/shows)

**Result:** All 6 moods available for every block, user can click to preview

### 5.3 Selections Generation

**File:** `skills/wireframe-rendering/scripts/render-wireframe.py` (line 335–348, `confirmSelections()`)

**Changes:**
- Capture `data-mood` value from checked mood radio per block
- Include `style_mood` field in YAML export

**Result:** selections.yaml contains mood for each block

### 5.4 Compose Pipeline Integration

**File:** `skills/block-composition/scripts/compose-blocks.py`

**Changes:**
1. Read `style_mood` from selections.yaml (or default to block's hardcoded mood)
2. Pass mood to `inject-tokens.py` as `--mood {mood_name}`
3. After block HTML injection, append mood CSS files:
   ```bash
   block-library/_styles/{mood}/palette.css
   block-library/_styles/{mood}/typography.css
   block-library/_styles/{mood}/motion.css
   ```
4. Append mood patterns (from existing `generate-theme.py` mapping)

**Result:** composed.html includes mood CSS + patterns, colors/fonts/patterns change

### 5.5 Token Injection with Mood

**File:** `skills/block-composition/scripts/inject-tokens.py`

**Changes:**
- Accept `--mood {mood_name}` parameter
- Load CSS vars from `block-library/_styles/{mood}/palette.css`
- Inject into block as `<style>:root { --lp-primary: #...; ... }</style>`
- Mood vars override block's default colors

**Result:** Block HTML renders with selected mood palette

---

## 6. Workflow Example

**User journey for neurokreator project:**

1. **Stage 07a (Wireframe):**
   ```
   /landing-wireframe neurokreator
   → Shows hero block with 5 layout variants
   → Each layout has 6 mood tabs (brutalist, editorial-warm, swiss-modernist, retro-windows, coral-soft, monochrome-precision)
   → User clicks "editorial-warm" → hero preview switches to editorial-warm colors
   → User confirms: hero layout #1, mood "editorial-warm"
   → Repeat for benefits, audience, curriculum, pricing
   → Download selections.yaml with mood selections
   ```

2. **Stage 07b (Compose):**
   ```
   /landing-compose neurokreator
   → Read selections.yaml: hero layout + "editorial-warm" mood
   → Inject hero block with "editorial-warm" CSS palette + patterns
   → Repeat for all blocks
   → composed.html styled with selected moods
   ```

3. **Stage 08+ (Build, Deploy, QA):**
   ```
   Final website uses selected moods (e.g., editorial-warm for hero, retro-windows for pricing)
   ```

---

## 7. Constraints & Assumptions

### Constraints

1. **No new moods** — only use existing 6 moods (brutalist, editorial-warm, swiss-modernist, retro-windows, coral-soft, monochrome-precision)
2. **Pattern mapping fixed** — patterns per mood come from existing `generate-theme.py` mapping
3. **Mood metadata immutable** — block's hardcoded mood in `meta.yaml` doesn't change
4. **CSS var injection order critical** — mood CSS must inject before block HTML so mood colors override defaults

### Assumptions

1. **CSS `:has()` works** — modern browsers support `:has()` pseudo-class (for mood tab CSS selectors)
2. **Mood infrastructure complete** — all 6 moods have full palette/typography/motion CSS
3. **Pattern library stable** — 38 patterns won't be added/removed during PR-S implementation
4. **Block metadata consistent** — all blocks in catalog.yaml have valid `style_mood` field

---

## 8. Testing Strategy

### Unit Tests

- `test-wireframe-mood-extraction.bats` — verify mood values parsed from iframes
- `test-mood-css-injection.bats` — verify mood CSS injected correctly
- `test-selections-yaml-mood-field.bats` — verify mood saved to YAML

### Integration Tests

- E2E wireframe → selections → compose workflow (test project)
- Backward compat: old selections.yaml (no mood field) still works
- Neurokreator retroactive: re-generate with different mood selections, verify visual differences

### Visual Tests

- Screenshot comparison: same block in 6 different moods
- Manual inspection: composed.html matches selected mood palette

---

## 9. Success Criteria

- ✅ Wireframe shows mood tabs for all blocks
- ✅ User can click mood → preview updates live
- ✅ Mood selection saved to selections.yaml
- ✅ Compose applies mood CSS + patterns
- ✅ Works for any project (flexible, not neurokreator-only)
- ✅ Backward compatible (old selections work)
- ✅ No regressions in layout selection (layout ⊥ mood)
- ✅ E2E tests pass

---

## 10. Future: PR-S.2 (Mood Auto-Detection)

**Out of scope for PR-S.1** — scheduled for PR-S.2:
- Detect mood from niche (e.g., "luxury" → "monochrome-precision")
- Recommend mood based on brand-kit colors
- Custom moods (would extend `block-library/_styles/`)

---

## 11. References

- **Block Library:** `landing-system/block-library/_styles/` — 6 complete moods
- **Pattern Library:** `landing-system/block-library/_patterns/` — 38 patterns
- **Catalog:** `landing-system/block-library/catalog.yaml` — block metadata with `style_mood`
- **Theme Generator:** `scripts/generate-theme.py` — mood → patterns mapping
- **Implementation Plan:** [`2026-06-02-pr-s-style-moods-system-plan.md`](../plans/2026-06-02-pr-s-style-moods-system-plan.md)


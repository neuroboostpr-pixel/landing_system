# PR-S: Style Moods System — Implementation Plan

**Date:** 2026-06-02  
**Status:** 📋 IN REVIEW  
**Scope:** 5 phases, ~800 SLOC, 5–7 days work  

---

## Phase 1: Wireframe UI Enhancement

**Goal:** Add mood tabs to wireframe.html, let users preview mood variants side-by-side with layout variants.

### 1.1 Update wireframe-shell.html template

**File:** `landing-system/skills/wireframe-rendering/templates/wireframe-shell.html`

**Changes:**
- Add mood tabs DOM below layout variant tabs (lines 320–350)
- Extend radio input structure with `data-mood` attribute
- Update CSS selectors to use `:has(:checked[data-mood=brutalist])` for mood previews
- Group mood previews via `data-mood` (one mood hidden at a time via CSS)
- Update `confirmSelections()` JS function to capture mood selections (line 335)

**Checklist:**
- [ ] Add mood tabs HTML structure
- [ ] Add CSS `:has()` selectors for mood visibility toggle
- [ ] Extend `confirmSelections()` to capture `data-mood` values
- [ ] Test tab switching (CSS works, no JS needed for preview)
- [ ] Verify iframes update correctly with mood tabs

### 1.2 Update render-wireframe.py

**File:** `landing-system/skills/wireframe-rendering/scripts/render-wireframe.py`

**Changes:**
- Modify `variant_rendering()` loop (lines 539–622): for each block variant, **generate 6 mood variants** (one for each mood in `block-library/_styles/`)
- Extract `style_mood` from `meta.yaml`, inject mood CSS vars into iframe `<style>` tag before block HTML
- Group mood previews in DOM via `data-mood` attribute (one per mood)
- Update wireframe metadata display to show mood tags (already there, line 594)

**Checklist:**
- [ ] Load mood CSS from `block-library/_styles/{mood}/palette.css`
- [ ] Inject mood CSS vars into iframe `<style>` before block HTML
- [ ] Generate 6 mood variants per candidate block
- [ ] Verify CSS var substitution works (colors change when mood tab clicked)
- [ ] Test with 2–3 blocks (hero, features, cta) across different moods

### 1.3 Update match-candidates.py (optional)

**File:** `landing-system/skills/wireframe-rendering/scripts/match-candidates.py`

**Changes:**
- If `--mood` filter passed, pre-filter candidates by `style_mood` before returning top N
- (This is optional — if not done, all 6 moods will be available for all blocks)

**Checklist:**
- [ ] Add `--mood` parameter parsing
- [ ] Filter candidates by mood (if parameter provided)
- [ ] Ensure backward compatibility (no mood parameter = all moods available)

---

## Phase 2: Selections.yaml Schema Extension

**Goal:** Update selections.yaml to store mood selection per block.

### 2.1 Update schema in render-wireframe.py

**File:** `landing-system/skills/wireframe-rendering/scripts/render-wireframe.py` (line 335–348, `confirmSelections()` function)

**Changes:**
- Capture `data-mood` attribute from checked mood radios
- Store mood in selections YAML as `style_mood` field per block
- Update YAML generation to include mood

**Schema before:**
```yaml
selections:
  - block_position: 1
    chosen_variant: hero-id
  - block_position: 2
    chosen_variant: features-id
```

**Schema after:**
```yaml
selections:
  - block_position: 1
    chosen_variant: hero-id
    style_mood: brutalist              # NEW
  - block_position: 2
    chosen_variant: features-id
    style_mood: editorial-warm         # NEW
```

**Checklist:**
- [ ] Update YAML generation to include `style_mood` per selection
- [ ] Test YAML output (download, inspect for mood values)
- [ ] Ensure mood defaults to block's hardcoded mood if not selected (backward compat)
- [ ] Validate YAML schema (mood ∈ {brutalist, editorial-warm, swiss-modernist, retro-windows, coral-soft, monochrome-precision})

---

## Phase 3: Compose Pipeline Integration

**Goal:** Apply mood CSS + patterns when composing final HTML.

### 3.1 Update compose-blocks.py

**File:** `landing-system/skills/block-composition/scripts/compose-blocks.py`

**Changes:**
- Read `style_mood` from selections.yaml (line 26, after variant lookup)
- Pass mood to `inject-tokens.py` as `--mood {mood_name}` (line 66)
- After block HTML injection, append mood CSS files:
  - `block-library/_styles/{mood}/palette.css`
  - `block-library/_styles/{mood}/typography.css`
  - `block-library/_styles/{mood}/motion.css`
- Append mood patterns (from `generate-theme.py` mapping, lines 73–76):
  - E.g., `_patterns/scroll-reveal/snippet.css` for brutalist mood
  - Pattern selection per mood is deterministic (from existing mapping)
- Log mood selection in `block-injection-log.md` (line 110)

**Checklist:**
- [ ] Read mood from selections.yaml
- [ ] Load mood CSS files from `block-library/_styles/{mood}/`
- [ ] Inject CSS before block HTML (so block colors override with mood palette)
- [ ] Append mood patterns based on `generate-theme.py` mapping
- [ ] Log mood in injection-log.md
- [ ] Handle backward compat: if mood missing, default to block's hardcoded mood

### 3.2 Update inject-tokens.py

**File:** `landing-system/skills/block-composition/scripts/inject-tokens.py`

**Changes:**
- Accept `--mood` parameter
- Load CSS variables from `block-library/_styles/{mood}/palette.css`
- Inject as `<style>:root { --lp-primary: {...}; ... }</style>` before block HTML
- Override block's inline color vars with mood palette

**Checklist:**
- [ ] Add `--mood` parameter to argument parser
- [ ] Load mood palette.css and extract CSS vars
- [ ] Inject mood CSS vars into block `<style>`
- [ ] Verify color substitution (test with 2 different moods)
- [ ] Handle missing mood gracefully (use defaults)

### 3.3 No changes needed to inject-content.py

**Why:** Mood doesn't affect content slots, only visual styling. Content injection is independent.

---

## Phase 4: Validation & Testing

### 4.1 E2E Test Workflow

**Create test project:**
```bash
/landing-start test-mood-project
# Upload minimal prototype (1 hero + 1 features block)
```

**Run wireframe:**
```bash
/landing-wireframe test-mood-project
# Expected: mood tabs appear below layout tabs
# Test: click 2–3 moods → preview colors change in iframes
```

**Confirm selections with mood:**
```bash
# In wireframe UI: select layout + mood for each block
# Click "Confirm" → download selections.yaml
# Verify: YAML contains style_mood field
```

**Run compose:**
```bash
/landing-compose test-mood-project
# Expected: composed.html includes mood CSS files
# Inspect: <head> should contain block-library/_styles/{mood}/*.css
```

**Visual inspection:**
```bash
# Open composed.html in browser
# Verify: colors, fonts, patterns match selected mood
# Test: compare 2 renders with different moods → visually different
```

### 4.2 Backward Compatibility Test

**Old selections.yaml (no mood field):**
```yaml
selections:
  - block_position: 1
    chosen_variant: hero-id
```

**Run compose with old selections:**
```bash
/landing-compose test-project
# Expected: should work, defaults to block's hardcoded mood
# Verify: composed.html renders without errors
```

### 4.3 Neurokreator Retroactive Test

**Re-generate wireframe with mood selection:**
```bash
/landing-wireframe neurokreator
# See: 6 mood variants for each block (hero, benefits, audience, curriculum, pricing)
# Select: different moods than original (e.g., "editorial-warm" instead of default)
```

**Compose with new mood selections:**
```bash
/landing-compose neurokreator
# Verify: composed.html styled with new moods
# Visual check: neurokreator hero now has "editorial-warm" palette instead of original
```

**Checklist:**
- [ ] E2E test passes (wireframe → selections → compose → HTML)
- [ ] Backward compat test passes (old selections still work)
- [ ] Neurokreator retroactive test passes (recomposes with new moods)
- [ ] No regressions in layout selection (layout + mood independent)

---

## Phase 5: Documentation & Onboarding

### 5.1 Create MOOD-SELECTION-GUIDE.md

**File:** `landing-system/docs/MOOD-SELECTION-GUIDE.md`

**Content:**
- When to use each mood (brutalist for tech/fintech, editorial-warm for lifestyle, etc.)
- Which niches match which moods (best practices)
- How moods affect visual hierarchy, color, typography, patterns
- Example: "neurokreator uses brutalist for modern/tech vibe"
- Decision tree: niche/brand style → recommended mood
- Screenshots showing same block in 6 different moods

### 5.2 Update wireframe.html inline help

**File:** `landing-system/skills/wireframe-rendering/templates/wireframe-shell.html`

**Changes:**
- Add `title` attributes to mood tabs (e.g., "Brutalist: geometric, high-contrast, minimal")
- Add help text explaining mood selection

### 5.3 Update /landing-wireframe skill description

**File:** `landing-system/.claude/commands/landing-wireframe.md`

**Changes:**
- Mention mood selection in description
- Add example: "Select layout + mood for each block, then confirm"

### 5.4 Update stage-gates.yaml

**File:** `landing-system/config/stage-gates.yaml`

**Changes:**
- Add soft-gate `has_mood_selection` (optional, warns if not set)
- Or add hard-gate if mood is mandatory (per project policy)

**Checklist:**
- [ ] Create MOOD-SELECTION-GUIDE.md with examples
- [ ] Update wireframe.html help text
- [ ] Update /landing-wireframe skill description
- [ ] Update stage-gates.yaml with mood gate (soft or hard)
- [ ] Document mood selection workflow in CLAUDE.md

---

## Implementation Order

1. **Phase 1:** Wireframe UI (2–3 days)
   - 1.1 wireframe-shell.html DOM + CSS
   - 1.2 render-wireframe.py mood variant generation
   - 1.3 match-candidates.py (optional)

2. **Phase 3:** Compose pipeline (1–2 days)
   - 3.1 compose-blocks.py mood reading + CSS injection
   - 3.2 inject-tokens.py mood vars

3. **Phase 2:** Selections schema (0.5 days)
   - 2.1 YAML generation in render-wireframe.py

4. **Phase 4:** Testing (1 day)
   - 4.1, 4.2, 4.3 test workflows

5. **Phase 5:** Documentation (1 day)
   - 5.1–5.4 guides + gates

**Total:** ~5–7 days, ~800 SLOC

---

## Files Modified

| File | Phase | Change Type | Approx. SLOC |
|------|-------|-------------|------------|
| `wireframe-shell.html` | 1 | DOM + CSS | 50 |
| `render-wireframe.py` | 1, 2 | Mood generation + YAML | 80 |
| `match-candidates.py` | 1 | Mood filter (optional) | 20 |
| `compose-blocks.py` | 3 | Mood reading + CSS injection | 50 |
| `inject-tokens.py` | 3 | Mood vars | 40 |
| `MOOD-SELECTION-GUIDE.md` | 5 | New doc | 100 |
| `landing-wireframe.md` | 5 | Updated description | 5 |
| Tests (bats/pytest) | 4 | New tests | 150 |

**Total:** ~495 SLOC (excluding tests and docs)

---

## Success Criteria

- ✅ Wireframe shows 5–8 mood variants per block with clickable tabs
- ✅ User can click mood tabs → preview changes live
- ✅ User can select mood per block → saved to selections.yaml
- ✅ Compose applies mood CSS + patterns to final HTML
- ✅ Works for any landing project (neurokreator, test projects, future projects)
- ✅ Backward compatible (old selections without mood still work)
- ✅ No regressions in existing layout selection
- ✅ E2E tests pass (wireframe → compose → visual verification)

---

## Future: PR-S.2 (Mood Auto-Detection)

**Out of scope for PR-S.1:**
- Auto-detect mood from niche/brand-kit (e.g., "luxury" niche → "monochrome-precision" mood)
- Mood recommendations based on content analysis
- Custom moods (would require extending `block-library/_styles/`)

**When:** PR-S.2 (next iteration after PR-S.1 ships)

---

## Notes for Implementer

1. **Mood CSS injection order matters:** Inject mood palette BEFORE block HTML so mood colors override block defaults.
2. **Backward compat:** Always default to block's hardcoded `style_mood` if selection is missing.
3. **Pattern mapping:** Use existing `generate-theme.py` mood→patterns mapping; don't create new patterns.
4. **Testing:** Test wireframe mood tabs in multiple browsers (CSS `:has()` is modern, older browsers may not support).
5. **Documentation:** MOOD-SELECTION-GUIDE.md should include screenshots of the same block in all 6 moods.


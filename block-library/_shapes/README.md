# Shape Library — Decorative SVG Shapes

18 reusable SVG background shapes for landing page blocks. Each shape is customizable with brand-kit colors (primary, secondary, accent) and opacity.

## What is a Shape?

A **shape** is a decorative SVG background element that can be applied to any block:
- Optional (no shape = just solid block)
- Customizable color (from brand-kit palette)
- Adjustable opacity (0–1)
- Applied BEFORE block content (background layer)

## Quick Start

### In Wireframe (07a)

1. Open `wireframe.html` in browser
2. Scroll to block you want to decorate
3. Under mood tabs, find **"Фон декоративный"** selector
4. Pick shape: "Волны" / "Облака" / "Горы" / etc.
5. Click color swatch (Primary / Secondary / Accent) or pick custom color
6. Slide opacity (0–1)
7. See preview update
8. Click "Confirm selections" → download `selections.yaml`

### In selections.yaml

```yaml
selections:
  - block_position: 1
    chosen_variant: hero-001
    background_shape: waves              # shape ID
    background_shape_color: primary      # or "secondary", "accent", or hex "#FFA500"
    background_shape_opacity: 0.15       # 0-1
```

### In composed.html (07b)

Shape SVG is injected as `<svg>` background layer, before block HTML:

```html
<svg class="lp-shape-bg" viewBox="0 0 1200 200" style="--shape-color: var(--lp-primary); --shape-opacity: 0.15;">
  <!-- path d="..." -->
</svg>
<!-- Block content below -->
```

## 18 Shapes

### Organic (8)
- **waves** — Smooth wavy line, calm water feel
- **clouds** — Fluffy cloud shapes, approachable
- **mountains** — Tall angular peaks, adventure
- **drops** — Water droplets scattered
- **curve** — Single smooth curve
- **curve-asymmetrical** — Asymmetric flowing curve
- **waves-brush** — Hand-drawn looking waves
- **blob** — Organic irregular form, modern

### Geometric (8)
- **triangle** — Simple triangle, sharp
- **pyramids** — 3+ pyramid shapes, structured
- **zigzag** — Zigzag line, dynamic
- **split** — Two halves split, contrast
- **tilt** — Tilted rectangle, movement
- **tilt-opacity** — Tilted with gradient opacity
- **fan-opacity** — Fan-like spread with gradient
- **triangle-asymmetrical** — Irregular triangle

### Pattern (2)
- **waves-pattern** — Repeating wave pattern, texture
- **book** — Pages/book metaphor, editorial

## Color Customization

Each shape supports **3 preset colors** + **custom**:

```yaml
background_shape_color: primary        # Use primary from brand-kit
background_shape_color: secondary      # Use secondary
background_shape_color: accent         # Use accent
background_shape_color: "#FF5733"      # Custom hex (optional)
```

Opacity is separate:

```yaml
background_shape_opacity: 0.1    # 10% visible, 90% transparent
background_shape_opacity: 0.3    # 30% visible
background_shape_opacity: 0.5    # 50% visible
```

## File Structure

```
_shapes/
  catalog.yaml                   # Index of all shapes
  README.md                      # This file
  waves/
    shape.svg                    # SVG template with CSS vars
    meta.yaml                    # Shape metadata
  clouds/
    shape.svg
    meta.yaml
  [16 more shapes...]
```

## SVG Template Format

Each `shape.svg` uses CSS variables for color/opacity:

```svg
<svg viewBox="0 0 1200 200">
  <defs>
    <style>
      .shape { 
        fill: var(--lp-shape-color, #FFA500);  /* fallback orange */
        opacity: var(--lp-shape-opacity, 0.1);
      }
    </style>
  </defs>
  <path class="shape" d="M0,100 Q300,50 600,100 T1200,100 L1200,200 L0,200 Z"/>
</svg>
```

At render time, variables are injected:

```html
<style>
  :root {
    --lp-shape-color: var(--lp-primary);  /* resolved from tokens.json */
    --lp-shape-opacity: 0.15;
  }
</style>
<svg class="lp-shape-bg" viewBox="0 0 1200 200">
  <!-- ... shape path uses CSS vars ... -->
</svg>
```

## Adding a New Shape

1. Create folder: `_shapes/<shape-id>/`
2. Create `shape.svg` with `--lp-shape-color` and `--lp-shape-opacity` CSS vars
3. Create `meta.yaml`:
   ```yaml
   id: my-shape
   name_ru: Моя форма
   category: organic  # or geometric / pattern
   svg_vars: ["{color}", "{opacity}"]
   recommended_colors: [primary, secondary, accent]
   ```
4. Add entry to `catalog.yaml`
5. Test in wireframe: select shape, pick color, check preview

## Best Practices

### When to Use Shapes

- **Hero section** → Large blob or curve (attention-grabbing)
- **Benefits list** → Subtle waves or dots (secondary emphasis)
- **Pricing table** → Geometric triangle/pyramid (structure)
- **Testimonials** → Organic clouds (warmth)
- **CTA section** → Bold asymmetric curve (action)

### When NOT to Use Shapes

- Blocks that already have complex backgrounds (avoid layering)
- When opacity is <0.05 (too faint, wastes file size)
- Conflicting with mood CSS patterns (can create visual noise)

### Color Matching

- **editorial-warm** → Use warmer colors (secondary, accent)
- **brutalist** → Use high-contrast (primary, but low opacity like 0.05)
- **swiss-modernist** → Use subtle geometric shapes (primary at 0.15)
- **coral-soft** → Use organic shapes (accent for warmth)

## Performance

- Each SVG is embedded as `<svg>` tag, not external file (no extra HTTP request)
- Opacity controlled via CSS, not canvas (fast)
- File size per shape ~500B–2KB (negligible)
- No JavaScript animation (only CSS)

## Future Enhancements

- [ ] Shape animation (slow rotate, fade in/out)
- [ ] Gradient fills (multi-color shapes)
- [ ] Shape combinations (two shapes per block)
- [ ] AI auto-selection (recommend shape by mood + niche)

# Stage-08 — Composed ↔ block-spec Lint

**Status:** required gate (strict mode).

## What it checks

Comparing `07b_COMPOSED/composed*.html` against `08_КОД/block-spec.yaml`, the
linter catches:

1. **Bullets** — `<ul.*-specs > li>` count must match available text-control fields.
2. **Color swatches** — `[style*="--c"]` presence requires a `colors` control.
3. **Multi-paragraph textareas** — `<p>` count must match `\n\n`-separated paragraphs in the default.
4. **Slider images** — `.slider-track > img` count must match populated `photoN` template fields.
5. **Inline SVG icons** — every `.feature-icon > svg` requires a non-empty `icon_svg` value.

## Commands

Verify only:
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path>
```

Auto-fix (multi-paragraph extraction):
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path> --fix
```

JSON output (for integration):
```bash
python3 skills/wp-gutenberg-block-builder/scripts/lint-composed-vs-spec.py \
    --project <project-path> --json
```

## probe_selector contract

Every block in `block-spec.yaml` that should be linted MUST set `probe_selector`.
Section blocks (`probe_kind: card-collection`) SHOULD also set
`card_probe_selector` — otherwise card-level heuristics fall back to scanning
the entire section soup, which inflates `<p>`/`<li>` counts and produces
false positives.

```yaml
# Single block — one DOM instance:
- slug: nav
  probe_selector: '.nav-bar'
  probe_kind: single             # default; can be omitted

# Section block with repeating cards inside:
- slug: features
  probe_selector: '.features-section'
  probe_kind: card-collection
  card_probe_selector: '.feature-card'   # picks individual cards inside the section
```

**How card_probe_selector changes heuristic scope:**

| Heuristic | Without `card_probe_selector` | With `card_probe_selector` |
|---|---|---|
| `bullets` / `color-swatches` | scanned across whole section | scanned per individual card |
| `multi-paragraph` (section controls) | counts every `<p>` in section | section soup minus card subtrees |
| `multi-paragraph` (card controls) | n/a — runs against section | runs per card, against that card only |
| `slider-images` / `inline-svg-icon` | `template_index` = section index | `template_index` = card index within section |

Note: `multi-paragraph` is skipped for textarea fields whose name is in the
SVG attribute list (`icon_svg`, `svg`, `background_svg`, …) since those carry
raw markup, not human paragraphs.

### card_skip_selector — exclude decorative cards

Some sections render a static "statement" card from the parent block rather
than from a card-template entry — but it shares the card class
(`.feature-statement` also has `.feature-card`). Without intervention, the
linter counts it as an extra card-template instance and reports a phantom
`template[N]` overflow.

```yaml
- slug: features
  probe_selector: '.features-section'
  card_probe_selector: '.feature-card'
  card_skip_selector: '.feature-statement'   # exclude statement from per-card loop
```

DOM matches are filtered: `card_probe_selector` minus `card_skip_selector`.
The skipped element is still available for section-level checks via
`target_selector` (see below).

### target_selector — scope multi-paragraph to a sub-element

A card may contain multiple sibling `<p>` blocks belonging to different
controls (e.g. `.model-tagline` + `.model-description` + `.model-disclaimer`).
The default `multi-paragraph` heuristic counts all of them — a false positive
for a control like `description` which actually owns only the middle block.

Set `target_selector` on the control to scope the check:

```yaml
controls:
  - id: c_mc_description
    name: description
    type: textarea
    target_selector: '.model-description'   # count <p> only inside this
    default: "…"
```

If `target_selector` is set but does not match any element in the current
scope, the check is silently skipped (no error, no warning). This makes it
safe to apply `target_selector` even when the same control rendering is
optional.

If `probe_selector` is missing, the block is **skipped** with a warning. To
enforce coverage, run with `--json` and grep for `"warning"`.

## Gate behavior

`scripts/gate-check.sh` invokes the linter automatically when checking stage-08.
Stage-08 cannot close until lint exits 0.

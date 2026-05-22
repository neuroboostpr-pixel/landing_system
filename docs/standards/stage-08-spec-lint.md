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

Every block in `block-spec.yaml` that should be linted MUST set:

```yaml
- slug: model-card
  probe_selector: '.model-card'    # CSS selector that finds this block in composed.html
  probe_kind: card-collection      # "single" | "card-collection"; default "single"
```

If `probe_selector` is missing, the block is **skipped** with a warning. To
enforce coverage, run with `--json` and grep for `"warning"`.

## Gate behavior

`scripts/gate-check.sh` invokes the linter automatically when checking stage-08.
Stage-08 cannot close until lint exits 0.

---
type: script
name: check-block-registration
language: bash
sources: ["scripts/lib/check-block-registration.sh"]
updated: 2026-05-18
---

# check-block-registration.sh

Hard-check: Lazy Blocks registration present in functions.php.
We register via lazyblocks()->add_block( inside an lzb/init action hook,
not register_block_type. Bypassed by legacy:true in .landing-state.yaml.

## Источник

- `scripts/lib/check-block-registration.sh`

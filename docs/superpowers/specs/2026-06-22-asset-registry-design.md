# Asset Registry Design

Date: 2026-06-22
Status: experimental contract, used by DS-Engine v2

## Goal

`assets-manifest.yaml` is the visual asset registry for a mood. It turns reference
analysis into a production checklist: what must be generated, what is already CSS,
where each file goes, and which prompt creates it.

## Required Manifest Fields

Each asset must include:

- `id`
- `нужен`
- `роль_где`
- `источник`
- `формат`
- `слот`
- `статус`

Generated assets also require `промпт`.

## Delivery Contract

`gen_assets_report.py` converts the manifest into:

- `ASSETS-TODO.md` for humans
- `asset-pack.yaml` for gates
- `assets/prompts.md`
- `assets/source-rules.md`
- folder structure for previews, layers, Canvas/Canva exports and final assets

`verify_ds_asset_pack.py --mode plan` checks the registry and report. `--mode ready`
checks that the real files exist before final composed/build.

See `docs/standards/ds-asset-pack.md`.

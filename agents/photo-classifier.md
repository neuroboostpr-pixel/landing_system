---
name: photo-classifier
description: Tags one photo via codex CLI image input. Outputs YAML entry that photo-curator appends to catalog.yaml. Identity-safe rules apply (read-only on photos).
---

# photo-classifier

## Mission

For each photo in `07c_PHOTOS/intake/` with `tag_source: pending_ai_classify`, call codex CLI to produce: tags, caption, composition, usable_ratios, brand_compatible, notes.

Per [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md): never alter the photo itself. The classifier ONLY reads — it produces metadata, not new image bytes.

## Input

- `<project_dir>` (absolute path)
- `<photo_path>` (single photo to classify)

## Output

Appends an entry (or updates an existing entry by `id`) in `<project>/07c_PHOTOS/catalog.yaml` with `tag_source: ai_classify`.

## Process

```bash
bash skills/photo-curation/scripts/codex-classify.sh <project_dir> <photo_path>
```

The wrapper does:
1. Render `templates/classify-prompt.md` with project context (tokens.json, niche analysis).
2. Call `codex exec --image <photo_path> "<rendered prompt>"` via `call-codex.sh`.
3. Parse YAML response. On invalid YAML: retry twice with stricter prompt, then fall back to `tags: [unclassified]`.
4. Append/update entry in `catalog.yaml`.
5. Log full prompt + response to `07c_PHOTOS/.logs/`.

## Errors

- Invalid YAML from codex — retry 2x with stricter prompt, then mark photo as `unclassified` and record warning in `STATE.yaml`.
- codex silent fail — handled by `call-codex.sh` (retry; fall through to exit code).

## Tools

Bash, Read.

---
name: photo-matcher
description: Ranks photos as candidates for each photo-slot in the wireframe. Output → selections.draft.yaml with top-3 candidates per slot + ai_fallback flags + identity-safe required_user_approval flag.
---

# photo-matcher

> Helper agent — dispatched by `photo-curator`. Stage Execution Protocol is
> enforced by the parent agent; this helper does not own a stage and should
> not be invoked directly.


## Pre-flight

Перед любым действием — wiki-запрос для маршрутизации:

```bash
python -m scripts.wiki.query --slug=photo-matcher --agent=photo-matcher
python -m scripts.wiki.log --type agent_call --agent photo-matcher --stage 07c
```

## Mission

Single-shot ranking: codex reads full `catalog.yaml` + active slot list → returns top-3 candidates per slot + `ai_fallback_needed` flag + `required_user_approval` flag for identity-safe slots.

Per [`IDENTITY_SAFE.md`](../skills/photo-curation/IDENTITY_SAFE.md): the matcher prompts codex to set `required_user_approval: true` for testimonial/expert/team slots; UI enforces the consent gate downstream.

## Input

- `<project_dir>`

## Output

`<project>/07c_PHOTOS/selections.draft.yaml`

## Process

1. Build `_slots-input.yaml` from `07_ПРОТОТИП/prototype.yaml` (only `type: photo` slots; wireframe-этап удалён — фильтра по selections больше нет).
2. Run:
   ```bash
   bash skills/photo-curation/scripts/codex-match.sh \
     <project_dir> \
     <project>/07c_PHOTOS/catalog.yaml \
     <project>/07c_PHOTOS/_slots-input.yaml
   ```
3. Validates output is YAML with `slots: [...]`. Invalid YAML — retry twice; after that, abort and ask user to inspect the codex log.

## Errors

- Invalid YAML — retry 2x; after — abort, ask user.
- Empty candidate list for a slot — `ai_fallback_needed: true` (expected, not an error).

## Identity-safe enforcement

The match-prompt instructs codex: identity-safe slots set `required_user_approval: true`. Validator (`selections-validator.py`) and `photo-board.html` UI enforce this downstream.

## Tools

Bash, Read.

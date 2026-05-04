---
name: references-collection
description: Maintains 03_РЕФЕРЕНСЫ/index.yaml — tracks reference URLs, files, and statuses (candidate/approved/rejected). Owned by references-curator agent.
---

# references-collection

## What I do

CRUD on a YAML index of references with statuses. Subcommands:
- `add <refs-dir> <ref> [--type url|file] [--status candidate|approved|rejected]`
- `update <refs-dir> <ref-id> --status <new>`
- `list <refs-dir> [--status <filter>]`
- `show <refs-dir> <ref-id>`
- `remove <refs-dir> <ref-id>`

See [scripts/index.py](scripts/index.py).

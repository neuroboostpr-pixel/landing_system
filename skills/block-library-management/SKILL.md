---
name: block-library-management
description: Manage the shared block-library — scaffold new blocks, validate catalog and per-block meta.yaml schemas. Used by ux-composer at injection time.
---

# block-library-management

Утилиты для управления `block-library/`:

- `scripts/validate-catalog.py <path>` — валидировать `catalog.yaml`
- `scripts/validate-meta.py <path>` — валидировать `meta.yaml` блока
- `scripts/scaffold-block.py --id <id> --category <cat>` — создать новый блок из шаблона

См. также: `block-library/README.md`.

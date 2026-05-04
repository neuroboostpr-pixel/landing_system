---
name: landing-versioning-and-cloning
description: Create version snapshots, rollback to previous versions, and create A/B clones of landing projects.
---

# landing-versioning-and-cloning

## Scripts

### create-version.sh
```bash
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> [version-label]
```
Saves snapshot to `09_ВЕРСИИ/<version>/`.

### clone-landing.sh
```bash
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```
Creates full project copy for A/B testing.

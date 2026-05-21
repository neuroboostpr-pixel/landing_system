---
name: landing-versioning-and-cloning
description: Create version snapshots, rollback to previous versions, and create A/B clones of landing projects (LEGACY single-site model only — for multisite, use skills/wp-multisite).
---

# landing-versioning-and-cloning

> ⚠️ **DEPRECATED для модели multisite.** Этот скилл клонирует проект целиком
> как **отдельный WP-инстанс** (filesystem copy + новый .env). Для новой
> модели «один клиентский домен = WP Multisite сеть с сегментами целевой аудитории»
> используйте `skills/wp-multisite/scripts/clone-subsite.sh`.
>
> Этот скилл оставлен для legacy single-site проектов без multisite-миграции.

## Scripts

### create-version.sh
```bash
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> [version-label]
```
Saves snapshot to `09_ВЕРСИИ/<version>/`. Не зависит от multisite — работает
для любого проекта.

### clone-landing.sh (legacy)
```bash
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```
Создаёт полную filesystem-копию проекта. **Только для single-site проектов.**
Для multisite сегментов используйте `clone-subsite.sh`.

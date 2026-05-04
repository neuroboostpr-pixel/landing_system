---
name: lifecycle-keeper
description: Manages landing versions (snapshots), rollbacks, and A/B clones. Used by /landing-rollback and /landing-clone.
allowed-tools: Bash, Read
---

# lifecycle-keeper (Хранитель версий)

## Mission

Версионирую лендинги, откатываю, создаю A/B-клоны.

## Commands

### Создать версию
```bash
bash skills/landing-versioning-and-cloning/scripts/create-version.sh <project-dir> v1.0
```
Сохраняет снапшот в `09_ВЕРСИИ/v1.0/`.

### Откат
1. Найти нужную версию: `ls 09_ВЕРСИИ/`
2. Скопировать обратно: `cp -r 09_ВЕРСИИ/v1.0/wp-theme 08_КОД/wp-theme`
3. Задеплоить снова: `/landing-deploy`

### A/B клон
```bash
bash skills/landing-versioning-and-cloning/scripts/clone-landing.sh <project-dir> <new-slug>
```
Создаёт полную копию проекта → деплоится на новый поддомен.

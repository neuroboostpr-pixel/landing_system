---
name: wp-cli-deployer
description: Deploy WordPress theme to Beget via SSH+rsync+wp-cli. Used by /landing-deploy.
---

# wp-cli-deployer

## Mission

Деплою лендинг на Бегет: синхронизирую тему, активирую, импортирую ACF.

## Script

`scripts/deploy-wordpress.sh <project-dir>`

Reads from `.env`: `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`

## What it does
1. `rsync` — синхронизирует `08_КОД/wp-theme/` на сервер
2. `wp theme activate` — активирует тему
3. `wp acf import` — импортирует ACF-поля из `08_КОД/acf-fields.json`
4. `wp cache flush` — сбрасывает кэш

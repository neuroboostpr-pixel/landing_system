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

## lp-preview-panel activation

After plugin sync, activate:

```bash
wp plugin activate lp-preview-panel
```

On first activation, the plugin defaults to `visible_to_anon = false`, so the
panel is admin-only on production by default. To enable client-facing preview:
admin → Settings → Превью-панель → "Показывать панель превью анонимным
посетителям" → save.

Deploy checklist add-on: before announcing a deploy to the client, open the
site in an incognito window and confirm the panel is either present (intended)
or absent (intended). No surprises.

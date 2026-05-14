---
name: wp-cli-deployer
description: Deploy WordPress theme to Beget via SSH+rsync+wp-cli. Used by /landing-deploy.
---

# wp-cli-deployer

## Mission

Деплою лендинг на Бегет: синхронизирую тему, ставлю плагины, импортирую
изображения в Media Library, подставляю их ID в page-content и сидирую главную
страницу как Gutenberg-страницу.

## Script

`scripts/deploy-wordpress.sh <project-dir>`

Reads from `.env`: `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`

## What it does

1. **rsync** — синхронизирует `08_КОД/wp-theme/` на сервер.
2. **`wp theme activate`** — активирует тему.
3. **Plugins** — устанавливает и активирует `lazy-blocks` (рендеринг блоков).
   ACF Free остаётся установленным как no-op (для возможных page-level meta-полей);
   `wp acf import` больше не вызывается.
4. **Media import** — для каждого файла в `theme/assets/img/*` вызывает
   `wp media import` идемпотентно: пропускает, если attachment с таким slug
   уже существует. Возвращает attachment ID для каждого имени файла.
5. **Page-content substitution** — заменяет placeholders
   `__IMAGE_ATTACHMENT_ID__<file>__` в `08_КОД/page-content.html` на bare
   integer literals (см. контракт `generate-page-content.py`).
6. **Front page seed** — `wp post create --post_type=page` с обработанным
   page-content (идемпотентно: при существующем slug делает `wp post update`),
   затем `wp option update show_on_front page` + `page_on_front=<id>`.
7. **`wp cache flush`** — сбрасывает кэш.

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

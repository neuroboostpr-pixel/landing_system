---
name: wp-theme-assembler
description: Bundle fonts/icons/images into wp-theme assets; render static build-preview.html. Used after wp-builder agent completes stage 08.
---

# wp-theme-assembler

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill wp-theme-assembler --stage 08
```

Финальная сборка темы: загрузка ресурсов + генерация preview.

## Scripts

### bundle-assets.py

- Записывает CDN-заглушки для шрифтов (Font Name + CDN) в `assets/fonts/`
- Скачивает SVG-иконки с Iconify API → `assets/icons/`
- Копирует `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` → `assets/images/`

```bash
python3 skills/wp-theme-assembler/scripts/bundle-assets.py <project-dir>
# stdout: JSON {"fonts": [...], "icons": [...], "images_copied": N}
```

### render-build-preview.py

Читает `tokens.json` + `design-stack.yaml` + `block-spec.yaml` + список Lazy Blocks
(сканирует `08_КОД/wp-theme/blocks/lazyblock-*/`).
Рендерит `08_КОД/build-preview.html` через Jinja2 (`build-preview.html.j2`).
Preview показывает: цветовые токены, типографику, стек, список Lazy Blocks, контролы из block-spec.

```bash
python3 skills/wp-theme-assembler/scripts/render-build-preview.py <project-dir>
# stdout: path to build-preview.html
```

## Usage sequence

```
1. wp-builder agent завершил Lazy Blocks (blocks/lazyblock-*/block.php) + CSS/JS
2. integrations-engineer добавил forms в functions.php
3. analytics-engineer добавил Metrika код
4. seo-optimizer добавил meta tags
5. Run bundle-assets.py → скачиваем ресурсы
6. Run render-build-preview.py → генерируем preview
7. HARD GATE: показываем build-preview.html пользователю
```

## lp-preview-panel integration

During theme assembly:

1. Copy plugin source:

   ```bash
   cp -r "$LANDING_SYSTEM_ROOT/template/08_КОД/plugins/lp-preview-panel" \
         "$PROJECT_ROOT/08_КОД/plugins/"
   ```

2. Generate palette CSS:

   ```bash
   python scripts/generate-palette-css.py --project "$PROJECT_ROOT"
   ```

   Output: `$PROJECT_ROOT/08_КОД/wp-theme/assets/css/palettes.css`.
   Include this file in the theme's main stylesheet enqueue.

3. Generate axes filter PHP:

   ```bash
   python scripts/generate-axes-filter.py \
       --project "$PROJECT_ROOT" \
       --default-palette <chosen-palette-id> \
       --hero static,parallax \
       --default-hero static
   ```

   Output: `$PROJECT_ROOT/08_КОД/wp-theme/inc/lp-preview-panel-axes.php`.
   In `functions.php` add: `require_once get_template_directory() . '/inc/lp-preview-panel-axes.php';`

4. Theme contract: any block whose visibility depends on hero variant must use
   `body.hero--<id>` selectors, with both variants present in DOM (visibility
   toggled by CSS). Non-active hero assets should use `loading="lazy"`.

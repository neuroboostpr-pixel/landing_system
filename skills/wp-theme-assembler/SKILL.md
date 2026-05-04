---
name: wp-theme-assembler
description: Bundle fonts/icons/images into wp-theme assets; render static build-preview.html. Used after wp-builder agent completes stage 08.
---

# wp-theme-assembler

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

Читает `tokens.json` + `design-stack.yaml` + `acf-fields.json` + список template-parts.
Рендерит `08_КОД/build-preview.html` через Jinja2 (`build-preview.html.j2`).
Preview показывает: цветовые токены, типографику, стек, template parts, ACF-группы.

```bash
python3 skills/wp-theme-assembler/scripts/render-build-preview.py <project-dir>
# stdout: path to build-preview.html
```

## Usage sequence

```
1. wp-builder agent завершил template-parts + CSS/JS
2. integrations-engineer добавил forms в functions.php
3. analytics-engineer добавил Metrika код
4. seo-optimizer добавил meta tags
5. Run bundle-assets.py → скачиваем ресурсы
6. Run render-build-preview.py → генерируем preview
7. HARD GATE: показываем build-preview.html пользователю
```

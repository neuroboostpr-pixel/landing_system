---
type: skill
name: wp-theme-assembler
sources: ["skills/wp-theme-assembler/SKILL.md"]
updated: 2026-05-26
triggers: []
stage: "08"
uses: ["wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "lp-preview-panel", "landing-build"]
tags: ["assets", "preview", "theme", "fonts", "icons", "images", "stage-08"]
---

# wp-theme-assembler — финальная сборка темы WordPress

## Что делает
Собирает все ресурсы темы (шрифты, иконки, изображения) в папку `assets/` и генерирует HTML-превью готовой темы с цветовыми токенами, типографикой и списком Lazy Blocks. Это последний шаг перед показом результата пользователю на этапе 08.

## Когда вызывать / в каком этапе
Запускается на этапе **08 (Сборка темы)** после того, как все остальные агенты этапа завершили свою работу:
1. `wp-builder` создал Lazy Blocks и CSS/JS
2. `integrations-engineer` добавил формы в `functions.php`
3. `analytics-engineer` встроил код Яндекс.Метрики
4. `seo-optimizer` прописал мета-теги

После этого последовательно запускаются два скрипта, завершающиеся **HARD GATE**: пользователь должен одобрить `build-preview.html` перед переходом к этапу 09.

## Что на вход / на выход

**Вход:**
- `tokens.json` — дизайн-токены проекта
- `design-stack.yaml` — стек технологий
- `block-spec.yaml` — спецификация блоков
- `08_КОД/wp-theme/blocks/lazyblock-*/` — собранные Lazy Blocks
- `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` — обработанные фото клиента

**Выход:**
- `assets/fonts/` — CDN-заглушки для шрифтов
- `assets/icons/` — SVG-иконки с Iconify API
- `assets/images/` — скопированные фото клиента
- `08_КОД/build-preview.html` — визуальное превью темы
- `08_КОД/wp-theme/assets/css/palettes.css` — CSS-палитра (если подключён lp-preview-panel)
- `08_КОД/wp-theme/inc/lp-preview-panel-axes.php` — PHP-фильтр осей превью

## Ключевые скрипты

**`bundle-assets.py`** — загружает ресурсы:
```bash
python3 skills/wp-theme-assembler/scripts/bundle-assets.py <project-dir>
# stdout: JSON {"fonts": [...], "icons": [...], "images_copied": N}
```

**`render-build-preview.py`** — генерирует превью через Jinja2:
```bash
python3 skills/wp-theme-assembler/scripts/render-build-preview.py <project-dir>
# stdout: путь к build-preview.html
```

**lp-preview-panel** — опциональный плагин с переключателем палитр и вариантов hero. Активируется копированием плагина + генерацией CSS/PHP через `generate-palette-css.py` и `generate-axes-filter.py`.

## Связанные концепты
- [[wp-builder]] — создаёт Lazy Blocks и тему, после которых запускается сборка
- [[integrations-engineer]] — добавляет формы в `functions.php` перед сборкой
- [[analytics-engineer]] — добавляет Метрику перед сборкой
- [[seo-optimizer]] — добавляет мета-теги перед сборкой
- [[landing-build]] — родительская команда этапа 08, вызывающая этот скилл
- [[lp-preview-panel]] — плагин переключения палитр, интегрируемый при сборке

## Источник
- `skills/wp-theme-assembler/SKILL.md`
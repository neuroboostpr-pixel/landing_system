---
type: skill
name: wp-theme-assembler
sources: ["skills/wp-theme-assembler/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "08"
uses: ["wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "lp-preview-panel", "landing-build"]
tags: ["theme", "assets", "preview", "fonts", "icons", "images", "stage-08"]
---

# wp-theme-assembler — Финальная сборка WordPress-темы

## Что делает
Собирает все ресурсы темы воедино: загружает шрифты, скачивает SVG-иконки, копирует обработанные фото клиента — и генерирует статичный `build-preview.html`, который показывает пользователю цвета, типографику, стек и список готовых блоков перед деплоем.

## Когда вызывать / в каком этапе
Вызывается на этапе **08 (Сборка темы)** — после того как `wp-builder` создал Lazy Blocks, `integrations-engineer` добавил формы, `analytics-engineer` добавил Метрику, а `seo-optimizer` прописал мета-теги. Это финальный шаг перед HARD GATE — показом preview пользователю.

## Что на вход / на выход

**Вход:**
- `<project>/tokens.json` — дизайн-токены (цвета, шрифты)
- `<project>/design-stack.yaml` — стек технологий
- `<project>/block-spec.yaml` — спецификация блоков
- `<project>/08_КОД/wp-theme/blocks/lazyblock-*/` — собранные Lazy Blocks
- `<project>/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` — обработанные фото клиента
- Font Name + CDN-адреса шрифтов
- Список иконок для Iconify API

**Выход:**
- `assets/fonts/` — CDN-заглушки шрифтов
- `assets/icons/` — скачанные SVG-иконки
- `assets/images/` — скопированные фото клиента
- `08_КОД/build-preview.html` — статичный preview темы
- `08_КОД/wp-theme/assets/css/palettes.css` — палитра CSS (через `generate-palette-css.py`)
- `08_КОД/wp-theme/inc/lp-preview-panel-axes.php` — фильтр осей preview-панели

## Ключевые скрипты

| Скрипт | Что делает |
|---|---|
| `bundle-assets.py <project>` | Загружает шрифты/иконки/фото; возвращает JSON с итогами |
| `render-build-preview.py <project>` | Рендерит `build-preview.html` через Jinja2 |
| `generate-palette-css.py --project` | Генерирует CSS с цветовыми палитрами |
| `generate-axes-filter.py --project` | Генерирует PHP-фильтр для lp-preview-panel |

## lp-preview-panel

Скилл интегрирует плагин `lp-preview-panel` — интерактивную панель переключения вариантов темы (палитра, тип hero). Блоки с hero-зависимостью рендерят оба варианта в DOM, видимость управляется через `body.hero--<id>` CSS-селекторы; неактивные ресурсы используют `loading="lazy"`.

## Связанные концепты
- [[wp-builder]] — создаёт Lazy Blocks до запуска сборки
- [[integrations-engineer]] — добавляет формы в functions.php перед сборкой
- [[analytics-engineer]] — добавляет код Метрики перед сборкой
- [[seo-optimizer]] — прописывает мета-теги перед сборкой
- [[lp-preview-panel]] — плагин интерактивного preview, подключается во время сборки
- [[landing-build]] — команда, запускающая этап 08 целиком

## Источник
- `skills/wp-theme-assembler/SKILL.md`
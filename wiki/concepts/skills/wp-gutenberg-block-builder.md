---
type: skill
name: wp-gutenberg-block-builder
sources: ["skills/wp-gutenberg-block-builder/SKILL.md"]
updated: 2026-05-25
triggers: []
stage: "08"
uses: ["landing-build", "landing-compose", "landing-design", "landing-deploy", "block-loader"]
tags: ["wordpress", "gutenberg", "lazy-blocks", "stage-08", "theme", "php"]
---

# wp-gutenberg-block-builder — Генератор WP-темы и Gutenberg-блоков

## Что делает
Автоматически создаёт WordPress-тему с блоками на базе **Lazy Blocks (free)** для лендинга: генерирует PHP-шаблоны блоков, регистрирует их в `functions.php`, подключает стили и визуальные паттерны, и собирает финальный `page-content.html` с Gutenberg-разметкой, готовый к деплою.

## Когда вызывать / в каком этапе
Запускается на **этапе 08** через команду `/landing-build` или оркестратор (`generate-wp-blocks.py`). Требует, чтобы были завершены этапы 05 (tokens.json), 06 (design-stack.yaml), 07 (final-copy.md) и заполнен файл `08_КОД/block-spec.yaml`. Без этих файлов генераторы прерываются с понятным сообщением.

## Что на вход / на выход

**Вход:**
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — цветовые токены, `style_mood`, `animation_mode`
- `06_СТЕК/design-stack.yaml` — конфигурация стека
- `07_КОНТЕНТ/final-copy.md` — утверждённые тексты
- `08_КОД/block-spec.yaml` — спецификация блоков лендинга

**Выход:**
- `08_КОД/wp-theme/style.css` — стилевой манифест темы
- `08_КОД/wp-theme/functions.php` — регистрация блоков через `add_block()`
- `08_КОД/wp-theme/assets/css/main.css` — CSS-патчи для InnerBlocks
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — по одному файлу на каждый блок
- `08_КОД/page-content.html` — Gutenberg-разметка страницы с плейсхолдерами изображений

## Ключевые детали

**5 генераторов** запускаются по порядку: theme → lzb-templates → lzb-registration → css-patches → page-content.

**Визуальные паттерны** (scroll-reveal, paper-texture, ambient-mesh-bg и др.) подключаются автоматически по значению `animation_mode` или `style_mood` из `tokens.json`. Например, `cinematic` включает scroll-reveal + ambient-mesh-bg + paper-texture.

**6 style moods** (brutalist, editorial-warm, swiss-modernist и др.) — каждый задаёт набор CSS-файлов и паттернов. Переопределяют `animation_mode`.

**Block Library Loader** (`scripts/block-loader.py`) используется для чтения блоков из `block-library/` — поддерживает оба формата (старый ru-* и новый imported).

**Что НЕ генерируется:** `acf-fields.json`, `block.json`, `front-page.php`, `template-parts/`. Формы, аналитика и SEO — отдельные генераторы в `/landing-build`.

**Существующий `block.php` не перезаписывается** — ручные правки блоков безопасны при повторном запуске.

## Связанные концепты
- [[landing-build]] — главная команда этапа 08, запускает этот скилл
- [[landing-deploy]] — следующий этап; использует `page-content.html` из этого скилла
- [[landing-design]] — этап 05, поставляет `tokens.json` на вход
- [[landing-compose]] — этап 07b, поставляет финальный HTML как основу для spec

## Источник
- `skills/wp-gutenberg-block-builder/SKILL.md`
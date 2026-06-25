---
slug: wp-theme-assembler
type: skill
name: "WP Theme Assembler — сборка ресурсов и build-preview"
stage: "08"
tags: [wp-theme, assets, preview, fonts, icons, images, stage-08]
triggers: [landing-build]
inputs: [08-kod, 05-dizayn-sistema, 07b-composed]
outputs: [08-kod]
gates: []
pre_reqs: [wp-builder, integrations-engineer, analytics-engineer, seo-optimizer]
related: [wp-builder, landing-build, 08-kod, integrations-engineer, analytics-engineer, seo-optimizer, landing-previews]
sources: ["skills/wp-theme-assembler/SKILL.md"]
updated: 2026-06-22
confidence: {triggers: low}
---

# WP Theme Assembler — сборка ресурсов и build-preview

## Что делает

Финализирует сборку WordPress-темы после того, как все инженеры этапа 08 завершили свою работу. Скилл выполняет два шага: сначала `bundle-assets.py` подтягивает CDN-заглушки шрифтов, скачивает SVG-иконки с Iconify API и копирует обработанные фотографии клиента в `assets/`; затем `render-build-preview.py` генерирует статичный `build-preview.html`, который наглядно показывает токены, типографику, стек и список Lazy Blocks. Дополнительно подключается плагин `lp-preview-panel`: копируется исходник плагина, генерируются `palettes.css` и PHP-фильтр осей, позволяющий переключать режимы отображения темы без публикации.

## Когда вызывается

Запускается как часть команды `/landing-build` (этап 08) — после того, как `wp-builder` завершил Lazy Blocks, `integrations-engineer` добавил формы, `analytics-engineer` — код Метрики, а `seo-optimizer` — мета-теги. Это последний шаг перед показом preview пользователю на HARD GATE.

## Вход → выход

**Вход:** готовый код темы в `08_КОД/wp-theme/` (Lazy Blocks, CSS, JS), файлы `tokens.json`, `design-stack.yaml`, `block-spec.yaml`, фотографии в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/`.

**Выход:** заполненная папка `assets/` (шрифты, иконки, изображения); файл `08_КОД/build-preview.html` для review пользователем; `palettes.css` и `lp-preview-panel-axes.php` для плагина переключения палитр.

## Failure modes

- **Iconify API недоступен** — иконки не скачаются, в `assets/icons/` останутся пустые слоты; сборка формально не падает, но preview будет неполным.
- **Отсутствует `tokens.json`** — `render-build-preview.py` не сможет отрисовать цветовую секцию preview; скрипт упадёт с KeyError.
- **Нет обработанных фото в `photos/processed/`** — `bundle-assets.py` скопирует 0 файлов; изображения в preview не появятся без сообщения об ошибке.
- **`palettes.css` не подключён в enqueue темы** — переключатель палитр (`lp-preview-panel`) не заработает; ошибка проявляется только на живом сайте, не в preview.
- **Lazy Blocks не созданы** — `render-build-preview.py` не найдёт папок `lazyblock-*/` и нарисует пустой список блоков, что введёт в заблуждение на HARD GATE.

## Related

- [[wp-builder]] — создаёт Lazy Blocks и CSS/JS темы; обязателен до запуска wp-theme-assembler
- [[landing-build]] — родительская команда, в рамках которой вызывается этот скилл
- [[08-kod]] — папка-артефакт: вход и выход одновременно
- [[integrations-engineer]] — добавляет формы в `functions.php` перед сборкой
- [[analytics-engineer]] — добавляет Метрику перед сборкой
- [[seo-optimizer]] — добавляет мета-теги перед сборкой
- [[landing-previews]] — смежный механизм генерации превью на других этапах
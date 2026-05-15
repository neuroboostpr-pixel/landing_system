---
type: skill
name: wp-theme-assembler
sources: ["skills/wp-theme-assembler/SKILL.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["wp-builder", "integrations-engineer", "analytics-engineer", "seo-optimizer", "landing-build"]
tags: ["wordpress", "theme", "assets", "build", "preview"]
---

# wp-theme-assembler — Финальная сборка WordPress-темы

## Что делает

Собирает готовую WordPress-тему: скачивает шрифты, SVG-иконки и обрабатывает фотографии в папку `assets/`, затем рендерит HTML-превью (`build-preview.html`), который показывает маркетологу финальный вид сайта до деплоя.

## Когда вызывать / в каком этапе

Этап **08** — после того как завершили работу все четыре предшествующих агента:
1. `wp-builder` — написал Lazy Blocks (`block.php`) + CSS/JS;
2. `integrations-engineer` — добавил формы в `functions.php`;
3. `analytics-engineer` — добавил код Яндекс.Метрики;
4. `seo-optimizer` — добавил мета-теги.

После этого запускаются два скрипта скилла, и их результат проходит **HARD GATE** — пользователь обязан утвердить `build-preview.html` перед деплоем.

## Что на вход / на выход

**Вход:**
- `<project>/04_БРЕНД/tokens.json` — дизайн-токены
- `<project>/06_СТЕК/design-stack.yaml` — стек (шрифты, иконки)
- `<project>/08_КОД/block-spec.yaml` — спецификация Lazy Blocks
- `<project>/08_КОД/wp-theme/blocks/lazyblock-*/` — скомпилированные блоки
- `<project>/02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/` — обработанные фото клиента

**Выход:**
- `assets/fonts/` — CDN-заглушки шрифтов
- `assets/icons/` — SVG-иконки (Iconify API)
- `assets/images/` — скопированные фото клиента
- `08_КОД/build-preview.html` — финальный HTML-превью темы
- `08_КОД/wp-theme/assets/css/palettes.css` — CSS цветовых палитр (lp-preview-panel)
- `08_КОД/wp-theme/inc/lp-preview-panel-axes.php` — фильтры осей превью-панели

## Ключевые скрипты

| Скрипт | Что делает |
|---|---|
| `bundle-assets.py <project-dir>` | Скачивает иконки с Iconify, фиксирует CDN-ссылки шрифтов, копирует фото |
| `render-build-preview.py <project-dir>` | Читает токены + стек + блоки → рендерит `build-preview.html` через Jinja2 |

Скрипты возвращают JSON/путь в stdout, пригодный для автоматического pipeline.

## lp-preview-panel

Скилл также интегрирует плагин `lp-preview-panel`: копирует его в проект, генерирует `palettes.css` с цветовыми вариантами и `lp-preview-panel-axes.php` с вариантами hero-секции (static / parallax). Блоки, зависящие от типа hero, используют CSS-классы `body.hero--<id>` — оба варианта присутствуют в DOM, видимость переключается через CSS без перезагрузки.

## Связанные концепты

- [[wp-builder]] — генерирует Lazy Blocks и CSS/JS, которые сборщик упаковывает
- [[integrations-engineer]] — добавляет формы до запуска сборки
- [[analytics-engineer]] — добавляет Метрику до запуска сборки
- [[seo-optimizer]] — добавляет мета-теги до запуска сборки
- [[landing-build]] — команда, которая оркестрирует весь этап 08 включая этот скилл
- [[design-tokens-generation]] — производит `tokens.json`, который читает `render-build-preview.py`
- [[stack-planner]] — производит `design-stack.yaml` с перечнем шрифтов и иконок

## Источник

- `skills/wp-theme-assembler/SKILL.md`
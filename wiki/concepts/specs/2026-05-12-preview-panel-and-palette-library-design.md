---
type: rule
name: preview-panel-and-palette-library
sources: ["docs/superpowers/specs/2026-05-12-preview-panel-and-palette-library-design.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - landing-brand
  - landing-design
  - landing-build
  - landing-deploy
  - wp-theme-assembler
  - brand-kit-build
  - design-tokens-generation
  - wp-cli-deployer
tags: ["palette", "plugin", "preview", "wp", "design-system"]
---

# Preview Panel + Global Palette Library

## Что делает

Описывает архитектуру двух связанных компонентов: WordPress-плагина `lp-preview-panel`, который показывает на сайте панель переключения палитр и hero-вариантов без перезагрузки страницы, и глобальной библиотеки палитр (`presets/palettes.yaml`), накапливающей все утверждённые цветовые схемы из всех проектов для повторного использования.

## Когда вызывать / в каком этапе

Архитектура вступает в силу на нескольких этапах:

- **Этап 05 `/landing-design`** — после апрува дизайн-системы (HARD GATE) скрипт экспортирует новые палитры из `05_ДИЗАЙН-СИСТЕМА/palettes.yaml` в `presets/palettes.yaml` (дедупликация по `id`).
- **Этап 04 `/landing-brand`** — агент предлагает палитры из библиотеки в одном из трёх режимов (1–3 / 4–6 / весь каталог), результат снапшотится в `04_БРЕНД/palettes.yaml`.
- **Этап 08 `/landing-build`** — `wp-theme-assembler` копирует плагин из шаблона, генерирует `assets/css/palettes.css` с классами `body.theme-<id>` и вставляет фильтр `lp_preview_panel_axes` в `functions.php`.
- **Этап 09 `/landing-deploy`** — `wp-cli-deployer` активирует плагин; чек-лист требует убедиться, что `visible_to_anon=false` на проде.

## Что на вход / на выход

**Вход:**
- `<project>/05_ДИЗАЙН-СИСТЕМА/palettes.yaml` — палитры, созданные на `/landing-design`
- `landing_system/presets/palettes.yaml` — глобальная библиотека (может быть пустой)
- `<project>/04_БРЕНД/palettes.yaml` — снапшот выбранных палитр

**Выход:**
- `template/08_КОД/plugins/lp-preview-panel/` — канонический WordPress-плагин с PHP-классами, JS-движком переключения осей и страницей в WP-админке
- `assets/css/palettes.css` — CSS-блоки `body.theme-<id> { --token: value; }` для каждой палитры проекта
- Обновлённая `presets/palettes.yaml` — накопленная библиотека всех утверждённых палитр

## Ключевые правила

- Панель скрыта от анонимов по умолчанию (`visible_to_anon=false`). Управляется через `Settings → Превью-панель` в WP-админке.
- Плагин не знает о конкретных палитрах — только о контракте `lp_preview_panel_axes`. Тема регистрирует оси через этот фильтр.
- Палитра и hero — независимые оси; смена одной не затрагивает другую.
- JS-приоритет применения: `URL ?palette=` → `localStorage` → серверный дефолт из WP-опции → `default` из фильтра темы.
- Экспорт в библиотеку происходит только после апрува (не из черновиков). При коллизии `id` — пропуск с notice, библиотечная запись сохраняется.

## Связанные концепты

- [[landing-brand]] — запрашивает режим выбора палитр из библиотеки (1–3 / 4–6 / весь каталог)
- [[landing-design]] — экспортирует новые палитры в библиотеку после HARD GATE
- [[landing-build]] — снапшотит палитры в тему, генерирует CSS и фильтр
- [[landing-deploy]] — активирует плагин, проверяет видимость панели на проде
- [[wp-theme-assembler]] — скилл, выполняющий генерацию CSS и `functions.php`
- [[brand-kit-build]] — скилл, дополненный шагом выбора палитр из библиотеки
- [[design-tokens-generation]] — скилл, связанный со структурой токенов палитры
- [[wp-cli-deployer]] — скилл, активирующий плагин через WP-CLI

## Источник

- `docs/superpowers/specs/2026-05-12-preview-panel-and-palette-library-design.md`
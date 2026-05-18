---
type: rule
name: preview-panel-and-palette-library-plan
sources: ["docs/superpowers/plans/2026-05-12-preview-panel-and-palette-library-plan.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses:
  - brand-kit-build
  - design-tokens-generation
  - wp-theme-assembler
  - wp-cli-deployer
  - paralaximus-codex
  - landing-brand
  - landing-design
  - landing-build
  - landing-deploy
tags: [palette, preview-panel, plugin, pipeline, migration, wordpress]
---

# Preview Panel + Global Palette Library — Plan

## Что делает

Описывает план замены хардкоженного переключателя палитр в neuroupgrade-v2 на переиспользуемый WP-плагин `lp-preview-panel` с двумя осями (palette + hero), глобальной библиотекой палитр и пайплайновой автоматикой для каждого нового проекта.

## Когда вызывать / в каком этапе

Применяется при разработке или доработке system-level функции preview-панели. Связан со стадиями 04 (`/landing-brand`), 05 (`/landing-design`) и 08 (`/landing-build`). Не вызывается пользователем напрямую — это внутренний план реализации фичи.

## Что на вход / на выход

**Вход:**
- `Lendings/neuroupgrade-v2/` — реальный проект для первой миграции
- `04_БРЕНД/palettes.yaml` — снапшот палитр проекта (19 токенов на палитру)
- `05_ДИЗАЙН-СИСТЕМА/palettes.yaml` — зеркало для экспортного хука

**Выход:**
- `template/08_КОД/plugins/lp-preview-panel/` — канонический PHP-плагин (4 класса + CSS + JS)
- `presets/palettes.yaml` — глобальная библиотека палитр (seed: nu-paper, nu-quiet-dark, nu-beige, nu-iqido)
- `scripts/validate-palettes.py` — валидатор схемы палитры (19 обязательных токенов)
- `scripts/export-palettes-to-library.py` — экспорт после approve стадии 05
- `scripts/snapshot-palettes-to-project.py` — копирование из библиотеки в проект на `/landing-brand`
- `scripts/generate-palette-css.py` — генерация `body.theme-<id> { --var: val; }` CSS
- `scripts/generate-axes-filter.py` — генерация PHP-файла с `lp_preview_panel_axes` фильтром
- `scripts/migrate-to-preview-panel.sh` — одноразовая миграция neuroupgrade-v2
- `tests/phase-preview-panel/*.bats` — ~33 bats-теста покрывающих pipeline
- `08_КОД/wp-theme/assets/css/palettes.css`, `inc/lp-preview-panel-axes.php` в каждом проекте

**Архитектурный контракт:**
- Класс-префиксы `body.theme-<id>` и `body.hero--<id>` зарезервированы плагином — тема не трогает их напрямую
- Схема палитры заморожена: 19 токенов, kebab-case id, YAML-ключ → CSS через замену `_` на `-`
- `visible_to_anon = false` по умолчанию — панель видят только администраторы

## Связанные концепты

- [[brand-kit-build]] — снапшот палитр из библиотеки на этапе `/landing-brand` (3 режима выбора)
- [[design-tokens-generation]] — экспортный хук после approve стадии 05
- [[wp-theme-assembler]] — копирование плагина, codegen CSS и axes-фильтра при сборке
- [[wp-cli-deployer]] — активация плагина и чеклист видимости панели при деплое
- [[paralaximus-codex]] — future-интеграция реального параллакс-слоя в hero--parallax ось

## Источник

- `docs/superpowers/plans/2026-05-12-preview-panel-and-palette-library-plan.md`
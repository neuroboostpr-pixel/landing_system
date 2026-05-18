---
type: stage
name: stage08-lazy-blocks-migration
sources: ["docs/superpowers/plans/2026-05-13-stage08-lazy-blocks-migration.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses:
  - wp-gutenberg-block-builder
  - wp-cli-deployer
  - landing-build
  - wp-builder
  - 08-kod
tags:
  - lazy-blocks
  - gutenberg
  - acf
  - code-generation
  - stage-08
---

# Stage-08 Миграция на Lazy Blocks

## Что делает

Переводит пайплайн генерации WordPress-блоков (этап 08) с устаревшего ACF Free + `register_block_type` подхода на Lazy Blocks Free через `lazyblocks()->add_block()`. Вводит артефакт `block-spec.yaml` как единый источник истины о структуре блоков лендинга — какие блоки существуют, их тип (`single` или `section-card`), controls и дефолты. Из этого файла четыре новых Python-генератора производят всё необходимое для рабочей Гутенберг-страницы.

## Когда вызывать / в каком этапе

Этап **08** (генерация кода), после утверждения `final-copy.md` (этап 07) и `DESIGN.md` (этап 05). Запускается через команду `/landing-build`. Предварительное условие — наличие заполненного `08_КОД/block-spec.yaml` (шаблон: `template/08_КОД/block-spec.example.yaml`).

Существующие задеплоенные лендинги (lixiang-dubai, neuroupgrade-old) **намеренно не мигрируются** — они продолжают работать через `front-page.php` на сервере до следующей регенерации.

## Что на вход / на выход

**Вход:**
- `08_КОД/block-spec.yaml` — описание блоков проекта (заполняется менеджером или скиллом `/landing-content`)
- `08_КОД/wp-theme/functions.php` — базовая тема (создаётся `generate-theme.py`)
- `08_КОД/wp-theme/assets/css/main.css` — стили темы
- `07_КОНТЕНТ/final-copy.md` — финальные тексты
- `08_КОД/wp-theme/assets/img/` — изображения для импорта в Media Library

**Выход:**
- `08_КОД/wp-theme/functions.php` — с секцией `lzb/init` (регистрация блоков)
- `08_КОД/wp-theme/blocks/lazyblock-<slug>/block.php` — PHP-шаблоны блоков
- `08_КОД/wp-theme/assets/css/main.css` — с патчами `display: contents` для section+card пар
- `08_КОД/page-content.html` — Гутенберг-разметка для seed'а фронт-страницы
- Живой WordPress-сайт с Lazy Blocks плагином, импортированными изображениями и установленной фронт-страницей

**Новые генераторы** (в `skills/wp-gutenberg-block-builder/scripts/`):
- `generate-lzb-registration.py` — пишет `lzb/init` блок в `functions.php`
- `generate-lzb-templates.py` — создаёт `block.php` шаблоны (не перезаписывает вручную отредактированные)
- `generate-css-patches.py` — добавляет `display: contents` правила в `main.css`
- `generate-page-content.py` — пишет `page-content.html` с Гутенберг-markup

**Удаляемые** (устаревшие): `generate-block-json.py`, `generate-block-registration.py`, `generate-acf.py`, режим `--blocks-only` в `generate-theme.py`, запись `front-page.php`.

## Связанные концепты

- [[wp-gutenberg-block-builder]] — скилл, содержащий все новые Python-генераторы и TDD-тесты
- [[wp-cli-deployer]] — скилл деплоя: получил install Lazy Blocks, `wp media import`, seed фронт-страницы через `wp post create`
- [[wp-builder]] — агент, выполняющий этап 08 в оркестраторе
- [[landing-build]] — команда, запускающая пайплайн stage-08
- [[08-kod]] — этап кодовой генерации в шаблоне проекта

## Источник

- `docs/superpowers/plans/2026-05-13-stage08-lazy-blocks-migration.md`
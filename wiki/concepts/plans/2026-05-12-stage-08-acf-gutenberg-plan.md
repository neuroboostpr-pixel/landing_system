---
type: stage
name: stage-08-acf-gutenberg-plan
sources: ["docs/superpowers/plans/2026-05-12-stage-08-acf-gutenberg-plan.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses:
  - wp-gutenberg-block-builder
  - wp-builder
  - landing-build
  - content-writer
  - wp-cli-deployer
  - stage-gates
tags: [stage-08, acf, gutenberg, wordpress, build, plan]
---

# Stage 08 — ACF Blocks + Gutenberg: план реализации

## Что делает

Описывает, как сделать `/landing-build` надёжным: скрипты автоматически генерируют ACF-поля и Gutenberg-блоки из `07_КОНТЕНТ/final-copy.md`, а gate блокирует деплой, если артефакты отсутствуют. Маркетолог получает редактируемые блоки в WordPress-сайдбаре без правки PHP.

## Когда вызывать / в каком этапе

Этап 08 (`08_КОД`). Запускается после того как `content-writer` сформировал `final-copy.md` и этап `07_content` одобрен. Точка входа — оркестратор `scripts/generate-wp-blocks.py --project <path>`, который вызывается агентом `wp-builder` или вручную через `/landing-build`.

## Что на вход / на выход

**Вход:**
- `07_КОНТЕНТ/final-copy.md` — единственный источник истины; каждый H2-заголовок становится одним блоком.
- `08_КОД/wp-theme/functions.php` — пре-существующий файл темы (сохраняется, не перезаписывается).

**Выход (четыре артефакта):**
- `08_КОД/acf-fields.json` — ACF Local JSON: группы полей, по одной на H2-блок; ключи детерминированы (`group_lp_<slug>`, `field_lp_<slug>_<field>`).
- `08_КОД/gutenberg-blocks/<slug>/block.json` — дескриптор блока (`apiVersion: 3`, namespace `acf/lp-<slug>`, категория `lp-blocks`).
- `08_КОД/wp-theme/functions.php` — дополняется секцией `AUTO-GENERATED` с регистрацией каждого блока и категории `lp-blocks`; код вне маркеров не трогается.
- `08_КОД/wp-theme/template-parts/block-<slug>.php` — PHP-шаблон рендера (создаётся только для отсутствующих файлов, существующие не перезаписываются).

**Архитектура трёх слоёв:**
- **Layer A** — `ContentParser` (Python + pytest): парсит H2 → `Block`, определяет типы полей (text/textarea/wysiwyg/url/image/repeater) по regex-эвристикам.
- **Layer B** — четыре генератора (Python + bats): `generate-acf.py`, `generate-block-json.py`, `generate-block-registration.py`, `generate-theme.py --blocks-only`.
- **Layer C** — hard gate + legacy-маркировка + backport (bash + Python): `stage_08_helper.py`, `gate-check.sh` с 10 проверками, `mark-legacy-projects.sh`, `backport-acf-to-legacy.sh`.

**Обход для legacy-проектов:** `legacy: true` в `.landing-state.yaml` пропускает все hard-checks; скрипт `backport-acf-to-legacy.sh` применяет генераторы к старым проектам и снимает флаг после успеха.

**Тесты:** ~60 тестов (pytest + bats): `npm run test:phase-stage-08`.

## Связанные концепты

- [[wp-gutenberg-block-builder]] — скилл, содержит сами скрипты генераторов
- [[wp-builder]] — агент этапа 08, вызывает оркестратор
- [[landing-build]] — команда, запускающая полный цикл этапа 08
- [[content-writer]] — производит `final-copy.md`, входной артефакт Layer A
- [[wp-cli-deployer]] — деплой; план исправляет silent-fail при `wp acf import`
- [[stage-gates]] — конфиг `config/stage-gates.yaml` дополняется 10 проверками `08_build`

## Источник

- `docs/superpowers/plans/2026-05-12-stage-08-acf-gutenberg-plan.md`
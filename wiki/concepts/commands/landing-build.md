---
slug: landing-build
type: command
name: "/landing-build — сборка WordPress-темы (этап 08)"
stage: "08"
tags: [build, wordpress, lazy-blocks, theme, analytics, seo, integrations]
triggers: [landing-build]
inputs:
  - 07_КОНТЕНТ/final-copy.md
  - 05_ДИЗАЙН-СИСТЕМА/tokens.json
  - 06_СТЕК/design-stack.yaml
  - 08_КОД/block-spec.yaml
outputs:
  - 08_КОД/wp-theme/
  - 08_КОД/page-content.html
  - 08_КОД/build-preview.html
  - 11_АНАЛИТИКА/
  - 12_SEO/
gates: [build-preview-approval]
pre_reqs: [07-kontent, 07b-composed, 05-dizayn-sistema, 06-stek]
related:
  - analytics-engineer
  - integrations-engineer
  - seo-optimizer
  - wp-gutenberg-block-builder
  - wp-theme-assembler
  - landing-deploy
  - 08-kod
sources: ["commands/landing-build.md"]
updated: 2026-06-22
---

# /landing-build — сборка WordPress-темы (этап 08)

## Что делает

Команда запускает детерминированный конвейер из 11 шагов, который превращает утверждённый макет `composed.html` и финальные тексты в полноценную WordPress-тему с Lazy Blocks, формами, аналитикой и SEO. Сначала конвертер `composed-to-build.py` генерирует `block-spec.yaml` из макета, затем пять Python-скриптов строят scaffolding темы, регистрацию блоков, CSS-патчи и Gutenberg-разметку страницы. Параллельно агенты `integrations-engineer`, `analytics-engineer` и `seo-optimizer` дописывают в `functions.php` CRM-хуки, Яндекс.Метрику и Schema.org. Заканчивается сборка созданием статического `build-preview.html` для финального одобрения.

## Когда вызывается

Запускается вручную командой `/landing-build` внутри папки проекта после того, как этапы 07 (контент) и 07b (composed.html) одобрены. Оркестратор `landing-orchestrator` может вызвать команду автоматически в рамках `/landing-go`. Если не пройдены онбординг или предыдущие гейты — команда останавливается с сообщением об ошибке.

## Вход → выход

**Вход:** `07_КОНТЕНТ/final-copy.md`, `05_ДИЗАЙН-СИСТЕМА/tokens.json`, `06_СТЕК/design-stack.yaml`, `07b_COMPOSED/composed.html`, `08_КОД/block-spec.yaml` (генерируется конвертером из composed).

**Выход:** `08_КОД/wp-theme/` (PHP + CSS + JS + ассеты), `08_КОД/page-content.html` (Gutenberg-разметка фронт-страницы), `08_КОД/build-preview.html` (статический превью для одобрения), `11_АНАЛИТИКА/metrika-config.md` + UTM-шаблоны, `12_SEO/meta-tags.yaml` + structured-data.

## Чем закрывается этап (gates)

- `build-preview-approval` — пользователь смотрит `08_КОД/build-preview.html` и явно подтверждает готовность к деплою; без этого этап 09 не открывается.

## Failure modes

- **Отсутствует `block-spec.yaml`** — генераторы 2–5 падают с явной ошибкой; нужно сначала запустить `composed-to-build.py`.
- **Гейт предыдущего этапа не пройден** — `gate-check.sh --stage 08_build` возвращает exit 1, команда прерывается и сообщает какой этап пропущен.
- **`block.php` не читает `$attributes`** — тексты в wp-admin не видны на сайте; ловится gate-чеком `block_php_uses_attributes`.
- **Прямые цвета вне `:root`** — `verify_tokens.py` падает; CSS-токенизация должна быть 100%, иначе переключатель мудов сломан.
- **Онбординг не пройден** — `setup-flag.sh is_complete` возвращает exit 1, команда не стартует.

## Related

- [[analytics-engineer]] — агент этапа 08, инжектирует Яндекс.Метрику и GTM
- [[integrations-engineer]] — агент этапа 08, добавляет CRM-вебхуки
- [[seo-optimizer]] — агент этапа 08, генерирует meta-теги и Schema.org
- [[wp-gutenberg-block-builder]] — скилл с Python-скриптами генерации (popup, JS, analytics, integrations)
- [[wp-theme-assembler]] — скилл с bundle-assets и render-build-preview
- [[landing-deploy]] — следующий этап (09) после одобрения build-preview
- [[08-kod]] — папка проекта, куда складываются все артефакты сборки
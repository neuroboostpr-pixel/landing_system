---
slug: landing-build
type: command
name: "/landing-build — Сборка WordPress-темы"
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
  - 08_КОД/integrations/
  - 11_АНАЛИТИКА/metrika-config.md
  - 12_SEO/meta-tags.yaml
gates: [build_preview_approved]
pre_reqs: [content-writer, design-system-generator, stack-planner]
related:
  - analytics-engineer
  - integrations-engineer
  - seo-optimizer
  - wp-builder
  - wp-gutenberg-block-builder
  - wp-cli-deployer
  - block-composer
sources: ["commands/landing-build.md"]
updated: 2026-05-26
---

# /landing-build — Сборка WordPress-темы

## Что делает

Команда запускает полный пайплайн генерации WordPress-темы для лендинга на этапе 08. Последовательно вызывает 11 шагов: детерминированные Python-генераторы (тема, Lazy Blocks, регистрация блоков, CSS-патчи, page-content), затем AI-агентов для форм/интеграций, аналитики и SEO, после чего собирает JS-библиотеки, popup-систему и финальный build-preview. Результат — полностью готовая WP-тема и статический превью для согласования с пользователем.

## Когда вызывается

Вызывается вручную командой `/landing-build` (или с флагом `--cinematic` для GSAP/ScrollTrigger) после того как контент-райтер завершил `07_КОНТЕНТ/final-copy.md` и пользователь его одобрил. Предварительно система проверяет флаг онбординга, gate этапа 08 и наличие `block-spec.yaml` — без любого из них сборка останавливается с диагностическим сообщением.

## Вход → выход

**Вход:** `final-copy.md` (контент), `tokens.json` (дизайн-токены), `design-stack.yaml` (стек), `block-spec.yaml` (спецификация блоков).

**Выход:** `08_КОД/wp-theme/` с PHP/CSS/JS, `page-content.html` с Gutenberg-разметкой, `build-preview.html` для финального согласования, конфиги аналитики в `11_АНАЛИТИКА/` и SEO-файлы в `12_SEO/`.

## Чем закрывается этап (gates)

- `build_preview_approved` — пользователь просматривает `08_КОД/build-preview.html` и явно подтверждает переход к деплою; без этого `gate-check.sh --approve` не выполняется и этап 09 не открывается.

## Failure modes

- Отсутствует `08_КОД/block-spec.yaml` — генераторы 2–5 падают с ошибкой, сборка останавливается полностью.
- Gate предыдущего этапа не закрыт — `gate-check.sh` возвращает exit 1, команда завершается до запуска генераторов.
- Онбординг не пройден (`setup_complete` не установлен) — команда отказывает с подсказкой `/landing-onboarding`.
- AI-агенты (`analytics-engineer`, `integrations-engineer`, `seo-optimizer`) могут вернуть неполный результат при нечётком брифе или отсутствии токенов CRM.
- `bundle-assets.py` не находит шрифты или фото — превью генерируется с плейсхолдерами, но деплой впоследствии может упасть на stage 09.

## Related

- [[analytics-engineer]] — агент аналитики: вставляет Yandex Metrika и GTM в functions.php
- [[integrations-engineer]] — агент интеграций: добавляет Fluent Forms / CRM-вебхук
- [[seo-optimizer]] — агент SEO: мета-теги и Schema.org
- [[wp-builder]] — скилл сборки WP-темы, вызывается внутри пайплайна
- [[wp-gutenberg-block-builder]] — скилл генерации popup, JS-инициализации и CSS-патчей
- [[wp-cli-deployer]] — следующий этап: деплой собранной темы на Beget
- [[block-composer]] — предшествующий этап: composed.html, из которого берётся структура блоков
- [[content-writer]] — поставляет `final-copy.md` как входной артефакт
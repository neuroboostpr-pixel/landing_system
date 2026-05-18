---
type: stage
name: phase-5-deploy-operations
sources: ["docs/superpowers/plans/2026-05-04-phase-5-deploy-operations.md"]
updated: 2026-05-18
triggers: []
stage: "09-12"
uses:
  - system-setup
  - wp-deployer
  - qa-auditor
  - lifecycle-keeper
  - wp-cli-deployer
  - landing-versioning-and-cloning
  - landing-setup
  - landing-deploy
  - landing-qa
  - landing-rollback
  - landing-clone
  - landing-build
  - landing-orchestrator
  - wp-gutenberg-block-builder
tags: [deploy, operations, phase-5, wordpress, beget, analytics, crm, versioning, ab-testing]
---

# Phase 5 — Deploy & Operations

## Что делает

Закрывает производственный цикл лендинга: устанавливает систему один раз (`/landing-setup`), расширяет WordPress-тему четырьмя Python-скриптами (попапы, JS-инит, аналитика, CRM), деплоит сайт на Бегет через SSH+rsync+wp-cli, проводит QA по 7 критериям и управляет версиями и A/B-клонами.

## Когда вызывать / в каком этапе

Этапы 09–12 pipeline. Активируется после завершения `/landing-build` (stage 08). Точки входа:

- **`/landing-setup`** — один раз при первом запуске системы.
- **`/landing-deploy`** — после утверждения сборки.
- **`/landing-qa`** — после деплоя, перед финальным закрытием.
- **`/landing-rollback <version>`**, **`/landing-clone <slug>`** — операционные команды в любое время.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/` — готовая тема из phase 4
- `08_КОД/acf-fields.json` — поля ACF
- `00_БРИФ/brief.md` — содержит YM счётчик, GTM контейнер, CRM и интеграции
- `06_СТЕК/design-stack.yaml` — список JS-библиотек
- `.env` — `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`, токены CRM/Telegram
- `config/system.yaml` — флаги интеграций (создаётся `/landing-setup`)

**Выход:**
- `assets/js/popup.js` + `assets/css/popup.css` + `template-parts/popup-overlay.php` — popup-система
- `assets/js/main.js`, `sliders.js`, `animations.js`, `counters.js` — JS-инициализация библиотек
- Яндекс Метрика и GTM, внедрённые в `functions.php`
- Fluent Forms webhook (AmoCRM / Bitrix24 / Telegram) в `functions.php`
- `08_КОД/integrations/*.md` — инструкции подключения CRM
- Живой сайт на Бегет (rsync + wp theme activate)
- `10_QA/qa-report.md` — отчёт 7 критериев
- `09_ВЕРСИИ/<version>/` — снапшоты для отката
- Клон-папка для A/B тестирования

## Блоки реализации

| Блок | Что | Инструмент |
|------|-----|-----------|
| A | Настройка системы | `scripts/preflight.sh`, `config/system.yaml.template` |
| B | Расширение темы | `generate-popup.py`, `generate-js-init.py`, `generate-analytics.py`, `generate-integrations.py` |
| C | Деплой | `deploy-wordpress.sh`, `scripts/deploy.sh` |
| D | QA | `qa-auditor` агент → `10_QA/qa-report.md` |
| E | Версии + A/B | `create-version.sh`, `clone-landing.sh` |

## Связанные концепты

- [[system-setup]] — агент одноразовой настройки окружения
- [[wp-deployer]] — агент деплоя на Бегет
- [[qa-auditor]] — агент QA-аудита по 7 критериям
- [[lifecycle-keeper]] — агент версионирования и A/B-клонирования
- [[wp-cli-deployer]] — скилл деплоя (rsync + wp-cli)
- [[landing-versioning-and-cloning]] — скилл снапшотов и клонов
- [[landing-setup]] — команда одноразовой настройки
- [[landing-deploy]] — команда деплоя (stage 09)
- [[landing-qa]] — команда QA-аудита (stage 10)
- [[landing-rollback]] — команда отката к версии
- [[landing-clone]] — команда A/B клонирования
- [[landing-build]] — предшествующая команда сборки (stage 08)
- [[landing-orchestrator]] — оркестратор, вызывающий все этапы
- [[wp-gutenberg-block-builder]] — скилл, скрипты которого расширяются в этой фазе

## Источник

- `docs/superpowers/plans/2026-05-04-phase-5-deploy-operations.md`
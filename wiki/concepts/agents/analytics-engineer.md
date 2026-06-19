---
slug: analytics-engineer
type: agent
name: "Инженер аналитики"
stage: "08"
tags: [analytics, yandex-metrika, gtm, stage-08, functions-php]
triggers: [landing-build]
inputs:
  - 08_КОД/wp-theme/functions.php
  - .env
outputs:
  - 08_КОД/wp-theme/functions.php
  - 11_АНАЛИТИКА/metrika-config.md
  - 11_АНАЛИТИКА/goals-and-events.json
  - 11_АНАЛИТИКА/utm-templates.md
gates: []
pre_reqs: [integrations-engineer]
related:
  - integrations-engineer
  - 08-kod
  - 11-analitika
  - landing-build
  - wp-theme-assembler
sources: ["agents/analytics-engineer.md"]
updated: 2026-06-19
confidence: {triggers: low}
---

# Инженер аналитики

## Что делает

Подключает Яндекс.Метрику и Google Tag Manager к WordPress-теме лендинга. Читает идентификаторы счётчиков из `.env`, дописывает PHP-функции в `functions.php` (вставка кода в `<head>` и `<body>`). Учитывает Cookie Consent: GTM noscript-фолбэк рендерится только при наличии согласия пользователя на аналитику. После правки кода генерирует три конфигурационных файла аналитики в папке `11_АНАЛИТИКА/`: человекочитаемую карту счётчика и целей, JSON для импорта целей и шаблоны UTM-меток для Яндекс.Директ.

## Когда вызывается

Запускается оркестратором на этапе 08 (сборка кода) после завершения `integrations-engineer`. Требует, чтобы в `.landing-state.yaml` был выставлен `current_stage == 11_analytics`; иначе агент останавливается и сообщает об ошибке.

## Вход → выход

**Вход:** существующий `08_КОД/wp-theme/functions.php` с плейсхолдерами `// [YM_COUNTER]` и `// [GTM_HEAD]`; переменная `YM_COUNTER_ID` в `.env` (обязательно); `GTM_CONTAINER_ID` в `.env` (опционально).

**Выход:** `functions.php` дополнен PHP-сниппетами Метрики и GTM; `11_АНАЛИТИКА/metrika-config.md` с ID и целями; `11_АНАЛИТИКА/goals-and-events.json` для импорта в Метрику; `11_АНАЛИТИКА/utm-templates.md` с шаблонами для рекламных кампаний.

## Failure modes

- `YM_COUNTER_ID` отсутствует или не является 8-значным числом — код Метрики вставляется с пустым ID, счётчик не работает.
- Плейсхолдеры `// [YM_COUNTER]` / `// [GTM_HEAD]` уже удалены из `functions.php` предыдущим запуском — агент не находит точки вставки и дублирует сниппеты.
- `.env` недоступен на сервере после деплоя — `getenv()` возвращает `false`, код Метрики не рендерится на проде.
- Папка `11_АНАЛИТИКА/` не создана (проект старее template PR-B) — Write завершится ошибкой пути.
- Stage-gate predecessor (`integrations-engineer`) не закрыт — `enforce_stage_gate.py` хук блокирует все Write/Edit операции.

## Related

- [[integrations-engineer]] — обязательный предшественник; запускается раньше в рамках этапа 08
- [[08-kod]] — этап, в котором живёт тема и `functions.php`
- [[11-analitika]] — папка и stage, куда пишутся конфиги аналитики
- [[landing-build]] — slash-команда этапа 08, которая оркестрирует вызов агента
- [[wp-theme-assembler]] — создаёт `functions.php` с плейсхолдерами, которые данный агент заполняет
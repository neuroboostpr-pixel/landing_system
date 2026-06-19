---
slug: analytics-engineer
type: agent
name: "Инженер аналитики"
stage: "08"
tags: [analytics, yandex-metrika, gtm, wordpress, stage-08]
triggers: [landing-build]
inputs: [08-kod, 11-analitika]
outputs: [08-kod, 11-analitika]
gates: [metrika_config_approved]
pre_reqs: [integrations-engineer, 08-kod]
related: [integrations-engineer, landing-build, landing-orchestrator, wp-theme-assembler, 11-analitika]
sources: ["agents/analytics-engineer.md"]
updated: 2026-06-19
confidence: {triggers: low, stage: low}
---

# Инженер аналитики

## Что делает

Подключает Яндекс.Метрику и опционально Google Tag Manager к сгенерированной WordPress-теме лендинга. Читает `YM_COUNTER_ID` и `GTM_CONTAINER_ID` из `.env`, вставляет готовые PHP-сниппеты в `functions.php` (через заменители `// [YM_COUNTER]` и `// [GTM_HEAD]`). GTM-тело рендерится только при наличии явного согласия пользователя на аналитику (интеграция с Cookie-consent lp_cookie_consent). По завершении формирует три конфигурационных файла аналитики в папке `11_АНАЛИТИКА/`.

## Когда вызывается

Вызывается оркестратором на этапе 08 после `integrations-engineer`, когда `functions.php` уже существует и в `.env` прописан `YM_COUNTER_ID`. Агент проверяет состояние `.landing-state.yaml` — ожидает `current_stage == 11_analytics`, иначе останавливается с предупреждением.

## Вход → выход

**Вход:** `08_КОД/wp-theme/functions.php` с маркерами `// [YM_COUNTER]` и `// [GTM_HEAD]`; `.env` с `YM_COUNTER_ID` (8 цифр) и опционально `GTM_CONTAINER_ID`.

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен сниппетами Метрики и GTM
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список целей
- `11_АНАЛИТИКА/goals-and-events.json` — цели для настройки в Метрике
- `11_АНАЛИТИКА/utm-templates.md` — шаблоны UTM для Яндекс.Директ

## Чем закрывается этап (gates)

- `metrika_config_approved` — агент показывает `metrika-config.md` пользователю и ждёт явного утверждения перед завершением этапа

## Failure modes

- `YM_COUNTER_ID` не задан в `.env` — агент пропускает вставку Метрики без ошибки, счётчик не устанавливается на сайт
- `// [YM_COUNTER]` отсутствует в `functions.php` — вставка не происходит, файл остаётся без изменений
- `current_stage` в `.landing-state.yaml` не соответствует `11_analytics` — агент блокируется stage-gate enforcement hook'ом
- GTM `<noscript>`-фолбэк зависит от cookie `lp_cookie_consent` — при деактивированном cookie-banner он никогда не рендерится
- Цели в `goals-and-events.json` формируются автоматически из структуры лендинга без ручной верификации — могут не совпасть с реальными CTA клиента

## Related

- [[integrations-engineer]] — обязательный предшественник: устанавливает интеграции форм до подключения аналитики
- [[landing-build]] — вызывает агента как часть сборки этапа 08
- [[landing-orchestrator]] — управляет последовательностью вызова агентов pipeline
- [[wp-theme-assembler]] — формирует `functions.php` с маркерами, которые заменяет этот агент
- [[11-analitika]] — целевой каталог выходных конфигов аналитики
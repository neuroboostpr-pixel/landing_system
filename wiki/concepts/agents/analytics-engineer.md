---
type: agent
name: analytics-engineer
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-25
triggers: []
stage: "11_analytics"
uses: ["landing-orchestrator", "integrations-engineer", "stage-execution-protocol"]
tags: ["аналитика", "яндекс-метрика", "utm", "stage-11"]
---

# Analytics Engineer (Инженер аналитики)

## Что делает

Подключает Яндекс.Метрику к готовому лендингу, определяет цели отслеживания (клики по CTA, отправки форм) и формирует UTM-шаблоны для рекламных кампаний в Яндекс.Директ.

## Когда вызывать / в каком этапе

Запускается на этапе **11\_analytics** — после `integrations-engineer` (этап 08), когда `functions.php` уже существует. Агент сначала проверяет `.landing-state.yaml`: `current_stage` должен быть `11_analytics`, иначе останавливается. Перед любыми изменениями запускает `gate-check.sh` и отображает Mermaid-карту пайплайна.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` с маркером `// [YM_COUNTER]`
- `.env` или `.env.example` с переменной `YM_COUNTER_ID` (8-значное число)

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функцией `lp_yandex_metrika()`, подключённой через `add_action('wp_head', ...)`
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список целей в читаемом виде
- `11_АНАЛИТИКА/goals-and-events.json` — цели для импорта в интерфейс Метрики
- `11_АНАЛИТИКА/utm-templates.md` — готовые UTM-шаблоны для Яндекс.Директ

Перед финализацией агент показывает `metrika-config.md` и ждёт явного утверждения пользователя (**HARD GATE**). После approve — вызывает `gate-state.sh approve`.

## Связанные концепты

- [[landing-orchestrator]] — вызывает агента как часть основного pipeline
- [[integrations-engineer]] — предшественник: должен быть завершён до старта аналитики
- [[stage-execution-protocol]] — обязательный протокол проверки gate-check перед любым Write/Edit
- [[landing-deploy]] — следующий этап после закрытия gate 11\_analytics

## Источник

- `agents/analytics-engineer.md`
---
type: agent
name: analytics-engineer
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-20
triggers: []
stage: "11"
uses: ["integrations-engineer", "landing-orchestrator", "stage-execution-protocol", "seo-optimizer"]
tags: ["analytics", "yandex-metrika", "stage-11", "wordpress"]
---

# analytics-engineer (Инженер аналитики)

## Что делает

Подключает Яндекс.Метрику к готовому WordPress-лендингу: вставляет счётчик в `functions.php` и создаёт набор конфигурационных файлов с целями, событиями и UTM-шаблонами для рекламных кампаний.

## Когда вызывать / в каком этапе

Запускается на **этапе 11 (11_АНАЛИТИКА)**, строго после [[integrations-engineer]] (этап 08). Агент сам проверяет, что в `.landing-state.yaml` стоит `current_stage == 11_analytics`; если нет — останавливается и сообщает об ошибке. Активируется [[landing-orchestrator]]-ом в рамках `/landing-go` или вручную на этапе 08/11.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — файл темы, в котором должен быть placeholder `// [YM_COUNTER]`
- `.env` или `.env.example` — переменная `YM_COUNTER_ID` (8-значный ID счётчика Метрики)

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функцией `lp_yandex_metrika()`, подключённой через `wp_head`
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список целей
- `11_АНАЛИТИКА/goals-and-events.json` — цели для ручной настройки в интерфейсе Метрики
- `11_АНАЛИТИКА/utm-templates.md` — шаблоны UTM-меток для Яндекс.Директ

**HARD GATE:** агент показывает `metrika-config.md` и ждёт явного подтверждения пользователя перед завершением этапа. После approve вызывает `gate-state.sh approve`.

## Что делает под капотом

1. Читает `YM_COUNTER_ID` из `.env`.
2. Генерирует PHP-функцию счётчика (с `webvisor:true`, `clickmap`, `trackLinks`, `accurateTrackBounce`) и вставляет её в `functions.php`.
3. Анализирует секции лендинга и определяет цели (клик по CTA, отправка формы и т.д.).
4. Записывает три файла в `11_АНАЛИТИКА/`.
5. Соблюдает [[stage-execution-protocol]]: читает state, рисует Mermaid-карту, создаёт TodoWrite, запускает `gate-check.sh`.

## Связанные концепты

- [[integrations-engineer]] — обязательный предшественник; настраивает формы и вебхуки перед аналитикой
- [[seo-optimizer]] — следующий этап после аналитики (этап 12)
- [[landing-orchestrator]] — диспатчит агента в нужный момент pipeline
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit действием

## Источник

- `agents/analytics-engineer.md`
---
type: agent
name: analytics-engineer
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-20
triggers: []
stage: "11"
uses: ["integrations-engineer", "wp-builder", "stage-execution-protocol", "seo-optimizer"]
tags: ["analytics", "yandex-metrika", "wordpress", "stage-11"]
---

# analytics-engineer (Инженер аналитики)

## Что делает

Подключает Яндекс.Метрику к лендингу: вставляет счётчик в WordPress-тему и формирует конфигурационные файлы с целями и UTM-шаблонами для рекламных кампаний.

## Когда вызывать / в каком этапе

Запускается на **этапе 11 (11_АНАЛИТИКА)**, строго после [[integrations-engineer]]. Требует, чтобы в `.landing-state.yaml` было `current_stage == 11_analytics`. Если предшественник не завершён — агент останавливается и сообщает об этом.

Перед любыми изменениями файлов агент обязан:
1. Прочитать `.landing-state.yaml` и убедиться в правильном текущем этапе.
2. Отрисовать Mermaid-карту pipeline через `render-pipeline-map.sh`.
3. Сформировать TodoWrite-список оставшихся этапов.
4. Пройти gate-check (`gate-check.sh --stage 11_analytics`).

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — тема WordPress, созданная [[wp-builder]]
- `.env` с переменной `YM_COUNTER_ID` (8-значный идентификатор счётчика)

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функцией `lp_yandex_metrika()`, подключённой через хук `wp_head`
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список настроенных целей
- `11_АНАЛИТИКА/goals-and-events.json` — цели для импорта в Яндекс.Метрику
- `11_АНАЛИТИКА/utm-templates.md` — UTM-шаблоны для Яндекс.Директ

**HARD GATE:** агент показывает `metrika-config.md` пользователю и ждёт явного подтверждения перед финальной отметкой этапа как `approved`.

## Связанные концепты

- [[integrations-engineer]] — обязательный предшественник; настраивает Fluent Forms, Telegram и CRM-вебхуки до запуска аналитики
- [[wp-builder]] — создаёт `functions.php`, в который analytics-engineer вставляет код Метрики
- [[stage-execution-protocol]] — общий протокол выполнения этапа: gate-check, TodoWrite, approve-flow
- [[seo-optimizer]] — следующий этап (12_SEO), запускается после закрытия 11_analytics

## Источник

- `agents/analytics-engineer.md`
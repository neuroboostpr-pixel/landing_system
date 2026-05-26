---
type: agent
name: analytics-engineer
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-26
triggers: []
stage: "11"
uses: ["landing-orchestrator", "stage-execution-protocol"]
tags: ["analytics", "yandex-metrika", "stage-11", "utm", "goals"]
---

# Analytics Engineer — Инженер аналитики

## Что делает
Подключает Яндекс.Метрику к лендингу: вставляет счётчик в тему WordPress и формирует конфиг-файлы с целями, событиями и UTM-шаблонами для рекламных кампаний.

## Когда вызывать / в каком этапе
Запускается на **этапе 11 (`11_analytics`)** — после того как `integrations-engineer` завершил свою работу. Перед любыми действиями агент обязан убедиться, что в `.landing-state.yaml` проставлен `current_stage == 11_analytics`, и пройти `gate-check.sh`. Если предшественник не закрыт — harness физически блокирует запись файлов (`enforce_stage_gate.py`).

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — тема WordPress с плейсхолдером `// [YM_COUNTER]`
- `.env` или `.env.example` с переменной `YM_COUNTER_ID` (8-значный номер счётчика)

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функцией `lp_yandex_metrika()`, подключённой через `add_action('wp_head', ...)`
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список настроенных целей
- `11_АНАЛИТИКА/goals-and-events.json` — цели в формате для импорта в Яндекс.Метрику
- `11_АНАЛИТИКА/utm-templates.md` — UTM-шаблоны для Яндекс.Директ

## Порядок работы
1. Читает `YM_COUNTER_ID` из `.env`.
2. Вставляет код счётчика (с webvisor, clickmap, trackLinks, accurateTrackBounce) заменой плейсхолдера в `functions.php`.
3. Анализирует секции лендинга и определяет цели: клики по CTA, отправки форм.
4. Формирует три файла аналитики.
5. **HARD GATE** — показывает `metrika-config.md` пользователю и ждёт явного утверждения перед закрытием этапа.

## Связанные концепты
- [[landing-orchestrator]] — диспатчит агента в нужный момент pipeline
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit действием на этапе

## Источник
- `agents/analytics-engineer.md`
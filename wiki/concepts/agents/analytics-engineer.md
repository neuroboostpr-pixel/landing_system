---
type: agent
name: analytics-engineer
sources: ["agents/analytics-engineer.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["integrations-engineer", "wp-builder", "seo-optimizer"]
tags: ["analytics", "yandex-metrika", "stage-08", "wordpress"]
---

# Analytics Engineer (Инженер аналитики)

## Что делает

Подключает счётчик Яндекс.Метрики к WordPress-лендингу: вставляет код счётчика в тему, определяет цели (клики по CTA, отправки форм) и готовит документацию по аналитике и UTM-шаблонам для рекламных кампаний.

## Когда вызывать / в каком этапе

Вызывается на **этапе 08** — после того, как `integrations-engineer` завершил настройку форм и webhook'ов. Агент не запускается самостоятельно; его запускает `landing-orchestrator` в рамках команды `/landing-build` или `/landing-go`.

Предусловия:
- `08_КОД/wp-theme/functions.php` уже создан агентом `wp-builder`
- В `.env` (или `.env.example`) прописана переменная `YM_COUNTER_ID` (8-значный идентификатор счётчика)

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/functions.php` — файл темы, содержащий плейсхолдер `// [YM_COUNTER]`
- `.env` — файл окружения с переменной `YM_COUNTER_ID`

**Выход:**
- `08_КОД/wp-theme/functions.php` — дополнен PHP-функцией `lp_yandex_metrika()`, подключённой через хук `wp_head`
- `11_АНАЛИТИКА/metrika-config.md` — ID счётчика и список настроенных целей (показывается пользователю перед финальным утверждением — **HARD GATE**)
- `11_АНАЛИТИКА/goals-and-events.json` — цели в формате JSON для настройки в интерфейсе Яндекс.Метрики
- `11_АНАЛИТИКА/utm-templates.md` — шаблоны UTM-меток для кампаний в Яндекс.Директ

**HARD GATE:** перед закрытием этапа агент показывает `metrika-config.md` и ждёт явного утверждения от пользователя.

## Связанные концепты

- [[integrations-engineer]] — предшественник: настраивает формы и webhook'и до запуска аналитики
- [[wp-builder]] — создаёт `functions.php`, куда инжектируется код Метрики
- [[seo-optimizer]] — следующий по цепочке: добавляет SEO-мета-теги после аналитики
- [[landing-orchestrator]] — мастер-оркестратор, диспатчит агента в нужный момент

## Источник

- `agents/analytics-engineer.md`
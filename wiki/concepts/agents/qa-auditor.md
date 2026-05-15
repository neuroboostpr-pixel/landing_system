---
type: agent
name: qa-auditor
sources: ["agents/qa-auditor.md"]
updated: 2026-05-15
triggers: ["после деплоя", "проверка сайта", "/landing-deploy завершён", "QA аудит"]
stage: "10"
uses: ["landing-deploy", "wp-deployer", "integrations-engineer", "analytics-engineer"]
tags: ["qa", "audit", "deploy", "checklist"]
---

# qa-auditor — QA-аудитор задеплоенного лендинга

## Что делает

Автоматически проверяет живой сайт по 7 критериям качества сразу после деплоя: от доступности и HTTPS до форм и аналитики. Формирует отчёт в виде таблицы и ждёт утверждения перед переходом к следующему этапу.

## Когда вызывать / в каком этапе

Вызывается на **этапе 10** — после того как агент [[wp-deployer]] завершил деплой (`/landing-deploy`). Запуск через `/landing-qa` или автоматически через [[landing-orchestrator]].

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — содержит URL задеплоенного сайта
- Живой HTML сайта (скачивается через `curl`)

**Выход:**
- `10_QA/qa-report.md` — таблица с результатами по 7 критериям (✅ / ❌)

**Семь проверяемых критериев:**
1. Доступность — HTTP 200
2. HTTPS + редирект с HTTP → HTTPS (301)
3. Meta-теги — `<title>`, `<meta description>`, `og:title`
4. Яндекс Метрика — счётчик `mc.yandex.ru` в HTML
5. Google Tag Manager — контейнер `googletagmanager` в HTML
6. Fluent Forms — shortcode `fluentform` отрендерен в HTML
7. Viewport — `<meta name="viewport">` для мобайла

**HARD GATE:** после формирования отчёта агент показывает его пользователю и ждёт явного подтверждения. Следующий этап не открывается до approve.

## Связанные концепты

- [[wp-deployer]] — выполняет деплой, после которого запускается qa-auditor
- [[integrations-engineer]] — настраивает Fluent Forms и Telegram webhook (проверяется в п. 6)
- [[analytics-engineer]] — добавляет счётчик Яндекс Метрики (проверяется в п. 4)
- [[landing-orchestrator]] — управляет порядком этапов и HARD GATE между ними

## Источник

- `agents/qa-auditor.md`
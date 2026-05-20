---
type: agent
name: qa-auditor
sources: ["agents/qa-auditor.md"]
updated: 2026-05-20
triggers: ["после деплоя", "проверить живой сайт", "QA после публикации", "/landing-qa"]
stage: "10_qa"
uses: ["landing-deploy", "landing-orchestrator", "analytics-engineer", "integrations-engineer"]
tags: ["qa", "audit", "deploy", "checklist"]
---

# qa-auditor — QA-аудитор живого сайта

## Что делает
После публикации лендинга проверяет 7 критериев качества: сайт доступен, HTTPS работает, мета-теги есть, аналитика подключена, форма рендерится, мобильный viewport настроен. Формирует отчёт `qa-report.md`.

## Когда вызывать / в каком этапе
Запускается на **этапе 10_qa** — строго после того, как `wp-deployer` завершил деплой (`/landing-deploy`). Команда: `/landing-qa`. Агент сначала проверяет `.landing-state.yaml` и убеждается, что `current_stage == 10_qa`; если нет — останавливается.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — содержит URL опубликованного сайта
- `.landing-state.yaml` — текущий статус pipeline
- Живой сайт (доступный по HTTP/HTTPS)

**Выход:**
- `10_QA/qa-report.md` — таблица с результатами по 7 критериям (✅/❌ на каждый пункт)

**Семь критериев:**
1. Доступность — `curl -sI <URL>` возвращает 200
2. HTTPS + редирект с HTTP → HTTPS (301)
3. Мета-теги: `<title>`, `<meta description>`, `og:title`
4. Яндекс Метрика — счётчик `mc.yandex.ru` в HTML
5. Google Tag Manager — контейнер `googletagmanager` в HTML
6. Fluent Forms — шорткод формы рендерится на странице
7. Viewport meta — `<meta name="viewport">` присутствует

## Связанные концепты
- [[wp-deployer]] — выполняет деплой на этапе 09, после которого запускается qa-auditor
- [[landing-orchestrator]] — управляет всем pipeline, диспатчит qa-auditor на этапе 10
- [[analytics-engineer]] — подключает Яндекс Метрику (критерий 4), которую проверяет аудитор
- [[integrations-engineer]] — настраивает Fluent Forms (критерий 6)
- [[landing-deploy]] — команда этапа 09, предшественник 10_qa

## Источник
- `agents/qa-auditor.md`
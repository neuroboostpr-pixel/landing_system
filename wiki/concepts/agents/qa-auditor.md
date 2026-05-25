---
type: agent
name: qa-auditor
sources: ["agents/qa-auditor.md"]
updated: 2026-05-25
triggers: []
stage: "10_qa"
uses: ["landing-deploy", "landing-orchestrator", "stage-execution-protocol"]
tags: ["qa", "audit", "stage-10", "deploy", "check"]
---

# QA-аудитор (qa-auditor)

## Что делает
Проверяет задеплоенный лендинг по 7 критериям качества: доступность, HTTPS, мета-теги, аналитика, форма и мобильная верстка. По итогам формирует отчёт `qa-report.md`.

## Когда вызывать / в каком этапе
Запускается на этапе **10_qa** — сразу после успешного деплоя (`/landing-deploy`, этап 09). Агент сам проверяет, что `current_stage == 10_qa` в `.landing-state.yaml`; если нет — останавливается и сообщает об ошибке. Вызывается через `landing-orchestrator` или вручную.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — содержит URL задеплоенного сайта.
- `<project>/.landing-state.yaml` — статус pipeline, должен быть `10_qa`.

**Выход:**
- `10_QA/qa-report.md` — таблица с результатами 7 проверок (✅/❌):
  1. Доступность сайта (HTTP 200)
  2. HTTPS + 301-редирект с http
  3. Мета-теги: `<title>`, `<meta description>`, `og:title`
  4. Яндекс Метрика (mc.yandex.ru)
  5. Google Tag Manager (googletagmanager)
  6. Fluent Forms (shortcode рендерится)
  7. Viewport meta (мобильная версия)

**HARD GATE:** отчёт показывается пользователю, этап не закрывается без явного утверждения. После approve — `bash scripts/gate-state.sh approve <project> 10_qa`.

## Протокол выполнения
Перед любыми действиями агент обязан:
1. Прочитать `.landing-state.yaml`, убедиться в стадии `10_qa`.
2. Показать Mermaid-карту pipeline через `render-pipeline-map.sh`.
3. Создать TodoWrite-список оставшихся этапов.
4. Пройти gate-check (`gate-check.sh --stage 10_qa`). При exit != 0 — остановиться.
5. Скачать HTML страницы (`curl -s <URL>`) и прогнать grep-проверки по чек-листу.

Хук `PreToolUse` (`scripts/hooks/enforce_stage_gate.py`) физически блокирует запись, если предшествующие этапы не закрыты — обходить не нужно, нужно закрывать предшественника.

## Связанные концепты
- [[landing-deploy]] — предшествующий этап (09), после него запускается qa-auditor
- [[landing-orchestrator]] — диспатчит qa-auditor как часть pipeline
- [[stage-execution-protocol]] — обязательный протокол предусловий для всех этапов
- [[landing-audit]] — расширенный SEO/tech-аудит (S2-E.1), отдельный от QA-аудитора

## Источник
- `agents/qa-auditor.md`
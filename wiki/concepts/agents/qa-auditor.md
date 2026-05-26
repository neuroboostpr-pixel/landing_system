---
type: agent
name: qa-auditor
sources: ["agents/qa-auditor.md"]
updated: 2026-05-26
triggers: []
stage: "10_qa"
uses: ["landing-deploy", "landing-orchestrator", "stage-execution-protocol"]
tags: ["qa", "audit", "deploy", "stage-10"]
---

# QA-аудитор — проверка живого сайта после деплоя

## Что делает
Проверяет задеплоенный лендинг по 7 критериям качества: доступность, HTTPS, мета-теги, аналитика, форма, мобильная адаптация. По результатам формирует отчёт `qa-report.md`.

## Когда вызывать / в каком этапе
Активируется на этапе **10_qa** — строго после завершения `/landing-deploy` (этап 09). Агент самостоятельно проверяет `current_stage == 10_qa` в `.landing-state.yaml` и отказывается работать вне своего этапа. Запускается через `landing-orchestrator` или вручную.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — URL задеплоенного сайта
- `.landing-state.yaml` — статус pipeline (должен быть `10_qa`)

**Выход:**
- `10_QA/qa-report.md` — таблица с результатами по 7 критериям (✅/❌)
- Обновлённый статус gate `10_qa` → `approved` при прохождении всех проверок

## Чек-лист проверок

| # | Критерий | Метод |
|---|---|---|
| 1 | Сайт доступен (HTTP 200) | `curl -sI <URL>` |
| 2 | HTTPS + редирект 301 | `curl -sI http://…` → `https://` |
| 3 | Мета-теги (title, description, og:title) | grep в HTML |
| 4 | Яндекс Метрика | grep `mc.yandex.ru` |
| 5 | Google Tag Manager | grep `googletagmanager` |
| 6 | Fluent Forms shortcode | grep `fluentform` |
| 7 | Viewport meta | grep `meta name="viewport"` |

## Протокол выполнения
Перед любым действием агент обязан: прочитать `.landing-state.yaml`, запустить `render-pipeline-map.sh`, создать TodoWrite со всеми оставшимися этапами, пройти `gate-check.sh --stage 10_qa`. Хук `enforce_stage_gate.py` физически блокирует запись в файлы этапа, если предшественники не закрыты — обходить запрещено. После PASS верификации — `gate-state.sh approve`.

**HARD GATE:** отчёт показывается пользователю, переход на следующий этап только после явного утверждения.

## Связанные концепты
- [[landing-deploy]] — предшествующий этап, после которого активируется аудитор
- [[landing-orchestrator]] — диспатчит qa-auditor в рамках общего pipeline
- [[stage-execution-protocol]] — обязательный протокол перед любым write-действием

## Источник
- `agents/qa-auditor.md`
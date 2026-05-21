---
type: agent
name: qa-auditor
sources: ["agents/qa-auditor.md"]
updated: 2026-05-20
triggers: ["после деплоя сайта", "проверить качество сайта", "qa проверка", "аудит после публикации"]
stage: "10_qa"
uses: ["landing-deploy", "analytics-engineer", "integrations-engineer", "landing-orchestrator"]
tags: ["qa", "аудит", "деплой", "проверка", "мета-теги", "https"]
---

# qa-auditor (QA-аудитор)

## Что делает

После деплоя лендинга проверяет 7 ключевых критериев качества живого сайта и формирует отчёт `qa-report.md`. Убеждается, что сайт доступен, безопасен, правильно проиндексируем и корректно работает на мобильных.

## Когда вызывать / в каком этапе

Запускается на **этапе 10 (QA)** — строго после завершения `/landing-deploy` (этап 09). Агент требует, чтобы `.landing-state.yaml` имел `current_stage == 10_qa`; если это не так — останавливается и сообщает пользователю.

Перед любыми действиями обязательно:
1. Читает `.landing-state.yaml`, подтверждает этап.
2. Запускает `render-pipeline-map.sh` — показывает Mermaid-карту pipeline.
3. Проверяет gate через `gate-check.sh --stage 10_qa`.
4. Создаёт TodoWrite-список оставшихся этапов.

Физически заблокирован `PreToolUse` hook (`enforce_stage_gate.py`) — не пытайся обойти гейт.

## Что на вход / на выход

**Вход:**
- `00_БРИФ/brief.md` — URL задеплоенного сайта
- Живой сайт (HTTP-доступ)

**Выход:**
- `10_QA/qa-report.md` — таблица с результатами 7 проверок (✅ / ❌ по каждому пункту)

**7 критериев проверки:**
| # | Что проверяется | Метод |
|---|---|---|
| 1 | Доступность (HTTP 200) | `curl -sI <URL>` |
| 2 | HTTPS + редирект с http | `curl -sI http://...` → 301 |
| 3 | Meta title, description, og:title | grep в HTML |
| 4 | Яндекс Метрика | grep `mc.yandex.ru` |
| 5 | Google Tag Manager | grep `googletagmanager` |
| 6 | Fluent Forms shortcode | grep `fluentform` |
| 7 | Viewport meta (мобайл) | grep `name="viewport"` |

После формирования отчёта — **HARD GATE**: показывает таблицу пользователю и ждёт утверждения. При PASS вызывает `gate-state.sh approve ... 10_qa`.

## Связанные концепты

- [[landing-deploy]] — предшественник: деплой должен быть завершён до QA
- [[analytics-engineer]] — добавляет ЯМ счётчик, который проверяется в п. 4
- [[integrations-engineer]] — настраивает Fluent Forms, проверяется в п. 6
- [[landing-orchestrator]] — диспатчит qa-auditor на этапе 10
- [[seo-optimizer]] — мета-теги, которые проверяются в п. 3

## Источник

- `agents/qa-auditor.md`
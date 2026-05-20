---
type: agent
name: wp-deployer
sources: ["agents/wp-deployer.md"]
updated: 2026-05-20
triggers: []
stage: "09"
uses: ["landing-orchestrator", "landing-build", "landing-deploy", "qa-auditor"]
tags: ["deploy", "wordpress", "beget", "ssh", "ssl"]
---

# wp-deployer — Деплой-инженер на Бегет

## Что делает

Загружает готовую WordPress-тему на хостинг Бегет через SSH и rsync, активирует тему, импортирует ACF-поля, настраивает SSL и редиректы. Проверяет, что сайт открывается по HTTPS после деплоя.

## Когда вызывать / в каком этапе

Этап **09_deploy** — после того как `/landing-build` завершён и одобрен пользователем. Агент не запускается, пока stage 08 не получил статус `approved` в `.landing-state.yaml`. Блокировка физически обеспечивается хуком `scripts/hooks/enforce_stage_gate.py`.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` с `current_stage == 09_deploy`
- `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- Собранный WordPress-проект из этапа 08 (тема, Lazy Blocks, CSS/JS)

**Выход:**
- Работающий сайт по `https://<domain>` (проверка через `curl -sI`)
- SSL-сертификат настроен (certbot или ручная инструкция)
- Редиректы HTTP→HTTPS и www→без www активны
- Этап 09 помечен как `approved` через `scripts/gate-state.sh`

**HARD GATE:** агент показывает URL сайта и ждёт явного утверждения от пользователя перед закрытием этапа.

## Протокол выполнения

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и убедиться, что `current_stage == 09_deploy`.
2. Запустить `render-pipeline-map.sh` и показать Mermaid-карту.
3. Создать TodoWrite со всеми оставшимися этапами (09→12).
4. Запустить `gate-check.sh --stage 09_deploy` — при exit != 0 остановиться.
5. Прочитать чеклист `stage-09_deploy-checklist.md` если существует.

Деплой выполняется скриптом `scripts/deploy.sh <project-dir>`. SSL настраивается через certbot на стороне сервера.

## Связанные концепты

- [[landing-build]] — предшествующий этап, собирает тему перед деплоем
- [[landing-deploy]] — команда, запускающая этого агента
- [[qa-auditor]] — следующий этап (10_qa), проверяет живой сайт
- [[landing-orchestrator]] — мастер-оркестратор, управляет порядком этапов
- [[stage-execution-protocol]] — обязательный протокол для всех stage-агентов

## Источник

- `agents/wp-deployer.md`
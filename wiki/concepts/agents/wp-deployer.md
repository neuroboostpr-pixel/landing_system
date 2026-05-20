---
type: agent
name: wp-deployer
sources: ["agents/wp-deployer.md"]
updated: 2026-05-20
triggers: []
stage: "09_deploy"
uses: ["landing-build", "landing-deploy", "qa-auditor", "landing-orchestrator"]
tags: ["deploy", "beget", "wordpress", "ssl", "ssh"]
---

# wp-deployer — Деплой-инженер

## Что делает

Загружает готовую WordPress-тему на хостинг Бегет по SSH, активирует её через wp-cli, проверяет доступность сайта и настраивает SSL. Финальный шаг перед QA-аудитом.

## Когда вызывать / в каком этапе

Этап **09_deploy**. Запускается командой `/landing-deploy` после того, как пользователь одобрил результаты `/landing-build`. Перед запуском агент обязан убедиться, что `.landing-state.yaml` показывает `current_stage == 09_deploy` — если нет, останавливается и сообщает о проблеме.

## Что на вход / на выход

**Вход:**
- Собранная тема из этапа 08 (папка проекта с wp-темой)
- `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- Закрытый stage-gate 08_kod (проверяется через `gate-check.sh`)

**На выход:**
- Тема задеплоена и активирована на Бегет
- Сайт доступен по HTTPS: проверка через `curl -sI https://<domain>`
- Настроены редиректы HTTP→HTTPS и www→без www
- Stage 09_deploy отмечен `approved` через `gate-state.sh`
- URL сайта передан пользователю для явного подтверждения (**HARD GATE**)

## Что делает шаг за шагом

1. Читает `.landing-state.yaml`, показывает Mermaid-карту pipeline через `render-pipeline-map.sh`.
2. Проверяет `.env` — все три переменные Бегета должны быть заполнены.
3. Запускает `scripts/deploy.sh <project-dir>` — rsync темы на сервер.
4. Проверяет доступность: `curl -sI https://<domain> | head -5`.
5. Если SSL отсутствует — выдаёт инструкцию для certbot через SSH.
6. Проверяет редиректы.
7. Показывает URL сайта пользователю, ждёт явного утверждения (HARD GATE).
8. После approve — закрывает gate через `gate-state.sh approve`.

## Правила и ограничения

- Никогда не деплоит без успешного preflight (`gate-check.sh` exit 0).
- Всегда делает curl-проверку после деплоя.
- Не обходит `PreToolUse` hook (`enforce_stage_gate.py`) — если хук блокирует Write/Edit, агент идёт закрывать предшественника.

## Связанные концепты

- [[wp-builder]] — генерирует тему, которую этот агент деплоит
- [[landing-deploy]] — slash-команда, запускающая этого агента
- [[qa-auditor]] — следующий этап после деплоя (этап 10)
- [[landing-orchestrator]] — мастер-оркестратор, диспатчащий агента в нужный момент
- [[landing-build]] — команда, чей approve является предусловием запуска

## Источник

- `agents/wp-deployer.md`
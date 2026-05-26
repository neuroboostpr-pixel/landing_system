---
type: agent
name: wp-deployer
sources: ["agents/wp-deployer.md"]
updated: 2026-05-26
triggers: []
stage: "09_deploy"
uses: ["landing-build", "landing-orchestrator", "stage-execution-protocol"]
tags: ["deploy", "beget", "ssh", "wordpress", "ssl"]
---

# wp-deployer — Деплой-инженер

## Что делает
Загружает готовую WordPress-тему на хостинг Бегет через SSH и rsync, активирует тему, импортирует ACF-поля и проверяет что сайт доступен по HTTPS.

## Когда вызывать / в каком этапе
Этап **09_deploy** — запускается автоматически оркестратором или вручную через `/landing-deploy` после того, как этап 08 (build) утверждён пользователем. Агент сам проверяет `.landing-state.yaml` и отказывается работать, если `current_stage != 09_deploy`.

## Что на вход / на выход

**Вход:**
- Собранная тема в `08_КОД/` (результат `/landing-build`)
- `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- Закрытый gate этапа 08

**Выход:**
- Задеплоенная тема на Бегете
- Активный сайт по HTTPS с корректными редиректами (HTTP→HTTPS, www→без www)
- Утверждённый gate `09_deploy` в `.landing-state.yaml`

## Порядок работы

1. Читает `.landing-state.yaml`, проверяет `current_stage == 09_deploy`.
2. Рендерит Mermaid-карту пайплайна через `scripts/render-pipeline-map.sh`.
3. Создаёт TodoWrite со всеми оставшимися этапами.
4. Запускает `scripts/gate-check.sh --stage 09_deploy` — при ненулевом exit останавливается.
5. Выполняет `scripts/deploy.sh <project-dir>`.
6. Проверяет доступность: `curl -sI https://<domain> | head -5`.
7. При отсутствии SSL — выдаёт инструкцию с `certbot`.
8. Показывает URL пользователю и ждёт явного утверждения (**HARD GATE**).
9. При approve — закрывает gate через `scripts/gate-state.sh approve`.

## Ограничения
- Деплой без пройденного preflight запрещён.
- Обход stage-gate через PreToolUse hook (`scripts/hooks/enforce_stage_gate.py`) невозможен — хук физически блокирует Write/Edit пока предшественники не закрыты.

## Связанные концепты
- [[landing-build]] — этап 08, результат которого деплоит этот агент
- [[landing-orchestrator]] — вызывает wp-deployer как часть пайплайна
- [[stage-execution-protocol]] — обязательный протокол перед любым действием
- [[landing-deploy]] — slash-команда для ручного запуска этого агента

## Источник
- `agents/wp-deployer.md`
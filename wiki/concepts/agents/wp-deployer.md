---
type: agent
name: wp-deployer
sources: ["agents/wp-deployer.md"]
updated: 2026-05-20
triggers: ["задеплоить лендинг", "залить на сервер", "деплой на Бегет", "опубликовать сайт", "загрузить тему на хостинг"]
stage: "09"
uses: ["stage-execution-protocol", "landing-build", "qa-auditor", "landing-deploy"]
tags: ["deploy", "beget", "ssh", "rsync", "ssl", "wordpress"]
---

# wp-deployer — Деплой-инженер

## Что делает

Загружает готовую WordPress-тему на хостинг Бегет по SSH, активирует её, импортирует ACF-поля и проверяет, что сайт открывается по HTTPS. Это финальный шаг перед QA-аудитом.

## Когда вызывать / в каком этапе

Этап **09_deploy**. Активируется командой `/landing-deploy` после того, как этап 08 (сборка темы) получил статус `approved`. Если `.landing-state.yaml` показывает `current_stage != 09_deploy` — агент останавливается и сообщает об ошибке.

## Что на вход / на выход

**Вход:**
- `.landing-state.yaml` с подтверждённым этапом 08
- `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- Собранная WordPress-тема в директории проекта

**Выход:**
- Развёрнутый сайт на Бегет (тема загружена и активирована)
- Проверенный HTTPS (`certbot --nginx` при необходимости)
- Настроенные редиректы HTTP→HTTPS и www→без www
- Статус этапа `approved` в `.landing-state.yaml`

## Порядок работы

1. Читает `.landing-state.yaml` и выводит Mermaid-карту pipeline через `scripts/render-pipeline-map.sh`.
2. Создаёт TodoWrite-список оставшихся этапов (09 → 12).
3. Запускает `scripts/gate-check.sh --stage 09_deploy` — при exit ≠ 0 останавливается.
4. Проверяет `.env` на наличие трёх обязательных переменных.
5. Запускает `scripts/deploy.sh <project-dir>` — rsync + wp-cli активация.
6. Проверяет доступность сайта: `curl -sI https://<domain> | head -5`.
7. При отсутствии SSL — выдаёт команду certbot.
8. Показывает пользователю URL — ждёт явного утверждения **(HARD GATE)**.
9. Закрывает этап через `scripts/gate-state.sh approve`.

## Важные ограничения

- **Никогда** не деплоит без preflight (`gate-check.sh` exit 0).
- Хук `scripts/hooks/enforce_stage_gate.py` физически блокирует запись в файлы этапа, если предшественники не закрыты — обходить его запрещено.
- Всегда сообщает точный URL для проверки после деплоя.

## Связанные концепты

- [[stage-execution-protocol]] — обязательный протокол перед любым действием на этапе
- [[landing-build]] — этап 08, предшественник; тема должна быть собрана
- [[landing-deploy]] — команда-триггер для этого агента
- [[qa-auditor]] — следующий этап 10, проверяет живой сайт

## Источник

- `agents/wp-deployer.md`
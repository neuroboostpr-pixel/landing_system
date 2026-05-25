---
type: agent
name: wp-deployer
sources: ["agents/wp-deployer.md"]
updated: 2026-05-25
triggers: []
stage: "09_deploy"
uses: ["landing-build", "landing-orchestrator", "stage-execution-protocol"]
tags: ["deploy", "beget", "ssh", "wordpress", "ssl"]
---

# wp-deployer (Деплой-инженер)

## Что делает
Загружает готовую WordPress-тему на хостинг Бегет по SSH, активирует её, проверяет доступность сайта и корректность SSL/редиректов.

## Когда вызывать / в каком этапе
Запускается на **этапе 09 (deploy)** после того, как `/landing-build` утверждён пользователем. Вызывается командой `/landing-deploy` или через `landing-orchestrator`. Агент не стартует, если `.landing-state.yaml` показывает `current_stage != 09_deploy` — в этом случае он останавливается и сообщает об ошибке.

## Что на вход / на выход

**Вход:**
- Собранная WordPress-тема в директории проекта (выход этапа 08).
- Файл `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`.
- `.landing-state.yaml` с подтверждённым статусом предыдущих этапов.

**Выход:**
- Работающий сайт на Бегете по HTTPS-адресу.
- Активированная тема и импортированные ACF/Lazy Blocks поля.
- Настроенные редиректы HTTP→HTTPS и www→без www.
- Обновлённый `.landing-state.yaml` с отметкой `09_deploy: approved`.

**Ход работы:**
1. Читает `.landing-state.yaml`, показывает Mermaid-карту pipeline.
2. Создаёт TodoWrite-список оставшихся этапов.
3. Запускает `scripts/gate-check.sh --stage 09_deploy`.
4. Выполняет `scripts/deploy.sh <project-dir>` (rsync + wp-cli).
5. Проверяет сайт: `curl -sI https://<domain>`.
6. При необходимости выдаёт инструкцию по certbot для SSL.
7. **HARD GATE**: показывает URL и ждёт явного утверждения пользователя.

## Связанные концепты
- [[landing-build]] — предшествующий этап 08, без его approve деплой не запустится
- [[landing-orchestrator]] — вызывает wp-deployer как часть общего pipeline
- [[stage-execution-protocol]] — обязательный протокол preflight перед любым действием
- [[landing-deploy]] — slash-команда, которая активирует этого агента

## Источник
- `agents/wp-deployer.md`
---
slug: wp-deployer
type: agent
name: "WP Deployer — Деплой-инженер"
stage: "09"
tags: [deploy, beget, ssh, rsync, wp-cli, ssl, dns]
triggers: [landing-deploy]
inputs: [08-kod]
outputs: [09-deploy]
gates: [deploy_gate]
pre_reqs: [08-kod]
related: [landing-deploy, wp-cli-deployer, landing-build, 09-deploy, 10-qa]
sources: ["agents/wp-deployer.md"]
updated: 2026-06-19
confidence: {gates: low, triggers: low}
---

# WP Deployer — Деплой-инженер

## Что делает

Разворачивает готовый WordPress-лендинг на хостинг Бегет. Проверяет переменные окружения, запускает скрипт деплоя, загружает и активирует тему, импортирует ACF-поля. После деплоя автоматически проверяет доступность сайта через curl, контролирует SSL и редиректы (HTTP→HTTPS, www→без www). Не переходит к следующему этапу без явного утверждения пользователем живого URL.

## Когда вызывается

Вызывается командой `/landing-deploy` после того, как этап 08 (генерация кода) закрыт и одобрен пользователем. Физически блокируется hook'ом `enforce_stage_gate.py`, если предшествующие этапы не завершены.

## Вход → выход

**Вход:** сгенерированный WordPress-код в `08_КОД/` (этап `08-kod` в статусе approved); `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`; `.landing-state.yaml` с `current_stage == 09_deploy`.

**Выход:** задеплоенный и работающий сайт на Бегете; подтверждённый HTTPS-URL; этап `09_deploy` переведён в статус `approved` через `gate-state.sh`.

## Чем закрывается этап (gates)

- deploy_gate — сайт открывается по HTTPS, curl -sI возвращает 200, SSL-сертификат активен, HTTP→HTTPS и www→не-www редиректы работают; пользователь явно одобрил живой URL.

## Failure modes

- `.env` отсутствует или содержит неверные BEGET_*-переменные — деплой падает на первом шаге до rsync.
- SSH-соединение с Бегетом не устанавливается (неправильный host, ключ не добавлен) — `deploy.sh` завершается с ненулевым кодом.
- SSL-сертификат не выпущен или certbot недоступен — сайт открывается по HTTP, hard gate не проходит.
- Тема загружена, но не активирована (конфликт имён или PHP-ошибка) — wp-cli возвращает ошибку, сайт показывает дефолтную тему.
- Предшественник `08-kod` не закрыт — hook `enforce_stage_gate.py` блокирует любые Write/Edit операции с файлами этапа.

## Related

- [[landing-deploy]] — slash-команда, которая вызывает этого агента
- [[wp-cli-deployer]] — скрипты деплоя и rsync-утилиты
- [[landing-build]] — предыдущий этап, генерирует код для деплоя
- [[09-deploy]] — этап pipeline, который закрывает агент
- [[10-qa]] — следующий этап после успешного деплоя
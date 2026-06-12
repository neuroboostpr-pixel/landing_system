---
slug: 09-deploy
type: stage
name: "09 Деплой"
stage: "09"
tags: [deploy, beget, ssh, wp-cli, wordpress]
triggers: [landing-deploy]
inputs: [08-kod, beget-config.yaml]
outputs: [deploy-log.md, beget-config.yaml]
gates: [deploy_success]
pre_reqs: [landing-build, wp-cli-deployer]
related: [landing-deploy, wp-deployer, wp-cli-deployer, landing-rollback, 06-stek]
sources: ["template/09_ДЕПЛОЙ/README.md"]
updated: 2026-05-26
confidence: {gates: low, inputs: low}
---

# 09 Деплой

## Что делает

Этап переносит собранную WordPress-тему и все её зависимости на хостинг Бегет через SSH+rsync+wp-cli. Агент `wp-deployer` подключается к серверу, копирует файлы темы, импортирует медиа-ассеты и активирует сайт. По завершении формируется `deploy-log.md` с результатами и временными метками. Credentials Бегет берутся из `beget-config.yaml`, который хранится только локально и не попадает в git.

## Когда вызывается

Запускается командой `/landing-deploy` после того, как этап 08 (сборка кода) завершён и пользователь явно подтвердил готовность к деплою. Без закрытого этапа 08 оркестратор не пускает на этот шаг.

## Вход → выход

**Вход:** готовый WordPress-theme из `08_КОД/`, `beget-config.yaml` с SSH-credentials (hostname, user, пароль или ключ), подтверждение пользователя о деплое.

**Выход:** сайт активен на Бегет-хосте; `deploy-log.md` с записью о прошедшем деплое; опционально `beget-config.yaml` если credentials вводились впервые.

## Чем закрывается этап (gates)

- deploy_success — SSH-соединение установлено, rsync завершился без ошибок, wp-cli активировал тему и вернул статус OK.

## Failure modes

- SSH-подключение не проходит — неверные credentials или ключ не добавлен в authorized_keys на Бегете.
- rsync падает из-за прав доступа — папка `public_html` не writable для SSH-пользователя.
- wp-cli недоступен на сервере — нужна ручная установка или путь к бинарнику не задан в `beget-config.yaml`.
- `beget-config.yaml` случайно добавлен в git — утечка credentials; нужен `.gitignore`-аудит перед пушем.
- Деплой прошёл, но тема не активировалась — конфликт с другой активной темой или плагином безопасности на сервере.

## Related

- [[landing-deploy]] — slash-команда, запускающая этот этап
- [[wp-deployer]] — агент, выполняющий SSH+rsync+wp-cli операции
- [[wp-cli-deployer]] — скилл с логикой импорта медиа и активации темы
- [[landing-rollback]] — откат деплоя при критической ошибке
- [[06-stek]] — этап выбора стека, определяет конфигурацию Бегет-сервера
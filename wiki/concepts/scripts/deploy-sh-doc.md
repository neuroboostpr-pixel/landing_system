---
type: script
name: deploy
language: bash
sources: ["scripts/deploy.sh"]
updated: 2026-05-18
triggers: []
stage: "09"
uses: ["wp-deployer", "wp-cli-deployer", "landing-deploy"]
tags: ["deploy", "bash", "orchestrator"]
---

# deploy.sh — Оркестратор деплоя лендинга

## Что делает
Bash-скрипт верхнего уровня, который запускает полный процесс деплоя лендинг-проекта на хостинг. Принимает путь к папке проекта и последовательно выполняет все шаги публикации сайта.

## Когда вызывать / в каком этапе
Используется на **этапе 09 (Deploy)** — после того как WordPress-тема собрана (`/landing-build`) и одобрена пользователем. Скрипт вызывается вручную или через агента `wp-deployer` / команду `/landing-deploy`.

```bash
deploy.sh <project-dir>
```

Аргумент `<project-dir>` — абсолютный или относительный путь к папке проекта (например `~/Lendings/my-project`).

## Что на вход / на выход

**Вход:**
- `<project-dir>` — папка лендинг-проекта со стандартной структурой (13 подпапок 00–12)
- Собранная WordPress-тема в `08_КОД/`
- Настроенный `.env` / `config/system.yaml` с SSH-доступом к Beget

**Выход:**
- Задеплоенный сайт на Beget (rsync + wp-cli)
- Сконфигурированный SSL и DNS
- Обновлённый статус этапа 09 в `.landing-state.yaml`

## Связанные концепты
- [[wp-deployer]] — агент, который вызывает этот скрипт; управляет SSH+rsync+wp-cli
- [[wp-cli-deployer]] — скилл с логикой деплоя через wp-cli
- [[landing-deploy]] — slash-команда `/landing-deploy`, точка входа для пользователя
- [[09-deploy]] — этап шаблона проекта, в котором выполняется деплой

## Источник
- `scripts/deploy.sh`
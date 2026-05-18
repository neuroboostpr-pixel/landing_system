---
type: rule
name: validate-all
sources: ["scripts/validate-all.sh", "scripts/validate-all.sh.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wp-cli-deployer", "deploy-wordpress"]
tags: ["validation", "bash", "ci", "stage-08", "api-validators"]
---

# validate-all.sh — общий валидатор системы

## Что делает

Запускает агрегированную проверку всей системы: сначала проверяет, что `deploy-wordpress.sh` устанавливает плагин `lazy-blocks`, затем вызывает Python-агрегатор `tools/api_validators/aggregate.py`, который собирает остальные валидации воедино.

## Когда вызывать / в каком этапе

Запускается вручную или в CI перед деплоем (этап 08+). Используется разработчиком и CI-пайплайном для проверки целостности системы до релиза. Можно вызвать с флагом `--service <name>` для проверки только одного сервиса.

## Что на вход / на выход

**Вход:**
- Опциональный аргумент `--service <name>` — ограничивает проверку одним сервисом.
- Файл `.env` в корне репо (если присутствует — загружается автоматически).
- `skills/wp-cli-deployer/scripts/deploy-wordpress.sh` — проверяется grep'ом на наличие команды `wp plugin install lazy-blocks`.

**Выход:**
- `exit 0` — все проверки прошли успешно.
- `exit 1` — `deploy-wordpress.sh` не устанавливает `lazy-blocks`, либо Python-агрегатор вернул ошибку. В консоль выводится сообщение с символом ❌.

## Связанные концепты

- [[wp-cli-deployer]] — скрипт `deploy-wordpress.sh` из этого скилла является одним из объектов проверки.
- [[08-kod]] — этап сборки, для которого критична установка `lazy-blocks` на prod.

## Источник

- `scripts/validate-all.sh`
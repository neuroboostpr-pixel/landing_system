---
slug: wp-deployer
type: agent
name: "WP Deployer — Деплой-инженер"
stage: "09"
tags: [deploy, beget, ssh, rsync, wp-cli, ssl, wordpress]
triggers: [landing-deploy]
inputs: [08_КОД]
outputs: [deployed-site-url]
pre_reqs: [frontend-builder]
related: [landing-orchestrator, lifecycle-keeper, integrations-engineer, frontend-builder]
sources: ["agents/wp-deployer.md"]
updated: 2026-05-26
confidence: {triggers: low, inputs: low}
---

# WP Deployer — Деплой-инженер

## Что делает

Берёт собранную WordPress-тему из этапа 08 и деплоит её на хостинг Бегет через SSH + rsync + wp-cli. После загрузки активирует тему, проверяет доступность сайта через curl, убеждается что SSL-сертификат установлен и редиректы HTTP→HTTPS и www→без www работают корректно. Завершает работу только после явного подтверждения пользователем — показывает финальный URL.

## Когда вызывается

Запускается командой `/landing-deploy` на этапе 09, строго после того как этап 08 (`08_КОД`) получил статус `approved`. `landing-orchestrator` вызывает агента автоматически, если пользователь следует основному workflow через `/landing-go`. Физический Stage Gate (`enforce_stage_gate.py`) блокирует любые действия, пока предшественник не закрыт.

## Вход → выход

**Вход:** Собранная тема WordPress в `08_КОД/` (файлы темы, ACF/Lazy Blocks конфиги), заполненный `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`, и статус этапа 08 = `approved` в `.landing-state.yaml`.

**Выход:** Рабочий сайт на Бегете — тема активирована, SSL настроен, редиректы проверены, URL сайта передан пользователю для финального апрува (HARD GATE).

## Failure modes

- **Нет `.env` или неполные переменные** — `scripts/deploy.sh` падает ещё до rsync; агент останавливается и сообщает какие переменные отсутствуют.
- **SSH-соединение отклонено** — неверный ключ или IP Бегета в firewall; агент выводит stderr rsync и предлагает проверить `~/.ssh/config`.
- **Сайт не открывается после деплоя** — curl возвращает 5xx или таймаут; обычно тема не активирована или `wp-cli` упал на импорте полей.
- **SSL не настроен** — curl показывает HTTP 200 без редиректа; агент выдаёт инструкцию для `certbot --nginx` по SSH, но не выполняет её автоматически.
- **Stage Gate не пройден** — `gate-check.sh --stage 09_deploy` возвращает exit != 0; агент полностью останавливается — обойти нельзя.

## Related

- [[frontend-builder]] — генерирует артефакты этапа 08, которые деплоит этот агент
- [[landing-orchestrator]] — диспатчит wp-deployer в нужный момент pipeline
- [[lifecycle-keeper]] — обновляет `.landing-state.yaml` после успешного деплоя
- [[integrations-engineer]] — настраивает CRM/аналитику до деплоя; конфиги должны быть готовы
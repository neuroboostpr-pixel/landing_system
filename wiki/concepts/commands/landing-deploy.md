---
slug: landing-deploy
type: command
name: "Деплой лендинга на Beget"
stage: "09"
tags: [deploy, beget, wordpress, ssh, rsync, wp-cli]
triggers: [landing-deploy]
inputs: [08-kod]
outputs: [09-deploy]
gates: [site_live, ssl_ok, http_https_redirect]
pre_reqs: [08-kod]
related: [landing-build, landing-qa, wp-cli-deployer, wp-deployer, landing-go, landing-onboarding]
sources: ["commands/landing-deploy.md"]
updated: 2026-06-22
confidence: {gates: low}
---

# Деплой лендинга на Beget

## Что делает

Команда публикует готовый WordPress-лендинг на хостинг Beget. Она берёт скомпилированную тему из папки `08_КОД/wp-theme/`, загружает её на сервер через rsync по SSH, активирует тему, импортирует ACF-поля и сбрасывает кэш. После деплоя проверяет что сайт доступен по HTTPS и работает редирект с HTTP. Этап завершается только после явного подтверждения пользователя — live URL показывается на экране и ждёт approve.

## Когда вызывается

Вызывается вручную командой `/landing-deploy` после того как этап 08 (сборка кода) пройден и пользователь его одобрил. Перед стартом проверяет завершённость onboarding и gate-check этапа 09. Если onboarding не пройден или предыдущий этап не закрыт — останавливается с сообщением об ошибке.

## Вход → выход

**Вход:** тема WordPress в `08_КОД/wp-theme/`; файл `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`; завершённый этап 08.

**Выход:** живой WordPress-сайт на Beget с активированной темой, импортированными ACF-полями и сброшенным кэшем. Статус этапа 09 в `.landing-state.yaml` помечается как выполненный.

## Чем закрывается этап (gates)

- **site_live** — `curl -sI https://<domain>` возвращает 200; сайт отвечает по HTTPS
- **ssl_ok** — SSL-сертификат валиден и активен
- **http_https_redirect** — HTTP-запросы корректно редиректятся на HTTPS (301/302)

## Failure modes

- `.env` не заполнен или отсутствует `BEGET_PATH` — rsync падает без понятного сообщения
- Onboarding не пройден (`setup-flag.sh` exit 1) — команда останавливается до деплоя
- Gate-check этапа 09 не прошёл — предыдущий этап не закрыт, деплой заблокирован
- SSL ещё не выпущен на Beget — HARD GATE не пройдёт, пользователь видит ошибку curl
- WordPress установлен в подпапку, а `.htaccess` настроен неверно — REST API отвечает 404, WP-admin ломается (фикс: `RewriteBase /slug/`, см. beget-cookbook §7)

## Related

- [[landing-build]] — предыдущий этап, поставляет `08_КОД/wp-theme/`
- [[landing-qa]] — следующий этап после деплоя
- [[wp-cli-deployer]] — скилл с логикой деплоя (deploy.sh, fix-page-content-images)
- [[landing-go]] — оркестратор, вызывает landing-deploy в автоматическом потоке
- [[landing-onboarding]] — онбординг, обязателен до первого деплоя
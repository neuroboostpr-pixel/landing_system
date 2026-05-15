---
type: command
name: landing-deploy
sources: ["commands/landing-deploy.md"]
updated: 2026-05-15
triggers:
  - "задеплой лендинг на сервер"
  - "выгрузи сайт на Бегет"
  - "загрузи тему на хостинг"
  - "опубликуй лендинг"
stage: "09"
uses:
  - landing-build
  - landing-orchestrator
  - wp-deployer
tags: ["deploy", "beget", "ssh", "rsync", "wp-cli", "stage-09"]
---

# /landing-deploy — Деплой лендинга на Бегет

## Что делает

Загружает готовую WordPress-тему на хостинг Бегет по SSH+rsync, активирует тему через WP-CLI и проверяет, что сайт живой. После деплоя пользователь видит рабочую ссылку и подтверждает результат.

## Когда вызывать / в каком этапе

Этап 09. Вызывается вручную командой `/landing-deploy` после того, как пользователь одобрил результат `/landing-build` (этап 08). Перед запуском система автоматически проверяет: онбординг пройден, предыдущие этапы закрыты.

## Что на вход / на выход

**Вход:**
- `08_КОД/wp-theme/` — собранная тема от `/landing-build`
- `.env` с переменными `BEGET_USER`, `BEGET_HOST`, `BEGET_PATH`
- Пройденный онбординг (`~/.landing-system/setup_complete`)

**Выход:**
- Живой WordPress-сайт на Бегет
- Тема активирована, ACF-поля импортированы, кэш сброшен
- HTTPS подтверждён, редирект HTTP→HTTPS работает

## Шаги выполнения

1. **Pre-flight проверка** — `scripts/setup-flag.sh is_complete`. Если онбординг не пройден — стоп.
2. **Gate-check** — `scripts/gate-check.sh --stage 09_deploy --project <project>`. Если предыдущий этап не закрыт — сообщает, чего не хватает, и стоп.
3. **Preflight среды** — `scripts/preflight.sh` проверяет окружение (ключи SSH, доступность сервера).
4. **Деплой** — `scripts/deploy.sh .` синхронизирует тему по rsync, активирует через WP-CLI.
5. **Проверка живости** — `curl -sI https://<domain>`, SSL и редирект.
6. **HARD GATE** — показывает живую ссылку, ждёт явного одобрения пользователя.
7. **Post-completion** — `scripts/gate-check.sh --approve` фиксирует этап 09 как завершённый.

## Связанные концепты

- [[landing-build]] — обязательный предыдущий этап, поставляет `08_КОД/wp-theme/`
- [[landing-orchestrator]] — мастер-оркестратор, управляет порядком этапов
- [[wp-deployer]] — специализированный агент, выполняющий SSH+rsync+WP-CLI операции
- [[landing-qa]] — следующий этап после деплоя (этап 10, проверка живого сайта)

## Источник

- `commands/landing-deploy.md`
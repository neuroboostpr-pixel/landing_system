---
slug: landing-onboarding
type: skill
name: "Онбординг landing-system"
stage: ""
tags: [setup, onboarding, dependencies, api-keys, mcp]
triggers: [landing-onboarding]
inputs: []
outputs: ["~/.landing-system/setup_complete"]
pre_reqs: []
related: [landing-go, landing-start, landing-new, landing-photos, landing-visuals, system-setup]
sources: ["skills/landing-onboarding/SKILL.md"]
updated: 2026-06-19
confidence: {inputs: low}
---

# Онбординг landing-system

## Что делает

Настраивает landing-system на новой машине за один прогон. Проверяет наличие локальных зависимостей, MCP-серверов, плагина superpowers и 15 API-ключей. При необходимости устанавливает codex CLI (`npm i -g @openai/codex`) и запускает `codex login`. По завершении создаёт файл-флаг `~/.landing-system/setup_complete` с ISO-меткой времени — все остальные `/landing-*` команды проверяют его перед началом работы.

## Когда вызывается

Явно — через слеш-команду `/landing-onboarding`. Автоматически — когда любая `/landing-*` команда не находит файл `~/.landing-system/setup_complete` и перенаправляет пользователя сюда. Без codex CLI этапы `07c` (photos) и `07d` (visuals) недоступны.

## Вход → выход

**Вход:** чистая машина с установленным Claude Code и доступом к сети; API-ключи в переменных окружения или готовые для ввода интерактивно.

**Выход:** `~/.landing-system/setup_complete` — файл-флаг с меткой времени; все 15 API-валидаторов возвращают OK; `codex` доступен на PATH; MCP-серверы сконфигурированы.

## Failure modes

- **codex не устанавливается** — отсутствует `npm` или Node.js; скрипт `install-codex.sh` падает без подсказки по причине.
- **API-валидатор зависает** — один из 15 сервисов недоступен, `validate-all.sh` ждёт timeout без промежуточного вывода.
- **setup_complete создан, но MCP сломан** — флаг выставлен, но MCP-серверы не стартуют; `/landing-go` не перенаправит на онбординг повторно.
- **Smoke-test падает на mock-codex** — `USE_CODEX_MOCK=1` не подхватывается окружением (Windows path issues).
- **Повторный прогон не перезаписывает флаг** — `setup-flag.sh` не обновляет ISO-метку при апдейте зависимостей, статус кажется актуальным, хотя окружение изменилось.

## Related

- [[landing-go]] — главная точка входа после онбординга; проверяет setup_complete перед запуском оркестратора
- [[landing-start]] — wizard для нового проекта; также требует setup_complete
- [[landing-photos]] — этап 07c, требует codex CLI установленного этим скиллом
- [[landing-visuals]] — этап 07d, аналогично зависит от codex
- [[system-setup]] — связанная концепция управления машинным окружением
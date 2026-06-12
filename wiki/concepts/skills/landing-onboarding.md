---
slug: landing-onboarding
type: skill
name: "Онбординг landing-system"
tags: [onboarding, setup, validation, deps, api-keys, mcp]
triggers: [landing-onboarding]
inputs: []
outputs: ["~/.landing-system/setup_complete"]
pre_reqs: []
related: [system-setup, landing-orchestrator, onboarding-guide]
sources: ["skills/landing-onboarding/SKILL.md"]
updated: 2026-05-26
confidence: {stage: low}
---

# Онбординг landing-system

## Что делает

Скилл выполняет первичную настройку landing-system на новой машине: проверяет локальные зависимости, MCP-серверы, плагин superpowers и все API-ключи (15 валидаторов). После успешной проверки записывает флаг `~/.landing-system/setup_complete` с ISO-таймстампом. Начиная с PR-D также устанавливает codex CLI (`npm i -g @openai/codex` + `codex login`), без которого не работают `/landing-photos` и `/landing-visuals`.

## Когда вызывается

Запускается явно командой `/landing-onboarding` или автоматически при первом вызове любой `/landing-*` команды, если файл `~/.landing-system/setup_complete` отсутствует. Это жёсткий prerequisite: без пройденного онбординга система блокирует любой следующий шаг.

## Вход → выход

**Вход:** чистая машина с установленным Claude Code и доступом к интернету. API-ключи и конфигурация MCP предполагаются наличными у пользователя (вводятся интерактивно в ходе wizard).

**Выход:** файл `~/.landing-system/setup_complete` (флаг с ISO-таймстампом), настроенные зависимости, проверенные API-ключи, установленный `codex` CLI. Машина готова к запуску `/landing-go`.

## Failure modes

- **codex CLI отсутствует после установки** — npm не на PATH или нет интернета; скрипт `install-codex.sh` падает без явной диагностики.
- **API-ключ невалиден** — `validate-all.sh` не проходит один из 15 валидаторов; setup_complete не создаётся, сообщение об ошибке может быть неочевидным.
- **MCP-сервер недоступен** — wizard зависает на проверке MCP-коннекта; нужно проверить конфиг `.mcp.json` вручную.
- **setup_complete устарел** — флаг есть, но окружение изменилось (новые ключи, новый MCP); система не запросит повторную проверку без ручного удаления файла.
- **Smoke-тест падает** — `USE_CODEX_MOCK=1 bash scripts/test-pipeline.sh smoke-onboarding ...` не прошёл, но setup_complete уже записан; пайплайн будет работать нестабильно.

## Related

- [[system-setup]] — низкоуровневая инфраструктура машины, которую онбординг проверяет
- [[landing-orchestrator]] — главный агент, который блокируется до появления setup_complete
- [[onboarding-guide]] — пользовательский гайд, параллельный этому скиллу
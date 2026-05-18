---
type: rule
name: stage-gates-onboarding-design
sources: ["docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-onboarding", "onboarding-guide", "landing-orchestrator", "stage-gates", "landing-new", "landing-go"]
tags: ["workflow-lock", "gates", "onboarding", "api-validators", "state"]
---

# Stage Gates & Onboarding — Design Spec (MVP)

## Что делает

Превращает landing-system из «набора агентов с декларативными HARD GATE» в **систему с принудительным workflow**: без пройденного onboarding никакая `/landing-*` команда не запустится, а переход между этапами проекта возможен только после автоматической проверки готовности (`gate-check`).

## Когда вызывать / в каком этапе

Это архитектурный spec — он описывает поведение, встроенное в **все** этапы (00–12). Активируется:
- При первой установке репо: `/landing-onboarding` до любой другой команды.
- На каждом этапе каждого проекта: `scripts/gate-check.sh --stage N` запускается автоматически из slash-команд.

## Что на вход / на выход

**Вход:**
- `config/stage-gates.yaml` — декларативный YAML с hard/soft-checks для каждого этапа.
- `~/.landing-system/setup_complete` — флаг пройденного onboarding (создаётся wizard'ом).
- `{project}/.landing-state.yaml` — статусы 13 этапов проекта (`locked` → `in_progress` → `approved`).

**Выход (артефакты, создаваемые подсистемой):**
- `~/.landing-system/setup_complete` — после успешного onboarding.
- `{project}/.landing-state.yaml` — создаётся при `/landing-new`, обновляется `gate-check.sh`.
- `.env` — пополняется API-ключами в ходе wizard.
- `tools/api_validators/*.py` — 15 Python-валидаторов (Firecrawl, Pexels, Telegram, Beget SSH и др.).

**Три подсистемы:**
1. **Onboarding** — одноразовый мастер-wizard `/landing-onboarding`: туториал + проверка зависимостей + валидация всех API-ключей.
2. **Stage Gates** — `gate-check.sh` читает `stage-gates.yaml`, прогоняет hard_checks автоматически и soft_checks через агента.
3. **Workflow Lock** — `.landing-state.yaml` хранит статус каждого этапа; `require_approved` в yaml запрещает запускать этап, если предыдущие не `approved`.

**Acceptance criteria:**
- Свежий клон → `/landing-new test` → отказ с редиректом на `/landing-onboarding`.
- `/landing-build` без approved 02–07 → `exit 1` с сообщением.
- Bats-тесты `tests/api_validators/`, `tests/onboarding/`, `tests/gate-check/`, `tests/e2e/` проходят.

## Связанные концепты

- [[stage-gates]] — конфиг `config/stage-gates.yaml`, источник всех проверок
- [[landing-onboarding]] — slash-команда точки входа в wizard
- [[onboarding-guide]] — агент-проводник через wizard (новый агент из этого spec)
- [[landing-orchestrator]] — читает `.landing-state.yaml` и enforce порядок этапов
- [[landing-new]] — создаёт `.landing-state.yaml` при старте проекта
- [[landing-go]] — главная команда, диспатчит следующий этап через orchestrator

## Источник

- `docs/superpowers/specs/2026-05-04-stage-gates-onboarding-mcp-design.md`
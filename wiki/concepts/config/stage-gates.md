---
type: rule
name: stage-gates-config
sources: ["config/stage-gates.yaml"]
updated: 2026-05-20
triggers: []
stage: ""
uses: ["gate-check-sh", "landing-orchestrator", "niche-analyst", "brand-architect", "wp-builder", "wp-deployer", "qa-auditor", "analytics-engineer", "seo-optimizer"]
tags: ["gates", "pipeline", "quality", "hard-gate", "soft-gate"]
---

# Stage Gates Config — конфигурация гейтов пайплайна

## Что делает
Главный файл истины для всех проверок между этапами лендинг-системы. Задаёт для каждого из 15 этапов: тип блокировки (hard/soft), список обязательных файлов, скриптов-валидаторов и вопросов для ручной проверки. Читается скриптом `gate-check.sh` перед тем, как `landing-orchestrator` перейдёт к следующему этапу.

## Когда вызывать / в каком этапе
Файл читается автоматически при каждом вызове `scripts/gate-check.sh` — а тот запускается оркестратором перед переходом на новый этап. Вручную редактировать только при добавлении нового этапа или изменении требований к существующему.

## Что на вход / на выход

**Вход:**
- Путь к проекту (`{project}` — подставляется gate-check.sh)
- Состояние `.landing-state.yaml` (какие этапы уже approved)

**Выход (через gate-check.sh):**
- `exit 0` — все проверки пройдены, оркестратор продолжает
- `exit 1` — блокировка; в stdout — список упавших проверок с `fix_hint` для автофикса

**Типы проверок:**
- `file_exists` / `dir_has_files` — наличие артефактов
- `script` — запуск валидаторов (Python/Bash)
- `api_validator` / `api_validator_any_of` — доступность API-ключей
- `http_ping` — доступность CDN
- `soft_checks[].prompt` — вопрос к пользователю (не блокирует, но фиксируется)

**Ключевые hard-гейты (lock: hard):**
| Этап | Требует approved |
|---|---|
| `07b_wireframe` | 04_brand, 05_design, 07a_prototype |
| `07c_composed` | 05_design, 07a_prototype, 07b_wireframe |
| `08_build` | 07c_composed |
| `09_deploy` | 08_build, 10_qa |
| `10_qa` | 08_build |

**Legacy bypass:** `legacy_allowed: []` — список пуст по умолчанию. Добавлять явно с `legacy_reason:` в state-файле.

## Связанные концепты
- [[gate-check-sh]] — скрипт, который читает этот файл и выполняет проверки
- [[landing-orchestrator]] — вызывает gate-check.sh перед каждым переходом
- [[landing-state-yaml]] — хранит статусы этапов (`approved`/`pending`/`n/a`)
- [[verify-composed-premium-sh]] — один из вызываемых скриптов (этап 07c)
- [[verify-content-preserved-sh]] — скрипт контент-интегрити (этапы 07c, 07f)
- [[niche-analyst]] — создаёт артефакты для этапа `01a_niche_analysis`
- [[wp-builder]] — создаёт артефакты для этапа `08_build`
- [[wp-deployer]] — активируется после прохождения гейта `09_deploy`

## Источник
- `config/stage-gates.yaml`
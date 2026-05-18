---
type: rule
name: stage-gates
sources: ["config/stage-gates.yaml"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["landing-orchestrator", "niche-analyst", "brand-architect", "references-curator", "design-system-generator", "block-composer", "wp-builder", "wp-deployer", "qa-auditor", "premium-07b-checklist"]
tags: ["gates", "pipeline", "quality", "validation"]
---

# Stage Gates — контроль качества этапов pipeline

## Что делает
Описывает все проверки (hard и soft), которые система обязана пройти перед переходом к каждому из 20 этапов производства лендинга. Это единственный «источник истины» для gate-check.sh — без него оркестратор не знает, что считать «готовым».

## Когда вызывать / в каком этапе
Файл читается автоматически при каждом вызове `scripts/gate-check.sh` — то есть при каждом переходе между этапами внутри `landing-orchestrator`. Пользователь не вызывает его напрямую; он срабатывает в фоне.

## Что на вход / на выход

**Вход:** путь к проекту (`{project}`) — gate-check.sh подставляет его в каждый `path` и `args`.

**Выход:** два вида проверок на каждый этап:

- **hard_checks** — автоматические: существование файла (`file_exists`), запуск валидирующего скрипта (`script`), доступность API (`api_validator`), HTTP-пинг CDN (`http_ping`). Провал = блокировка этапа.
- **soft_checks** — вопрос к пользователю (prompt). Провал = предупреждение, не блокировка.

**Типы lock:**
- `soft` — оркестратор предупреждает, но движется дальше.
- `hard` — оркестратор стоит, пока все hard_checks не зелёные.

**Ключевые зависимости между этапами** (`require_approved`): например, `07b_wireframe` требует утверждения `04_brand`, `05_design`, `07a_prototype`; `09_deploy` требует `08_build` и `10_qa`.

**Примеры hard_checks:**
- `01a_niche_analysis` — 7 файлов + 4 валидирующих Python-скрипта.
- `07c_composed` — скрипт `verify-composed-premium.sh` проверяет premium-стандарт (13 фич: parallax, glassmorphism, slider…).
- `08_build` — PHP-синтаксис темы, JSON-схема Gutenberg-блоков, регистрация блоков.
- `09_deploy` — SSH к Бегету, Яндекс.Метрика, Telegram-бот, CRM-вебхук.

Каждый hard_check содержит `fix_hint` — подсказку что запустить при провале.

## Связанные концепты
- [[landing-orchestrator]] — читает gate-check.sh на каждом переходе
- [[niche-analyst]] — создаёт артефакты для этапа `01a_niche_analysis`
- [[brand-architect]] — создаёт `brand-kit.md` для этапа `04_brand`
- [[references-curator]] — создаёт `index.yaml` для этапа `03_references`
- [[block-composer]] — создаёт `composed.html` для этапов `07c_composed` и `07f_composed_final`
- [[premium-07b-checklist]] — стандарт, который проверяет `verify-composed-premium.sh`
- [[wp-builder]] — создаёт `wp-theme` для этапа `08_build`
- [[wp-deployer]] — деплоит на Бегет в этапе `09_deploy`
- [[qa-auditor]] — отвечает за этап `10_qa`

## Источник
- `config/stage-gates.yaml`
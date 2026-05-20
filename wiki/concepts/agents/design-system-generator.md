---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-20
triggers: []
stage: "05"
uses: ["brand-architect", "design-tokens-generation", "stage-execution-protocol", "landing-orchestrator"]
tags: ["design", "tokens", "stage-05", "дизайн-система"]
---

# design-system-generator (Генератор дизайн-системы)

## Что делает
Читает `brand-kit.md`, который собрал [[brand-architect]], и генерирует полноценную дизайн-систему: машиночитаемые токены, документ DESIGN.md и живой HTML-превью с компонентами. Всё с провенансом — каждый токен ведёт к источнику в бренд-ките.

## Когда вызывать / в каком этапе
Этап **05_design**. Запускается после того, как [[brand-architect]] создал `04_БРЕНД/brand-kit.md` и пользователь его утвердил. Агент активируется командой `/landing-design` или через [[landing-orchestrator]].

Перед любым действием агент обязан:
1. Прочитать `.landing-state.yaml` и убедиться, что `current_stage == 05_design`.
2. Запустить `scripts/render-pipeline-map.sh` и показать Mermaid-карту пользователю.
3. Пройти `scripts/gate-check.sh --stage 05_design` — при ненулевом exit остановиться.
4. После завершения запустить `scripts/verify-05_design.sh` и, если PASS, закрыть гейт через `scripts/gate-state.sh approve`.

**HARD GATE:** agент ждёт явного утверждения (`утверждаю`, `ok`, `дальше`) перед переходом к этапу 06.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — источник цветов, шрифтов, иконок, motion, grid

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый документ токенов с YAML frontmatter
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены (colors, typography, spacing, grid, radius, shadow, breakpoints, motion)
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живые компоненты, сгенерированные по токенам

**Структура токенов:** цвета (primary/secondary/accent/text/bg с провенансом), типографика (display/body/sizes), отступы (xs→3xl), сетка (columns/gap/max_width), радиусы, тени, брейкпоинты (mobile/tablet/desktop), motion (duration_fast/base/slow, easing).

## Связанные концепты
- [[brand-architect]] — предшественник: создаёт brand-kit.md, который агент читает как единственный источник данных
- [[design-tokens-generation]] — скилл, которому принадлежит агент; скрипты `build-tokens.py` и `render-preview.py` живут в нём
- [[stage-execution-protocol]] — обязательный протокол, которому следует агент перед каждым действием на этапе
- [[landing-orchestrator]] — мастер-оркестратор, который диспатчит агента в нужный момент pipeline

## Источник
- `agents/design-system-generator.md`
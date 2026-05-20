---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-20
triggers: []
stage: "05"
uses: ["brand-architect", "design-tokens-generation", "stage-execution-protocol", "stack-planner", "landing-orchestrator"]
tags: ["design", "tokens", "stage-05", "дизайн-система"]
---

# design-system-generator (Генератор дизайн-системы)

## Что делает
Превращает готовый `brand-kit.md` в полноценную дизайн-систему: токены, типографику, отступы, анимации — и выдаёт живой HTML-превью, чтобы заказчик мог сразу увидеть, как всё выглядит.

## Когда вызывать / в каком этапе
Запускается на **этапе 05 (05_ДИЗАЙН-СИСТЕМА)** после того, как [[brand-architect]] завершил работу и `04_БРЕНД/brand-kit.md` уже существует. Вызывается агентом [[landing-orchestrator]] или вручную через скилл [[design-tokens-generation]]. Без утверждённого `brand-kit.md` агент остановится.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — полный бренд-кит с палитрой, шрифтами, иконками (создаётся [[brand-architect]])
- `<project>/.landing-state.yaml` — должен быть `current_stage == 05_design`

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины: все токены с YAML frontmatter и провенансом (каждый цвет/шрифт трассируется к источнику)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для сборщика (цвета, типографика, отступы xs→3xl, сетка, радиусы, тени, брейкпоинты, motion)
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — интерактивный превью живых компонентов

## Порядок работы
1. Читает `.landing-state.yaml` и проверяет, что этап 05 активен; иначе STOP.
2. Запускает `render-pipeline-map.sh` — показывает Mermaid-карту пайплайна.
3. Создаёт TodoWrite со всеми оставшимися этапами.
4. Проходит `gate-check.sh --stage 05_design` — если не exit 0, блокируется.
5. Запускает `build-tokens.py` → `render-preview.py`.
6. Показывает путь к `design-preview.html`.
7. **HARD GATE:** ждёт явного `утверждаю` / `ok` / `дальше` от пользователя перед переходом к этапу 06.

Физическая блокировка через `PreToolUse` hook (`enforce_stage_gate.py`) — обойти нельзя, нужно закрыть предшественников.

## Связанные концепты
- [[brand-architect]] — создаёт `brand-kit.md`, который является основным входом
- [[design-tokens-generation]] — скилл, которому принадлежит агент; содержит скрипты `build-tokens.py` и `render-preview.py`
- [[stack-planner]] — следующий агент этапа 06, ожидает закрытого `05_design`
- [[landing-orchestrator]] — диспатчит агента в рамках общего пайплайна
- [[stage-execution-protocol]] — обязательный протокол перед любым действием

## Источник
- `agents/design-system-generator.md`
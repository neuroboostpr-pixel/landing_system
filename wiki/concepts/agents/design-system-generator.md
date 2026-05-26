---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-26
triggers: []
stage: "05_design"
uses: ["brand-architect", "design-tokens-generation", "landing-orchestrator", "stage-execution-protocol"]
tags: ["design", "tokens", "stage-05", "agent"]
---

# design-system-generator (Генератор дизайн-системы)

## Что делает

Берёт готовый бренд-кит и автоматически строит полную дизайн-систему проекта: цвета, шрифты, отступы, сетку, анимации — всё в единых токенах с живым HTML-превью для согласования с клиентом.

## Когда вызывать / в каком этапе

Запускается на **этапе 05 (`05_design`)** — строго после того, как [[brand-architect]] завершил работу и в `04_БРЕНД/brand-kit.md` есть утверждённый бренд. До запуска агент обязательно проверяет, что `.landing-state.yaml` показывает `current_stage == 05_design`. Если предшественник (этап 04) не закрыт — агент останавливается. Встроенный хук `enforce_stage_gate.py` физически блокирует запись файлов при незакрытых предшественниках.

После генерации агент ждёт явного утверждения пользователя (`утверждаю`, `ok`, `дальше`) — это **HARD GATE** перед переходом к этапу 06.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — утверждённый бренд-кит (цвета, шрифты, иконки, motion, grid)
- `<project>/.landing-state.yaml` — текущий статус pipeline

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины токенов с YAML frontmatter и провенансом
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены (colors, typography, spacing, grid, radius, shadow, breakpoints, motion)
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — интерактивный HTML с живыми компонентами по токенам

**Что входит в токены:**
цвета (primary/secondary/accent/text/bg), типографика (display/body/sizes), отступы (xs→3xl), сетка (columns/gap/max_width), скругления, тени, брейкпоинты (mobile/tablet/desktop), motion (длительности + easing).

## Связанные концепты

- [[brand-architect]] — предоставляет `brand-kit.md`, из которого агент извлекает все параметры
- [[design-tokens-generation]] — скилл, скрипты которого (`build-tokens.py`, `render-preview.py`) агент вызывает напрямую
- [[landing-orchestrator]] — диспатчит агента в рамках общего pipeline
- [[stage-execution-protocol]] — обязательный протокол проверок перед любым Write-действием (gate-check, Mermaid-карта, TodoWrite)

## Источник

- `agents/design-system-generator.md`
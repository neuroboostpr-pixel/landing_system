---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-19
triggers: []
stage: "05"
uses: ["brand-architect", "design-tokens-generation", "frontend-design", "moodboard-composer"]
tags: ["design", "tokens", "stage-05", "brand"]
---

# design-system-generator (Генератор дизайн-системы)

## Что делает
Берёт утверждённый `brand-kit.md` и строит полную дизайн-систему: выбирает смелую визуальную концепцию (editorial / brutalist / swiss-minimal и т.д.), генерирует дизайн-токены и рендерит живой HTML-превью компонентов. Главная задача — уйти от «AI-slop» (пурпурный градиент, центрированный hero) к конкретной, узнаваемой эстетике.

## Когда вызывать / в каком этапе
Этап **05**. Вызывается после того, как [[brand-architect]] завершил работу и в `04_БРЕНД/brand-kit.md` зафиксированы цвета, шрифты и иконки. Активируется командой `/landing-design` или оркестратором.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — источник цветов, шрифтов, иконок, motion и сетки
- `03_РЕФЕРЕНСЫ/moodboard.md` — mood-контекст для выбора концепции
- `00_БРИФ/brief.md` — тональность и ниша

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины токенов (YAML frontmatter + секция §2 Visual Direction)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены (colors, typography, spacing, grid, radius, shadow, breakpoints, motion)
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — живые компоненты по токенам

**HARD GATE:** агент ждёт явного утверждения пользователя перед переходом к этапу 06.

## Алгоритм работы
1. Вызывает скилл [[frontend-design]] — выбирает конкретную aesthetic-стратегию.
2. Читает `brand-kit.md`, извлекает токены.
3. Запускает `build-tokens.py` → `tokens.json` и `DESIGN.md`.
4. Запускает `render-preview.py` → `design-preview.html`.
5. Сообщает пользователю путь к превью и одной фразой описывает выбранную концепцию.
6. Ждёт утверждения.

**Anti-slop правила:** запрещены формулировки «modern minimalist clean», запрещён дефолтный градиент 135deg, запрещён центрированный hero без явного требования из бриф. Концепция должна иметь один «герой» — типографику, цвет или композицию.

## Связанные концепты
- [[brand-architect]] — предшественник, создаёт brand-kit.md, который читает этот агент
- [[design-tokens-generation]] — скилл-владелец агента, содержит скрипты build-tokens.py и render-preview.py
- [[frontend-design]] — скилл, вызывается первым для выбора визуальной концепции
- [[moodboard-composer]] — создаёт moodboard.md, контекст для выбора концепции
- [[ux-composer]] — следующий этап, использует DESIGN.md и tokens.json для wireframe

## Источник
- `agents/design-system-generator.md`
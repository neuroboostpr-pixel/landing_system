---
type: agent
name: design-system-generator
sources: ["agents/design-system-generator.md"]
updated: 2026-05-15
triggers: []
stage: "05"
uses:
  - brand-architect
  - brand-kit-build
  - design-tokens-generation
  - stack-planner
  - scene-director
tags:
  - дизайн-система
  - токены
  - этап-05
---

# design-system-generator (Генератор дизайн-системы)

## Что делает

Берёт готовый бренд-кит и превращает его в полноценную дизайн-систему: файл с токенами, машиночитаемый JSON и живой HTML-превью с компонентами. Это «единый источник истины» для всех следующих этапов: цвета, шрифты, отступы, тени, сетка и анимации — всё в одном месте с указанием откуда взялось каждое значение (провенанс).

## Когда вызывать / в каком этапе

Этап **05 — Дизайн-система**. Запускается строго после того, как агент [[brand-architect]] завершил работу и файл `04_БРЕНД/brand-kit.md` существует. До этого запускать нельзя — нечего будет читать. Переход к этапу 06 ([[stack-planner]]) возможен только после явного подтверждения пользователя (`утверждаю`, `ok`, `дальше`) — это **HARD GATE**.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/brand-kit.md` — бренд-кит с цветами, шрифтами, иконками, motion-параметрами и сеткой

**Выход:**
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — единый источник истины, токены с YAML frontmatter и провенансом (каждый цвет/шрифт ссылается на источник)
- `05_ДИЗАЙН-СИСТЕМА/tokens.json` — машиночитаемые токены для сборки темы
- `05_ДИЗАЙН-СИСТЕМА/design-preview.html` — интерактивный превью живых компонентов по токенам

**Структура токенов:**
цвета (primary / secondary / accent / text / bg), типографика (display / body / sizes), отступы (xs→3xl), сетка (columns / gap / max_width), скругления, тени, брейкпоинты (mobile / tablet / desktop), анимации (duration_fast/base/slow, easing).

**Скрипты:**
- `skills/design-tokens-generation/scripts/build-tokens.py <project-dir>` — строит DESIGN.md и tokens.json
- `skills/design-tokens-generation/scripts/render-preview.py <project-dir>` — рендерит design-preview.html

## Связанные концепты

- [[brand-architect]] — предшествующий агент, создаёт brand-kit.md, который этот агент читает
- [[brand-kit-build]] — скилл-владелец: design-system-generator входит в его область ответственности
- [[design-tokens-generation]] — скилл, которому принадлежит агент; содержит скрипты build-tokens и render-preview
- [[stack-planner]] — следующий этап (06): получает токены и определяет плагины/библиотеки
- [[scene-director]] — альтернативный следующий шаг (только cinematic mode): использует tokens.json для motion-плана

## Источник

- `agents/design-system-generator.md`
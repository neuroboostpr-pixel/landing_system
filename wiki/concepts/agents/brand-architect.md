---
type: agent
name: brand-architect
sources: ["agents/brand-architect.md"]
updated: 2026-05-26
triggers: []
stage: "04"
uses: ["brand-kit-build", "style-extractor", "landing-orchestrator", "stage-execution-protocol"]
tags: ["brand", "stage-04", "design", "legal", "provenance"]
---

# Brand Architect — Агент сборки бренд-кита (этап 04)

## Что делает

Собирает единый бренд-кит из всех извлечённых стилевых данных: цвета, шрифты, иконки, сетка, анимации. Каждый токен имеет ссылку на источник (провенанс). Также собирает юридические реквизиты Оператора ПД для соответствия 152-ФЗ. На выходе — `brand-kit.md` и визуальный HTML-превью.

## Когда вызывать / в каком этапе

Запускается на **этапе 04_brand** — после того, как `style-extractor` отработал и в папке `04_БРЕНД/extracted/` появились все пять файлов: `palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`. Вызывается через `landing-orchestrator` или вручную через `/landing-brand`. До этапа нельзя работать, пока не закрыт этап 03 (Референсы).

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/extracted/palette.yaml` — цвета
- `04_БРЕНД/extracted/fonts.yaml` — шрифты
- `04_БРЕНД/extracted/icons.yaml` — иконки
- `04_БРЕНД/extracted/grid.md` — сетка и отступы
- `04_БРЕНД/extracted/motion.md` — анимационные токены
- `03_РЕФЕРЕНСЫ/index.yaml` — одобренные референсы
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (влияет на палитру и типографику)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — уровень премиальности, культурный контекст
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — список блоков, которые бренд-кит обязан покрыть

**Выход:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом
- `04_БРЕНД/brand-kit.html` — визуальный превью (свотчи, образцы шрифтов, иконки)
- `04_БРЕНД/extracted/legal.yaml` — юридические реквизиты (после опроса пользователя)

## Связанные концепты

- [[brand-kit-build]] — скилл, содержащий Python-скрипты `build.py` и `render-html.py`, которые агент запускает
- [[style-extractor]] — предшественник: извлекает цвета, шрифты, иконки из материалов клиента
- [[landing-orchestrator]] — вышестоящий агент, который запускает brand-architect в нужный момент pipeline
- [[stage-execution-protocol]] — обязательный протокол: проверка `.landing-state.yaml`, Mermaid-карта, TodoWrite, gate-check перед любым действием
- [[landing-design]] — следующий этап (05): дизайн-система строится поверх утверждённого бренд-кита

## Источник

- `agents/brand-architect.md`
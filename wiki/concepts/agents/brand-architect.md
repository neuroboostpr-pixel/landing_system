---
type: agent
name: brand-architect
sources: ["agents/brand-architect.md"]
updated: 2026-05-20
triggers: []
stage: "04"
uses: ["style-extractor", "brand-kit-build", "niche-analyst", "design-system-generator", "landing-orchestrator"]
tags: ["brand", "stage-04", "palette", "fonts", "icons", "provenance"]
---

# Brand Architect — Архитектор бренд-кита

## Что делает

Собирает все извлечённые стилевые данные (цвета, шрифты, иконки, сетку, анимации) в единый бренд-кит с полной прослеживаемостью источников. Каждый цвет, шрифт и иконка в итоговом документе указывает, откуда он взят. Рендерит визуальный HTML-превью для утверждения клиентом.

## Когда вызывать / в каком этапе

Этап **04_brand**. Запускается после того, как `style-extractor` завершил работу и все 5 файлов в `04_БРЕНД/extracted/` присутствуют: `palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`. До запуска `design-system-generator` (этап 05) не продвигаться — бренд-кит должен быть утверждён пользователем.

Активируется командой `/landing-brand` или вызывается `landing-orchestrator` автоматически.

## Что на вход / на выход

**Входные артефакты:**
- `04_БРЕНД/extracted/palette.yaml` — цвета из референсов
- `04_БРЕНД/extracted/fonts.yaml` — найденные шрифты
- `04_БРЕНД/extracted/icons.yaml` — подобранные иконки
- `04_БРЕНД/extracted/grid.md` — система сетки и отступов
- `04_БРЕНД/extracted/motion.md` — токены анимации
- `03_РЕФЕРЕНСЫ/index.yaml` — список утверждённых референсов
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (влияет на выбор палитры и типографики)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — уровень премиальности и культурный контекст
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — список блоков, которые бренд-кит обязан покрыть

**Выходные артефакты:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом
- `04_БРЕНД/brand-kit.html` — визуальный превью: свотчи палитры, образцы шрифтов, миниатюры иконок

**HARD GATE:** агент не закрывает этап 04 и не передаёт управление этапу 05 до явного утверждения `brand-kit.html` пользователем.

## Связанные концепты

- [[style-extractor]] — предшественник: готовит все 5 extracted-файлов, без которых brand-architect не стартует
- [[brand-kit-build]] — скилл, владелец бизнес-логики; агент вызывает его Python-скрипты `build.py` и `render-html.py`
- [[niche-analyst]] — поставляет `positioning.md` и `market-profile.md`, от которых зависит выбор стиля
- [[design-system-generator]] — следующий этап: потребляет `brand-kit.md` как источник истины
- [[landing-orchestrator]] — диспатчит агента в нужный момент пайплайна

## Источник

- `agents/brand-architect.md`
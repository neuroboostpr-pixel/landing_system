---
type: agent
name: brand-architect
sources: ["agents/brand-architect.md"]
updated: 2026-05-20
triggers: []
stage: "04"
uses: ["style-extractor", "brand-kit-build", "niche-analyst", "design-system-generator", "references-curator"]
tags: ["brand", "design", "stage-04", "provenance"]
---

# Brand Architect — сборщик бренд-кита

## Что делает
Собирает единый бренд-кит проекта: берёт все извлечённые стилевые данные (цвета, шрифты, иконки, сетку, анимацию) и синтезирует из них `brand-kit.md` с полной трассировкой источников — каждый цвет, шрифт и иконка ссылается на конкретный файл-источник. Параллельно рендерит визуальный HTML-превью со свотчами и образцами типографики.

## Когда вызывать / в каком этапе
Запускается на **этапе 04 (Бренд)** после того, как агент [[style-extractor]] завершил извлечение и в `04_БРЕНД/extracted/` появились все 5 артефактов. До этапа 05 (Design System) не переходить, пока пользователь не утвердил `brand-kit.html`.

Предусловие: `.landing-state.yaml` должен показывать `current_stage == 04_brand`, иначе агент останавливается.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/extracted/palette.yaml` — цвета (из `extract-palette.py`)
- `04_БРЕНД/extracted/fonts.yaml` — шрифты (из `identify-fonts.py`)
- `04_БРЕНД/extracted/icons.yaml` — иконки (из `match-icons.py`)
- `04_БРЕНД/extracted/grid.md` — система сетки и отступов
- `04_БРЕНД/extracted/motion.md` — токены анимации
- `03_РЕФЕРЕНСЫ/index.yaml` — список утверждённых референсов
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (`emotional_aspiration` / `trust_authority` / `rational`) — влияет на выбор палитры и типографики
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — `accessibility_tier` и `cultural_context` — задают уровень премиальности и культурные ограничения
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — список блоков, которые бренд-кит обязан покрыть

**Выход:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с провенансом
- `04_БРЕНД/brand-kit.html` — визуальный превью (свотчи, образцы шрифтов, иконки)

**Процесс:** вызывает два Python-скрипта через Bash:
1. `skills/brand-kit-build/scripts/build.py` → `brand-kit.md`
2. `skills/brand-kit-build/scripts/render-html.py` → `brand-kit.html`

## Связанные концепты
- [[style-extractor]] — обязательный предшественник, поставляет `extracted/*.yaml`
- [[brand-kit-build]] — скилл, которому принадлежит агент; содержит логику build.py и render-html.py
- [[niche-analyst]] — поставляет `positioning.md` и `market-profile.md`, влияющие на выбор стиля
- [[references-curator]] — поставляет утверждённый `index.yaml` референсов
- [[design-system-generator]] — следующий этап (05), потребляет `brand-kit.md`

## Источник
- `agents/brand-architect.md`
---
type: agent
name: brand-architect
sources: ["agents/brand-architect.md"]
updated: 2026-05-15
triggers: []
stage: "04"
uses: ["style-extractor", "niche-analyst", "references-curator", "design-system-generator", "brand-kit-build"]
tags: ["brand", "palette", "fonts", "icons", "provenance", "stage-04"]
---

# brand-architect — Архитектор бренд-кита

## Что делает

Берёт все извлечённые стилевые данные (цвета, шрифты, иконки, сетку, анимации) и собирает из них единый бренд-кит с полной «родословной» каждого элемента — откуда взят каждый цвет, шрифт и иконка. Дополнительно отрисовывает HTML-превью для утверждения заказчиком.

## Когда вызывать / в каком этапе

**Этап 04.** Запускается строго после того, как агент `style-extractor` завершил работу и в папке `04_БРЕНД/extracted/` появились все пять файлов: `palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`. До следующего этапа (05 — design-system) не идти, пока пользователь не одобрит `brand-kit.html`.

## Что на вход / на выход

**Вход:**
- `04_БРЕНД/extracted/palette.yaml` — извлечённые цвета
- `04_БРЕНД/extracted/fonts.yaml` — идентифицированные шрифты
- `04_БРЕНД/extracted/icons.yaml` — подобранные иконки
- `04_БРЕНД/extracted/grid.md` — сетка и отступы
- `04_БРЕНД/extracted/motion.md` — токены анимации
- `03_РЕФЕРЕНСЫ/index.yaml` — список одобренных референсов
- `01a_АНАЛИЗ_НИШИ/positioning.md` — позиционирование (mode: rational / emotional_aspiration / trust_authority)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — профиль рынка (accessibility_tier, cultural_context)
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — контракт с wp-builder, список блоков

**Выход:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с полной провенансом
- `04_БРЕНД/brand-kit.html` — визуальный превью (свотчи палитры, образцы шрифтов, миниатюры иконок)

**Процесс:**
1. `python3 skills/brand-kit-build/scripts/build.py <project-dir>` → `brand-kit.md`
2. `python3 skills/brand-kit-build/scripts/render-html.py <project-dir>` → `brand-kit.html`
3. Открыть HTML на ревью пользователю → HARD GATE

**HARD GATE:** все 5 extracted-файлов обязательны; продолжение без одобрения `brand-kit.html` заблокировано.

## Связанные концепты

- [[style-extractor]] — обязательный предшественник: создаёт все 5 extracted/*.yaml файлов
- [[niche-analyst]] — поставляет positioning.md и market-profile.md, определяющие стиль палитры и типографики
- [[references-curator]] — поставляет одобренные референсы (index.yaml)
- [[brand-kit-build]] — скилл, которому принадлежит этот агент; содержит Python-скрипты build.py и render-html.py
- [[design-system-generator]] — следующий этап (05): читает brand-kit.md и генерирует DESIGN.md + tokens.json

## Источник

- `agents/brand-architect.md`
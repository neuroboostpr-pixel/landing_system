---
type: agent
name: brand-architect
sources: ["agents/brand-architect.md"]
updated: 2026-05-25
triggers: []
stage: "04_brand"
uses: ["brand-kit-build", "style-extractor", "landing-orchestrator", "stage-execution-protocol"]
tags: ["brand", "stage-04", "design-tokens", "legal", "152-fz"]
---

# Brand Architect — Агент сборки бренд-кита (Этап 04)

## Что делает

Собирает единый бренд-кит проекта: берёт все извлечённые стилевые данные (цвета, шрифты, иконки, сетка, анимации) и синтезирует из них `brand-kit.md` с полной трассировкой источников — каждый токен знает, откуда он взят. Дополнительно собирает юридические реквизиты Оператора ПД для соответствия 152-ФЗ.

## Когда вызывать / в каком этапе

Этап **04_brand**. Запускается автоматически оркестратором (`landing-orchestrator`) или вручную после того, как `style-extractor` завершил работу и в папке `04_БРЕНД/extracted/` присутствуют все пять файлов: `palette.yaml`, `fonts.yaml`, `icons.yaml`, `grid.md`, `motion.md`.

**Предусловия (Stage Execution Protocol):**
1. `.landing-state.yaml` показывает `current_stage == 04_brand`.
2. `scripts/gate-check.sh --stage 04_brand` возвращает exit 0.
3. Готов `03_РЕФЕРЕНСЫ/index.yaml` с одобренными референсами.
4. Готовы `01a_АНАЛИЗ_НИШИ/positioning.md`, `market-profile.md`, `landing-structure.md`.

**HARD GATE:** агент не передаёт управление этапу 05 (Design System) до явного одобрения пользователем `brand-kit.html`.

## Что на вход / на выход

**Входные артефакты:**
- `04_БРЕНД/extracted/palette.yaml` — цветовая палитра
- `04_БРЕНД/extracted/fonts.yaml` — шрифты
- `04_БРЕНД/extracted/icons.yaml` — иконки
- `04_БРЕНД/extracted/grid.md` — сетка и отступы
- `04_БРЕНД/extracted/motion.md` — анимационные токены
- `03_РЕФЕРЕНСЫ/index.yaml` — одобренные референсы
- `01a_АНАЛИЗ_НИШИ/positioning.md`, `market-profile.md`, `landing-structure.md` — контекст позиционирования, рынка и структуры лендинга

**Выходные артефакты:**
- `04_БРЕНД/brand-kit.md` — канонический бренд-кит с provenance
- `04_БРЕНД/brand-kit.html` — визуальный превью (палитра, шрифты, иконки)
- `04_БРЕНД/extracted/legal.yaml` — юридические реквизиты Оператора ПД (собирается в диалоге с пользователем)

**Процесс:**
1. `python3 skills/brand-kit-build/scripts/build.py <project>` → `brand-kit.md`
2. `python3 skills/brand-kit-build/scripts/render-html.py <project>` → `brand-kit.html`
3. Диалог с пользователем для сбора legal-данных → `legal.yaml` → перезапуск `build.py`

## Связанные концепты

- [[brand-kit-build]] — скилл, которому принадлежит агент; содержит Python-скрипты сборки и рендера
- [[style-extractor]] — предшествующий агент; поставляет все `extracted/*.yaml` файлы
- [[landing-orchestrator]] — запускает brand-architect в цепочке pipeline
- [[stage-execution-protocol]] — обязательный протокол проверок перед любым действием
- [[landing-design]] — следующий этап (05); принимает brand-kit.md как вход

## Источник

- `agents/brand-architect.md`
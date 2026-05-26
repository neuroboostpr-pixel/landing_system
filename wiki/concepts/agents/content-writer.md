---
type: agent
name: content-writer
sources: ["agents/content-writer.md"]
updated: 2026-05-26
triggers: []
stage: "07"
uses: ["landing-orchestrator", "niche-analyst", "brand-architect", "design-system-builder", "landing-prototype"]
tags: ["copywriting", "content", "stage-07", "seo"]
---

# Content Writer — Контент-райтер

## Что делает
Берёт прототип текста лендинга и адаптирует его под конкретные блоки страницы: пишет финальный копирайт и SEO-тексты на основе реальных данных клиента, позиционирования и дизайн-системы. Lorem ipsum запрещён — только живые тексты.

## Когда вызывать / в каком этапе
Активируется на **этапе 07 (07_content)**. Запускается агентом `landing-orchestrator` или вручную командой `/landing-content`. Перед стартом агент проверяет, что `.landing-state.yaml` содержит `current_stage == 07_content`, иначе останавливается. Все предшествующие этапы (01a, 02, 05, 06, 07_прототип) должны быть закрыты — harness-хук `enforce_stage_gate.py` физически блокирует запись в файлы, если гейты открыты.

## Что на вход / на выход

**Вход:**
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим (Mode) и углы отстройки
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — таблица блоков (источник истины по порядку)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — `accessibility_tier` и `cultural_context`
- `07_ПРОТОТИП/prototype.md` — исходный прототип текста
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — детали секций
- `06_СТЕК/design-stack.yaml` — компонентная библиотека
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` + `assets-manifest.yaml` — реальные отзывы и ассеты

**Выход:**
- `07_КОНТЕНТ/final-copy.md` — финальный копирайт, разложенный строго по блокам из `landing-structure.md`
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, meta description и варианты h1

После записи файлов агент показывает `final-copy.md` пользователю и ждёт явного утверждения (**HARD GATE**).

## Тональность по режиму (Mode)
Режим берётся из `positioning.md` (строка `**Mode:**`):
- **rational** — факты, цифры, функциональный benefit; без статусных обещаний
- **emotional_aspiration** — aspirational, структура StoryBrand; цифры — не в Hero
- **trust_authority** — каждый claim с доказательством (имя, дата, число)
- **hybrid:X+Y** — основной тон + 1–2 блока поддержки secondary
- **legacy_v1** — старые проекты до 2026-05-06, без mode-аугментации

## Связанные концепты
- [[landing-orchestrator]] — диспатчит агента в рамках pipeline
- [[niche-analyst]] — поставляет positioning.md и landing-structure.md
- [[landing-prototype]] — поставляет prototype.md как исходник текста
- [[design-system-builder]] — поставляет DESIGN.md с деталями секций
- [[landing-content]] — slash-команда для ручного запуска этапа

## Источник
- `agents/content-writer.md`
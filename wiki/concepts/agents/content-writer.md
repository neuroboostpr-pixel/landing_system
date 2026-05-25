---
type: agent
name: content-writer
sources: ["agents/content-writer.md"]
updated: 2026-05-25
triggers: []
stage: "07_content"
uses: ["landing-orchestrator", "niche-analyst", "brand-architect", "design-system-builder"]
tags: ["copywriting", "content", "stage-07", "seo"]
---

# content-writer (Контент-райтер)

## Что делает
Превращает сырой прототип текста в готовые тексты для каждого блока лендинга. Адаптирует тон под стратегический режим (rational / emotional / trust), исключает Lorem ipsum, использует только реальные данные клиента.

## Когда вызывать / в каком этапе
Активируется на **этапе 07_content**. Запускается оркестратором (`landing-orchestrator`) или вручную через `/landing-content`. До запуска требует закрытых этапов 01a (анализ ниши), 05 (дизайн-система) и 06 (стек). `PreToolUse`-хук физически блокирует запись файлов, если предшественники не закрыты.

## Что на вход / на выход

**Входные артефакты:**
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим (Mode) и углы отстройки
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — таблица блоков (источник истины по порядку)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — тир доступности, культурный контекст
- `07_ПРОТОТИП/prototype.md` — исходный прототип текста
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — детали секций
- `06_СТЕК/design-stack.yaml` — компонентная библиотека
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` — реальные отзывы
- `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` — перечень ассетов

**Выходные артефакты:**
- `07_КОНТЕНТ/final-copy.md` — финальные тексты, разложенные по блокам лендинга
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, meta description, варианты h1

**Hard gate:** показывает `final-copy.md` пользователю и ждёт явного утверждения перед закрытием этапа.

## Связанные концепты
- [[landing-orchestrator]] — вызывает агента в рамках pipeline как часть stage-07
- [[niche-analyst]] — поставляет positioning.md и landing-structure.md (источник истины по блокам)
- [[brand-architect]] — поставляет brand-kit и тональность, необходимые для адаптации режима
- [[design-system-builder]] — поставляет DESIGN.md с деталями типографики и секций
- [[block-composer]] — использует final-copy.md на этапе 07b для наполнения composed.html
- [[stage-execution-protocol]] — обязательный протокол: gate-check → Mermaid-карта → TodoWrite → verify → approve

## Источник
- `agents/content-writer.md`
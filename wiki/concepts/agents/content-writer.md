---
type: agent
name: content-writer
sources: ["agents/content-writer.md"]
updated: 2026-05-15
triggers: []
stage: "07"
uses: ["niche-analyst", "prototype-importer", "design-system-generator", "stack-planner", "client-assets-collector"]
tags: ["content", "copywriting", "seo", "stage-07"]
---

# Content Writer — Контент-райтер

## Что делает

Берёт черновой прототип текста лендинга и превращает его в готовый копирайт, разложенный по конкретным блокам страницы. Параллельно пишет SEO-копию с мета-заголовками и вариантами h1.

## Когда вызывать / в каком этапе

Запускается на **этапе 07** после того, как завершены: анализ ниши (01a), дизайн-система (05), подбор стека (06) и импорт прототипа (07). Агент не переходит дальше без явного одобрения пользователем итогового `final-copy.md`.

## Что на вход / на выход

**Входные артефакты:**

| Файл | Зачем |
|------|-------|
| `01a_АНАЛИЗ_НИШИ/positioning.md` | Режим позиционирования (`rational` / `emotional_aspiration` / `trust_authority` / `hybrid`) |
| `01a_АНАЛИЗ_НИШИ/landing-structure.md` | Эталонный список и порядок блоков лендинга |
| `01a_АНАЛИЗ_НИШИ/market-profile.md` | Тон: `accessibility_tier` и `cultural_context` |
| `01a_АНАЛИЗ_НИШИ/competitors.yaml` | Поле `key_messages` — что НЕ повторять |
| `07_КОНТЕНТ/prototype.md` | Исходный прототип текста |
| `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` | Детали секций, типографика |
| `06_СТЕК/design-stack.yaml` | Компонентная библиотека |
| `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` | Реальные отзывы клиентов |
| `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` | Список доступных фото/иконок |

**Выходные артефакты:**

- `07_КОНТЕНТ/final-copy.md` — копирайт, разложенный по блокам из `landing-structure.md`
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, description, варианты h1

**Жёсткие правила:**

- Запрещён Lorem ipsum — только реальные данные из `prototype.md` и `testimonials/`
- Каждый блок содержит явную ссылку на иконку/фото из `assets-manifest`
- HARD GATE: показывает `final-copy.md` пользователю и ждёт подтверждения

## Режимы тона (mode-aware)

Агент адаптирует регистр копирайта под режим позиционирования:

- **rational** — факты, цифры, без аспирации
- **emotional_aspiration** — эмоциональный крюк, структура StoryBrand
- **trust_authority** — каждый claim с доказательством (имя, число, дата)
- **hybrid:X+Y** — основной тон + поддержка 1–2 блоками вторичного
- **legacy_v1** — без mode-аугментации (старые проекты до 2026-05-06)

## Связанные концепты

- [[niche-analyst]] — поставляет `positioning.md`, `landing-structure.md`, `competitors.yaml`
- [[prototype-importer]] — поставляет `prototype.md` как сырой входной текст
- [[design-system-generator]] — поставляет `DESIGN.md` с деталями секций
- [[stack-planner]] — поставляет `design-stack.yaml` с компонентной библиотекой
- [[client-assets-collector]] — поставляет `testimonials/` и `assets-manifest.yaml`

## Источник

- `agents/content-writer.md`
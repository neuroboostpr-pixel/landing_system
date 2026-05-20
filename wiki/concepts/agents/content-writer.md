---
type: agent
name: content-writer
sources: ["agents/content-writer.md"]
updated: 2026-05-20
triggers: []
stage: "07"
uses: ["niche-analyst", "prototype-importer", "design-system-generator", "stack-planner", "client-assets-collector", "landing-content", "stage-execution-protocol", "ux-composer", "block-composer"]
tags: ["copywriting", "content", "stage-07", "final-copy", "seo"]
---

# content-writer — Контент-райтер

## Что делает

Адаптирует текст прототипа лендинга под конкретные блоки, определённые в `landing-structure.md` и `DESIGN.md`. Раскладывает итоговый копирайт по блокам с учётом позиционирования бренда, тональности аудитории и реальных материалов клиента. Параллельно пишет SEO-тексты (заголовки, description, h1-варианты).

## Когда вызывать / в каком этапе

Вызывается на **этапе 07** (`07_content`) через команду `/landing-content`. Перед запуском обязаны быть завершены:
- этап `01a` — готов `positioning.md` с полем `Mode`
- этап `05` — готов `DESIGN.md` и `design-stack.yaml`
- этап `07_prototype` — готов `prototype.md`

Агент проверяет `.landing-state.yaml` и отказывается работать, если `current_stage != 07_content`. `PreToolUse` хук физически блокирует запись файлов при незакрытых предшественниках.

## Что на вход / на выход

**Вход:**
| Файл | Назначение |
|---|---|
| `01a_АНАЛИЗ_НИШИ/positioning.md` | Режим (rational / emotional_aspiration / trust_authority / hybrid) |
| `01a_АНАЛИЗ_НИШИ/landing-structure.md` | Источник истины: список и порядок блоков |
| `01a_АНАЛИЗ_НИШИ/market-profile.md` | `accessibility_tier` и `cultural_context` для тона |
| `01a_АНАЛИЗ_НИШИ/competitors.yaml` | Поле `key_messages` — чего избегать в текстах |
| `07_КОНТЕНТ/prototype.md` | Исходный прототип текста |
| `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` | Типографика, контейнеры секций |
| `06_СТЕК/design-stack.yaml` | Компонентная библиотека |
| `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` | Реальные отзывы |
| `02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml` | Ассеты клиента |

**Выход:**
- `07_КОНТЕНТ/final-copy.md` — итоговый копирайт, разбитый по блокам (как в `landing-structure.md`)
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, description, варианты h1

После генерации агент показывает `final-copy.md` пользователю и ждёт явного подтверждения (HARD GATE).

## Особенности тональности по режиму

- **rational** — факты, цифры, без аспирационных обещаний
- **emotional_aspiration** — структура StoryBrand: эмоциональный хук в Hero, цифры — глубже на странице
- **trust_authority** — каждый claim с доказательством (имя, дата, число)
- **hybrid:X+Y** — основной тон по primary, вторичный — в 1–2 блоках

Lorem ipsum в `final-copy.md` запрещён. Только реальные данные из `prototype.md` и `testimonials/`.

## Связанные концепты

- [[niche-analyst]] — создаёт `positioning.md`, `landing-structure.md`, `competitors.yaml`
- [[prototype-importer]] — поставляет `prototype.md` как исходный текст
- [[design-system-generator]] — поставляет `DESIGN.md` с деталями секций
- [[stack-planner]] — поставляет `design-stack.yaml`
- [[client-assets-collector]] — поставляет отзывы и `assets-manifest.yaml`
- [[landing-content]] — команда, запускающая этого агента
- [[ux-composer]] — потребляет `final-copy.md` для wireframe
- [[block-composer]] — потребляет `final-copy.md` для composed.html
- [[stage-execution-protocol]] — обязательный протокол перед любым Write/Edit

## Источник

- `agents/content-writer.md`
---
type: agent
name: content-writer
sources: ["agents/content-writer.md"]
updated: 2026-05-20
triggers: []
stage: "07"
uses: ["niche-analyst", "prototype-importer", "design-system-generator", "stack-planner", "client-assets-collector", "landing-orchestrator"]
tags: ["content", "copywriting", "seo", "stage-07"]
---

# content-writer (Контент-райтер)

## Что делает

Берёт исходный прототип текста и адаптирует его под конкретные блоки лендинга: формирует финальные тексты по каждому блоку с учётом позиционирования бренда (рациональное, эмоциональное, доверительное), а также пишет SEO-копирайт.

## Когда вызывать / в каком этапе

Запускается на **этапе 07 (Контент)**. Предшественники должны быть закрыты: `.landing-state.yaml` обязан показывать `current_stage == 07_content`. До запуска агент проверяет gate через `gate-check.sh`; если предшественники не утверждены — останавливается.

## Что на вход / на выход

**Вход:**
- `01a_АНАЛИЗ_НИШИ/positioning.md` — режим позиционирования (`rational` / `emotional_aspiration` / `trust_authority` / `hybrid`)
- `01a_АНАЛИЗ_НИШИ/landing-structure.md` — таблица блоков лендинга (источник истины по порядку и составу блоков)
- `01a_АНАЛИЗ_НИШИ/market-profile.md` — тон и культурный контекст (`accessibility_tier`, `cultural_context`)
- `01a_АНАЛИЗ_НИШИ/competitors.yaml` — ключевые сообщения конкурентов (чтобы их не повторять)
- `07_ПРОТОТИП/prototype.md` — исходный прототип текста
- `05_ДИЗАЙН-СИСТЕМА/DESIGN.md` — типографика и структура секций
- `06_СТЕК/design-stack.yaml` — компонентная библиотека
- `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` и `assets-manifest.yaml` — реальные отзывы и ассеты клиента

**Выход:**
- `07_КОНТЕНТ/final-copy.md` — финальные тексты, разбитые по блокам из `landing-structure.md`
- `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, description, варианты h1

**HARD GATE:** после создания файлов агент показывает `final-copy.md` пользователю и ждёт явного утверждения перед закрытием этапа.

## Ключевые правила

- Блоки берутся строго из `landing-structure.md`, а не угадываются из DESIGN.md.
- Lorem ipsum в `final-copy.md` **запрещён** — только реальные данные из прототипа и отзывов.
- Тон копирайта определяется полем `Mode` из `positioning.md`:
  - `rational` — факты, цифры, без аспирации;
  - `emotional_aspiration` — эмоциональный крючок, структура StoryBrand;
  - `trust_authority` — каждый claim подкреплён доказательством (число, имя, дата);
  - `hybrid:X+Y` — основной тон + 1–2 вспомогательных блока.
- Не повторять ключевые сообщения конкурентов из `competitors.yaml`.

## Связанные концепты

- [[niche-analyst]] — формирует `positioning.md` и `landing-structure.md`, которые контент-райтер использует как основу
- [[prototype-importer]] — производит `prototype.md`, исходный текст для адаптации
- [[design-system-generator]] — создаёт `DESIGN.md` с деталями секций
- [[stack-planner]] — поставляет `design-stack.yaml` с компонентной библиотекой
- [[client-assets-collector]] — собирает отзывы и ассеты клиента
- [[landing-orchestrator]] — диспатчит агента в нужный момент pipeline

## Источник

- `agents/content-writer.md`
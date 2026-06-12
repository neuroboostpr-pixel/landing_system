---
slug: landing-content
type: command
name: "Контент-адаптация прототипа (Stage 07)"
stage: "07"
tags: [content, copywriting, seo, gutenberg, prototype]
triggers: [landing-content]
inputs:
  - 07_ПРОТОТИП/prototype.md
  - 06_СТЕК/design-stack.yaml
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/
  - DESIGN.md
outputs:
  - 07_КОНТЕНТ/final-copy.md
  - 07_КОНТЕНТ/seo-copy.md
gates: []
pre_reqs:
  - stack-planner
  - prototype-import
related:
  - content-writer
  - landing-onboarding
  - landing-orchestrator
  - prototype-importer
  - seo-optimizer
  - wp-gutenberg-block-builder
sources: ["commands/landing-content.md"]
updated: 2026-05-26
---

# Контент-адаптация прототипа (Stage 07)

## Что делает

Команда адаптирует текстовый прототип лендинга в финальный копирайт, структурированный по Gutenberg-блокам. Запускает агента `content-writer`, который читает `prototype.md`, блочную структуру из `DESIGN.md` и реальные отзывы клиента, после чего формирует два артефакта: финальный текст по блокам и SEO-вариации. Весь этап завершается обязательным ревью пользователем — без явного утверждения переход на stage 08 невозможен.

## Когда вызывается

Команда вызывается вручную через `/landing-content` после того как стек одобрен (`06_СТЕК/design-stack.yaml`) и прошёл gate-check для stage 07_content. Если стек не утверждён или onboarding не пройден, команда останавливается с объяснением причины.

## Вход → выход

**Вход:** `07_ПРОТОТИП/prototype.md` — текст прототипа; `06_СТЕК/design-stack.yaml` — блочная структура; `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` — реальные отзывы клиента; `DESIGN.md` — структура блоков по этапам.

**Выход:** `07_КОНТЕНТ/final-copy.md` — финальный копирайт, разложенный по каждому Gutenberg-блоку; `07_КОНТЕНТ/seo-copy.md` — варианты SEO-заголовков, мета-описаний и H1.

## Failure modes

- `07_ПРОТОТИП/prototype.md` отсутствует или пустой — агент `content-writer` не может сформировать финальный копирайт; нужно сначала запустить `/landing-prototype`.
- `06_СТЕК/design-stack.yaml` не одобрён — gate-check вернёт exit 1 и команда остановится раньше основного flow.
- Onboarding не пройден (`setup_complete` флаг отсутствует) — pre-flight check блокирует выполнение на первом же шаге.
- Отсутствуют реальные отзывы в `02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/` — SEO-копирайт и testimonial-блоки могут быть заполнены-заглушками, что потребует ручной доработки.
- Пользователь не дал явного approve `final-copy.md` — stage 08 не может начаться; HARD GATE не допускает пропуска.

## Related

- [[content-writer]] — агент, непосредственно генерирующий копирайт по блокам
- [[prototype-importer]] — предшествующий этап: импорт прототипа в `prototype.md`
- [[stack-planner]] — предшествующий этап: формирование `design-stack.yaml`
- [[seo-optimizer]] — SEO-логика, используемая при создании `seo-copy.md`
- [[landing-orchestrator]] — оркестратор, управляющий переходами между этапами
- [[wp-gutenberg-block-builder]] — следующий по цепочке: использует `final-copy.md` при сборке блоков
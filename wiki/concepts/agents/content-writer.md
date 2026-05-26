---
slug: content-writer
type: agent
name: "Контент-райтер"
stage: "07"
tags: [copywriting, content, seo, stage-07]
triggers: [landing-content]
inputs:
  - 01a_АНАЛИЗ_НИШИ/positioning.md
  - 01a_АНАЛИЗ_НИШИ/landing-structure.md
  - 01a_АНАЛИЗ_НИШИ/market-profile.md
  - 07_ПРОТОТИП/prototype.md
  - 05_ДИЗАЙН-СИСТЕМА/DESIGN.md
  - 06_СТЕК/design-stack.yaml
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/testimonials/
  - 02_МАТЕРИАЛЫ_КЛИЕНТА/assets-manifest.yaml
outputs:
  - 07_КОНТЕНТ/final-copy.md
  - 07_КОНТЕНТ/seo-copy.md
gates: [user-approve-final-copy]
pre_reqs: [landing-niche, landing-prototype, landing-design, landing-stack]
related: [landing-content, landing-orchestrator, landing-wireframe, landing-compose]
sources: ["agents/content-writer.md"]
updated: 2026-05-26
confidence: {triggers: low, pre_reqs: low}
---

# Контент-райтер

## Что делает

Адаптирует исходный прототип текста под конкретные блоки лендинга. Читает `landing-structure.md` как единственный источник истины по порядку блоков, извлекает из `positioning.md` режим коммуникации (`rational`, `emotional_aspiration`, `trust_authority` и др.) и перекладывает тексты из `prototype.md` в итоговые файлы. Регистр и структура копирайта строго подчиняются выбранному Mode: без аспирации для `rational`, StoryBrand-нарратив для `emotional_aspiration`, доказательства на каждый claim для `trust_authority`. Параллельно пишет SEO-тексты и мета-данные. Завершается жёсткой паузой на утверждение пользователем.

## Когда вызывается

Вызывается командой `/landing-content` или диспетчируется `landing-orchestrator` при переходе к этапу `07_content`. Условие: этап `07_content` должен быть активным в `.landing-state.yaml`, а все предшественники (01a, 02, 05, 06, prototype) — закрыты. `PreToolUse`-хук физически блокирует запись, если gate не пройден.

## Вход → выход

**Вход:** `positioning.md` с Mode, `landing-structure.md` с картой блоков, `prototype.md` с исходными текстами, `DESIGN.md` с деталями секций, `design-stack.yaml`, реальные отзывы из `testimonials/` и `assets-manifest.yaml`.

**Выход:** `07_КОНТЕНТ/final-copy.md` — тексты всех блоков без Lorem ipsum, каждый блок помечен заголовком из landing-structure; `07_КОНТЕНТ/seo-copy.md` — SEO-заголовки, description, варианты h1.

## Чем закрывается этап (gates)

- `user-approve-final-copy` — пользователь явно утверждает `final-copy.md`; агент показывает файл и ждёт подтверждения перед переходом к следующему этапу.

## Failure modes

- **Блоки взяты из DESIGN.md, а не из landing-structure.md** — несоответствие порядка блоков, потеря секций или дублирование.
- **Mode не считан из positioning.md** — тексты идут в нейтральном регистре вместо требуемого, Hero получает неправильный акцент.
- **Реальные отзывы не подключены** — testimonials-блок содержит заглушки вместо данных из `testimonials/`.
- **Gate-check не пройден** — `enforce_stage_gate.py` блокирует запись, агент не сообщает причину и зависает.
- **assets-manifest не прочитан** — копирайт ссылается на несуществующие иконки или фото, что ломает верстку на этапе 08.

## Related

- [[landing-content]] — slash-команда / skill, которая запускает этого агента
- [[landing-orchestrator]] — диспетчер; вызывает агента в рамках общего pipeline
- [[landing-wireframe]] — следующий этап (07a); работает с текстами из final-copy.md
- [[landing-compose]] — этап 07b; вставляет тексты из final-copy.md в composed.html
---
type: rule
name: plan-dorabotok
sources: ["docs/ПЛАН-ДОРАБОТОК.md"]
updated: 2026-05-15
triggers: []
stage: ""
uses:
  - landing-orchestrator
  - block-composer
  - photo-curator
  - visual-qa
  - stage-gates
  - premium-07b-checklist
  - landing-final-check
  - landing-previews
  - landing-import-blocks
  - landing-visuals
  - landing-photos
tags: [roadmap, planning, pr-series, доработки]
---

# План доработок системы

## Что делает

Главный дорожный план развития landing-system на 2026 год — список всех PR-серий с описанием задач, статусом выполнения и ответственными специалистами. Является живым документом: по мере завершения PR статус меняется на «✅ ГОТОВО».

## Когда вызывать / в каком этапе

Справочный документ. Читается при планировании новых задач, при оценке текущего состояния системы, при onboarding нового специалиста. Не является частью pipeline — в автоматическом режиме не вызывается.

## Что на вход / на выход

**На вход:** обсуждения и договорённости с командой (Кирилл + Валерия)

**На выход:** приоритизированный список PR с двумя ответственными зонами:
- **Специалист 1 (Визуал/фото)** — PR-F, PR-G, PR-H, PR-I, PR-J, PR-K, PR-L, PR-M, PR-N, PR-O, PR-P
- **Специалист 2 (WordPress/интеграции)** — интеграции CRM/Telegram/WhatsApp, редактирование head, мультисайт, клонирование

**Все PR Специалиста 1 закрыты (на 2026-05-16):**
- PR-F — системная wiki (102 концепта)
- PR-G — hard-lock этапов + auto-update wiki
- PR-H — защита текста прототипа (verify-content-preserved)
- PR-I — фото-pipeline + visual QA loop
- PR-J — per-type identity thresholds + revert логика
- PR-K — AI-классификация фоток + автоматическое matching к слотам
- PR-L — финальная авто-проверка `/landing-final-check`
- PR-M — превью desktop/mobile отдельно
- PR-N — адаптация фото под регион
- PR-O, PR-P — расширение библиотеки блоков (190+) + premium effects (38 паттернов)

**PR Специалиста 2 — в приоритетной очереди:**
- Интерфейс подключения интеграций в админке
- Редактирование `<head>` без программиста
- Этап настройки куда идут заявки и кнопки
- Деление блоков на editable / semi-editable / hardcoded

## Связанные концепты

- [[stage-gates]] — система hard-lock/soft-warning, описанная в PR-G
- [[premium-07b-checklist]] — расширена до 20 пунктов в PR-P
- [[photo-curator]] — фото-pipeline реализован в PR-I, PR-J, PR-K
- [[visual-qa]] — новый скилл, создан в PR-I.b
- [[landing-final-check]] — команда из PR-L, bundle всех verify-скриптов
- [[landing-previews]] — команда из PR-M, desktop+mobile preview
- [[landing-import-blocks]] — инфраструктура из PR-O для импорта блоков
- [[block-composition]] — затрагивается правилом неприкосновенности текста (PR-H)
- [[landing-orchestrator]] — усилен в PR-G (обязательное чтение state перед действием)

## Источник

- `docs/ПЛАН-ДОРАБОТОК.md`
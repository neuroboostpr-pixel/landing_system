---
type: rule
name: dokrutka-system
sources: ["docs/superpowers/DOKRUTKA-system.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["content-writer", "landing-orchestrator", "photo-curator", "photo-matcher", "ux-composer", "block-composition", "prototype-import", "stage-gates", "integrations-engineer", "qa-auditor"]
tags: ["pipeline", "quality", "backlog", "systemic-issues", "improvements"]
---

# DOKRUTKA System — Системный журнал доработок pipeline

## Что делает
Фиксирует критичные системные ошибки pipeline, выявленные в ходе первого полного прогона на реальном проекте (dubai-avto-liza, 2026-05-14). Каждая проблема — паттерн, повторяющийся на любом проекте, а не баг конкретного сайта. Документ служит источником задач для всех будущих PR (Pull Requests) в landing-system.

## Когда вызывать / в каком этапе
Читать перед планированием нового PR или при разработке изменений в `agents/`, `skills/`, `commands/`, `config/`. При возникновении проблемы в pipeline — сверяться с этим документом: скорее всего, паттерн уже описан. После закрытия issue — отмечать чекбокс.

## Что на вход / на выход

**Вход:** Результаты тестового прогона pipeline (этапы 07a → 07c), наблюдения агентов и маркетолога.

**Выход:** Приоритизированный список проблем с категориями 🔴/🟡/🟢, ссылками на конкретные файлы для фикса и pipeline-level изменениями (P1–P3).

**Ключевые проблемы:**

- **S1** — `content-writer` переписывает финальный текст клиента из `prototype.yaml` вместо сохранения. Фикс: поле `text_source: client_final | template_placeholder`.
- **S2** — Неверный порядок stages: photos должны идти **до** первого composed, не после. Новый порядок: `07b wireframe → 07c photos → 07d composed_draft → 07e visuals → 07f composed_final`.
- **S3** — `photo-curator` не вызывается автоматически: агент делает работу вручную в обход PR-B pipeline.
- **S4** — 480 inspiration photos не участвуют в matching — `photo-matcher` не знает об этом источнике.
- **S5** — `ux-composer` «переоптимизирует» wireframe selections после явного approve пользователем.
- **S5-A** — Отсутствует stage `07g_self_review`: автопроверка content / visual / functional / performance / SEO / brand перед сборкой WP.
- **S5-B** — Отсутствует stage `07h_integrations`: сбор реальных WhatsApp/CRM/analytics/Maps ссылок и их подстановка в composed.html.

## Связанные концепты
- [[content-writer]] — S1: запрет переписывания client_final текста
- [[landing-orchestrator]] — S2/P1: исправление порядка stages в dispatch table
- [[photo-curator]] — S3: обязательный автодиспатч на 07c
- [[photo-matcher]] — S4: учёт inspiration photos как secondary source
- [[ux-composer]] — S5: заморозка selections после approve
- [[block-composition]] — P2: gate-check на соответствие текста прототипу
- [[prototype-import]] — S1: добавить metadata `text_source` в prototype.yaml
- [[stage-gates]] — P2/P3: новые проверки text-matches-prototype и photo-mapping schema
- [[integrations-engineer]] — S5-B: нужен dedicated stage 07h
- [[qa-auditor]] — S5-A: расширение для stage 07g_self_review

## Источник
- `docs/superpowers/DOKRUTKA-system.md`
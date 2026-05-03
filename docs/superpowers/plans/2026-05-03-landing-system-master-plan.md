# Landing System — Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement each phase. Phases run sequentially; each phase has its own detailed plan.

**Goal:** Построить MVP агентской системы для производства лендингов на WordPress, упакованной в ZIP-архив для раздачи ученикам и сотрудникам агентства.

**Architecture:** Шесть последовательных фаз. Каждая фаза = отдельный детальный план + рабочий проверяемый продукт. Каждая фаза зависит от предыдущей. Реализация ведётся через subagent-driven-development (свежий субагент на каждый таск + двухступенчатое ревью).

**Tech Stack:** WordPress + Gutenberg + GenerateBlocks + ACF, Бегет (SSH/WP-CLI/rsync), Bash + Node.js + Python, Bats для тестов, GSAP/ScrollTrigger/Lenis (cinematic), Iconify, Fontshare, Firecrawl, WhatTheFont, Я.Метрика/Wordstat.

**Spec source:** [`docs/superpowers/specs/2026-05-03-landing-system-design.md`](../specs/2026-05-03-landing-system-design.md)

---

## Phase Index

| # | Phase | Detailed Plan | Tasks | Estimated Time | Status |
|---|---|---|---|---|---|
| 1 | **Skeleton & Infrastructure** | [phase-1-skeleton.md](2026-05-03-phase-1-skeleton.md) | ~18 tasks | 4–6 ч | 🟢 Complete (2026-05-03) |
| 2 | **Brainstorming Pipeline** (00–04) | TBD после Phase 1 | ~25 tasks | 6–8 ч | ⚪ Not started |
| 3 | **Design Pipeline** (05–07) | TBD после Phase 2 | ~20 tasks | 5–6 ч | ⚪ Not started |
| 4 | **WP Build Pipeline** (08) | TBD после Phase 3 | ~30 tasks | 8–10 ч | ⚪ Not started |
| 5 | **Deploy & Operations** (09–12) | TBD после Phase 4 | ~25 tasks | 6–8 ч | ⚪ Not started |
| 6 | **Packaging & Pilot** | TBD после Phase 5 | ~10 tasks | 2–3 ч | ⚪ Not started |

**Итого:** ~128 bite-sized tasks по 2–5 минут × 6 фаз ≈ **30–40 часов реализации MVP** (с учётом ревью и отладки).

---

## Зависимости между фазами

```
Phase 1: Skeleton
    │
    ├─► Phase 2: Brainstorming Pipeline
    │       │
    │       ├─► Phase 3: Design Pipeline
    │       │       │
    │       │       ├─► Phase 4: WP Build Pipeline
    │       │       │       │
    │       │       │       ├─► Phase 5: Deploy & Operations
    │       │       │       │       │
    │       │       │       │       └─► Phase 6: Packaging & Pilot
```

Каждая фаза **строго зависит** от предыдущей. Параллельной работы между фазами нет (это последовательный конвейер «бриф → дизайн → код → деплой»).

**Внутри каждой фазы** некоторые задачи могут идти параллельно (помечено в детальном плане).

---

## Phase 1 — Skeleton & Infrastructure

**Цель:** базовая папка `landing-system/` со всем необходимым каркасом + работающая команда `/landing-new` создаёт пустую папку проекта со структурой 00–12.

**Что появится:**
- Готовая структура мастер-системы
- Шаблон проекта-лендинга (`template/`) с 13 папками
- Скилл `landing-project-init` — копирует template → новый проект
- Скилл `landing-from-context` — старт из родительской папки агентства
- Slash-команды `/landing-new`, `/landing-from-context`, `/landing-help`, `/landing-status`
- Базовый агент `landing-orchestrator` (stub: создаёт папку, говорит «фаза 2 ещё не реализована»)
- CLAUDE.md, README.md, .env-логика
- Bats-тесты для всей инфраструктуры

**Acceptance criteria:**
- ✅ В Claude Code запуск `/landing-new my-test-project` создаёт папку со всеми 13 секциями
- ✅ Все bats-тесты проходят
- ✅ ZIP-архив можно распаковать в новой папке и команды работают
- ✅ `/landing-status` показывает «Phase 1 complete, awaiting Phase 2»

**Detailed plan:** [`2026-05-03-phase-1-skeleton.md`](2026-05-03-phase-1-skeleton.md)

---

## Phase 2 — Brainstorming Pipeline (этапы 00–04)

**Цель:** агенты, которые обрабатывают первые 5 этапов workflow одного лендинга (бриф → контекст → материалы клиента → референсы → бренд-кит).

**Что появится:**
- Агент `client-assets-collector` — сбор фото/видео + парсинг отзывов с Я.Карты/2GIS/Otzovik через Firecrawl MCP
- Агент `photo-stylist` — обработка фото identity-safe (cutout, edge cleanup)
- Агент `references-curator` — статусы (candidate/approved/rejected), index.yaml
- Агент `moodboard-composer` — `moodboard.md` + HTML preview
- Агент `style-extractor` — декомпозиция референсов: палитра (color-thief), шрифты (WhatTheFont API), иконки (Iconify), сетка, motion
- Агент `brand-architect` — `brand-kit.md` с provenance + `brand-kit.html`
- Slash-команды `/landing-references`, `/landing-moodboard`, `/landing-brand`
- Hook на utверждение каждого этапа
- HTML-генераторы для preview артефактов

**Acceptance criteria:**
- ✅ Из ссылки на сайт + 3 скриншотов референса агенты строят полноценный мудборд
- ✅ `style-extractor` извлекает палитру с пиксельными координатами источника
- ✅ `brand-kit.html` показывает каждый цвет/шрифт/иконку с источником

---

## Phase 3 — Design Pipeline (этапы 05–07)

**Цель:** генерация `DESIGN.md` (единый источник истины токенов) и адаптация контента под блоки.

**Что появится:**
- Агент `design-system-generator` — `DESIGN.md` + `tokens.json` + `design-preview.html`
- Агент `scene-director` — cinematic режим (scene grammar, motion-план для GSAP)
- Агент `stack-planner` — выбор плагинов и библиотек, `design-stack.yaml`
- Агент `content-writer` — раскладка прототипа текста по блокам
- Slash-команды `/landing-design`, `/landing-stack`, `/landing-content`
- Превью-генераторы для DESIGN.md

**Acceptance criteria:**
- ✅ Из brand-kit агент генерирует валидный `DESIGN.md` с полным набором токенов
- ✅ `design-preview.html` показывает живые компоненты по токенам
- ✅ Cinematic-режим даёт scene grammar для 8 сцен

---

## Phase 4 — WP Build Pipeline (этап 08)

**Цель:** генерация WordPress-темы, Gutenberg-блоков, ACF-полей под `DESIGN.md`. Локальный preview работает.

**Что появится:**
- Агент `wp-builder` — Gutenberg-блоки (PHP+JS), ACF JSON-конфиг, WordPress-тема
- Агент `integrations-engineer` — Fluent Forms + интеграции (Telegram, CRM webhook, email)
- Агент `analytics-engineer` — Я.Метрика код, цели, события, UTM
- Агент `seo-optimizer` — мета-теги, Schema.org, sitemap, robots.txt
- Скилл `wp-gutenberg-block-builder`
- Скилл `wp-theme-assembler`
- Локальный preview через wp-env или Local
- Slash-команда `/landing-build`

**Acceptance criteria:**
- ✅ На localhost разворачивается WP с темой и блоками
- ✅ Все блоки рендерятся с правильными токенами из DESIGN.md
- ✅ ACF-поля видны в админке для клиента
- ✅ Формы шлют в Telegram/email

---

## Phase 5 — Deploy & Operations (этапы 09–12)

**Цель:** деплой на Бегет, QA, версионирование, A/B-копии.

**Что появится:**
- Агент `wp-deployer` — SSH + WP-CLI + rsync + DNS API
- Агент `qa-auditor` — Lighthouse, Pa11y, скриншоты на 3 устройствах
- Агент `lifecycle-keeper` — версии, откат, A/B-клоны, авто-сравнение по конверсии
- Скилл `wp-cli-deployer`
- Скилл `landing-versioning-and-cloning`
- Hooks: `pre-deploy-check`, `post-deploy-actions`, `on-error-rollback`, `on-session-stop`
- Bash-скрипт `deploy.sh`
- DNS-модули: Beget API, Reg.ru API, Cloudflare API + manual fallback
- Slash-команды `/landing-deploy`, `/landing-redeploy`, `/landing-rollback`, `/landing-clone`, `/landing-qa`

**Acceptance criteria:**
- ✅ Из готовой папки проекта `/landing-deploy` развёртывает живой сайт на Бегете
- ✅ DNS привязывается через API, SSL ставится автоматом
- ✅ QA-чек проходит 7 пунктов
- ✅ `/landing-clone` создаёт независимую A/B-копию на новом поддомене
- ✅ `/landing-rollback v1.0` возвращает прошлую версию

---

## Phase 6 — Packaging & Pilot

**Цель:** собрать MVP в ZIP, прогнать pilot-проект, подготовить документацию для учеников.

**Что появится:**
- Pilot-проект на собственной нише агентства (полный цикл от бриф до live-сайта)
- Скрипт `build-zip.sh` — собирает `landing-system.zip` для раздачи
- Учебная документация в `docs/student-guide/`
- Видео-демонстрации (опционально)
- Чек-лист тестирования установки
- Финальная самопроверка против spec

**Acceptance criteria:**
- ✅ Pilot-лендинг работает в проде, формы шлют, метрика собирает
- ✅ ZIP-архив распаковывается на чистом маке и работает с первого раза
- ✅ Все 23 пункта чек-листа из spec пройдены

---

## Глобальные правила реализации

### TDD строго

- Каждая задача начинается с **failing test**
- Имплементация — минимум, чтобы тест прошёл
- Только потом — refactor
- Никакой «допишу тесты потом»

### Frequent commits

- Один commit = одна логическая единица
- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`
- Каждый коммит — рабочее состояние (тесты проходят)

### YAGNI

- Никакой функциональности «на будущее»
- Если в spec нет — не делаем
- Расширения — в Roadmap, не в MVP

### DRY

- Общая логика выносится в общие модули с первого повторения
- Конфигурация — через `.env`, никогда не хардкод

### File-per-responsibility

- Один файл — одна ответственность
- Если файл больше 300 строк — задумайся о разбиении
- Тесты живут рядом с кодом или в `tests/<phase>/`

### Test stack

- **Bash-скрипты** → bats-core (Bash Automated Testing System)
- **Node.js (hooks)** → vitest
- **Python (color-extractor, image-pipeline)** → pytest
- **Интеграционные** → bash + curl + жесткие assertions

### Code review между задачами

- После каждой задачи — двухступенчатое ревью через `code-reviewer`-агент:
  1. **Spec compliance** — соответствует ли требованиям spec?
  2. **Code quality** — чистый ли, нет ли дублирования, тесты ли пройдены?
- Найденные критические проблемы — блокируют переход к следующей задаче

### Worktree

- На MVP — без worktree (последовательная работа)
- Если будет параллельная разработка фич — переключаемся на worktree через `using-git-worktrees`

---

## Self-Review мастер-плана

**1. Spec coverage:**
- ✅ Все 12 этапов workflow попадают в Phases 1–5
- ✅ Все 18 агентов распределены по фазам
- ✅ Все 10 наших скиллов попадают в фазы
- ✅ Все hooks и slash-команды — в фазах
- ✅ Cinematic режим — Phase 3 (`scene-director`) + Phase 4 (`wp-builder` подключает GSAP)
- ✅ DNS автоматизация — Phase 5
- ✅ Версионирование и A/B — Phase 5
- ✅ ZIP-упаковка и pilot — Phase 6

**2. Placeholder scan:**
- Phase 2–6 имеют пометку «TBD после Phase N» — это **не плагины placeholder**, а явное указание что детальные планы будут писаться по очереди.

**3. Internal consistency:**
- ✅ Зависимости между фазами явные
- ✅ Acceptance criteria каждой фазы измеримые
- ✅ Tech stack согласован со spec

**4. Scope check:**
- ✅ Каждая фаза производит рабочий, тестируемый продукт
- ✅ Размеры фаз сбалансированы (~20–30 задач каждая)

---

## Status

**Текущий статус:** Phase 1 plan готов, ожидается утверждение пользователя для запуска реализации.

**Следующий шаг:**
1. Пользователь читает [Phase 1 plan](2026-05-03-phase-1-skeleton.md)
2. Утверждает или просит правки
3. После «утверждаю» — запуск `subagent-driven-development` для реализации Phase 1
4. После завершения Phase 1 — пишу детальный план Phase 2

---

## Execution Handoff

После утверждения Phase 1 plan я предложу два варианта реализации:

**1. Subagent-Driven (рекомендую)** — свежий субагент на каждую задачу, ревью между задачами, fast iteration. Идеально для длинных планов.

**2. Inline Execution** — задачи выполняются в текущей сессии через `executing-plans`, batch с чекпоинтами.

Выбор сделаешь после прочтения Phase 1 plan.

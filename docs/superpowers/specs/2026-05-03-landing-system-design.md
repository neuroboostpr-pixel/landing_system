# Landing System — Design Spec & Operations Manual

**Версия:** 1.0 (MVP)
**Дата:** 2026-05-03
**Автор брейншторма:** Кирилл Безиков (neuroboost)
**Статус:** Pending user approval

---

## 0. TL;DR — что это за продукт

Агентская система внутри Claude Code, которая создаёт production-grade лендинги на WordPress по полному циклу: от сбора референсов и материалов клиента — до публикации на боевом домене с подключёнными формами, аналитикой и SEO. Один проект = одна папка = один независимый WordPress на российском хостинге.

**Используется внутри маркетингового агентства neuroboost** для производства лендингов под Я.Директ (живые A/B-тесты офферов) и **раздаётся ученикам** как обучающий + рабочий инструмент.

**Главный принцип:** не «волшебная кнопка», а **управляемый production-инструмент** — на каждом этапе видны визуальные артефакты (HTML preview), агент ждёт подтверждения, можно вернуться к любому этапу.

---

## 1. Содержание документа

1. [TL;DR](#0-tldr--что-это-за-продукт)
2. [Содержание](#1-содержание-документа)
3. [Глоссарий и принципы](#2-глоссарий-и-принципы)
4. [Архитектура верхнего уровня](#3-архитектура-верхнего-уровня)
5. [Структура папки одного проекта-лендинга](#4-структура-папки-одного-проекта-лендинга)
6. [Workflow одного лендинга — 12 этапов](#5-workflow-одного-лендинга--12-этапов)
7. [Карта агентов (18 шт.)](#6-карта-агентов-18-шт)
8. [Карта скиллов и MCP-серверов](#7-карта-скиллов-и-mcp-серверов)
9. [Frontend-стек и библиотеки](#8-frontend-стек-и-библиотеки)
10. [Cinematic Premium режим](#9-cinematic-premium-режим)
11. [Точка входа — slash-команды](#10-точка-входа--slash-команды)
12. [Деплой на Бегет — детальный механизм](#11-деплой-на-бегет--детальный-механизм)
13. [DNS-автоматизация](#12-dns-автоматизация)
14. [Версионирование и A/B-копии](#13-версионирование-и-ab-копии)
15. [Хранение секретов](#14-хранение-секретов)
16. [Hooks (автоматизации)](#15-hooks-автоматизации)
17. [Управляемость — визуальные артефакты](#16-управляемость--визуальные-артефакты)
18. [Упаковка и раздача (MVP → плагин → SaaS)](#17-упаковка-и-раздача-mvp--плагин--saas)
19. [Установка системы — пошагово](#18-установка-системы--пошагово)
20. [Получение всех API-ключей — где и как](#19-получение-всех-api-ключей--где-и-как)
21. [Использование — типовые сценарии](#20-использование--типовые-сценарии)
22. [Расширения и Roadmap](#21-расширения-и-roadmap)
23. [Антипаттерны (чего не делаем)](#22-антипаттерны-чего-не-делаем)
24. [Чек-лист готовности к релизу MVP](#23-чек-лист-готовности-к-релизу-mvp)

---

## 2. Глоссарий и принципы

### Глоссарий

- **Лендинг** — одностраничный сайт под одну рекламную кампанию (Я.Директ).
- **Проект-лендинг** — одна папка на диске, содержащая всё для одного лендинга.
- **Большой проект** — родительская папка агентства (например, «курс по копирайтингу») с исследованиями ЦА, отзывами, прототипами текстов. Лендинг **копирует** оттуда нужные данные снепшотом.
- **Мастер-система** (она же «landing-system») — папка с агентами, скиллами, командами, шаблонами. Раздаётся как ZIP на MVP, потом — как плагин Claude Code.
- **Бренд-кит с трассировкой (provenance)** — каждый цвет/шрифт/иконка имеет источник: «откуда взято».
- **Cinematic premium режим** — опциональный режим для дорогих проектов: GSAP + ScrollTrigger + Lenis + scene-based архитектура.
- **A/B-копия** — независимый клон лендинга с другим оффером/заголовком на отдельном поддомене.
- **EDU_MODE** — флаг, включающий расширенные обучающие комментарии в выводе агентов (для учеников).

### Принципы

1. **Изоляция:** 1 проект = 1 папка = 1 WordPress = 1 поддомен.
2. **Управляемая система:** не чёрный ящик. На каждом этапе — HTML preview + явное подтверждение.
3. **Provenance:** каждое решение трассируется до источника.
4. **Бесплатно для учеников:** весь стек на open-source / бесплатных тарифах.
5. **Российский хостинг:** Бегет как основа.
6. **Автоматизация:** ученик предоставляет данные — агент делает остальное.
7. **Hard gates между этапами:** не идём дальше без явного утверждения.
8. **Provenance в коде:** каждый сгенерированный блок имеет комментарий «откуда взят дизайн, какой токен, какой агент».

---

## 3. Архитектура верхнего уровня

### Решения брейншторма

| Параметр | Значение |
|---|---|
| Платформа | Классический WordPress (не headless) |
| Стек | Gutenberg + GenerateBlocks (free) + ACF (free) |
| Тема-основа | GeneratePress (free) |
| Изоляция | 1 проект = 1 WP-инсталляция = 1 хостинг-аккаунт |
| Хостинг | **Бегет** (российский, доступный) |
| Сценарий правок | **Гибрид**: агенты ↔ код, клиент ↔ WP-админка |
| Раздача | MVP — ZIP-архив, далее плагин Claude Code, далее SaaS |
| Главный цикл | superpowers brainstorming → writing-plans → subagent-driven-development |
| Я.Директ-лендинги | Каждый оффер на своём поддомене |
| Я.Метрика, формы, виджеты | Подключены автоматически на этапе деплоя |

### Что НЕ делаем (важно)

- ❌ Headless WordPress + Vercel — Vercel в РФ нестабилен.
- ❌ Tilda — нет автоматизированного деплоя, нет git-версионирования, платно для учеников.
- ❌ Elementor / Bricks / Breakdance — платные, либо раздутый код.
- ❌ Multi-site WordPress — нельзя раздавать ученикам.
- ❌ FTP-деплой — только SSH + WP-CLI + rsync.

---

## 4. Структура папки одного проекта-лендинга

```
проект-лендинг-XYZ/
├─ 00_БРИФ/
│  ├─ brief.md                      # ниша, ЦА, цели, KPI, бюджет
│  └─ approved-design-brief.md      # утверждённый бриф (выход этапа 0)
│
├─ 01_КОНТЕКСТ/
│  ├─ niche.md                      # снепшот: что за ниша
│  ├─ competitors.md                # снепшот: конкуренты
│  ├─ audience.md                   # снепшот: целевая аудитория
│  └─ source-references.yaml        # откуда копировалось (для трассировки)
│
├─ 02_МАТЕРИАЛЫ_КЛИЕНТА/
│  ├─ photos/
│  │  ├─ original/                  # как есть от клиента
│  │  ├─ processed/                 # после photo-stylist
│  │  └─ stylesheet.md              # правила обработки (что можно/нельзя)
│  ├─ videos/                       # видео-отзывы клиента
│  ├─ testimonials/
│  │  ├─ written/                   # текстовые отзывы
│  │  ├─ yandex-maps/               # парсинг с Я.Карт
│  │  ├─ 2gis/
│  │  └─ other/                     # Otzovik, Flamp, соцсети
│  └─ assets-manifest.yaml          # что используем где (hero/about/proof)
│
├─ 03_РЕФЕРЕНСЫ/
│  ├─ refs/                         # скриншоты, ссылки, файлы Behance
│  ├─ index.yaml                    # статусы (candidate/approved/rejected)
│  ├─ moodboard.md
│  └─ moodboard.html                # 🎨 визуальный preview
│
├─ 04_БРЕНД/
│  ├─ extracted/                    # выход style-extractor
│  │  ├─ palette.yaml               # цвета с пиксельными источниками
│  │  ├─ fonts.yaml                 # шрифты + WhatTheFont confidence
│  │  ├─ icons.yaml                 # подобранные через Iconify
│  │  ├─ grid.md                    # сетка/ритм
│  │  ├─ motion.md                  # motion-паттерны (cinematic)
│  │  └─ components.yaml            # UI-элементы
│  ├─ brand-kit.md                  # финальный бренд-кит с provenance
│  └─ brand-kit.html                # 🎨 палитра + шрифты + иконки видны
│
├─ 05_ДИЗАЙН-СИСТЕМА/
│  ├─ DESIGN.md                     # единственный источник истины токенов
│  ├─ tokens.json                   # машиночитаемая версия
│  ├─ design-preview.html           # 🎨 живые компоненты, кликабельные
│  └─ scenes.md                     # cinematic-режим: scene grammar
│
├─ 06_СТЕК/
│  ├─ design-stack.yaml             # список плагинов и библиотек
│  ├─ component-library-plan.md     # откуда берётся каждый компонент
│  ├─ effects-plan.md               # анимации, motion
│  └─ font-and-color-plan.md        # шрифты + цвета с token-маппингом
│
├─ 07_КОНТЕНТ/
│  ├─ prototype.md                  # вход: прототип текста (копия)
│  ├─ final-copy.md                 # финальные тексты под блоки
│  └─ seo-copy.md                   # SEO-варианты заголовков
│
├─ 08_КОД/
│  ├─ wp-theme/                     # собранная WordPress-тема
│  │  ├─ style.css
│  │  ├─ functions.php
│  │  ├─ index.php
│  │  ├─ template-parts/
│  │  └─ assets/
│  │     ├─ fonts/                  # скачанные шрифты
│  │     ├─ icons/                  # скачанные иконки
│  │     └─ images/                 # ассеты
│  ├─ gutenberg-blocks/             # кастомные блоки (PHP + JS)
│  ├─ acf-fields.json               # конфиг ACF полей
│  └─ generateblocks-templates.json # экспорт шаблонов GenerateBlocks
│
├─ 09_ДЕПЛОЙ/
│  ├─ wp-config.yaml                # хост, домен, креды (зашифровано)
│  ├─ deploy.sh                     # SSH + WP-CLI + rsync скрипт
│  ├─ history.log                   # лог всех деплоев
│  ├─ dns-history.log               # лог DNS-настроек
│  └─ versions/                     # снепшоты для отката
│     ├─ 2026-05-03_v1.0/
│     ├─ 2026-05-04_v1.1/
│     └─ 2026-05-10_v2.0/
│
├─ 10_QA/
│  ├─ checklist.md                  # пройденные/не пройденные пункты
│  ├─ screenshots/                  # 1440px / 768px / 375px
│  ├─ lighthouse-report.json
│  └─ accessibility-report.md
│
├─ 11_АНАЛИТИКА/
│  ├─ metrika-config.md             # ID счётчика, цели, события
│  ├─ utm-templates.md              # шаблоны UTM-меток
│  ├─ goals-and-events.json
│  └─ ab-test-results/              # выходы lifecycle-keeper по A/B
│
├─ 12_SEO/
│  ├─ keywords.md                   # из Wordstat
│  ├─ meta-tags.yaml                # title/description/og по страницам
│  ├─ structured-data.json          # Schema.org
│  ├─ sitemap.xml                   # генерируется при деплое
│  ├─ robots.txt
│  └─ seo-audit-report.md
│
├─ agents/                         # локальные агенты этого проекта
├─ skills/                         # локальные скиллы этого проекта
├─ .specs/                          # superpowers spec-документы проекта
│
├─ .claude/
│  ├─ settings.json                 # hooks, разрешения
│  └─ commands/                     # slash-команды (наследуются от plugin)
│
├─ CLAUDE.md                        # инструкции для Claude в этом проекте
├─ README.md                        # инструкции для человека
├─ .env                             # секреты (в .gitignore!)
├─ .env.example                     # шаблон секретов
└─ .gitignore
```

### Связь с большим проектом

При создании лендинга через `/landing-from-context` система **копирует** (не симлинкует) данные из родительского проекта в `01_КОНТЕКСТ/` и `02_МАТЕРИАЛЫ_КЛИЕНТА/`. Это даёт **полную изоляцию**: лендинг работает на снепшоте на момент создания. Изменения в родительском проекте не ломают живые лендинги.

---

## 5. Workflow одного лендинга — 12 этапов

Каждый этап имеет:
- 🎯 **Цель**
- 🔌 **Входные данные**
- 🤖 **Агенты**
- 📤 **Выход**
- ✅ **Hard gate** (что должно быть утверждено перед переходом)
- 👁 **Визуальный артефакт**

### Этап 00 — Бриф

- 🎯 Зафиксировать намерение, нишу, KPI
- 🔌 Запрос пользователя или прототип текста
- 🤖 `landing-orchestrator`
- 📤 `00_БРИФ/approved-design-brief.md`
- ✅ Пользователь утвердил бриф
- 👁 `brief-summary.html` (краткое резюме)

### Этап 01 — Контекст

- 🎯 Снепшот данных о нише, ЦА, конкурентах
- 🔌 Родительский проект агентства ИЛИ ручной ввод
- 🤖 `landing-orchestrator` копирует, при отсутствии — спрашивает
- 📤 `01_КОНТЕКСТ/*.md`
- ✅ Контекст полон (есть ниша, ЦА, конкуренты)
- 👁 `context-overview.html`

### Этап 02 — Материалы клиента

- 🎯 Собрать оригинальные фото, видео, отзывы клиента
- 🔌 Файлы клиента, ссылки на Я.Карты / 2GIS / Otzovik
- 🤖 `client-assets-collector` (парсинг отзывов через Firecrawl), `photo-stylist` (обработка фото identity-safe)
- 📤 `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/processed/`, `testimonials/`
- ✅ Все материалы собраны, фото обработаны под референс-стиль
- 👁 `assets-gallery.html` (галерея + превью отзывов)

### Этап 03 — Референсы

- 🎯 Собрать визуальное направление
- 🔌 Ссылки на сайты / Behance / скриншоты / описание
- 🤖 `references-curator` (статусы), `moodboard-composer` (мудборд), `style-extractor` (декомпозиция: палитра + шрифты + иконки + сетка + motion)
- 📤 `03_РЕФЕРЕНСЫ/index.yaml`, `moodboard.md`, `04_БРЕНД/extracted/*.yaml`
- ✅ Минимум 3 референса в статусе `approved`, мудборд утверждён
- 👁 `moodboard.html` — все референсы с тегами

### Этап 04 — Бренд

- 🎯 Зафиксировать палитру, типографику, тон, иконки с **provenance**
- 🔌 `04_БРЕНД/extracted/*.yaml`
- 🤖 `brand-architect`
- 📤 `04_БРЕНД/brand-kit.md` + `brand-kit.html`
- ✅ Каждый цвет/шрифт/иконка имеет источник
- 👁 `brand-kit.html` — палитра, шрифты, иконки видны на одной странице

### Этап 05 — Дизайн-система

- 🎯 Создать `DESIGN.md` (единый источник истины токенов)
- 🔌 `04_БРЕНД/brand-kit.md`
- 🤖 `design-system-generator`, `scene-director` (если cinematic)
- 📤 `05_ДИЗАЙН-СИСТЕМА/DESIGN.md`, `tokens.json`, `design-preview.html`, `scenes.md`
- ✅ Все компоненты определены, токены полные
- 👁 `design-preview.html` — живые компоненты

### Этап 06 — Стек

- 🎯 Зафиксировать выбор плагинов, библиотек, иконок, шрифтов
- 🔌 `DESIGN.md`, бренд, режим (обычный/cinematic)
- 🤖 `stack-planner`
- 📤 `06_СТЕК/design-stack.yaml`, `component-library-plan.md`, `effects-plan.md`
- ✅ Никаких ad-hoc пакетов
- 👁 Текстовый список (не визуальный)

### Этап 07 — Контент

- 🎯 Адаптировать прототип текста под блоки лендинга
- 🔌 `07_КОНТЕНТ/prototype.md`, `DESIGN.md`
- 🤖 `content-writer`
- 📤 `07_КОНТЕНТ/final-copy.md`, `seo-copy.md`
- ✅ Тексты разложены по блокам
- 👁 Чтение в редакторе (без preview)

### Этап 08 — Код

- 🎯 Сгенерировать WP-тему, Gutenberg-блоки, ACF-поля
- 🔌 `DESIGN.md`, `final-copy.md`, `assets-manifest.yaml`
- 🤖 `wp-builder`, `integrations-engineer`, `analytics-engineer`, `seo-optimizer`
- 📤 `08_КОД/wp-theme/`, `gutenberg-blocks/`, `acf-fields.json`
- ✅ Локальный preview работает, все блоки рендерятся
- 👁 `localhost:8080` (через Local by Flywheel или wp-env)

### Этап 09 — Деплой

- 🎯 Опубликовать на Бегет, привязать домен, SSL
- 🔌 `08_КОД/`, `wp-config.yaml`, `.env`
- 🤖 `wp-deployer`
- 📤 Боевой сайт по URL
- ✅ Сайт открывается, формы шлют, SSL валиден
- 👁 Боевая ссылка

### Этап 10 — QA

- 🎯 Финальная проверка
- 🔌 Боевой сайт
- 🤖 `qa-auditor`
- 📤 `10_QA/checklist.md`, `screenshots/`, `lighthouse-report.json`
- ✅ Все 7 пунктов QA пройдены (см. ниже)
- 👁 `qa-report.html`

### Этап 11 — Аналитика

- 🎯 Подключить Я.Метрику, цели, события, UTM
- 🔌 Боевой сайт, ID счётчика
- 🤖 `analytics-engineer`
- 📤 `11_АНАЛИТИКА/metrika-config.md`
- ✅ Метрика собирает данные, цели работают
- 👁 Дашборд Метрики (внешний)

### Этап 12 — SEO

- 🎯 Оптимизировать под поиск
- 🔌 Боевой сайт, Wordstat
- 🤖 `seo-optimizer`
- 📤 `12_SEO/keywords.md`, `meta-tags.yaml`, `structured-data.json`, `sitemap.xml`
- ✅ Lighthouse SEO ≥ 95, валидный sitemap
- 👁 `seo-audit-report.md`

### QA Hard Gate (этап 10) — обязательные пункты

1. ✅ Десктоп 1440px без артефактов
2. ✅ Мобильный 375px без горизонтального скролла
3. ✅ Один главный CTA на экран
4. ✅ Контраст текста по WCAG AA
5. ✅ Видимый focus для клавиатурной навигации
6. ✅ Все токены из `DESIGN.md`, ничего руками
7. ✅ `prefers-reduced-motion` — анимации отключаются

---

## 6. Карта агентов (18 шт.)

Имена на английском (для машинной адресации). Русское описание — для людей.

| # | Имя (англ) | RU название | Что делает | Этап |
|---|---|---|---|---|
| 1 | `landing-orchestrator` | Главный дирижёр | Принимает запрос → ведёт по этапам, дёргает агентов | 00, координация |
| 2 | `client-assets-collector` | Сборщик клиентских материалов | Собирает фото/видео/отзывы клиента, парсит Я.Карты/2GIS/Otzovik | 02 |
| 3 | `photo-stylist` | Фото-стилист | Обработка фото под референс. Identity-safe (лицо/возраст не меняем) | 02 |
| 4 | `references-curator` | Куратор референсов | Сбор + статусы (candidate/approved/rejected) | 03 |
| 5 | `moodboard-composer` | Мудборд-композитор | Делает `moodboard.md` + `moodboard.html` | 03 |
| 6 | `style-extractor` | Декомпозитор стиля | Извлекает палитру, шрифты, иконки, сетку, motion из референсов с provenance | 03 |
| 7 | `brand-architect` | Бренд-архитектор | Из extracted-материала строит `brand-kit.md` | 04 |
| 8 | `design-system-generator` | Генератор дизайн-системы | `DESIGN.md` + `tokens.json` + `design-preview.html` | 05 |
| 9 | `scene-director` | Режиссёр сцен (cinematic) | Scene grammar 6–8 сцен, motion-план, parallax-логика | 05 (cinematic) |
| 10 | `stack-planner` | Планировщик стека | Плагины WP, библиотеки, иконки, шрифты | 06 |
| 11 | `content-writer` | Контент-райтер | Адаптация прототипа под блоки | 07 |
| 12 | `wp-builder` | WP-сборщик | Gutenberg-блоки + ACF-поля + WP-тема. Включает pop-up, всплывающие CTA, квиз-блоки | 08 |
| 13 | `integrations-engineer` | Инженер интеграций | Fluent Forms + CRM/Telegram/email + чат-виджеты | 08 |
| 14 | `analytics-engineer` | Инженер аналитики | Я.Метрика + цели + события + UTM. Тянет статистику A/B | 08, 11 |
| 15 | `seo-optimizer` | SEO-оптимизатор | Wordstat → ключи → мета-теги → h-структура → alt → Schema.org → sitemap → speed | 08, 12 |
| 16 | `qa-auditor` | QA-аудитор | Контраст / мобайл / формы / скорость / prefers-reduced-motion | 10 |
| 17 | `wp-deployer` | Деплоер | SSH + WP-CLI + rsync на Бегет, привязка домена, SSL | 09 |
| 18 | `lifecycle-keeper` | Хранитель жизненного цикла | Снепшоты, откаты, A/B-копии, авто-сравнение по конверсии | пост-деплой |

---

## 7. Карта скиллов и MCP-серверов

### 7.1 Скиллы — что используем

#### Из superpowers (только что установлен)

- `brainstorming` — сократическое уточнение
- `writing-plans` — планы по 2–5 минут
- `executing-plans` — батчевое выполнение с чекпоинтами
- `subagent-driven-development` — свежий субагент на каждый таск
- `dispatching-parallel-agents` — параллельные агенты
- `test-driven-development` — RED-GREEN-REFACTOR
- `verification-before-completion` — проверка результата
- `using-git-worktrees` — изолированные ветки
- `finishing-a-development-branch` — мерж/PR
- `requesting-code-review` / `receiving-code-review`
- `writing-skills` / `using-superpowers`

#### Из anthropic/skills (берём в систему)

- 🔴 `brand-guidelines` — стандартные паттерны бренд-гайда
- 🔴 `web-artifacts-builder` — генерация HTML-preview
- 🔴 `webapp-testing` — автотесты лендинга
- 🔴 `mcp-builder` — для написания собственных MCP (WP-CLI MCP)
- ✅ `pdf`, `docx`, `pptx`, `xlsx` — документы
- ✅ `canvas-design`, `algorithmic-art` — генеративная графика
- ✅ `skill-creator`, `doc-coauthoring`

#### Из tapestry-skills (берём)

- 🔴 `article-extractor` — Mozilla Readability для парсинга статей
- 🔴 `learn-this` — универсальное «дай URL — извлеки суть»
- 🟡 `youtube-transcript-downloader` — для парсинга видео-кейсов

#### Уже подключенные у пользователя (используем)

- `ui-ux-pro-max` — главный дизайн-эксперт
- `frontend-design` — генерация UI-кода
- `theme-factory` — темизация артефактов
- `figma`, `figma-use`, `figma-implement-design` — Figma → код
- `quiz-landing-builder` — квиз-блоки
- `competitor-screenshot-audit` — захват экранов конкурентов
- `firecrawl-audience-parser` — парсинг отзывов
- `audience-research-analyzer` — анализ аудитории
- `bulletproof` — устойчивые workflow
- `pptx-brand-deck-builder` — брендовые презентации
- `anthropic-skills:yandex-wordstat` — Wordstat (улучшенная версия пользователя добавляется в `skills/yandex-wordstat/`)

#### Свои скиллы (создаём 10 штук)

| Скилл | Что делает |
|---|---|
| `landing-project-init` | Создаёт папку проекта со структурой 00–12 |
| `landing-from-context` | Стартует из родительского проекта со снепшотом |
| `references-collection` | Сбор/статусы/index.yaml |
| `moodboard-creation` | Мудборд + HTML preview |
| `style-decomposition` | Извлечение палитры/шрифтов/иконок/motion |
| `design-tokens-generation` | DESIGN.md + tokens.json + preview |
| `wp-gutenberg-block-builder` | Генерация Gutenberg-блоков + ACF |
| `wp-theme-assembler` | Сборка финальной WP-темы |
| `gsap-scene-director` | Cinematic-сцены (только premium-режим) |
| `wp-cli-deployer` | Деплой через SSH + WP-CLI |
| `landing-versioning-and-cloning` | Снепшоты, откаты, A/B-копии |

### 7.2 MCP-серверы

| MCP | Зачем | Приоритет | Где взять |
|---|---|---|---|
| **Firecrawl MCP** | Парсинг референсов и отзывов | 🔴 must | https://www.firecrawl.dev (есть API-ключ) |
| **Figma MCP** | Pixel-perfect верстка из Figma | 🟡 опционально | Figma Desktop App с включённым MCP |
| **WP-CLI MCP** | Команды WordPress удалённо | 🔴 must (пишем сами) | Через `mcp-builder` за 1–2 дня |
| **Cloudflare/Reg.ru/Beget DNS MCP** | Авто-привязка поддоменов и SSL | 🟡 nice | Пишем сами через `mcp-builder` |
| **21st.dev/magic** | Inspiration для motion (cinematic) | ⚫ donor-layer | Уже подключен у пользователя |

---

## 8. Frontend-стек и библиотеки

### 8.1 База (всегда)

| Компонент | Цена | Зачем |
|---|---|---|
| **WordPress** | 0₽ | Платформа |
| **GeneratePress** (тема) | 0₽ | Базовая лёгкая тема |
| **GenerateBlocks** | 0₽ | Контейнеры, сетки в Gutenberg |
| **ACF (Advanced Custom Fields)** | 0₽ | Кастомные поля для клиента |
| **Fluent Forms Lite** | 0₽ | Формы (альтернатива Contact Form 7) |

### 8.2 Cinematic premium (опционально)

Подключаются через CDN в `functions.php` темы:

| Библиотека | Зачем | URL CDN |
|---|---|---|
| **GSAP** | Главный motion-движок | https://cdn.jsdelivr.net/npm/gsap@3 |
| **ScrollTrigger** | Scroll-driven storytelling | https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js |
| **Lenis** | Smooth scroll | https://cdn.jsdelivr.net/npm/@studio-freight/lenis |
| **SplitType** | Choreography заголовков | https://cdn.jsdelivr.net/npm/split-type |
| **Lucide Icons** | Точечные SVG | https://unpkg.com/lucide-static |

### 8.3 Утилитарный стек (по необходимости)

| Библиотека | Зачем |
|---|---|
| **Swiper** | Слайдеры/карусели |
| **CountUp.js** | Анимированные числа в proof-блоках |
| **Lottie Web** | Lottie-анимации |
| **AOS** | Лёгкие fade-up для не-cinematic режима |
| **Plyr** | Кастомный видео-плеер |

### 8.4 Иконки и шрифты

| Сервис | Зачем | URL |
|---|---|---|
| **Iconify** | 200k+ иконок единым API | https://iconify.design |
| **Lucide** | Базовая библиотека (через Iconify) | https://lucide.dev |
| **Phosphor** | Альтернатива | https://phosphoricons.com |
| **Heroicons** | Tailwind-style | https://heroicons.com |
| **Tabler Icons** | Линейные | https://tabler-icons.io |
| **Material Symbols** | Google | https://fonts.google.com/icons |
| **Fontshare** | Премиум-шрифты бесплатно | https://www.fontshare.com |
| **Google Fonts** | Стандарт | https://fonts.google.com |
| **Bunny Fonts** | GDPR/РФ-friendly CDN | https://fonts.bunny.net |

### 8.5 Запрещено в системе

- ❌ shadcn/ui, Radix, Base UI, React Aria — несовместимо с WP-стеком
- ❌ Mantine, DaisyUI, Tremor — не нужны под WP
- ❌ Motion for React — есть GSAP
- ❌ Bootstrap — устарел, raздутый
- ❌ Tailwind CSS — не дружит с GenerateBlocks из коробки

---

## 9. Cinematic Premium режим

Опциональный режим для дорогих проектов (например, премиальный finance-brand). Активируется флагом `--cinematic` при создании проекта.

### Архитектура

- Сайт построен из **6–8 сцен** вместо линейных секций
- Каждая сцена имеет: глубину, motion, scroll-логику
- Используется **GSAP + ScrollTrigger + Lenis + SplitType**
- Pinned hero, parallax depth, scroll-scrub transitions, stagger reveal
- Mobile — упрощённая версия (меньше parallax, короче timeline)

### Scene Grammar (типовая)

1. **Hero Film Frame** — full-height split composition, layered planes, slow parallax
2. **Chaos to Clarity** — text blocks слоями, фоновые орбиты с разной скоростью
3. **What You Get** — карточки с controlled stagger
4. **The Diagnostic Process** — quasi-timeline с parallax
5. **About the Expert** — portrait scene, premium light-depth
6. **Proof / Trust** — цифры, кейсы, restrained motion
7. **FAQ** — лёгкая сцена, clear interactions
8. **Final Call** — кульминация, contrast shift

### Motion Rules

✅ Hero layered parallax, scroll-scrub transitions, stagger reveal, orbital drift, portrait depth shift
❌ Scroll hijack, тяжёлые 3D, дешёвые fade-up на каждом блоке, particle systems

### Image Pipeline (cinematic)

- Identity-safe (лицо/возраст/черты НЕ меняем)
- Только: cutout, edge cleanup, light compositing, кадрирование под сцену
- Запрещено: AI-репейнт человека, beauty-retouch, омоложение

---

## 10. Точка входа — slash-команды

### Главный путь

```bash
/landing-new <project-slug>           # старт нового проекта (с нуля)
/landing-from-context <project-slug>  # старт из родительского проекта
/landing-clone <source> --as <new>    # A/B-копия независимого лендинга
```

### Точечный возврат к этапам

```bash
/landing-references                # перезапуск этапа 03
/landing-moodboard                 # перезапуск этапа 03
/landing-brand                     # перезапуск этапа 04
/landing-design                    # перезапуск этапа 05
/landing-stack                     # перезапуск этапа 06
/landing-content                   # перезапуск этапа 07
/landing-build                     # перезапуск этапа 08
/landing-qa                        # запуск QA (этап 10)
/landing-deploy                    # деплой (этап 09)
/landing-redeploy                  # повторный деплой после правок
/landing-rollback <version>        # откат к версии
```

### Сервисные

```bash
/landing-status            # где сейчас находится проект (этап X из 12)
/landing-help              # список команд + краткая справка
/landing-update            # ручное обновление мастер-системы
```

### Главный поток (вариант C — гибрид)

- **Новичок**: `/landing-new lp-kurs` → автопилот ведёт через все 12 этапов с подтверждениями
- **Опытный**: `/landing-references --rerun` → точечно перезапускает этап
- **Ремонт**: `/landing-rollback v1.0` → откат

---

## 11. Деплой на Бегет — детальный механизм

### Технология: SSH + WP-CLI + rsync

Скрипт `deploy.sh` в каждом проекте делает следующее:

```bash
#!/bin/bash
# Пример для иллюстрации; финальный код — в этапе реализации

set -e
source .env

# 1. Сборка темы
echo "📦 Сборка темы..."
# (минификация CSS/JS, оптимизация изображений)

# 2. Snapshot перед деплоем
VERSION=$(date +"%Y-%m-%d_v$(cat .version)")
mkdir -p 09_ДЕПЛОЙ/versions/$VERSION
cp -r 08_КОД/wp-theme/ 09_ДЕПЛОЙ/versions/$VERSION/

# 3. Rsync на Бегет
echo "🚀 Деплой на $BEGET_HOST..."
rsync -avz --delete \
  -e "ssh -i $SSH_KEY_PATH" \
  08_КОД/wp-theme/ \
  $BEGET_USER@$BEGET_HOST:$WP_PATH/wp-content/themes/$THEME_SLUG/

# 4. Активация темы и плагинов через WP-CLI
ssh -i $SSH_KEY_PATH $BEGET_USER@$BEGET_HOST <<EOF
  cd $WP_PATH
  wp theme activate $THEME_SLUG
  wp plugin install advanced-custom-fields generateblocks fluentform --activate
  wp acf import --json_file=acf-fields.json
  wp cache flush
  wp option update blogname "$SITE_TITLE"
EOF

# 5. Лог
echo "$(date) deploy $VERSION → $WP_HOST" >> 09_ДЕПЛОЙ/history.log

echo "✅ Готово: https://$DOMAIN"
```

### Что нужно от Бегета

1. **SSH-доступ** — есть на всех тарифах от 199₽/мес.
2. **WP-CLI** — установлен на Бегете по умолчанию.
3. **PHP версия** — 8.1+ (рекомендация).
4. **MySQL/MariaDB** — есть.

### Тарифы Бегета

- **Стартовый** — 199₽/мес — 1 сайт, 1 ГБ — для тестов
- **Стандарт** — 290₽/мес — без ограничений по сайтам — рекомендую
- **VPS** — от 1000₽/мес — если 50+ лендингов

---

## 12. DNS-автоматизация

### Поддерживаемые провайдеры

| Провайдер | API | Приоритет |
|---|---|---|
| **Бегет API** | https://beget.com/ru/kb/api | 🔴 must |
| **Reg.ru API** | https://www.reg.ru/reseller/api2_doc | 🔴 must |
| **Timeweb API** | https://timeweb.cloud/api-docs | 🟡 nice |
| **Cloudflare API** | https://api.cloudflare.com | 🟡 nice |
| **Прочие** | ручная инструкция | 🔴 fallback |

### Workflow

1. Агент `wp-deployer` читает `.env`: `DNS_PROVIDER=beget`
2. Получает API-ключ
3. Создаёт A-запись поддомена → IP Бегета
4. Ждёт пропагации DNS (опрос `dig` каждые 30 сек, до 10 мин)
5. Активирует SSL через Let's Encrypt (через панель Бегета или certbot по SSH)
6. Настраивает редиректы HTTP→HTTPS, www→без www
7. Логирует в `09_ДЕПЛОЙ/dns-history.log`

### Если провайдер не поддерживается

Агент выдаёт **готовый текст-инструкцию** для пользователя:

```
⚠️ Провайдер X пока не поддерживается. Выполни эти шаги вручную:

1. Зайди в панель X
2. Найди раздел DNS / Записи
3. Добавь A-запись:
   Имя: lp-kurs
   Значение: 87.236.16.123  (IP Бегета)
   TTL: 300
4. Сохрани и подожди 5–30 минут
5. Вернись и нажми /landing-deploy --continue
```

---

## 13. Версионирование и A/B-копии

### Версионирование (гибрид C)

- **Локально**: git-репо в каждом проекте
  - `git tag v1.0`, `v1.1`, `v2.0`
  - История всех правок
- **На Бегете**: snapshot-папки в `09_ДЕПЛОЙ/versions/`
  - `2026-05-03_v1.0/` (полная копия темы)
  - Автоматически создаётся перед каждым деплоем
  - Откат: `/landing-rollback v1.0` → rsync прошлой версии

### A/B-копии (отдельная команда)

```bash
/landing-clone lp-kurs --as lp-kurs-v2
```

Что происходит:
1. Создаётся **новая папка проекта** `проект-лендинг-lp-kurs-v2/` (рядом, не подпапкой)
2. Копируется код, конфиги, ассеты
3. Записывается `parent.yaml` со ссылкой на оригинал
4. Создаётся новый WP на новом поддомене (`lp-kurs-v2.example.ru`)
5. Импортируется тема + ACF + GenerateBlocks
6. Я.Метрика подключается с новым счётчиком (или общим)

A/B-копия = **независимый лендинг**, не «вариант страницы».

### Авто-сравнение по конверсии

`lifecycle-keeper` раз в день/неделю:
1. Через `analytics-engineer` тянет из Я.Метрики: показы, CTR, цели, цена лида
2. Считает статистическую значимость (chi-square test)
3. Если v2 побеждает с p < 0.05 — генерирует отчёт
4. Уведомляет пользователя: «v2 победил, переключить основной поддомен?»

---

## 14. Хранение секретов

### MVP (старт) — `.env` per project + `.env.local` глобально

**Глобальные ключи** живут в `landing-system/.env.local` (вне git):

```bash
# DNS API ключи
BEGET_API_LOGIN=
BEGET_API_PASSWORD=
REGRU_API_USERNAME=
REGRU_API_PASSWORD=
CLOUDFLARE_API_TOKEN=

# Шрифты и иконки (большинство — без ключей)
WHATTHEFONT_API_KEY=        # https://www.myfonts.com/WhatTheFont (free tier 25/day)

# Парсинг
FIRECRAWL_API_KEY=          # https://www.firecrawl.dev

# Я.Метрика и Wordstat
YANDEX_OAUTH_TOKEN=         # https://yandex.ru/dev/wordstat
YANDEX_METRIKA_OAUTH=       # https://yandex.ru/dev/metrika

# Опциональные
TELEGRAM_BOT_TOKEN=         # @BotFather для уведомлений деплоя
GITHUB_TOKEN=               # если деплоим через CI
```

**Проектные ключи** живут в `<проект>/.env`:

```bash
# Бегет SSH доступ
BEGET_HOST=server123.beget.tech
BEGET_USER=neuroboost
SSH_KEY_PATH=~/.ssh/beget_neuroboost
WP_PATH=/home/n/neuroboost/landing-kurs.example.ru

# WP креды
WP_ADMIN_LOGIN=
WP_ADMIN_PASSWORD=

# Домен
DOMAIN=lp-kurs.neuroboost.ru
DNS_PROVIDER=beget

# Я.Метрика для этого лендинга
YM_COUNTER_ID=12345678

# CRM/Telegram-интеграции
TELEGRAM_NOTIFY_CHAT_ID=    # куда шлёт лиды бот
CRM_WEBHOOK_URL=
```

**Никогда не коммитятся** — добавлены в `.gitignore`.

### Этап 2 (для агентства) — vault

Через `1Password CLI` или `age` — зашифрованные секреты, расшариваемые между сотрудниками. Расширение в `Roadmap`.

---

## 15. Hooks (автоматизации)

В `landing-system/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/pre-deploy-check.js",
            "comment": "Блокирует /landing-deploy если QA не пройден"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/post-deploy-actions.js",
            "comment": "После деплоя: запускает analytics + seo + лог"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/on-session-stop.js",
            "comment": "Snapshot текущего состояния проекта"
          }
        ]
      }
    ]
  }
}
```

| Hook | Срабатывает | Что делает |
|---|---|---|
| `pre-deploy-check` | Перед `/landing-deploy` | Проверяет: QA пройден? Все ассеты на месте? |
| `post-deploy-actions` | После успешного деплоя | Запускает `analytics-engineer`, `seo-optimizer`, лог |
| `on-error-rollback` | При ошибке деплоя | Автоматический rollback на прошлую версию |
| `on-session-stop` | Закрытие Claude | Snapshot текущего состояния |

---

## 16. Управляемость — визуальные артефакты

После каждого этапа — `.html` файл, который можно открыть в браузере:

| Этап | Артефакт | Что видно |
|---|---|---|
| 02 | `assets-gallery.html` | Галерея фото + плеер видео + список отзывов |
| 03 | `moodboard.html` | Все референсы со статусами на одной странице |
| 04 | `brand-kit.html` | Палитра, шрифты, иконки, тон-голоса — всё на одном экране |
| 05 | `design-preview.html` | Живые компоненты (кнопки, карточки, формы) — кликабельные |
| 08 | localhost preview | WordPress тема локально |
| 10 | `qa-report.html` | Чек-лист с пройденными/не пройденными пунктами |
| 12 | `seo-audit-report.md` | SEO-отчёт |

---

## 17. Упаковка и раздача (MVP → плагин → SaaS)

### Этап 1 — MVP (сейчас)

**ZIP-архив `landing-system.zip` (5–10 МБ).**

Содержимое:
```
landing-system/
├─ agents/                # 18 агентов
├─ skills/                # все наши + копии нужных
├─ .claude/
│  ├─ commands/            # slash-команды
│  └─ settings.json        # hooks
├─ template/               # шаблон будущего проекта-лендинга
├─ docs/
│  └─ superpowers/specs/   # этот документ
├─ scripts/                # bash-скрипты (deploy.sh, init.sh)
├─ README.md               # инструкция установки
├─ CLAUDE.md               # инструкции для Claude в этой папке
├─ .env.example
└─ .env.local.example
```

**Раздача ученикам:**
1. Я zip-ую → `landing-system.zip`
2. Отправляю ученику (Telegram / почта / облако)
3. Ученик распаковывает в любую папку
4. Открывает Claude Code в папке: `cd landing-system && claude`
5. Читает `README.md` → заполняет `.env.local`
6. Запускает `/landing-new lp-первый-проект`

**Никакого маркетплейса. Никаких git-фокусов.**

### Этап 2 — Плагин Claude Code (через 1–2 месяца)

Превращаем папку в плагин на собственном маркетплейсе:
- Свой git-репо `neuroboost/marketplace` (приватный)
- Плагин `landing-system@neuroboost`
- Установка ученика: `/plugin marketplace add neuroboost/marketplace` + `/plugin install landing-system@neuroboost`
- Обновления: `/plugin update`
- Преимущество: команды глобально, проекты изолированно

### Этап 3 — SaaS (когда стабилизируется)

Защита IP от сотрудников:
- Тонкий клиент у сотрудника → MCP-сервер на твоём VPS → твоя логика
- Шаблоны и ноу-хау — на сервере
- Сотрудники получают только функционал, не код

---

## 18. Установка системы — пошагово

### Что нужно перед стартом

- macOS / Linux / Windows (WSL)
- Установленный **Claude Code**: https://docs.claude.com/claude-code
- **Node.js 20+**: https://nodejs.org
- **Git**: https://git-scm.com
- **SSH-клиент**: встроен в macOS/Linux, для Windows — Git Bash или WSL
- Хостинг **Бегет** с тарифом «Стандарт» от 290₽/мес (или выше)

### Шаг 1 — Установить Claude Code

```bash
# macOS
brew install anthropic/tap/claude-code

# Linux / Windows WSL
curl -fsSL https://claude.com/install.sh | bash
```

Проверка: `claude --version`.

### Шаг 2 — Установить плагин superpowers

```bash
claude
> /plugin install superpowers@claude-plugins-official
```

Проверь: `/plugin list` → должен быть `superpowers v5.x`.

### Шаг 3 — Распаковать `landing-system.zip`

```bash
mkdir -p ~/Lendings
cd ~/Lendings
unzip /path/to/landing-system.zip
cd landing-system
```

### Шаг 4 — Заполнить глобальные секреты

```bash
cp .env.local.example .env.local
# Открой .env.local в редакторе и заполни ключи
# (см. раздел 19 — где взять ключи)
```

### Шаг 5 — Установить локальные зависимости

```bash
npm install        # Node-зависимости hooks-скриптов
pip install -r requirements.txt  # Python для color-extractor
```

### Шаг 6 — Активировать систему в Claude

```bash
claude
> /landing-help
```

Если видишь список команд `/landing-*` — система работает. Если нет — проверь `CLAUDE.md` в папке.

### Шаг 7 — Сделать первый проект

```bash
> /landing-new lp-первый-проект
```

Ответь на вопросы оркестратора. Тебя проведут через все 12 этапов.

### Шаг 8 — Настроить SSH-доступ к Бегету

(Делается один раз)

1. Создай SSH-ключ:
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/beget_neuroboost -N ""
   ```
2. Скопируй публичный ключ:
   ```bash
   cat ~/.ssh/beget_neuroboost.pub
   ```
3. Добавь в Бегет: панель → SSH-доступ → добавить ключ.
4. Проверь:
   ```bash
   ssh -i ~/.ssh/beget_neuroboost user@server123.beget.tech
   ```

---

## 19. Получение всех API-ключей — где и как

Этот раздел — **главный гид**. Каждый сервис: ссылка → шаги → стоимость → куда вставить.

### 19.1 Бегет (хостинг + DNS)

**Зачем:** хостить WP, управлять поддоменами, SSL.

1. Регистрация: https://beget.com → «Регистрация»
2. Купить тариф «Стандарт» (290₽/мес) или «Стартовый» (199₽/мес для теста)
3. **Получить API-ключ:**
   - Панель управления → «API»
   - Включить API
   - Логин = твой логин панели; пароль = тот же или сгенерированный отдельно
4. Вставить в `.env.local`:
   ```bash
   BEGET_API_LOGIN=neuroboost
   BEGET_API_PASSWORD=ваш_пароль_или_API_password
   ```

**Доки API:** https://beget.com/ru/kb/api

### 19.2 Reg.ru (домены, опционально DNS)

**Зачем:** если домен куплен на Reg.ru — управлять DNS через API.

1. https://www.reg.ru → купить домен
2. Включить API: панель → «Партнёрский кабинет» → «API»
3. Получить логин и пароль API (отдельные от панели)
4. В `.env.local`:
   ```bash
   REGRU_API_USERNAME=
   REGRU_API_PASSWORD=
   ```

**Доки:** https://www.reg.ru/reseller/api2_doc

### 19.3 Cloudflare (опционально, для иностранных доменов)

**Зачем:** если домен на Cloudflare DNS — управлять через API.

1. https://dash.cloudflare.com
2. Профиль → «API Tokens» → «Create Token»
3. Шаблон «Edit zone DNS» → выбрать твою зону
4. Скопировать токен
5. В `.env.local`:
   ```bash
   CLOUDFLARE_API_TOKEN=
   ```

**Бесплатно** для базовых задач.

### 19.4 Firecrawl (парсинг сайтов и отзывов)

**Зачем:** парсить отзывы с Я.Карт, 2GIS, конкурентов.

1. https://www.firecrawl.dev → Sign up (через GitHub)
2. Dashboard → API Keys → Create
3. **Free tier:** 500 запросов/мес — хватит для теста
4. **Hobby:** $19/мес — рекомендую для агентства
5. В `.env.local`:
   ```bash
   FIRECRAWL_API_KEY=fc-...
   ```

### 19.5 WhatTheFont (определение шрифтов)

**Зачем:** автоопределение шрифта по скриншоту референса.

1. https://www.myfonts.com/WhatTheFont
2. Зарегистрироваться → раздел «Developers» → «API»
3. **Free tier:** 25 запросов/день — нам хватит
4. Запросить ключ через форму
5. В `.env.local`:
   ```bash
   WHATTHEFONT_API_KEY=
   ```

**Альтернатива (бесплатная навсегда):** Claude vision как fallback — встроено.

### 19.6 Yandex Wordstat (ключевые слова)

**Зачем:** ключи для SEO-оптимизатора.

1. https://yandex.ru/dev/wordstat — почитай условия
2. Зарегистрировать приложение: https://oauth.yandex.ru/client/new
3. Подключить scope: `direct:api`, `wordstat:use`
4. Получить **OAuth-токен**: https://yandex.ru/dev/wordstat/doc/dg/concepts/auth.html
5. В `.env.local`:
   ```bash
   YANDEX_OAUTH_TOKEN=
   ```

**Бесплатно**, но требует одобрения Яндекса (1–3 дня).

### 19.7 Yandex Metrika (аналитика)

**Зачем:** подключение к лендингу + чтение статистики A/B.

1. https://metrika.yandex.ru → создать счётчик для каждого лендинга
2. Скопировать **ID счётчика** → в `.env` проекта (`YM_COUNTER_ID`)
3. Для **API чтения** статистики:
   - https://oauth.yandex.ru/client/new
   - Scope: `metrika:read`
   - Получить OAuth-токен
   - В `.env.local`:
     ```bash
     YANDEX_METRIKA_OAUTH=
     ```

**Бесплатно**.

### 19.8 Telegram Bot (уведомления о деплое и лиды с форм)

**Зачем:** уведомления когда лид пришёл / деплой готов.

1. Открыть Telegram → найти `@BotFather`
2. `/newbot` → задать имя → получить **токен бота**
3. Получить chat_id куда слать уведомления:
   - Создать канал/группу, добавить бота как админа
   - Написать в группу любое сообщение
   - Открыть `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Найти `chat.id`
4. В `.env.local` (глобальные) и `.env` (проектные):
   ```bash
   TELEGRAM_BOT_TOKEN=
   TELEGRAM_NOTIFY_CHAT_ID=          # для деплоя
   TELEGRAM_LEADS_CHAT_ID=           # для лидов с форм этого проекта
   ```

**Бесплатно**.

### 19.9 GitHub (опционально, этап 2)

**Зачем:** хостить плагин на собственном маркетплейсе (этап 2).

1. https://github.com → Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic)
3. Scope: `repo`, `read:packages`
4. В `.env.local`:
   ```bash
   GITHUB_TOKEN=
   ```

### 19.10 Iconify (бесплатно, без ключа)

200k+ иконок через публичный API: https://iconify.design — **API-ключ не требуется**.

### 19.11 Fontshare / Google Fonts / Bunny Fonts

Все три — **без ключа**, прямой CDN.

---

### Сводная таблица

| Сервис | Цена | Где взять | Куда |
|---|---|---|---|
| Бегет | 290₽/мес | beget.com | `.env.local` |
| Reg.ru | per domain | reg.ru | `.env.local` |
| Cloudflare | бесплатно | dash.cloudflare.com | `.env.local` |
| Firecrawl | $0–$19/мес | firecrawl.dev | `.env.local` |
| WhatTheFont | бесплатно | myfonts.com | `.env.local` |
| Yandex Wordstat | бесплатно | yandex.ru/dev | `.env.local` |
| Yandex Metrika | бесплатно | metrika.yandex.ru | `.env.local` + `.env` |
| Telegram Bot | бесплатно | @BotFather | `.env.local` + `.env` |
| GitHub | бесплатно | github.com | `.env.local` (этап 2) |
| Iconify, Fontshare, Google Fonts, Bunny Fonts | бесплатно | без ключа | — |

**Минимальный набор для запуска MVP:**
- Бегет (хостинг)
- Firecrawl (парсинг)
- Yandex Metrika
- Telegram Bot

Остальное — по мере необходимости.

---

## 20. Использование — типовые сценарии

### Сценарий 1 — «Новый лендинг с нуля»

```bash
cd ~/Lendings/landing-system
claude
> /landing-new lp-кpc-марафон

# Оркестратор спрашивает:
# - Ниша? → "онлайн-курс по копирайтингу"
# - Прототип текста есть? → "да, у меня файл prototype.md"
# - Материалы клиента (фото/видео/отзывы)? → "вот папка с фото"
# - Референсы? → "вот ссылки и Behance-папка"

# Дальше автопилот:
# - Этап 02: client-assets-collector обработает фото, спарсит Я.Карты-отзывы
# - Этап 03: references-curator + style-extractor → moodboard.html → ждёт твоего "ок"
# - Этап 04: brand-architect → brand-kit.html → ждёт "ок"
# - ... до этапа 12

# Финал: твой сайт https://lp-kurs.neuroboost.ru
```

### Сценарий 2 — «Из контекста большого проекта»

Ты в папке агентства, где уже есть исследования ЦА, отзывы, прототип:

```bash
cd ~/Desktop/Агентство\ лидогенерации/04_документы/курс-копирайтинг
claude
> /landing-from-context lp-марафон-2026

# Система:
# 1. Создаёт ../landing-system/projects/lp-марафон-2026/
# 2. Копирует снепшотом 01_контекст/, 05_исследования/
# 3. Ищет prototype.md → копирует в 07_КОНТЕНТ/
# 4. Запускает оркестратор, начиная с Этап 02 (материалы)
```

### Сценарий 3 — «A/B тест нового заголовка»

Лендинг `lp-марафон-2026` живой, льётся реклама. Хочешь протестировать новый hero:

```bash
> /landing-clone lp-марафон-2026 --as lp-марафон-2026-v2-bold-hero

# Что происходит:
# 1. Создаётся независимая папка проекта
# 2. Копируется тема, ассеты, конфиги
# 3. Создаётся новый WP на поддомене lp-марафон-v2.neuroboost.ru
# 4. Линкуется parent.yaml → знает откуда клонировано
# 5. Открывается /landing-content для правки заголовка

> # Правишь hero-заголовок → /landing-deploy
> # Льёшь Я.Директ 50/50 на оба
> # Через 7 дней:
> /landing-status lp-марафон-2026

# lifecycle-keeper показывает:
# "v1: CR 3.2%, цена лида 450₽
#  v2: CR 4.1%, цена лида 380₽
#  Победил v2 (p=0.03). Переключить основной поддомен?"
```

### Сценарий 4 — «Откат после неудачной правки»

```bash
> /landing-deploy
# Ой, что-то сломалось

> /landing-rollback v1.0
# Откатились к версии перед правкой
```

### Сценарий 5 — «Клиент хочет поменять текст и цену»

Клиент логинится в WordPress-админку. Видит ACF-поля:
- «Заголовок героя»
- «Цена курса»
- «Текст кнопки»

Меняет → жмёт «Обновить» → лендинг обновлён без программиста.

### Сценарий 6 — «Cinematic premium лендинг»

```bash
> /landing-new lp-екатерина-finance --cinematic

# Оркестратор спрашивает дополнительно:
# - Сколько сцен? (default 8)
# - Главный референс motion?
# - Запреты на эффекты?

# scene-director проектирует grammar 8 сцен
# wp-builder подключает GSAP + ScrollTrigger + Lenis в functions.php
# Генерит блоки с motion-логикой
```

---

## 21. Расширения и Roadmap

### 🟡 Этап 2 (через 1–2 месяца после MVP)

- [ ] Превратить ZIP в плагин Claude Code на собственном маркетплейсе агентства
- [ ] Создать приватный git-репо `neuroboost/claude-marketplace`
- [ ] Перевести секреты на 1Password CLI / age-encrypted vault для агентства
- [ ] WP-CLI MCP-сервер собственный (через скилл `mcp-builder`)
- [ ] DNS MCP-серверы (Бегет, Reg.ru, Cloudflare) собственные
- [ ] Учебный режим `EDU_MODE` с расширенными комментариями
- [ ] GitHub Actions для CI деплоя (автоматический деплой на push)

### 🟡 Этап 3 (когда продукт стабилизируется)

- [ ] **SaaS-режим** — критическая логика и шаблоны на твоём сервере
- [ ] Закрытая версия для сотрудников агентства (тонкий клиент)
- [ ] Биллинг для учеников (доступ через подписку)
- [ ] Web-интерфейс для не-CLI пользователей (опционально)
- [ ] Маркетплейс шаблонов / готовых блоков между учениками

### ⚫ Long-term

- [ ] Поддержка не-WordPress целей: Tilda export, headless static sites, Webflow
- [ ] Интеграция с Я.Директ API для авто-запуска кампаний
- [ ] Multi-language лендинги (i18n)
- [ ] AI-A/B (агент сам предлагает гипотезы)

---

## 22. Антипаттерны (чего не делаем)

### Архитектура

- ❌ Один WordPress на много лендингов (multisite или категории)
- ❌ Headless WP с фронтом на Vercel/Netlify (РФ-нестабильно)
- ❌ FTP-деплой
- ❌ Ручное создание поддоменов через панель

### Дизайн

- ❌ Стоковые шаблоны Elementor / Wix-style
- ❌ Glassmorphism без причины («просто потому что в моде»)
- ❌ Particle systems на финансовых/премиум брендах
- ❌ Scroll hijack, ломающий UX
- ❌ Бесконечные fade-up на каждом блоке (cinematic это запрещает)

### Контент

- ❌ Lorem ipsum в финальном лендинге
- ❌ Ad-hoc копирайт без брифа
- ❌ AI-генерация ЦА без живых исследований/отзывов

### Изображения

- ❌ AI-репейнт людей (изменение лица, омоложение, beauty-retouch)
- ❌ Только стоки без оригинальных материалов клиента
- ❌ Низкое разрешение / неоптимизированный JPG

### Процесс

- ❌ Пропускать утверждение этапа («давай быстрее, потом исправим»)
- ❌ Деплой без QA
- ❌ Ad-hoc плагины вне `design-stack.yaml`

---

## 23. Чек-лист готовности к релизу MVP

Это **что должно быть готово** для первого релиза `landing-system.zip` ученикам.

### Скиллы

- [ ] `landing-project-init` — создание структуры папки
- [ ] `landing-from-context` — старт из родительского
- [ ] `references-collection` — сбор и статусы
- [ ] `moodboard-creation` — мудборд + HTML
- [ ] `style-decomposition` — извлечение палитры/шрифтов/иконок
- [ ] `design-tokens-generation` — DESIGN.md
- [ ] `wp-gutenberg-block-builder` — Gutenberg-блоки
- [ ] `wp-theme-assembler` — финальная тема
- [ ] `gsap-scene-director` — cinematic-сцены
- [ ] `wp-cli-deployer` — деплой
- [ ] `landing-versioning-and-cloning` — версии и клоны

### Агенты

- [ ] Все 18 агентов в `agents/` с правильными manifest.json
- [ ] У каждого: описание, инструменты, скиллы

### Команды

- [ ] `/landing-new`
- [ ] `/landing-from-context`
- [ ] `/landing-clone`
- [ ] `/landing-status`
- [ ] `/landing-deploy`, `/landing-redeploy`, `/landing-rollback`
- [ ] `/landing-references`, `/landing-moodboard`, `/landing-brand`, `/landing-design`, `/landing-stack`, `/landing-content`, `/landing-build`
- [ ] `/landing-qa`
- [ ] `/landing-help`, `/landing-update`

### Hooks

- [ ] `pre-deploy-check.js`
- [ ] `post-deploy-actions.js`
- [ ] `on-error-rollback.js`
- [ ] `on-session-stop.js`

### Шаблон проекта

- [ ] Папки 00–12 с placeholder-файлами
- [ ] `CLAUDE.md` шаблон
- [ ] `README.md` шаблон
- [ ] `.env.example`
- [ ] `.gitignore`

### Документация

- [ ] `README.md` мастер-системы
- [ ] Этот spec-документ
- [ ] Видео/гифки use-кейсов (опционально для этапа 2)

### Тестирование

- [ ] Pilot-проект на собственной нише (например, лендинг агентства)
- [ ] Вторая итерация — другая ниша (для проверки переносимости)
- [ ] QA пройден на pilot

### Раздача

- [ ] ZIP-архив `landing-system.zip` собран
- [ ] Инструкция установки (этот раздел 18)
- [ ] Минимум 1 ученик прошёл установку с первой попытки

---

## Самопроверка spec-документа

Применил self-review по superpowers brainstorming:

1. **Placeholder scan:** ✅ Нет TBD/TODO в финальной версии
2. **Internal consistency:** ✅ Все ссылки между разделами совпадают
3. **Scope check:** ⚠️ Документ описывает MVP + Roadmap. MVP — реализуемый объём. Roadmap — отдельные циклы spec → plan → implementation.
4. **Ambiguity check:** ✅ Решения зафиксированы однозначно

---

## Следующий шаг

После твоего утверждения этого документа — **переход к `writing-plans` skill** (создание детального плана реализации MVP, разбитого на куски по 2–5 минут с точными файлами и кодом).

**Жду твоё:**
- ✅ «Утверждаю» → перехожу к writing-plans
- 📝 «Правки: …» → корректирую spec и обновляю

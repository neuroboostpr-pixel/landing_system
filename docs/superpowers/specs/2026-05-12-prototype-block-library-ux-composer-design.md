# Prototype + Block Library + ux-composer — Design Spec (PR-A)

**Date:** 2026-05-12
**Status:** Draft (pending user review)
**Author:** brainstorming session with user
**Scope:** PR-A из 4-частного апгрейда. Цели PR-B (photo pipeline), PR-C (icon/infographic generators), PR-D (orchestrator integration) — описаны как Out of scope.

## Problem

Текущий workflow содержит этап `05 Дизайн-система` (Design.md — токены/шрифты/отступы) → `06 Стек` → `07 Контент` → `08 Код`. Между Design.md и Кодом — **пустота**: нет ни структурированного прототипа как источника правды, ни выбора композиций блоков, ни промежуточного preview «как блок выглядит с наложенной дизайн-системой и плейсхолдерами контента».

В результате:

1. **Контент и фото подгоняются под уже сделанную верстку**, а не наоборот. Переделки.
2. **Блоки каждый раз придумываются с нуля.** Качество скачет, скорость падает.
3. **Mobile делается вторично.** На макете норм, на телефоне — нет.
4. **Прототип как артефакт отсутствует.** Тексты, смыслы, офферы лежат в брифе/контенте, но не консолидированы в единый утверждённый документ, по которому строится всё дальнейшее.
5. **Существующий `ui-ux-pro-max` скилл подключён к системе как библиотека, но НЕ к workflow.** Его паттерны не используются `landing-orchestrator`.

## Goals

1. Сделать **Прототип** явным входным артефактом каждого проекта (импорт PDF/MD от пользователя → нормализация в MD+YAML).
2. Создать **Block Library** — общий каталог `landing-system/block-library/` с переиспользуемыми мини-скиллами блоков (формат позаимствован из OpenDesign).
3. Создать агент **`ux-composer`** — между Design.md и Кодом. Читает прототип + design tokens + библиотеку → рендерит интерактивный `wireframe.html` с переключателями вариантов composition (radio-кнопки, CSS-only) + `composed.html` с наложенной дизайн-системой.
4. Mobile зашить **на уровне блока**: каждый блок в библиотеке существует парой `template.html` + `template-mobile.html`. Без исключений.
5. Использовать существующие инструменты максимально: `ui-ux-pro-max` как движок паттернов, OpenDesign как источник формата и эталонных Design.md, `anthropic-skills:pdf` для парсинга прототипа.

## Non-goals (PR-A specific)

- **Photo Pipeline** (photo-curator, доработка paralaximus-codex под client-photo, photo-preview-board) — отдельный PR-B.
- **Icon Generator / Infographic Builder** через gpt-image-2 — отдельный PR-C.
- **Stage-gates интеграция** (вшивание новых этапов в `landing-orchestrator`, `config/stage-gates.yaml`, `.landing-state.yaml`) — отдельный PR-D.
- **Калькуляторы под нишу** (quiz-calc-repair/courses/services) — отложено, добавляем после стабилизации основной библиотеки.
- **Pinterest «20 Customizable Headers»** разбор — отложено до получения скриншота.
- **Discovery form + Direction picker** + **OKLch 5 visual systems** (E+F из OpenDesign) — отложено до следующих итераций.
- Автогенерация прототипа агентом — на старте только импорт от пользователя.
- React/shadcn компоненты — все блоки в чистом HTML + inline CSS.
- Visual regression тесты для блоков — это задача QA.

## Decisions log

| # | Решение | Источник |
|---|---|---|
| D1 | Прототип — гибрид MD+YAML. Человек редактирует MD, скрипт автогенерит YAML. | 1.1 → C |
| D2 | Прототип импортируется, не создаётся агентом. Новый агент `prototype-importer`. | 1.2 → import-only |
| D3 | Block library в `landing-system/block-library/` (общая для всех проектов). | 2.1 |
| D4 | Seed-блоки: гибрид (драфт из `ui-ux-pro-max` + `OpenDesign` → пользователь прикладывает референсы где не нравится). | 2.2 → C |
| D5 | Ниши seed: услуги + B2C + локальный бизнес равномерно (по 1 hero на каждую). | 2.4 → D |
| D6 | Квиз-блоки: все 5 + комментарии к вопросам. WhatsApp ❌, Telegram ✅, Max Messenger ✅. Калькуляторы — позже. | 2.5 |
| D7 | `wireframe.html` интерактивен: radio-кнопки + CSS `:checked + sibling`. Без JS-фреймворков. | Q3 |
| D8 | Стек блоков: чистый HTML + CSS (CSS внутри `<style>` тега в `template.html` для портабельности — каждый блок самодостаточен и открывается двойным кликом). | 5.2 → A |
| D9 | PR-A и PR-D разделены. | 4.2 → B |
| D10 | OpenDesign забираем: A+B+C+D+G+H+I+J+K. Копируем нужные файлы с атрибуцией в `THIRD_PARTY_NOTICES.md`. | 6.1, 6.2, 6.3 |
| D11 | PDF-парсинг: текст → OCR (через `anthropic-skills:pdf`) → fallback "уточняющие вопросы пользователю". | Q1 |
| D12 | DESIGN.md обновляем под 9-секционную структуру OpenDesign (color/typo/spacing/layout/components/motion/voice/brand/anti-patterns). | OpenDesign G |

## Lifecycle (как один проект проходит через PR-A)

```
[05 Design System]  ← существующий этап, без изменений (artifact: DESIGN.md, tokens.json)
       │
       ▼
[06 Стек]           ← существующий этап, без изменений
       │
       ▼
[07 Прототип]       ← переименование "Контент". Новый flow:
       │
       ├─ пользователь кладёт prototype.pdf (или .md) в <project>/07_ПРОТОТИП/source/
       │
       ├─ запуск `/landing-prototype` → агент `prototype-importer`:
       │    1. читает source/prototype.{pdf,md}
       │    2. если PDF: extract text → если нет текста → OCR через anthropic-skills:pdf
       │    3. парсит структуру блоков (порядок, заголовки, тексты, CTA)
       │    4. размечает слоты (фото / иконки / инфографика) из контекстных подсказок
       │    5. если что-то не понял — задаёт уточняющие вопросы
       │    6. пишет:
       │         <project>/07_ПРОТОТИП/prototype.md     (человеко-читаемый)
       │         <project>/07_ПРОТОТИП/prototype.yaml   (машинно-читаемый, для ux-composer)
       │
       ├─ HARD GATE: пользователь правит .md если надо (yaml перегенерится автоматически)
       │
       ▼
[08 UX-Wireframe]   ← НОВЫЙ этап. `/landing-wireframe`:
       │
       ├─ агент `ux-composer`:
       │    1. читает prototype.yaml + tokens.json + ui-ux-pro-max/data/landing.csv
       │    2. для каждого блока прототипа подбирает 2-3 кандидата из block-library
       │       (matching по category + use-case + slots)
       │    3. рендерит wireframe.html — desktop+mobile рядом, для каждого блока radio-кнопки
       │       переключения вариантов. CSS-only (no JS).
       │
       ├─ HARD GATE: пользователь тыкает radio-кнопки → "вот эти варианты выбрал"
       │           → нажимает "Confirm" → агент сохраняет выбор в:
       │           <project>/08_WIREFRAME/selections.yaml
       │
       ▼
[09 Block-Compose]  ← НОВЫЙ этап. `/landing-compose`:
       │
       ├─ агент `block-composer`:
       │    1. читает selections.yaml + tokens.json
       │    2. для каждого выбранного варианта блока:
       │       - копирует template.html из block-library
       │       - инжектит CSS-переменные из tokens.json (цвета, шрифты, отступы)
       │       - вставляет реальные тексты/заголовки/CTA из prototype.yaml
       │       - placeholders для фото/иконок/инфографики (visible placeholders с описанием слота)
       │    3. собирает composed.html (полный лендинг, цветной, с плейсхолдерами контента)
       │
       ├─ HARD GATE: пользователь видит "вот так будет с дизайн-системой, без финального визуала"
       │
       ▼
[10 Visual Content per-block]   ← PR-B + PR-C. В PR-A: пустой stub.
       │
       ▼
[Code stage]        ← существующий "08 Код". Перенумерация и перемещение —
                       ответственность PR-D, не PR-A. В рамках PR-A только
                       создаются артефакты composed.html, которые PR-D
                       потом подключит к /landing-build.
       │
       ▼
[deploy, QA, …]     — без изменений
```

**Важно:** PR-A создаёт **новые артефакты, команды, агенты и папки**, но НЕ модифицирует `landing-orchestrator.md`, `config/stage-gates.yaml`, `.landing-state.yaml`. Эта интеграция — задача PR-D. До PR-D новые команды `/landing-prototype`, `/landing-wireframe`, `/landing-compose` вызываются пользователем напрямую вручную, без enforce порядка через orchestrator.

## Architecture

### Слои

| Слой | Что | Где |
|---|---|---|
| **Pattern Engine** | Описательная база паттернов лендингов (правила, не визуалы) | `ui-ux-pro-max/data/landing.csv` (существует, переиспользуем как есть) |
| **Block Library** | Визуальные wireframe-блоки + meta + примеры | `landing-system/block-library/` (новое) |
| **Prototype** | Утверждённый источник правды по содержимому | `<project>/07_ПРОТОТИП/prototype.{pdf,md,yaml}` |
| **Wireframe** | Интерактивный preview с выбором вариантов композиций | `<project>/08_WIREFRAME/wireframe.html + selections.yaml` |
| **Composed** | Цветной макет с tokens + контентом из прототипа, без финального визуала | `<project>/09_COMPOSED/composed.html` |

### Block Library — структура каталога

```
landing-system/block-library/
  README.md                     ← как добавлять новые блоки
  catalog.yaml                  ← индекс всех блоков (id, category, file paths, RU-флаг)
  references/                   ← скриншоты/Pinterest/ссылки, источники вдохновения
  hero/
    ru-hero-01-photo-bg-offer/
      SKILL.md                  ← когда применять, какие slots, конверсионные заметки
      assets/
        template.html           ← desktop wireframe, ч/б
        template-mobile.html    ← mobile wireframe, ч/б
      references/
        examples.md             ← где видели, почему работает
      meta.yaml                 ← see schema below
    ru-hero-02-photo-right-text-left/
    ru-hero-03-text-over-photo/
  features/
    ru-features-01-3col-icons/
    ru-features-02-bento-grid/
  social-proof/
    ru-testimonials-video-circles/
    ru-testimonials-text-photo/
  process/
    ru-how-we-work-4steps-icons/
  pricing/
    ru-pricing-with-rub-from/
  trust/
    ru-trust-guarantees-docs/
  cta/
    ru-cta-callback-tg-max/     ← обратный звонок / Telegram / Max
  quiz/
    ru-quiz-step-card/
    ru-quiz-progress-top/
    ru-quiz-intermediate/
    ru-quiz-lead-form/          ← без WhatsApp, с TG+Max+phone
    ru-quiz-thankyou/
```

### Block `meta.yaml` schema

```yaml
id: ru-hero-01-photo-bg-offer
category: hero
ru_market: true
use_cases: [services, b2c, local]   # одна из 3 ниш или несколько
description: "Hero с фото объекта на фоне + оффер слева + кнопка расчёта"
slots:
  - {type: photo, name: hero-bg, ratio: "16:9", mobile_ratio: "9:16", required: true}
  - {type: text, name: headline, max_chars: 60, required: true}
  - {type: text, name: subhead, max_chars: 120, required: false}
  - {type: cta, name: primary, default_text: "Рассчитать стоимость", required: true}
conversion_notes: |
  Sticky CTA в шапке. Контраст 7:1. Подсказка "от X ₽" в углу плашки.
source: opendesign:saas-landing | manual | pinterest
source_attribution: "Adapted from OpenDesign saas-landing skill (Apache-2.0)"
created: 2026-05-12
```

### Interactive wireframe — как работают переключатели

`wireframe.html` — один файл, открывается в браузере без сервера. Каждая секция прототипа отрендерена как набор скрытых `<div>`-кандидатов + radio-кнопки сверху:

```html
<section class="block-slot" data-block-position="hero">
  <fieldset class="variant-picker">
    <legend>Hero — выбери композицию</legend>
    <input type="radio" name="hero" id="hero-v1" value="ru-hero-01-photo-bg-offer" checked>
    <label for="hero-v1">Фото на фон + оффер слева</label>
    <input type="radio" name="hero" id="hero-v2" value="ru-hero-02-photo-right">
    <label for="hero-v2">Фото справа + текст слева</label>
    <input type="radio" name="hero" id="hero-v3" value="ru-hero-03-text-over">
    <label for="hero-v3">Текст поверх фото</label>
  </fieldset>

  <div class="variants-stage">
    <!-- desktop + mobile рядом для каждого варианта -->
    <div class="variant" data-variant="hero-v1">
      <div class="device desktop">… template.html embedded …</div>
      <div class="device mobile">… template-mobile.html embedded …</div>
    </div>
    <div class="variant" data-variant="hero-v2">…</div>
    <div class="variant" data-variant="hero-v3">…</div>
  </div>
</section>

<style>
  .variant { display: none; }
  #hero-v1:checked ~ .variants-stage [data-variant="hero-v1"] { display: flex; }
  #hero-v2:checked ~ .variants-stage [data-variant="hero-v2"] { display: flex; }
  #hero-v3:checked ~ .variants-stage [data-variant="hero-v3"] { display: flex; }
  /* ... аналогично для каждого блока */
</style>
```

**Сохранение выбора:** в конце страницы кнопка "Confirm selections". Клик читает `document.querySelectorAll('input[type=radio]:checked')` через ~30 строк inline JS, формирует JSON, копирует в clipboard ИЛИ предлагает скачать `selections.yaml`. Пользователь кладёт файл в `<project>/08_WIREFRAME/selections.yaml`, и команда `/landing-compose` его подхватывает.

Compromise: 30 строк inline JS — оправдано тем, что без них пользователю пришлось бы вручную писать YAML. Никаких внешних зависимостей.

### Новые компоненты системы

| Type | Name | Path | Mission |
|---|---|---|---|
| Agent | `prototype-importer` | `agents/prototype-importer.md` | Импорт PDF/MD прототипа → prototype.{md,yaml}. Уточняющие вопросы при неоднозначностях. |
| Agent | `ux-composer` | `agents/ux-composer.md` | Чтение prototype.yaml + tokens.json + block-library/catalog.yaml → подбор 2-3 кандидатов на блок → рендер wireframe.html. Pre-flight injection всего необходимого. |
| Agent | `block-composer` | `agents/block-composer.md` | Чтение selections.yaml + tokens.json + prototype.yaml → рендер composed.html с инжектом токенов и контента. |
| Skill | `prototype-import` | `skills/prototype-import/` | Парсинг PDF/MD. Использует `anthropic-skills:pdf`. Schema validator для prototype.yaml. |
| Skill | `block-library-management` | `skills/block-library-management/` | Скрипты: создать новый блок (scaffold), валидировать meta.yaml, обновить catalog.yaml. |
| Skill | `wireframe-rendering` | `skills/wireframe-rendering/` | Рендер интерактивного wireframe.html с radio-переключателями. |
| Skill | `block-composition` | `skills/block-composition/` | Инжект CSS-переменных из tokens.json в template.html; подстановка текстов из prototype.yaml. |
| Command | `/landing-prototype` | `commands/landing-prototype.md` | Триггер `prototype-importer`. |
| Command | `/landing-wireframe` | `commands/landing-wireframe.md` | Триггер `ux-composer`. |
| Command | `/landing-compose` | `commands/landing-compose.md` | Триггер `block-composer`. |

### Проект-структура (новые папки)

```
<project>/
  07_ПРОТОТИП/
    source/
      prototype.pdf             ← пользовательский исходник
      prototype.md              ← если изначально MD
    prototype.md                ← человеко-читаемая нормализация
    prototype.yaml              ← машинно-читаемая для ux-composer
    import-log.md               ← что агент понял, что переспросил
  08_WIREFRAME/
    wireframe.html              ← интерактивный preview с переключателями
    selections.yaml             ← подтверждённый выбор пользователя
    candidates.yaml             ← все 2-3 кандидата на блок (от ux-composer)
  09_COMPOSED/
    composed.html               ← цветной макет с tokens, плейсхолдеры контента
    composed-mobile.html        ← mobile-версия отдельным файлом для удобства
    block-injection-log.md      ← что куда подставлено
```

## OpenDesign integration — что и куда копируем

**Подключение:** copy-only with attribution (D10). Не git-submodule.

**Целевые папки:**

```
landing-system/
  THIRD_PARTY_NOTICES.md        ← новый, общий attribution файл
  vendor/opendesign-extracts/   ← новая папка с скопированными файлами
    LICENSE                     ← Apache-2.0 копия
    ATTRIBUTION.md              ← список взятого + commit hash
    prompt-templates/           ← 93 промпта (для PR-C, но кладём сейчас)
    design-systems-refs/        ← 72 эталонных DESIGN.md (референсы качества)
    skill-block-template/       ← формат-шаблон для создания новых блоков
    device-frames/              ← iPhone/Pixel/MacBook (для wireframe.html preview)
```

Каждый скопированный файл получает header-комментарий:
```
<!-- Source: github.com/nexu-io/open-design @ <commit-hash> | Licensed: Apache-2.0 -->
```

**Что именно копируем (по решению D10):**

| Letter | Что | Куда у нас | Используется в |
|---|---|---|---|
| A | Формат skill-блока (SKILL.md+assets+meta) | `vendor/opendesign-extracts/skill-block-template/` → шаблон для `block-library/*/` | Каждый блок в library |
| B | 93 prompt-templates | `vendor/opendesign-extracts/prompt-templates/` | PR-C (кладём сейчас, юзаем потом) |
| C | 72 эталонных DESIGN.md | `vendor/opendesign-extracts/design-systems-refs/` | Референсы для `design-system-generator` |
| D | Pre-flight injection паттерн | Применяется в логике `ux-composer` (no files, only pattern) | `ux-composer` mission |
| G | 9-секционная DESIGN.md структура | Применяется в `design-tokens-generation` skill (обновление шаблона) | DESIGN.md format |
| H | `saas-landing` skill как seed для B2C-блоков | Анализируется при создании 4 B2C блоков | seed phase |
| I | `assets/frames/` device-рамки | `vendor/opendesign-extracts/device-frames/` | `wireframe.html` mobile preview обёрнут в iPhone-рамку |
| J | TodoWrite plan streaming паттерн | Применяется в `landing-orchestrator` mission (no files) | Orchestrator UX |
| K | Sandboxed iframe preview | Применяется в `wireframe.html` (iframe sandbox attribute) | wireframe safety |

## Block Library — seed plan (~12 блоков)

| # | Block ID | Category | Use cases | Source |
|---|---|---|---|---|
| 1 | `ru-hero-01-services-calc` | hero | services | manual (RU-spec) |
| 2 | `ru-hero-02-b2c-expert` | hero | b2c | adapted from `opendesign:saas-landing` |
| 3 | `ru-hero-03-local-interior` | hero | local | manual |
| 4 | `ru-features-01-3col-icons` | features | all | `ui-ux-pro-max:landing.csv` pattern #1 |
| 5 | `ru-features-02-bento-grid` | features | all | adapted from OpenDesign |
| 6 | `ru-testimonials-video-circles` | social-proof | all | manual (RU-spec) |
| 7 | `ru-testimonials-text-photo` | social-proof | all | `ui-ux-pro-max:landing.csv` pattern #2 |
| 8 | `ru-how-we-work-4steps` | process | services, local | manual |
| 9 | `ru-pricing-rub-from` | pricing | all | manual (RU-spec "от X ₽") |
| 10 | `ru-trust-guarantees-docs` | trust | services, local | manual (RU-spec — договор/лицензия) |
| 11 | `ru-cta-callback-tg-max` | cta | all | manual (RU-spec, без WhatsApp) |
| 12 | `ru-faq-accordion` | faq | all | adapted from OpenDesign |

**Quiz блоки добавляются отдельной партией (5 шт)** — параллельно с базовыми 12:

| # | Block ID | Notes |
|---|---|---|
| Q1 | `ru-quiz-step-card` | вопрос + варианты + комментарий "зачем спрашиваем" |
| Q2 | `ru-quiz-progress-top` | прогресс-бар "вопрос N из M" |
| Q3 | `ru-quiz-intermediate` | "осталось 2 шага" мотивация |
| Q4 | `ru-quiz-lead-form` | финал: телефон + Telegram + Max, БЕЗ WhatsApp |
| Q5 | `ru-quiz-thankyou` | "свяжемся в TG/Max через 5 минут" |

Каждый блок — desktop + mobile. Итого seed = **17 блоков × 2 (desktop+mobile) = 34 HTML-файла**.

## Artifacts contracts

### `prototype.yaml` schema

```yaml
project:
  slug: example-project
  niche: services    # services | b2c | local
  source_file: prototype.pdf

blocks:
  - position: 1
    type: hero
    headline: "Ремонт квартир под ключ в Москве"
    subhead: "Срок 30 дней, договор, гарантия 3 года"
    cta:
      text: "Рассчитать стоимость"
      action: scroll-to-quiz
    slots:
      - {type: photo, name: hero-bg, hint: "интерьер до/после"}
    mobile_notes: ""

  - position: 2
    type: features
    headline: "Почему мы"
    items:
      - {title: "Договор", text: "Фиксированная смета", icon_slot: "document"}
      - {title: "Гарантия 3 года", text: "...", icon_slot: "shield"}
    mobile_notes: "Свернуть в 1 колонку"
  # ...
```

### `selections.yaml` schema (выход wireframe-этапа)

```yaml
project_slug: example-project
selections:
  - block_position: 1
    chosen_variant: ru-hero-01-services-calc
  - block_position: 2
    chosen_variant: ru-features-02-bento-grid
  # ...
confirmed_at: 2026-05-12T14:23:00Z
```

### `catalog.yaml` schema (индекс библиотеки)

```yaml
version: 1
updated: 2026-05-12
blocks:
  - id: ru-hero-01-services-calc
    path: hero/ru-hero-01-services-calc/
    category: hero
    use_cases: [services]
  # ...
```

## ux-composer — pre-flight injection логика

Перед запуском LLM-вызова агент собирает контекст по строго определённому шаблону. Это решение взято из OpenDesign и решает проблему "галлюцинаций":

```
[INJECTED CONTEXT]
1. prototype.yaml содержимое целиком
2. tokens.json содержимое целиком
3. brand-kit.md содержимое
4. block-library/catalog.yaml — список доступных блоков
5. Для каждого блока прототипа: SKILL.md и meta.yaml кандидатов
   (top-3 по matching score: category + use_case + slot compatibility)
6. ui-ux-pro-max/data/landing.csv — релевантные паттерны для ниши

[TASK]
Для каждого block_position в prototype.yaml выбери 2-3 варианта
из block-library, обоснуй выбор. НЕ ПРИДУМЫВАЙ блоки.
Если ни один блок не подходит — верни {needs_new_block: true, reason: "..."}.

[OUTPUT FORMAT]
candidates.yaml + список файлов для сборки wireframe.html
```

## Dependencies

- **Existing skills used:**
  - `anthropic-skills:pdf` — парсинг PDF прототипа
  - `ui-ux-pro-max` — pattern engine
  - `design-tokens-generation` — обновляется под 9-секционную структуру (D12)
- **External:**
  - OpenDesign (Apache-2.0) — copy-only extraction
- **Internal new:**
  - 3 агента, 4 скилла, 3 команды (см. таблицу выше)

## Risks

| Risk | Mitigation |
|---|---|
| PDF-парсинг ломается на нестандартных макетах | Fallback на уточняющие вопросы пользователю; ручная правка `prototype.md` всегда возможна |
| Block library растёт хаотично без правил | `catalog.yaml` валидируется скриптом перед commit; `block-library/README.md` фиксирует правила |
| ux-composer "придумывает" блоки вопреки pre-flight контракту | Hard rule в mission: `needs_new_block:true` вместо синтеза; failing tests на injection |
| Radio-переключатели в wireframe не работают в старых браузерах | Целевой браузер — современный Chrome/Firefox. Документируем в README блока. |
| Селектор `:checked ~ .stage [data-variant=…]` ломается при перестановке DOM | Стабилизировать DOM через генератор wireframe; tests на структуру |
| Mobile-вариант блока расходится с desktop по смыслу | Жёсткое правило: оба варианта показывают **тот же контент**, отличается только layout. Валидатор в `block-library-management` skill |
| OpenDesign update ломает наши extracts | Pin commit-hash в `vendor/opendesign-extracts/ATTRIBUTION.md`. Обновляем сознательно |

## Acceptance criteria

PR-A считается готовым когда:

1. Существуют 17 seed-блоков в `landing-system/block-library/` (12 базовых + 5 quiz), у каждого desktop + mobile + meta.yaml + SKILL.md.
2. `catalog.yaml` валиден, индексирует все 17 блоков.
3. `prototype-importer` успешно импортирует тестовый PDF и тестовый MD в `prototype.{md,yaml}`.
4. `ux-composer` на тестовом `prototype.yaml` выдаёт `wireframe.html`, где для каждого блока 2-3 варианта переключаются radio-кнопками (проверено вручную в браузере).
5. `block-composer` на тестовом `selections.yaml` выдаёт `composed.html` с правильно инжектированными tokens и текстами.
6. `THIRD_PARTY_NOTICES.md` создан, attribution OpenDesign корректное.
7. Все 4 новых скилла имеют bats-тесты (минимум: парсинг тестового PDF, валидация meta.yaml, рендер wireframe, инжект токенов).
8. `landing-system/CLAUDE.md` обновлён: упомянуты новые команды и этапы 07/08/09.

## Open questions (для финального согласования перед planning)

1. **Hosting wireframe.html — нужен ли локальный сервер?** Если файл двойным кликом открывается из Finder — radio-кнопки работают, но iframe sandbox для preview может ругаться на `file://`. Альтернатива: добавить простой `python -m http.server` хелпер. _Рекомендация: добавить опциональный хелпер_.
2. **PDF-парсинг сложных макетов с колонками.** `anthropic-skills:pdf` хорошо работает с line-based PDF, но многоколоночные могут давать кашу. Будем проверять на реальных прототипах от пользователя. _Mitigation: fallback на вопросы пользователю._
3. **Когда блок надо обновить — версионирование.** Если правим `ru-hero-01-services-calc`, ломаем ли старые проекты? _Рекомендация: блоки в library — иммутабельны. Изменение = новый id (`ru-hero-01-services-calc-v2`)._ Подтвердить?

---

**Next step:** после ревью этого спека → invoke `superpowers:writing-plans` для генерации implementation plan.

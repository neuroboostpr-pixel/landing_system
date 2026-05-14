# PR-B — Photo Pipeline (design spec)

**Date:** 2026-05-13
**Status:** draft (awaiting user review)
**Author:** brainstorming session with project owner (marketer / agency lead)
**Scope:** PR-B из 4-частного апгрейда landing-system. Цели PR-B.1 (paralaximus client-photo), PR-C (icon/infographic), PR-D (orchestrator integration) — описаны как Out of scope.

---

## Problem

После PR-A пользователь имеет `composed.html` с реальными текстами и токенами дизайн-системы, но **на месте фото — плейсхолдеры**: `[photo slot: hero-bg — hint: ...]`. Клиент присылает 30-50 фоток разного качества (телефон, разные пропорции, HEIC от iPhone), и сейчас нет автоматизированного пути:

1. **Привести фотки к единому формату** (HEIC→JPEG, очистка EXIF, дедупликация).
2. **Понять что на каждой фотке** (портрет / процесс / интерьер / команда / документ).
3. **Сопоставить фотки слотам прототипа** (какая фотка идёт в hero, какие 5 в карусель отзывов, какая в команду).
4. **Обработать под нужные пропорции** (16:9 для hero, 1:1 для аватаров, 9:16 для mobile вариантов).
5. **Заполнить слоты для которых клиент не прислал фото** (AI-generative fallback под brand-kit стиль).
6. **Получить preview «фото в макетных местах»** для финального approve.
7. **Подставить обработанные фото в `composed.html`** (заменить placeholders).

## Goals

1. Команда `/landing-photos` запускает полный pipeline обработки клиентских фоток.
2. Все промпты codex параметризованы `tokens.json` + `DESIGN.md` → AI-генерация в едином стиле с сайтом.
3. Identity-safe: клиентские фото никогда не репеинтятся AI; для AI-генерации лиц (testimonial/expert/team) — обязательное per-slot подтверждение пользователем.
4. Stage gate: pipeline запускается только после approved `05_design` и `07a_wireframe`.
5. Идемпотентность: перезапуск продолжает с прерванного этапа.
6. Backward compatible с PR-A: `composed.html` продолжает рисовать placeholders если photo-stage ещё не пройден.

## Non-goals (PR-B specific)

- **Paralaximus client-photo режим** (превращение клиентского фото в 4-слойный параллакс hero) — отдельный PR-B.1.
- **Icon Generator / Infographic Builder** через codex `image_gen` — отдельный PR-C.
- **Интеграция в `landing-orchestrator`** + `config/stage-gates.yaml` + `.landing-state.yaml` — отдельный PR-D.
- Видео-обработка.
- Bulk-upload через web UI (пользователь руками кладёт фото в подпапки `inbox/`).
- Cloud-сторадж (S3, Yandex Object Storage) — всё локально.
- ML depth-estimation (отложено).
- Face detection через OpenCV (codex сам тегирует `face_count`).
- Smart-crop по точкам интереса (`style.py` режет по центру; продвинутые crop'ы — задача дизайнера).

## Decisions log

| # | Решение | Источник |
|---|---|---|
| D1 | Классификация фоток — через `codex exec` с image input, **не** Anthropic SDK напрямую. Manual review поэтапно в HTML галерее. | Q1 → "делать через codex cli обязательно наверное ручное обозначение поэтапно" |
| D2 | Paralaximus client-photo режим (фото клиента в параллакс) **исключён** из PR-B, отложен на PR-B.1. Hero с client photo = статичный crop через `style.py`. | "Нам нужна только обработка фотки на данном этапе. Пролакс потом будем докручивать" |
| D3 | Generative fallback через `codex image_gen` для **всех** missing photo-слотов, без allowlist. | Q3 → "Generative fallback через codex image_gen" |
| D4 | UX галереи — split-view drag-drop с pre-filled selections от AI-matcher. Не wizard, не обратный modal. | Q4 → "главное оптимальный путь, codex предлагает расстановку, я докручиваю" |
| D5 | Промпты codex параметризованы `tokens.json` + `DESIGN.md` → единый стиль с сайтом. | Q2 → "под дизайн систему которая будет разработана чтобы было всё в одном стиле" |
| D6 | Порядок этапов: `05 design approved` → `07 prototype` → `07a wireframe approved` → **`07c photos (PR-B)`** → `07b composed re-render`. Гейт: design AND wireframe утверждены. | "прототип → дизайн системы → обработка под эту дизайн систему" |
| D7 | Все 3 codex template-файла повторяют структуру `paralaximus-codex/templates/atlas-prompt.md` (How to use → Placeholders → Prompt body → Filled example). Все shell-обёртки копируют `generate-atlas.sh` (snapshot `~/.codex/generated_images/`, exec, copy fresh PNG). | "Бери paralaximus за основу, он уже работает и протестирован" |
| D8 | Identity-safe правила в едином `skills/photo-curation/IDENTITY_SAFE.md`; на него ссылаются все агенты PR-B и `photo-stylist`. | Architecture review |
| D9 | Локация артефактов — `07c_PHOTOS/` рядом с `07a_WIREFRAME/`, `07b_COMPOSED/`. НЕ `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/`. | Architecture review |
| D10 | `inbox/` имеет **7 предсозданных под-папок с русскими именами** (`портреты_и_команда/`, `процесс_работы/`, ...) + `_свалка/`. Файлы в подпапке получают folder-tag без вызова codex. | "материалы в чат или папки, ты указываешь куда что" |
| D11 | Переиспользуем 5 паттернов из nexu-io/open-design (Apache-2.0): `image-manifest.json` slot schema, three-strategy enum (`generate|placeholder|bring-your-own`), `placeholder.ts` (SVG-as-PNG), DESIGN.md anti-patterns list для генерации, `imagegen.ts` skip-if-exists + --force pattern. | open-design audit |
| D12 | `selections.yaml` имеет поле `strategy: generate|placeholder|bring-your-own` для каждого слота (формат из open-design). | D11 |
| D13 | Логирование всех codex-вызовов в `07c_PHOTOS/.logs/` с полным prompt+response для аудита. | Architecture review |

---

## Architecture

### Поток данных (как PR-B встаёт между PR-A и кодом)

```
[00 brief] → [01 niche] → [02 client materials/photos/inbox] → [03 references]
→ [04 brand-kit] → [05 design-system ✅ approved] → [06 stack]
→ [07 prototype.yaml] → [07a wireframe ✅ approved (variants chosen)]
→ [07c_PHOTOS (PR-B)] ←─── HERE
    │
    ▼
[07b_COMPOSED/composed.html re-rendered с реальными фото]
    │
    ▼
[08 code → 09 deploy → ...]
```

PR-B не модифицирует stages 00-07a и 08+. Только новые артефакты в `07c_PHOTOS/` + расширение `compose-blocks.py` (PR-A) для подстановки фоток.

### Компоненты

#### Новые агенты (4 в `agents/`)

| Агент | Триггер | Что делает | Выход |
|---|---|---|---|
| `photo-curator` | `/landing-photos` | Оркестратор PR-B. Intake (HEIC→JPEG sips, EXIF strip, hash dedupe, folder-tag detection). Запускает остальных 3. Рендерит HTML галерею. Ждёт user approve. Управляет `STATE.yaml` | `07c_PHOTOS/photo-board.html`, `STATE.yaml` |
| `photo-classifier` | от curator | Batch tagging через codex CLI с image input для файлов в `_свалка/` (под-папки уже имеют folder-tag). Chunks по 5 фоток для rate-limit. ⚠️ См. Known risks ниже про точный механизм image input | `07c_PHOTOS/catalog.yaml` |
| `photo-matcher` | от curator | Codex читает `catalog.yaml` + `prototype.yaml` slots + `wireframe selections.yaml` + `tokens.json` + `01a/positioning.md`. Рекомендует top-3 фотки на каждый слот. Mark `ai_fallback_needed` | `07c_PHOTOS/selections.draft.yaml` |
| `photo-preview-board` | от curator после selections.yaml утверждён | Запускает `style.py` per slot (crop/resize под ratio+mobile_ratio из meta.yaml) + codex `image_gen` для AI fallback. Собирает `photo-preview.html` «фото в макетных местах» используя block templates | `07c_PHOTOS/processed/`, `photo-preview.html` |

#### Новый skill (1)

```
skills/photo-curation/
├── SKILL.md
├── IDENTITY_SAFE.md                  ← единый источник правил
├── templates/
│   ├── classify-prompt.md            ← в стиле atlas-prompt.md
│   ├── match-prompt.md
│   └── generate-fallback.md
└── scripts/
    ├── intake.py                     ← HEIC→JPEG, EXIF strip, dedupe, folder-tag detect
    ├── render-prompt.py              ← placeholder substitution из tokens.json + context
    ├── codex-classify.sh             ← обёртка в стиле generate-atlas.sh, image input
    ├── codex-match.sh                ← обёртка text-only
    ├── codex-generate-fallback.sh    ← клон generate-atlas.sh
    ├── gallery-render.py             ← рендерит photo-board.html
    ├── preview-render.py             ← рендерит photo-preview.html
    └── selections-validator.py       ← валидирует selections.yaml schema
```

#### Расширения существующих

- `skills/photo-styling/scripts/style.py` — добавить `--target-ratio` и `--target-ratio-mobile` режимы. Обрезка по центру (smart-crop отложен), resize под максимальную сторону 1920px для desktop / 1080px для mobile. Сохранение JPEG quality 85.
- `scripts/compose-blocks.py` (PR-A) — добавить опциональное чтение `07c_PHOTOS/selections.yaml` + `processed/`. Если файлы есть — подставлять в `data-slot type=photo` вместо placeholder. Если нет — fallback к текущему placeholder поведению.
- `THIRD_PARTY_NOTICES.md` — обновить атрибуцию nexu-io/open-design (image-manifest schema, placeholder pattern, anti-patterns).

#### Новая команда (1)

`commands/landing-photos.md` (в существующей папке `commands/`, рядом с другими `landing-*.md`) — слэш-команда:
- Проверяет stage gates (`05_design` approved, `07a_wireframe` approved). Exit 1 с понятным русским сообщением если не пройдены.
- Вызывает `photo-curator` агент.
- Поддерживает флаги:
  - `--force-stage <name>` (intake|classify|match|preview) — принудительный сброс конкретного этапа
  - `--all-ai` — пропустить inbox-сканирование, на все слоты — generative fallback (требует отдельного подтверждения)

### Дерево артефактов (`07c_PHOTOS/`)

```
07c_PHOTOS/
├── README.md                              ← инструкция для клиента/маркетолога на русском
├── inbox/
│   ├── _свалка/                           ← если не знаешь куда — сюда, AI разберётся
│   ├── портреты_и_команда/
│   │   └── README.md                      ← подсказка «портреты в 1:1 или 3:4, светлый фон»
│   ├── процесс_работы/
│   │   └── README.md
│   ├── объекты_и_продукты/
│   │   └── README.md
│   ├── интерьер_экстерьер/
│   │   └── README.md
│   ├── до_после/
│   │   └── README.md
│   └── документы_сертификаты/
│       └── README.md
├── intake/                                 ← после intake.py
│   ├── photo_001.jpg                       (HEIC→JPEG, EXIF stripped, hash-named)
│   ├── photo_001.thumb.jpg                 (256px для галереи)
│   └── intake-report.yaml                  (исходные имена → новые, дубликаты, folder-tag)
├── catalog.yaml                           ← photo-classifier output
├── selections.draft.yaml                  ← photo-matcher output (AI ranking)
├── selections.yaml                        ← после approve в photo-board.html
├── processed/                             ← photo-preview-board output
│   ├── hero-bg/
│   │   ├── desktop.jpg                    (16:9)
│   │   └── mobile.jpg                     (9:16)
│   ├── testimonial-1-avatar/
│   │   ├── ai-generated.jpg
│   │   └── ai-prompt.txt
│   └── ...
├── photo-board.html                       ← split-view drag-drop UI
├── photo-preview.html                     ← «фото в местах» для approve
├── STATE.yaml                             ← статусы этапов (intake/classify/match/preview/approved)
└── .logs/                                 ← все codex prompt+response для аудита
```

### Жизненный цикл selections (draft → canonical)

1. `photo-matcher` пишет `selections.draft.yaml`. В draft каждый слот имеет дополнительное поле `required_user_approval: bool` (для identity-safe слотов = true если требуется AI fallback).
2. Пользователь открывает `photo-board.html`, видит pre-filled выбор. Для слотов с `required_user_approval: true` — отдельный modal «Согласен на AI face?» с обязательной галочкой.
3. После Confirm → `selections.yaml` (canonical) **без** поля `required_user_approval` — оно заменяется на `ai_approved_by_user: bool` (что пользователь решил по факту).

### Структура `selections.yaml` (canonical, после user approve)

```yaml
strategy_default: bring-your-own         # из open-design enum
slots:
  - slot_id: hero-bg
    block_id: ru-hero-01-services-calc
    ratio: "16:9"
    mobile_ratio: "9:16"
    strategy: bring-your-own
    chosen_photo_id: photo_017
    processed:
      desktop: processed/hero-bg/desktop.jpg
      mobile: processed/hero-bg/mobile.jpg
    ai_approved_by_user: false           # n/a для bring-your-own
    log_ref: null
  - slot_id: testimonial-1-avatar
    block_id: ru-testimonials-text-photo
    ratio: "1:1"
    strategy: generate
    chosen_photo_id: null
    processed:
      desktop: processed/testimonial-1-avatar/ai-generated.jpg
      mobile: null
    ai_approved_by_user: true            # ✅ для identity-safe слотов
    ai_prompt: "Portrait of satisfied client, soft studio lighting, brand color #c47a3a..."
    log_ref: .logs/2026-05-13_154212_generate.log
  - slot_id: process-step-3-photo
    block_id: ru-process-4steps-icons
    ratio: "4:3"
    strategy: placeholder                # SVG-placeholder из open-design pattern
    chosen_photo_id: null
    processed:
      desktop: processed/process-step-3-photo/placeholder.png
      mobile: null
    ai_approved_by_user: false
    log_ref: null
```

### Структура `catalog.yaml`

```yaml
photos:
  - id: photo_001
    path: intake/photo_001.jpg
    original_name: IMG_3284.heic
    hash: a3f2c1...
    duplicates: [IMG_3285.heic]                    # того же hash
    dimensions: [3024, 4032]
    ratio: "3:4"
    folder_origin: портреты_и_команда              # null если из _свалка
    tag_source: folder                             # folder | ai_classify
    tags: [portrait, expert]
    caption: "Мужчина 40 лет, деловая одежда, на фоне здания"
    face_count: 1
    composition: medium-shot
    usable_ratios: ["1:1", "3:4", "9:16"]
    brand_compatible: yes
    notes: ""
```

### Структура `STATE.yaml`

```yaml
project: my-landing
started: 2026-05-13T15:42:00+03:00
stages:
  intake:    {status: done,        finished: 2026-05-13T15:43:10, photos_in: 47, photos_out: 42, duplicates_removed: 5}
  classify:  {status: done,        finished: 2026-05-13T15:51:33, ai_classified: 18, folder_tagged: 24, errors: 0}
  match:     {status: done,        finished: 2026-05-13T15:54:11, slots_matched: 22, slots_ai_fallback: 4}
  approval:  {status: in_progress, started: 2026-05-13T15:55:00}
  process:   {status: pending}
warnings: []
errors: []
```

---

## Codex template-шаблоны (3 файла)

Все три повторяют структуру `paralaximus-codex/templates/atlas-prompt.md`: секции "How to use → Placeholders → Prompt body → Filled example".

### Общие placeholders (из `tokens.json` + `DESIGN.md` + niche analysis)

```
[VISUAL_STYLE]      — tokens.json:design.visual_style
[BRAND_PRIMARY]     — tokens.json:colors.primary
[BRAND_ACCENT]      — tokens.json:colors.accent
[BRAND_MOOD]        — DESIGN.md:mood line
[LIGHTING]          — derived из [BRAND_MOOD]
[COLOR_GRADING]     — собрано из primary + accent + DESIGN.md
[NICHE]             — 01a_АНАЛИЗ_НИШИ/market-profile.md:niche
[AUDIENCE]          — 01a_АНАЛИЗ_НИШИ/positioning.md:audience
[SLOT_HINT]         — meta.yaml:slots[].name + photo_hint
[RATIO]             — meta.yaml:slots[].ratio
```

`render-prompt.py` единая точка подстановки. TDD-tested через pytest.

### 3.1 `classify-prompt.md`

Codex принимает одну фотку → возвращает YAML.

```
ВОЗВРАЩАЙ СТРОГО YAML, БЕЗ КОММЕНТАРИЕВ ДО И ПОСЛЕ.

Ты анализируешь фотографию для лендинга в нише [NICHE], целевая аудитория [AUDIENCE].
Brand style: [VISUAL_STYLE], primary color [BRAND_PRIMARY].

Верни строго YAML:
tags: [список из portrait, group, object, process, interior, exterior, before-after, document, team, abstract]
caption: одна строка на русском, до 100 символов
face_count: число
composition: tight-portrait | medium-shot | wide-shot | object-only
usable_ratios: список из 1:1, 4:3, 3:4, 16:9, 9:16 — где фото обрежется без потери сюжета
brand_compatible: yes | no | maybe
notes: технические дефекты (размытие, шум, плохой свет) или пусто
```

### 3.2 `match-prompt.md`

Codex принимает каталог + слоты → возвращает YAML ranking.

```
Тебе дан каталог фотографий клиента и список слотов из прототипа лендинга.
Подбери top-3 фото на каждый слот.

Каталог:
[CATALOG_YAML]

Слоты:
[SLOTS_YAML]

Brand context:
- primary: [BRAND_PRIMARY]
- visual_style: [VISUAL_STYLE]
- niche: [NICHE]
- audience: [AUDIENCE]

Правила matching:
- ratio фото (после crop) должно совпадать или близко к slot.ratio
- tag фото должен соответствовать hint слота
- testimonial-* / expert-* / team-* слоты требуют tag=portrait или group, face_count>=1
- hero-bg требует composition=wide-shot, usable_ratios содержит 16:9
- если ни одна фотка не подходит — candidates=[] и ai_fallback_needed=true
- если ai_fallback_needed — собери ai_prompt под design-system и slot.hint
- для безопасных слотов (background, process, abstract, interior) AI-fallback по умолчанию ok
- для identity-safe слотов (testimonial/expert/team) AI-fallback нужен только если явно нет фотки — required_user_approval: true

Верни YAML:
slots:
  - slot_id: ...
    candidates: [{photo_id, score 0-1, reason}, ...]
    ai_fallback_needed: bool
    required_user_approval: bool
    ai_prompt: "..." (если fallback нужен)
```

### 3.3 `generate-fallback.md`

Codex генерирует одно фото через `image_gen` под brand.

```
Use the built-in image_gen tool. Generate ONE PNG, size [WIDTH]x[HEIGHT] (ratio [RATIO]),
for slot [SLOT_HINT] on a landing page in [NICHE] niche for audience [AUDIENCE].

This is a personal local prototype. Save the result.

No text, no letters, no logos, no watermarks anywhere in the image.

VISUAL STYLE: [VISUAL_STYLE]
LIGHTING: [LIGHTING]
COLOR GRADING: [COLOR_GRADING]
BRAND MOOD: [BRAND_MOOD]

[FORBIDDEN list — adapted from nexu-io/open-design DESIGN.md anti-patterns:]
- No lens flare
- No glitch effects, no chromatic aberration
- No photoreal human faces (UNLESS this is a portrait slot AND user has explicitly approved AI face generation — see IDENTITY_SAFE rules)
- No AI watermarks (no "AI", no "Midjourney", no "DALL-E" visual signatures)
- No cartoonish/anime style unless brand mood demands it
- No surreal melting / flowing artifacts
- Photoreal premium editorial / commercial digital art quality
```

---

## Identity-safe правила (`IDENTITY_SAFE.md`)

```markdown
# Identity-safe rules for PR-B

## Absolute forbiddens
- NEVER alter the face, age, body proportions, or skin of a real client photo.
- NEVER AI-repaint a person.
- NEVER swap a face.
- NEVER apply beauty retouching.

## AI fallback for portrait slots (testimonial/expert/team)
- Default behavior: AI fallback is BLOCKED unless `selections.yaml:ai_approved_by_user == true` for that slot.
- The photo-board UI presents an explicit modal: "Этот слот требует AI-сгенерированного лица человека. Согласен на использование AI? (Это будет видно посетителям сайта как настоящий человек)". User must check the box.
- Without approval: slot processed as `strategy: placeholder` (SVG placeholder).

## Future PR-B.1 (paralaximus client-photo)
- Subject layer = client cutout PNG, composited byte-for-byte. No AI modification.
- Background/far/near layers = AI-generated (only environment around subject).
- If AI-generated background implicitly contains a person — regenerate without person.
```

---

## Error handling и edge cases

(полная матрица из Section 4 brainstorming — переносится один-к-одному)

| Сценарий | Поведение |
|---|---|
| `05_design` не approved | Exit 1: «Сначала утверди дизайн-систему — без tokens.json промпты codex не могут попасть в стиль» |
| `07a_wireframe` не approved | Exit 1: «Сначала выбери варианты блоков в wireframe.html» |
| `inbox/` пустой | Exit 0 warning: «Нет фоток. `--all-ai` для полного AI fallback (доп. подтверждение)» |
| HEIC без `sips` (не macOS) | Skip с warning, требует ручной конверт |
| `codex` не залогинен | Exit 2 (как в paralaximus) |
| `codex exec` silent fail | retry 1×, после — exit 3, инструкция «проверь `ls -t ~/.codex/generated_images/`» |
| classify YAML invalid | retry с уточнённым промптом 2×, после — tag=`unclassified`, warning |
| matcher не нашёл кандидатов | `ai_fallback_needed: true` |
| Identity-safe слот без фото и без approval | placeholder.svg в processed/, плашка «требуется фото клиента» |
| Generative fallback failed | retry 1×, после — placeholder + `STATE.yaml:errors[]` |
| Перезапуск посреди процесса | Читает `STATE.yaml`, продолжает |
| Новые фото дозагружены в inbox/ после classify | Detect по hash, classify только новые |
| wireframe selections изменились | Инвалидация `selections.draft.yaml`, прогон matcher заново |
| Дубликаты | Один canonical, остальные в `duplicates: [...]` |
| Очень большая фотка >20MB | resize до max 4096px по длинной стороне |
| `inbox/` структура повреждена (нет под-папок) | Авто-восстановление под-папок из template |
| AI testimonial без approval | composed.html re-render оставляет placeholder, preview html явная плашка |

**Логирование:** все codex-вызовы → `07c_PHOTOS/.logs/YYYY-MM-DD_HHMMSS_<stage>.log` (prompt + response). В `selections.yaml:log_ref` для AI-слотов.

**Soft vs hard errors:** только пустой inbox и unapproved gates — hard exit. Всё остальное — soft warnings в `STATE.yaml`.

---

## Testing strategy

TDD per CLAUDE.md: сначала падающий тест, потом код.

| Что | Чем | Сценарий |
|---|---|---|
| `intake.py` HEIC/EXIF/dedupe/folder-tag | pytest | папка с 3 фотками (1 HEIC, 1 дубликат, 1 с GPS), folder-tag из подпапки → 2 JPEG без GPS, правильные теги |
| `render-prompt.py` подстановка | pytest | `[BRAND_PRIMARY]` + context → готовый промпт без скобок |
| `gallery-render.py` | pytest | catalog.yaml + selections.draft → HTML с data-attributes для drag-drop |
| `style.py --target-ratio` | pytest | 3000×2000 → 16:9 → 3000×1687 без искажений |
| Stage gate проверки | bats | fake `.landing-state.yaml` с разными статусами → правильный exit code |
| `compose-blocks.py` подстановка фоток | pytest | fake selections.yaml + processed/ → composed.html с `<img src>` |
| `selections-validator.py` | pytest | invalid strategy enum / missing ai_approved_by_user → schema error |
| End-to-end pipeline | bats (`scripts/test-pipeline.sh` расширенный) | тестовый проект + тестовые фотки → весь цикл проходит |

**Mock codex:** `tests/fixtures/codex-mock.sh` отдаёт зафиксированные ответы, подмена через env `CODEX_BIN`.

**Не тестируем:** subjective quality (AI gen качество, accuracy matcher ranking, accuracy AI tags — variable, smoke-test «не пусто» достаточно).

**Объём:** ~25-30 новых тестов. Прогон ~10 секунд без сети.

---

## Acceptance criteria

- [ ] `bash scripts/test-pipeline.sh` проходит включая photo-stage
- [ ] `/landing-photos` в живом проекте даёт `composed.html` с реальными фото
- [ ] `photo-board.html` корректно показывает слоты с pre-filled candidates, drag-drop работает в Chrome/Safari
- [ ] 25-30 unit-тестов проходят
- [ ] `STATE.yaml` фиксирует каждый этап, перезапуск продолжает с прерванного
- [ ] Идемпотентность: 2 запуска подряд = одна работа
- [ ] Identity-safe гейт работает: testimonial слот без `ai_approved_by_user` → placeholder, не AI
- [ ] `THIRD_PARTY_NOTICES.md` обновлён с атрибуцией open-design
- [ ] `07c_PHOTOS/README.md` написан на русском с понятной инструкцией для маркетолога
- [ ] Backward compatibility: проект без `07c_PHOTOS/selections.yaml` продолжает работать (placeholders в composed.html)

---

## Dependencies

- `codex` CLI v0.125+ (уже используется paralaximus)
- `sips` (macOS built-in, для HEIC→JPEG)
- Python 3.10+ с `Pillow`, `PyYAML`, `pytest`
- `rembg` опционально (если есть — используем для cutout, иначе Pillow alpha-mask)
- `bats` для shell-тестов (уже в проекте)

НЕТ зависимости от:
- Anthropic SDK напрямую (всё через codex CLI)
- ML-моделей (depth-estimation, OpenCV face detection)
- Cloud сервисов

---

## Migration / backward compatibility

- PR-A артефакты (`07a_WIREFRAME/`, `07b_COMPOSED/`, `prototype.yaml`) — без изменений.
- `compose-blocks.py` расширяется, не переписывается: если `07c_PHOTOS/selections.yaml` не существует — старое placeholder поведение.
- `block-library/` метаданные блоков — без изменений (slots[].ratio уже есть в meta.yaml).
- Существующий `agents/photo-stylist.md` остаётся (стадия 02 raw photo intake в `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/`), новый `photo-curator` работает поверх него на стадии 07c (`07c_PHOTOS/inbox/`).
- **Dual-path intake**: `photo-curator` при запуске сканирует **оба** места — `02_МАТЕРИАЛЫ_КЛИЕНТА/photos/original/` (старый путь) и `07c_PHOTOS/inbox/` (новый). Фотки из старого пути копируются в `07c_PHOTOS/inbox/_свалка/` (или соответствующую под-папку если можно вывести из имени файла). Это позволяет плавную миграцию — старые проекты с фотками в `02_` не сломаются.
- Существующий `skills/photo-styling/` расширяется флагом `--target-ratio`, текущий API сохраняется.

---

## Attribution

Обновить `THIRD_PARTY_NOTICES.md`:

```
## nexu-io/open-design (Apache-2.0)

In PR-B Photo Pipeline (2026-05-13), the following patterns were ported from
nexu-io/open-design (https://github.com/nexu-io/open-design):

- `selections.yaml` schema's `strategy: generate|placeholder|bring-your-own` enum
  (from design-templates/open-design-landing/schema.ts:413)
- `image-manifest.json`-style slot description fields (id, file, width, height,
  ratio, required, rekey_on_brand_change) — adapted to `selections.yaml` shape
- `placeholder.ts` SVG-rendered-as-PNG technique — re-implemented in
  scripts/preview-render.py for placeholder fallback
- AI-imagery anti-patterns list (no lens flare / glitch / AI faces / watermarks)
  — incorporated verbatim into skills/photo-curation/templates/generate-fallback.md
- `imagegen.ts` skip-if-exists + --force pattern — applied to STATE.yaml
  stage tracking

License: Apache-2.0. Full text at:
https://github.com/nexu-io/open-design/blob/main/LICENSE
```

---

## Known risks

### R1 — Codex CLI image input mechanism (HIGH)

`paralaximus-codex` использует codex только для **генерации** изображений через built-in `image_gen` tool. Для классификации (PR-B) нам нужен обратный путь — **отдать фотку codex'у на анализ**. Точный синтаксис codex CLI для image input не подтверждён на момент написания spec.

**Mitigation plan** (research → fallback chain):

1. **Research-первая задача в implementation plan:** проверить codex CLI v0.125+ docs / `codex exec --help` на флаги `--image`, `--attach`, `--read-files`, или возможность передать `file://path/to/image.jpg` в prompt.
2. Если codex CLI поддерживает image input нативно → используем как первый вариант (single dependency).
3. Если codex CLI не поддерживает или поддерживает плохо → fallback A: дать codex'у промпт с filesystem instructions «прочитай файл X через свой read tool и опиши». Codex имеет read access по умолчанию.
4. Если fallback A не работает → fallback B: для classifier-агента (только!) использовать Anthropic SDK напрямую с `messages.create` + image base64 content blocks + prompt caching. Это **единственное исключение** из D1 «всё через codex CLI», ограниченное только классификатором. Документируется в SKILL.md.

**Решение о fallback принимается на спайке в начале implementation** (1-2 часа research перед основным кодом).

### R2 — codex exec rate limits на batch operations

`generate-atlas.sh` пока вызывался по 1 разу за хеллоу. PR-B вызывает codex до 50+ раз подряд (по 5 фоток × N батчей для classify + N слотов для match/generate). Возможны rate-limits.

**Mitigation:** chunk by 5 photos для classifier, sleep 2s между batches; для generative fallback — последовательно, не параллельно; expone-backoff в `call-codex.sh` обёртке.

### R3 — HEIC формат на не-macOS

`sips` есть только на macOS. Linux/WSL пользователи получат warning и должны вручную конвертить HEIC.

**Mitigation:** документация в `07c_PHOTOS/inbox/README.md` + опциональная зависимость `pillow-heif` (если установлен — используем; иначе skip+warn).

### R4 — codex sandbox refuses to write into project

Уже знакомая проблема из paralaximus (codex генерит в `~/.codex/generated_images/`, не может скопировать в проект из-за своей же sandbox-политики).

**Mitigation:** копируем `generate-atlas.sh` snapshot+comm паттерн в все 3 codex-обёртки PR-B. Уже решено архитектурно.

---

## Open questions / future PRs

- **PR-B.1** (paralaximus client-photo): расширить `generate-atlas.sh --mode client-photo`. Subject = client cutout, BG/far/near = codex `image_gen` под brand. Atlas-prompt-client-photo.md шаблон. Identity-safe: BG не должен содержать людей если subject = портрет.
- **PR-C** (icon / infographic generator): отдельные codex шаблоны для иконок (line / filled / duotone) и инфографики под brand. SVG output preferred.
- **PR-D** (orchestrator integration): добавить stage `07c_photos` в `config/stage-gates.yaml`. Wire через `landing-orchestrator.md` так чтобы `/landing-photos` запускался автоматически после approved `07a_wireframe`. Добавить hard+soft checks.
- **Smart-crop по точкам интереса**: использовать saliency detection (Pillow + simple heuristic) для cropping не по центру, а по «интересной» части кадра. Сейчас по центру.
- **Bulk upload через web UI**: пользователь открывает локальный URL, drag-dropит фото из браузера. Альтернатива копированию в `inbox/`.

# PR-C — Visual Generation (Icons + Infographics)

**Date:** 2026-05-13
**Status:** draft (awaiting user review)
**Scope:** PR-C из 4-частного апгрейда landing-system. Простая задача: визуальные элементы под design-system и нишу. Никакого overengineering.

---

## Problem

После PR-A + PR-B пользователь имеет `composed.html` с реальными текстами, дизайн-токенами и фотографиями. Но на месте **иконок и инфографики** — placeholder `[SLOT: feature-N-icon]`. В block-library уже есть 5 блоков с `type: icon` слотами (14 слотов суммарно — `features`, `process`, `trust`). Слотов `type: infographic` пока нет — PR-C добавит инфраструктуру и пару образцовых блоков.

Без PR-C — лендинг выходит «без иконок», что обедняет визуал и снижает конверсию.

## Goals

1. Команда `/landing-visuals` сканирует `composed.html` (PR-A) на `data-slot type="icon"` и `data-slot type="infographic"`, генерит PNG через codex `image_gen`, подставляет в HTML.
2. Промпты codex параметризованы `tokens.json` (colors.accent, design.icon_style) + niche analysis → визуалы в едином стиле с сайтом.
3. Переиспользуем 90 OpenDesign image-prompts (CC-BY-4.0) + icons.csv (100 типов) + charts.csv (25 типов диаграмм).
4. Stage gate: pipeline запускается только после approved `05_design` И существующего `07b_COMPOSED/composed.html`.
5. Идемпотентность: кэш по hash(hint + style + brand_color); skip-if-exists (паттерн open-design `imagegen.ts`).
6. Backward compatible с PR-A/PR-B: composed.html продолжает рисовать placeholders если PR-C не запущен.
7. PR-C добавляет 2-3 примерных блока с `type: infographic` слотами в block-library.

## Non-goals (PR-C specific)

- **SVG output** — отложен на PR-C.1. PNG transparent достаточно для MVP.
- **Editable infographics** (числа меняются в браузере) — будущее. Сейчас инфографика это статичный PNG.
- **Fallback на Iconify/Lucide для простых иконок** — добавляет сложность, отложено.
- **Интеграция в `landing-orchestrator`** — PR-D.
- **Видео-генерация** через seedance — не входит, хотя 114 video-prompts в vendor уже есть.

## Decisions log

| # | Решение | Источник |
|---|---|---|
| D1 | PNG transparent (через chroma-key, как paralaximus) — единственный output format в PR-C. SVG отложен. | Pre-decided + speed |
| D2 | Стиль иконок по умолчанию: **outlined**. Override через `tokens.json:design.icon_style` ∈ {outlined, filled, duotone, 3d}. | Universal default |
| D3 | Только gpt-image-2 через codex CLI. Никаких Iconify/Material fallback (KISS). | Consistency с PR-B |
| D4 | Цвет иконок из `tokens.json:colors.accent`. Override через `meta.yaml:slots[].icon_color` (rare). | Design-system единство |
| D5 | Промпт-источники приоритет: (1) OpenDesign 90 JSON, (2) icons.csv keyword match, (3) generic template если ничего не нашли. | User intro doc |
| D6 | Кэш по `hash(hint + style + brand_color)` в `07d_VISUALS/.cache/`. Skip-if-exists. `FORCE=1` обходит. | open-design imagegen.ts pattern |
| D7 | Локация: `07d_VISUALS/` (PR-B занял `07c_PHOTOS/`, держим 07a/07b/07c/07d последовательно). | Consistency |
| D8 | Одна команда `/landing-visuals` для обоих типов (icons + infographics). Флаг `--type icons\|infographics` для частичного прогона. | Simpler UX |
| D9 | Identity-safe правила НЕ применяются (нет людей в иконках/чартах). | Scope |
| D10 | infographic slot имеет дополнительные поля: `chart_type` (из charts.csv), `data` (опционально, числа+метки). Если данных нет — используем плейсхолдерные. | Practical default |
| D11 | PR-C размечает 2 примерных блока с `type: infographic`: один в `features/` (KPI-метрики) и один в `social-proof/` (рост за N лет). | Showcase infrastructure |
| D12 | Stage gate: `05_design.approved == true` AND `07b_COMPOSED/composed.html` exists. PR-B (`07c_PHOTOS/`) НЕ требуется — PR-C независим от PR-B. | Modularity |

---

## Architecture

### Где PR-C встаёт в pipeline

```
[00-04] → [05 design ✅] → [06 stack] → [07 prototype] → [07a wireframe]
       → [07b composed] → [07c photos (PR-B, опционально)]
       → [07d_VISUALS (PR-C)] ←─── HERE
            │
            ▼
       [07b composed re-render с подставленными иконками + инфографикой]
            │
            ▼
       [08 code → ...]
```

PR-C не модифицирует stages 00-07c и 08+. Артефакты в `07d_VISUALS/` + расширение `inject-content.py` для подстановки PNG.

### Компоненты

**Новые агенты (2 в `agents/`):**

| Агент | Триггер | Что делает | Выход |
|---|---|---|---|
| `icon-generator` | от visual-curator | Для каждого `data-slot type="icon"` в composed.html: читает hint, выбирает промпт-шаблон (OpenDesign / icons.csv / generic), вызывает codex `image_gen`, chroma-key remove, сохраняет PNG | `07d_VISUALS/icons/<slot-name>.png` |
| `infographic-builder` | от visual-curator | То же для `type="infographic"` слотов. Использует charts.csv для chart-type определения. | `07d_VISUALS/infographics/<slot-name>.png` |

**Новый агент-оркестратор:** `visual-curator` — управляет workflow обоих (как `photo-curator` в PR-B). Lightweight: scan slots → dispatch sub-agents → handle STATE.yaml → final inject. Держим отдельным для DRY (как PR-B 4-agent pattern).

**Новый skill (1):**

```
skills/visual-generation/
├── SKILL.md
├── templates/
│   ├── icon-prompt.md                ← стиль atlas-prompt.md
│   └── infographic-prompt.md
├── data/
│   └── opendesign-index.yaml         ← индекс 90 JSON-промптов по тегам (build-time)
└── scripts/
    ├── slot-scanner.py               ← парсит composed.html, выдаёт список визуальных слотов
    ├── prompt-picker.py              ← выбирает шаблон под hint
    ├── codex-generate-icon.sh        ← клон codex-generate-fallback.sh из PR-B
    ├── codex-generate-infographic.sh ← клон с другим шаблоном
    └── visual-cache.py               ← hash-based кэш
```

**Расширения существующих:**

- `skills/block-composition/scripts/inject-content.py` (PR-A/PR-B) — добавить ветку `type: icon` и `type: infographic`: если `07d_VISUALS/<type>s/<slot-name>.png` существует → подставить `<img>`. Иначе — placeholder как сейчас.
- `skills/photo-curation/scripts/selections-validator.py` (PR-B) — НЕ трогаем. Визуалы не идут через selections.yaml.
- `THIRD_PARTY_NOTICES.md` — обновить (OpenDesign 90 image-prompts CC-BY-4.0 — отдельные per-prompt лицензии).

**Новая команда (1):**

`commands/landing-visuals.md` — слэш-команда. Флаги:
- `--type <icons|infographics>` — прогон только одного типа
- `--force` — игнорировать кэш, перегенерить всё
- `--slot <name>` — только один конкретный слот

**Block-library дополнения (2-3 блока):**

PR-C добавляет в `block-library/`:
1. `features/ru-features-XX-kpi-metrics/` — блок с 3-4 `type: infographic` слотами (метрики 87%, 12 лет, 1000+ клиентов с иконкой+числом)
2. `social-proof/ru-stats-growth-chart/` — блок с одним `type: infographic` слотом (линейный chart роста)

---

## Data flow

```
composed.html (PR-A artifact)
      │
      ▼
slot-scanner.py → список визуальных слотов:
[
  {block_id: ru-features-01, slot_name: feature-1-icon, type: icon, hint: shield},
  {block_id: ru-features-XX, slot_name: kpi-1, type: infographic, chart_type: number, data: {value: 87, label: "%"}}
]
      │
      ▼
для каждого слота:
  ├─ prompt-picker.py выбирает шаблон:
  │    - icons.csv keyword match по hint (cheap, no AI)
  │    - OR OpenDesign JSON если категория matches
  │    - OR generic icon-prompt.md если ничего не нашли
  ├─ visual-cache.py: hash(hint+style+brand) → если кэш есть, использовать
  ├─ codex-generate-icon.sh / -infographic.sh → PNG
  └─ chroma-key remove → 07d_VISUALS/icons/<slot>.png
      │
      ▼
inject-content.py читает 07d_VISUALS/ + composed.html
      │
      ▼ перерендеривает composed.html с <img src="...">
07b_COMPOSED/composed.html (финальный)
```

### Структура slot-scanner output (`07d_VISUALS/_slots.yaml`)

```yaml
icons:
  - slot_name: feature-1-icon
    block_id: ru-features-01-3col-icons
    hint: ""                      # или "shield" если в meta.yaml есть
    icon_color: ""                # пусто = взять из tokens.json:colors.accent
infographics:
  - slot_name: kpi-clients
    block_id: ru-features-XX-kpi-metrics
    chart_type: number            # из meta.yaml
    data:
      value: 1000
      label: "+"
      caption: "клиентов"
```

### Структура `STATE.yaml` (упрощённая по сравнению с PR-B)

```yaml
project: my-landing
started: 2026-05-13T18:00:00
stages:
  scan:      {status: done, slots_found: 14, icons: 14, infographics: 0}
  generate:  {status: in_progress, generated: 8, cached: 4, failed: 0}
  inject:    {status: pending}
warnings: []
errors: []
```

### Структура cache (`07d_VISUALS/.cache/<hash>.png`)

Имя файла = `sha256(hint + style + brand_color + niche)[:16].png`. При запуске:
- Если cache file exists → копируем в `icons/<slot>.png` без вызова codex.
- Иначе → генерим, после генерации копируем И в cache И в `icons/`.

`FORCE=1` env var обходит кэш.

---

## Codex template-шаблоны (2 файла)

Оба повторяют структуру `paralaximus-codex/templates/atlas-prompt.md` (How to use → Placeholders → Prompt body → Filled example).

### Общие placeholders

```
[VISUAL_STYLE]      — tokens.json:design.visual_style
[BRAND_PRIMARY]     — tokens.json:colors.primary
[BRAND_ACCENT]      — tokens.json:colors.accent (главный цвет для иконок)
[ICON_STYLE]        — tokens.json:design.icon_style (default: outlined)
[NICHE]             — 01a/market-profile.md:niche
[SLOT_HINT]         — meta.yaml:slots[].hint OR slot.name parsed
[CHART_TYPE]        — meta.yaml:slots[].chart_type (только для infographic)
[CHART_DATA]        — JSON-stringified slots[].data
[CHROMA_KEY]        — `#00ff00` default; `#ff00ff` если accent зелёный
```

### icon-prompt.md (краткий)

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, transparent
background using chroma-key [CHROMA_KEY], for: [SLOT_HINT].

VISUAL STYLE: [VISUAL_STYLE], [ICON_STYLE] icon
COLOR: [BRAND_ACCENT] primary, monochrome on chroma-key [CHROMA_KEY] background
NICHE CONTEXT: [NICHE]

FORBIDDEN (from open-design DESIGN.md):
- No lens flare, no glitch, no AI watermarks
- No text, no numbers on the icon
- No photoreal human faces or recognizable people
- No surreal artifacts

The icon must be a single clean shape, centered, occupying ~70% of the canvas,
on a perfectly flat [CHROMA_KEY] background for clean chroma-key removal.
```

### infographic-prompt.md (краткий)

```
Use the built-in image_gen tool. Generate ONE PNG, 1024x1024, transparent
background using chroma-key [CHROMA_KEY], for a [CHART_TYPE] infographic.

DATA: [CHART_DATA]
VISUAL STYLE: [VISUAL_STYLE]
COLOR: [BRAND_ACCENT] primary, monochrome accents allowed
NICHE CONTEXT: [NICHE]

For [CHART_TYPE]:
- "number" — large number with unit/label, ornamental frame
- "bar" — simple bar chart, 3-5 bars max
- "line" — single line chart, growth trend
- "donut" — donut chart, 2-4 segments

FORBIDDEN: lens flare, glitch, photoreal faces, surreal artifacts, text labels
LONGER than 30 chars per element.

Single clean composition centered, ~80% canvas, flat [CHROMA_KEY] background.
```

### Prompt-picker logic (3-step waterfall)

```python
def pick_prompt(hint: str, slot_type: str) -> str:
    # Step 1: try OpenDesign 90 JSON by category/tags match
    for p in opendesign_prompts:
        if hint.lower() in p["title"].lower() or hint in p["tags"]:
            return adapt_opendesign_prompt(p, brand_context)
    # Step 2: try icons.csv keyword match (icons only)
    if slot_type == "icon":
        match = icons_csv_match(hint)
        if match:
            return generic_icon_prompt(match)
    # Step 3: generic fallback prompt
    return generic_prompt(slot_type, hint, brand_context)
```

---

## Error handling

| Сценарий | Поведение |
|---|---|
| `05_design` не approved | Exit 1: «Сначала утверди дизайн-систему — без tokens.json промпты codex не попадут в стиль» |
| `composed.html` отсутствует | Exit 1: «Сначала запусти `/landing-compose` (PR-A)» |
| 0 visual slots в composed.html | Exit 0 warning: «Не нашли слотов с type=icon или type=infographic. Проверь что выбрал блоки с иконками в wireframe.» |
| `codex` не залогинен | Exit 2 (как paralaximus) |
| codex silent fail | retry 1×, после — slot помечается `failed: true`, fallback на SVG-placeholder (svg-placeholder.py из PR-B!) |
| Chroma-key removal даёт мусор | retry с другим chroma_key (`#ff00ff`) |
| OpenDesign промпт не найден под hint | Fallback в icons.csv → generic prompt |
| Кэш-hit но файл повреждён (size < 1KB) | Считаем cache invalid, регенерим |
| Один и тот же hint в разных слотах | Используем один cache entry, копируем в каждый slot |
| Запуск без PR-B (только PR-A + PR-C) | Работает — PR-C не зависит от `07c_PHOTOS/` |
| Запуск только `--type icons` | Infographic слоты пропускаются (STATE.yaml.infographics.status = skipped) |

**Логирование:** все codex-вызовы → `07d_VISUALS/.logs/YYYY-MM-DD_HHMMSS_<stage>.log`.

**Soft vs hard errors:** только unapproved gates — hard exit. Остальное — soft warnings в STATE.yaml. Если слот failed после retry → SVG placeholder, продолжаем.

---

## Testing

TDD per CLAUDE.md.

| Что | Чем | Сценарий |
|---|---|---|
| `slot-scanner.py` | pytest | Mini composed.html с 3 icon + 2 infographic слотами → правильный YAML output |
| `prompt-picker.py` | pytest | hint="shield" → match в icons.csv; hint="growth-chart" → match в OpenDesign; hint="unknown-xyz" → generic |
| `visual-cache.py` | pytest | Одинаковый hint+style+brand → одинаковый hash, skip codex |
| `codex-generate-icon.sh` | bats + codex-mock | Дополнительный test в `tests/phase-prc/test-codex-wrappers.bats` |
| `inject-content.py` icon branch | pytest | composed.html с `data-slot type=icon` + 07d_VISUALS/icons/X.png → `<img src>` |
| Block meta.yaml new infographic blocks | pytest | meta.yaml валидируется по существующей schema (block-library-management) |
| Stage gate `/landing-visuals` | bats | fake .landing-state.yaml → правильный exit |
| E2E pipeline | bats (test-pipeline.sh) | Добавить PR-C stage в pipeline + mock codex для предсказуемости |

**Mock codex:** переиспользуем `tests/phase-prb/fixtures/codex-mock.sh` через `CODEX_BIN`.

**Объём:** ~20-25 новых тестов.

---

## Acceptance criteria

- [ ] `/landing-visuals` в живом проекте даёт `composed.html` с реальными PNG-иконками вместо placeholders
- [ ] `slot-scanner.py` находит все `data-slot type=icon|infographic` в composed.html (тест)
- [ ] `prompt-picker.py` правильно выбирает источник промпта (OpenDesign → icons.csv → generic) (тест)
- [ ] `visual-cache.py` skip-if-exists работает, `FORCE=1` обходит (тест)
- [ ] Все 20-25 unit-тестов проходят
- [ ] Backward compat: проект без `07d_VISUALS/` продолжает работать (placeholders)
- [ ] Backward compat: PR-A + PR-B регрессионные тесты не падают (66 PR-B + 93 PR-A)
- [ ] 2 новых блока с `type: infographic` слотами добавлены в block-library и валидны
- [ ] `THIRD_PARTY_NOTICES.md` обновлён (OpenDesign image-prompts CC-BY-4.0)
- [ ] `07d_VISUALS/README.md` на русском (для маркетолога — короткий, объясняет что это)
- [ ] `CLAUDE.md` обновлён с PR-C workflow

---

## Dependencies

- `codex` CLI v0.125+ (уже используется)
- Python 3.10+ с `Pillow`, `PyYAML`, `BeautifulSoup4`
- bats для shell тестов
- НЕТ: ML-моделей, Iconify/Lucide, SDK прямо

---

## Known risks

### R1 — OpenDesign 90 промптов сделаны не под иконки

Просмотр первого промпта показал: они скорее complex infographics + illustrations, не minimalist icons. Реально использовать их для иконок может быть проблематично.

**Mitigation:** в `prompt-picker.py` priority: для `type: icon` — icons.csv keyword match → generic icon-prompt.md (НЕ OpenDesign по умолчанию). OpenDesign задействуется только для infographics + сложных иллюстраций.

### R2 — Chroma-key remove на иконках может оставлять fringe

Иконки имеют тонкие линии — chroma-key bleed может их разрушать.

**Mitigation:** использовать `--edge-contract 1` опцию в `remove_chroma_key.py` (есть в imagegen helper). Если всё ещё плохо — переключиться на `#ff00ff` chroma и retry.

### R3 — icons.csv keyword match слабый

icons.csv ~100 строк, keyword matching grep-style может пропускать. Качество: 60-70%.

**Mitigation:** добавить semantic match через codex (вызов "найди в этом CSV ближайшую иконку к hint X") — но это лишний codex call. Лучше: расширить keywords в csv по мере использования (post-MVP improvement).

### R4 — gpt-image-2 не всегда отдаёт чистый chroma-key

Уже знакомая проблема из paralaximus.

**Mitigation:** копируем тот же retry + alternative chroma паттерн из paralaximus-codex.

---

## Migration / backward compatibility

- PR-A + PR-B артефакты — без изменений
- `compose-blocks.py` + `inject-content.py` расширяются: новые ветки `type: icon` и `type: infographic` activated только если `07d_VISUALS/<type>s/<slot>.png` exists. Иначе — старое placeholder поведение
- Block library: добавляем 2 новых блока, существующие 63 — без изменений
- Existing `skills/paralaximus-codex/` — НЕ модифицируем; используем как pattern reference

---

## Attribution

Обновить `THIRD_PARTY_NOTICES.md`:

```
## OpenDesign image-prompts (90 JSON, per-file licenses)

PR-C uses image-prompt JSON templates from
vendor/opendesign-extracts/prompt-templates/image/ (Apache-2.0 wrapper).
Each prompt has its own license in `source.license` field (mostly CC-BY-4.0,
some MIT). When PR-C includes these prompts in generated assets, the per-prompt
attribution must be preserved.

When using a prompt template, the resulting PNG inherits the prompt's license.
Attribution is recorded in 07d_VISUALS/prompts.yaml for each generated icon.

Original repo: YouMind-OpenLab/awesome-gpt-image-2 (CC-BY-4.0 main).
```

---

## Open questions / future PRs

- **PR-C.1 (SVG output)** — рефактор PNG-flow в SVG для editable icons. Требует libsvg/vector libraries.
- **PR-C.2 (Iconify/Lucide fallback)** — для простых иконок (menu, arrow, check) не звать gpt-image-2, использовать готовые. Сэкономит ~70% генераций.
- **PR-C.3 (Animated SVG / video infographics)** — 114 video-prompts уже в vendor/ для seedance, готово к использованию.
- **PR-D (orchestrator integration)** — wire `/landing-visuals` в `landing-orchestrator`, добавить stage `07d_visuals` в `config/stage-gates.yaml`.
- **Smart prompt-picker через embeddings** — заменить keyword grep на semantic search (sentence-transformers offline).

---
name: gen-images
description: Генерация изображений для сайта — иконок и фото. ТРИГГЕРЫ ИКОНОК — (1) пользователь указывает блок ("сгенерируй иконки для hero/process/features", "иконки для блока X") → система собирает элементы блока (списки/буллеты/фичи/шаги) и генерит когезивный набор; (2) в макете пустые иконо-слоты/роли feature/trust-item/process-step без svg; (3) гейт нашёл пустые кружки-иконки. Два флоу: A1 готовые (Lucide → vtracer SVG), A2 генерация с нуля (codex image_gen ЛИСТ-сетка → нарезка по bbox → vtracer SVG → подстановка по концепциям). codex кладёт картинку в ~/.codex/generated_images/<session>/ и печатает путь (НЕ в указанную папку). ФОТО — клиентское фото → вырез rembg+alpha-matting → feather (эрозия+порог+blur) → autocrop → 07c_PHOTOS/processed/. Identity-safe. Этапы 07c (фото) / 07d (иконки). Триггерится из gen-html или по запросу "сгенерируй иконки для блока".
---

# gen-images

> ⛔ **ОБЯЗАТЕЛЬНЫЙ этап, не «потом».** `gen-html` вызывает gen-images ДО закрытия макета для КАЖДОГО
> визуального слота (фигуры/иконки/фоны). Финал с пустыми placeholder («фото эксперта», голый кружок-иконка)
> = незакрытый этап (гейт `verify_html_vs_ds.py` это ловит). Если фото клиента есть в `07c_PHOTOS/` —
> вырезать и вставить; иконки фишей/cta-note/контактов — SVG по смыслу, не голый цветной кружок.

## Pre-flight

```bash
python -m scripts.wiki.log --type skill_call --skill gen-images --stage 07c
```

Два пайплайна в одном скиле: **иконки → inline-SVG** и **клиентское фото → вырез с размытием края**.

## Инструменты (в этом скиле: `scripts/`)

| Скрипт | Когда | Что делает |
|---|---|---|
| `scripts/slice-icons-to-svg.py <sheet.png> --out <dir> --expect N --concepts "a;b;c"` | A2 после codex | детект bbox-ов иконок на белом фоне → вырез каждой → `vtracer` PNG→SVG → `icon-{i}-{slug}.svg` + `manifest.json` |
| `scripts/cutout-feather.py <src> --out <dir> [--preview]` | пайплайн B (фото) | `rembg` вырез + feather (эрозия+порог+blur) + autocrop → RGBA PNG |

> ⚙️ **Работа с codex (A2):** генерация — `codex exec --dangerously-bypass-approvals-and-sandbox '<промт>'`.
> codex кладёт PNG в `~/.codex/generated_images/<session-id>/ig_*.png` и печатает путь (НЕ в указанную папку!).
> Перед запуском: `date +%s` (метка старта) → после: взять путь из stdout ИЛИ свежайший png НОВЕЕ метки старта
> (`find ~/.codex/generated_images -iname '*.png' -newermt @<метка>`). Не брать «самый свежий вообще» — там старые генерации.

## Триггеры — КОГДА запускается (условия, автомат, не пропускать)

> gen-images запускается из `gen-html` ДО закрытия макета. Срабатывает, если выполнено ХОТЯ БЫ ОДНО условие.
> Условие детерминированное (по файлам/ролям/HTML) — агент не «решает на глаз», запускать ли.

| # | Условие (триггер) | Пайплайн | Что делает |
|---|---|---|---|
| T1 | В `07c_PHOTOS/inbox/*` (или указанном источнике) есть фото **И** в макете роль `figure-cutout`/`figure-center`/`avatar`/`case-card`-фото | B | вырез + feather + autocrop → вставить `<img>`/`<picture>` |
| T2 | В активном прототипе/ТЗ есть роль с иконкой: `feature`/`cta-note`/`trust-item`/`contact-line`/`process-step` **ИЛИ** в HTML есть иконо-слот без `<svg>` | A | SVG по смыслу → inline в слот |
| T3 | Роль `section-bg` требует фонового ИЗОБРАЖЕНИЯ (`bg: фото/тематич.`) — напр. тёмный мод с фон-фото | A/B | подобрать/обработать фоновое фото (затемнение/оверлей) |
| T4 | Роль-декор требует SVG-фигур: `diamond-decor`/`brand-scribble`/волны-разделители/блобы | A | сгенерить/нарисовать SVG-декор (currentColor=accent) |
| T5 | **Принудительный:** гейт `verify_html_vs_ds.py` нашёл пустой placeholder/иконку | A/B | отработать недостающий визуал, затем повторить гейт |

⛔ Если ни одно условие не выполнено (нет фото, нет иконо-ролей, нет фон/декор-ролей) — gen-images НЕ нужен,
этап чист. Но если условие есть, а визуал не вставлен — этап НЕ закрыт (T5 поймает).

## Вход (yaml/файлы проекта)

- Слоты иконок — из `07b_COMPOSED/build-spec.md` / `composed.html` (`[SLOT: …]`, роли `feature`/`cta-note` с иконкой по смыслу).
- Клиентские фото — `07c_PHOTOS/inbox/*` (или Desktop-источник, указанный пользователем).
- Бренд-контекст — `05_ДИЗАЙН-СИСТЕМА/tokens.json` / `moods/*/palette.css` (цвет иконок), `market-profile.md` (ниша).

## Выход

- Иконки → `07d_VISUALS/icons/*.svg` (+ inline в `composed.html` по слотам).
- Фото-вырезы → `07c_PHOTOS/processed/*.png` (RGBA, feathered).

---

## Пайплайн A — ИКОНКИ (ДВА флоу: A1 готовые → SVG · A2 генерация с нуля → SVG)

⛔ Оба флоу заканчиваются inline `<svg>` в слоте макета (`currentColor`/`stroke=var(--lp-accent)`, мод-токенизированный).
⛔ **Иконка ВСЕГДА по смыслу текста** (метафора из концепции), не «для красоты». Не колокольчик у лид-магнита.

### A1 — SVG из ГОТОВЫХ (простые иконки)
1. Простые/универсальные (стрелка, галочка, телефон, документ, человек) — бесплатный **Lucide** напрямую.
2. Если нужна не-Lucide растровая → **трассировка PNG→SVG** через **vtracer** (`line` контурные / `rich` заливочные).
3. Inline `<svg>` в слот. Кэш по hash(name+style+brand).

### A2 — ГЕНЕРАЦИЯ С НУЛЯ (codex image_gen → нарезка → SVG)
Для блоков со списками/фичами/шагами, где нужен КОГЕЗИВНЫЙ набор в едином стиле (готовых не хватает).

**Флоу:**
1. **Пользователь указывает блок** (напр. `hero.features`, `process.benefits`, `problem-solution`).
2. **Система собирает все элементы блока, которым можно подобрать иконку** — списки, буллеты, фичи, шаги,
   trust-пункты (роли `feature`/`trust-item`/`process-step`/`pain`/`gain`/`benefit`). ТЕКСТ каждого = КОНЦЕПЦИЯ.
3. **Тексты → CONCEPTS в промт** (ниже). Запуск через `codex exec` (НЕ интерактив):
   ```bash
   codex exec --dangerously-bypass-approvals-and-sandbox '<промт ниже>. After generating, print the absolute file path of the saved PNG.'
   ```
   ⛔ **codex НЕ сохраняет в указанную папку по CLI.** Он кладёт картинку в `~/.codex/generated_images/<session-id>/ig_*.png`
   и ПЕЧАТАЕТ абсолютный путь в конце вывода. Забрать путь так:
   - из stdout codex (последняя строка с `...generated_images/...png`), ЛИБО
   - найти свежайший файл: `find ~/.codex/generated_images -iname '*.png' -newermt '<время старта>' -printf '%T@ %p\n' | sort -rn | head -1`.
   ⛔ Картинки от ПРОШЛЫХ генераций тоже лежат там — брать ТОЛЬКО новее времени старта (`date +%s` перед запуском), не «самую свежую вообще».
   Лист = СЕТКА (иконок может быть МНОГО, не один ряд), по одной на концепцию, единый стиль.
4. **Нарезка ЛИСТА + трассировка** скриптом `scripts/slice-icons-to-svg.py <sheet.png> --out <dir> --expect N --concepts "a;b;c"`:
   детект bbox-ов тёмных объектов на белом фоне (склейка частей одной иконки, упорядочивание по сетке сверху-вниз/слева-направо) →
   вырез каждой в квадрат с полями → `vtracer` PNG→SVG → `icon-{i}-{slug}.svg` + `manifest.json`. Сверить `--expect N` с числом концепций.
5. **Сопоставление концепций ↔ SVG** (по порядку: концепция-i ↔ icon-i, см. manifest.json) → подстановка inline в слоты блока.
   Иконка ч/б генерится → на сайте красится токеном мода (`fill/stroke:var(--lp-accent)` через `currentColor`).
6. Кэш по hash(concepts+style+brand+niche). Метафоры/стиль — под нишу из `market-profile.md` + мод.

**Промт (codex image_gen) — подставить только CONCEPTS из текстов блока; стиль, ограничения и output уже зафиксированы:**

```
Create a cohesive professional 3D icon set for the following concepts:

CONCEPTS:
1. {текст элемента 1}
2. {текст элемента 2}
...
N. {текст элемента N}

Generate exactly one icon for each listed concept.

CONCEPT SELECTION

Mode 1 — Reference Image Provided

If a reference image is provided, analyze it only as instructed below.

If the reference defines the meaning of a specific concept:

* Preserve the primary semantic idea communicated by the reference.
* Do not invent a different metaphor.
* Do not replace it with a more common symbol.
* Extract the minimum number of elements needed to preserve recognition.
* Remove decorative and non-essential details.
* Preserve meaning rather than exact appearance.

If the reference is provided only as a style reference:

* Preserve its material, depth, lighting, outline shape, proportions, shadows, and overall visual language.
* Do not copy its specific objects or concepts.
* Apply the same style consistently to all requested icons.

If the written concept and its semantic reference communicate slightly different ideas, follow the semantic reference.

Mode 2 — No Semantic Reference Provided

For every concept:

* Select the simplest and most recognizable visual metaphor.
* Use established symbols from modern software, fintech, automotive, and premium digital interfaces.
* Prioritize instant recognition over originality.
* Use no more than two primary semantic elements whenever possible.
* Avoid abstract, artistic, experimental, or overly clever interpretations.
* Do not force vehicles, arrows, people, or other objects into concepts where they are unnecessary.
* Make every icon recognizable at small interface sizes.

STYLE

Premium monochrome 3D outline icon set.

Black and dark graphite icons on a pure white background.

Rounded tubular outlines with visible physical thickness.

Soft extruded depth.

Smooth beveled edges.

Subtle glossy highlights along the upper-left edges.

Soft ambient shadows directly beneath and slightly behind each icon.

Gentle studio lighting from the upper left.

Matte black or dark graphite material with restrained metallic highlights.

Clean, polished, tactile appearance.

Modern premium digital product aesthetic.

The icons should look like sculpted 3D versions of high-quality monoline UI icons.

CONSISTENCY

All icons must belong to one coherent visual system.

Maintain consistent:

* outline thickness
* extrusion depth
* bevel radius
* corner rounding
* lighting direction
* shadow softness
* material response
* perspective
* visual weight
* scale
* level of detail

Do not mix flat icons, filled icons, realistic objects, or different rendering styles.

ICON CONSTRUCTION

Use one clear visual metaphor per concept.

Use the minimum number of shapes required to communicate the meaning.

Prefer simple geometric construction.

Use clean curves and rounded corners.

Keep balanced proportions and centered compositions.

Avoid unnecessary internal lines and small details.

Do not create complete scenes or illustrations.

Do not add decorative elements that do not improve recognition.

Avoid complex overlaps.

Ensure every icon remains clear when reduced to a small size.

COMPOSITION

Arrange all icons in a clean, structured layout appropriate to their number.

For a small number of icons:

* use a single horizontal row when practical

For a larger number of icons:

* use a balanced grid with equal columns and rows

Keep:

* equal spacing
* equal visual size
* consistent alignment
* generous white margins
* enough separation for easy cropping

Each icon must occupy its own clear visual area and be easy to crop into an individual square asset.

Do not place icons inside cards, circles, tiles, frames, or containers unless explicitly requested.

RESTRICTIONS

No text.

No captions.

No labels.

No letters unless the letter or symbol is essential to the concept.

No unnecessary currency symbols.

No colored elements.

No colored background.

No background gradient.

No dramatic reflections.

No transparent glass.

No photorealistic materials.

No excessive gloss.

No heavy metallic texture.

No dramatic perspective.

No complex environment.

No floating particles.

No decorative objects.

No visual clutter.

No duplicated metaphors unless two concepts genuinely require the same symbol.

No additional icons beyond the supplied concept list.

OUTPUT

Generate one cohesive image containing one icon for every listed concept.

The total number of icons must exactly match the number of concepts.

Use one final interpretation per concept.

Do not generate alternative versions.

Do not omit, combine, or add concepts.

Use a pure white background.

Use a canvas and aspect ratio appropriate for the number of icons.

Use high resolution.

Professional 3D icon library quality.
```

> ⚙️ В A2 передаём модели только список `CONCEPTS`; стиль, ограничения, sheet-композиция и правила соответствия количеству иконок зафиксированы прямо в prompt.
> Отраслевая узнаваемость метафор допускается через список "modern software, fintech, automotive, and premium digital interfaces", без динамической пересборки `STYLE`-блока под нишу.
> Цвет иконок на сайте по-прежнему может задаваться CSS-токенами после трассировки/inline-вставки, но baseline-генерация самого sheet теперь монохромная.

---

## Пайплайн B — ФОТО (вырез + feather)

1. **Вырез фона:** `rembg` (модель `isnet-general-use` + alpha_matting) — лучше держит края, чем chroma-key.
2. **Feather краёв (ОБЯЗАТЕЛЬНО):** к alpha-каналу —
   эрозия (`MinFilter 7` ≈ срез 3px каймы фона) → порог альфы (`<40 → 0`, убрать полупрозрачную кайму) →
   `GaussianBlur ~3px` (мягкий край). RGB не трогать. Резкий край rembg = видимая «вырезанность» + остатки фона.
3. **Autocrop** по bbox объекта.
4. Сохранить в `07c_PHOTOS/processed/*.png` (RGBA). Опц. preview на тёмной/светлой карточке для оценки краёв.

Скрипт: [`scripts/cutout-feather.py`](scripts/cutout-feather.py) (rembg + feather + autocrop; флаги `--no-feather`, `--preview`, `--webp`).

⛔ **Feather обязателен** для всех вырезов. **Identity-safe:** клиентские лица НЕ репейнтятся AI;
AI-генерация лиц (testimonial/expert/team) — только по явному флагу `ai_approved_by_user`.

---

## Стандарты

- Image-pipeline: [`docs/standards/image-pipeline.md`](../../docs/standards/image-pipeline.md).
- Asset-pipeline (как ассет попадает на сайт): [`docs/asset-pipeline.md`](../../docs/asset-pipeline.md).
- Иконка по смыслу — правило словаря ролей (`07_ПРОТОТИП/prototypes-index.md`) + стандарт §7 п.5.

## Следующий шаг

← `gen-html` (слоты иконок/фото в макете) · → build (ассеты в тему).

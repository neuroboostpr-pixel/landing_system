# B34 — План реализации: двухуровневая семантическая таксономия блоков

**Дата:** 2026-06-02
**Spec:** [docs/BACKLOG.md § B34](../../BACKLOG.md)
**Цель:** перевести таксономию блоков с одноуровневой (`category` + `layout_pattern` в комбобоксах) на двухуровневую семантическую (`category` → `variant` по роли на лендинге), русский UI, чистка библиотеки, умный импортёр.

---

## Контекст текущего состояния (факты из кода)

| Артефакт | Сейчас |
|---|---|
| `block-library/catalog.yaml` | version 3, 183 блока. Поля: id, path, category, type, layout_pattern, signature, display_name_ru, created, has_bg_image, slots, source. **Нет `variant`.** |
| 14 текущих категорий | contacts(4), cta(22), faq(9), features(26), footer(9), gallery(7), header(10), hero(21), pricing(11), process(12), quiz(13), social-proof(18), team(1), trust(20) |
| `meta.yaml` блоков | поле `category` часто содержит мусор (`Footer`, `Conversion`, `Content`) — расходится с canonical-слагом. `variant` отсутствует. Есть `use_cases`, `ru_market`, `recommended_styles_ru`. |
| `scripts/generate-catalog.py` | `extract_block_info()` (стр.18-60) копирует 10 полей. `category` берётся из имени папки-категории, НЕ из meta. |
| `scripts/generate-gallery.py` | `patterns_by_cat` (стр.51-68) строит 2-й уровень из `layout_pattern`. JS `CAT_PATTERNS`. Лейблы = слаги. |
| `match-candidates.py` | фильтр `b.category == args.type` (стр.139), scoring, отсечка `score>0` (стр.146). |
| `render-wireframe.py` | `--type btype --niche --top 999` (стр.510-518). `SECTION_TO_CATALOG_TYPE` (стр.81-103), напр. `cta→conversion`. |
| `wireframe-shell.html` | карусель всех кандидатов, radio-tabs. Двухуровневого комбобокса нет. |
| `prototype.yaml` | `blocks[].type` → передаётся как `--type` в match-candidates. Нет `variant`. |
| Тесты | для catalog/gallery/match-candidates **нет**. Фреймворк в проекте — pytest. |

**Главное расхождение:** canonical category живёт в имени папки (catalog), а meta.yaml `category` ненадёжен. Новые `category`/`variant` нужно класть в meta.yaml как **source of truth** и научить generate-catalog.py их читать оттуда (с миграцией старого мусора).

---

## Целевая таксономия (из B34)

11 категорий. Слаг → русская метка → подкатегории:

| Слаг | Метка | Подкатегории (слаг→метка) |
|---|---|---|
| `header` | Шапка / Навигация | — |
| `hero` | Первый экран | — |
| `marquee` | Бегущая строка | — |
| `features` | Преимущества | — |
| `content` | Контент | about→о продукте, problem-solution→проблема → решение, process→как это работает |
| `social-proof` | Соц. доказательства | testimonials→отзывы, clients→наши клиенты, ratings→рейтинги, numbers→цифры, cases→кейсы, media→упоминания в медиа |
| `trust` | Доверие | certificates→сертификаты, guarantees→гарантии, security→безопасность |
| `pricing` | Цены | cards→карточки тарифов, comparison→сравнительные таблицы |
| `forms` | Формы | email→сбор email, multi-step→многошаговая, quiz→квиз, booking→бронирование |
| `faq` | FAQ | — |
| `footer` | Подвал | — |

Уровень 3 есть только у: content, social-proof, trust, pricing, forms.

---

## Архитектурное решение: единый словарь таксономии

Создать **один источник истины** — `block-library/taxonomy.yaml`:

```yaml
version: 1
categories:
  social-proof:
    label_ru: "Соц. доказательства"
    order: 6
    variants:
      testimonials: { label_ru: "отзывы" }
      clients:      { label_ru: "наши клиенты" }
      ratings:      { label_ru: "рейтинги" }
      numbers:      { label_ru: "цифры" }
      cases:        { label_ru: "кейсы" }
      media:        { label_ru: "упоминания в медиа" }
  hero:
    label_ru: "Первый экран"
    order: 2
    variants: {}   # нет уровня 3
  # ... все 11
```

Все потребители (`generate-catalog.py`, `generate-gallery.py`, `match-candidates.py`, `render-wireframe.py`) читают лейблы и валидируют значения отсюда. Никаких хардкод-словарей в коде или HTML.

---

## Фазы реализации

### Фаза 0 — Словарь таксономии (фундамент)
**Файлы:** `block-library/taxonomy.yaml` (новый), `scripts/lib/taxonomy.py` (новый загрузчик).

1. Создать `taxonomy.yaml` с 11 категориями, метками, подкатегориями, порядком.
2. `scripts/lib/taxonomy.py` — загрузчик: `load_taxonomy()`, `category_label(slug)`, `variant_label(cat, slug)`, `categories_ordered()`, `has_variants(cat)`, `valid_variant(cat, variant)`.
3. **Тест:** `tests/block-library/test_taxonomy.py` — словарь парсится, 11 категорий, 5 с variants, лейблы русские, нет дублей order.

**TDD:** тест первым (failing) → taxonomy.yaml → loader → green.

---

### Фаза 1 — Поле `variant` в схеме + миграция meta.yaml
**Файлы:** `scripts/migrate-block-taxonomy.py` (новый), все `block-library/*/*/meta.yaml`.

Это **самая объёмная** фаза — переклассификация 183 блоков. Делается полу-автоматически:

1. **Скрипт-помощник** `migrate-block-taxonomy.py`:
   - Читает каждый блок (path, текущая category-папка, display_name_ru, slots).
   - По правилам маппинга старая→новая категория (из B34 «Миграция»):
     - `header`→`header`, `hero`→`hero`, `features`→`features`, `faq`→`faq`
     - `contacts`,`footer`→`footer`
     - `about`,`manifesto`,`process`→`content` (variant по эвристике из id/display_name)
     - `social-proof`,`stats`,`partners`,`team`→`social-proof` (variant по эвристике)
     - `trust`,`guarantees`→`trust` (variant по эвристике)
     - `pricing`→`pricing` (variant: comparison если в id/name «таблиц»/«comparison», иначе cards)
     - `quiz`→`forms`/quiz, прочие формы→`forms` (variant по эвристике)
     - `cta`→ **пропустить** (удаляется целиком в Фазе 3, решение 2 — не размечаем)
     - `gallery`→ **пропустить** (удаляется целиком в Фазе 3, решение 3 — не размечаем)
     - `team`→`content` (решение 4; variant: about→«о продукте», или cases если кейс команды)
   - Пишет `category` + `variant` (или `variant: null`) в каждый meta.yaml.
   - Эвристика variant по ключевым словам в `id`/`display_name_ru`/`slots` (напр. слот типа `infographic`+`number`→`numbers`; слот `quote`/`testimonial`→`testimonials`; `logo`→`clients`).
   - **Генерирует отчёт** `migration-report.md`: что куда отнесено + список «требует ручной проверки» (низкая уверенность эвристики).

2. **Ручная доводка:** пройти по `migration-report.md`, поправить неуверенные блоки эвристики. `cta`(22) и `gallery`(7) НЕ трогаем — они удаляются целиком в Фазе 3.

3. **Переименование `display_name_ru`** (B34 Часть 5) — в том же проходе: формат `"Категория · подкатегория: структура"`.

**Тест:** `tests/block-library/test_meta_taxonomy.py` — каждый meta.yaml имеет валидную `category` из taxonomy.yaml; для категорий с уровнем 3 `variant` ОБЯЗАТЕЛЕН и валиден (решение 1); для категорий без уровня 3 `variant` должен быть null/отсутствовать.

---

### Фаза 2 — generate-catalog.py читает variant
**Файл:** `scripts/generate-catalog.py`.

1. `extract_block_info()`: добавить `"variant": meta.get("variant")`.
2. `category` брать из meta.yaml (canonical), с fallback на имя папки; если meta.category не в taxonomy.yaml — WARNING.
3. Валидация против taxonomy.yaml: неизвестная category/variant → stderr warning, блок не падает.
4. Регенерировать `catalog.yaml`.

**Тест:** `tests/block-library/test_generate_catalog.py` — на фикстуре из 2-3 блоков catalog содержит variant; невалидная категория → warning.

---

### Фаза 3 — Чистка библиотеки (B34 Часть 3) — КОНСЕРВАТИВНАЯ
**Файлы:** удаление папок `cta/` и `gallery/`, регенерация catalog.

Решение 5 — консервативно. Удаляем только то, что явно решено:

1. **Удалить `block-library/cta/`** целиком (22 блока, решение 2). `git rm -r`.
2. **Удалить `block-library/gallery/`** целиком (7 блоков, решение 3). `git rm -r`.
3. `team` уже переехал в `content` на Фазе 1 (решение 4) — папку `team/` переименовать/переместить либо оставить с обновлённой meta (category=content). Проще: оставить файлы, в meta уже content; имя папки не влияет на category (читается из meta).
4. **Дубли НЕ схлопываем.** `scripts/find-block-duplicates.py` создаётся как диагностика (печатает группы по `(category, variant, layout_pattern)`), но ничего не удаляет — для будущих ревизий.
5. Регенерировать catalog + gallery. Ожидаемо: 183 − 29 = **~154 блока**.

> Папки cta/gallery удаляются. Всё остальное сохраняется (консервативно).

---

### Фаза 4 — Галерея: 2 комбобокса category→variant, русский UI
**Файл:** `scripts/generate-gallery.py`.

1. Импортировать `scripts/lib/taxonomy.py`.
2. Заменить `patterns_by_cat` (layout_pattern) на `variants_by_cat` (variant).
3. Комбобокс 1 «Категория»: пункты из taxonomy, **русские метки**, в порядке `order`.
4. Комбобокс 2 «Подкатегория»: русские метки вариантов; **скрыт** (`display:none`) для категорий без уровня 3, не просто disabled.
5. JS-карта `CAT_VARIANTS = {slug: {variantSlug: {label, count}}}` + `CAT_LABELS`, `VARIANT_LABELS`.
6. Карточка: бейдж русской категории + бейдж русской подкатегории (если есть) + мелкий тех-тег `layout_pattern`.
7. `data-variant` на карточки.

**Тест:** `tests/block-library/test_generate_gallery.py` — в выводе нет англ. слагов в видимых лейблах (проверка что метки из taxonomy.yaml присутствуют); комбобокс 2 для hero/footer скрыт; для social-proof есть 6 вариантов.

---

### Фаза 5 — match-candidates + render-wireframe: variant-aware
**Файлы:** `match-candidates.py`, `render-wireframe.py`, `wireframe-shell.html`.

1. `match-candidates.py`:
   - Принять опц. `--variant`. Если задан — фильтровать `b.category==type AND b.variant==variant`.
   - **Убрать жёсткую отсечку `score>0`** (стр.146) — иначе при новой категории без use_cases все блоки выпадают (это и была причина «hero только 3»). Вместо: сортировать по score, но возвращать ВСЕ (до `--top`).
   - Обновить `SECTION_TO_CATALOG_TYPE` под 11 новых категорий (убрать `cta→conversion`).
2. `render-wireframe.py`:
   - Маппинг prototype `block.type` → новая category через taxonomy (+ опц. `block.variant`).
   - Передавать `--variant` если есть в прототипе.
3. `wireframe-shell.html`: бейджи кандидатов на русском (категория · подкатегория) из catalog.
4. Сверка: число hero-кандидатов в варфрейме == число hero-блоков в галерее.

**Тест:** `tests/wireframe/test_match_candidates.py` — для type=hero без niche возвращаются ВСЕ hero-блоки (не 3); `--variant testimonials` сужает social-proof корректно.

---

### Фаза 6 — Умный импортёр (B34 Часть 4) — ОТДЕЛЬНАЯ итерация
**Файл:** новый скил `skills/block-import/` + команда `/landing-import-blocks`.

Выносится в **B34.1** как самостоятельная задача (зависит от стабильной таксономии Фаз 0-5). В этот план включаю только заглушку-спеку, не реализуем сейчас.

---

## Порядок и зависимости

```
Фаза 0 (словарь) ── фундамент для всех
   └─> Фаза 1 (variant в meta + миграция 183) ── самая трудоёмкая, ручная доводка
          └─> Фаза 2 (catalog читает variant)
                 ├─> Фаза 3 (чистка дублей)
                 ├─> Фаза 4 (галерея 2 комбобокса)
                 └─> Фаза 5 (wireframe variant-aware)
Фаза 6 (импортёр) ── отдельная итерация B34.1
```

## Оценка
- Фаза 0: 1-2 ч
- Фаза 1: 3-5 ч (переразметка 154 блоков, без cta/gallery; + ручная доводка)
- Фаза 2: 1 ч
- Фаза 3: 1 ч (только удаление cta/gallery, дубли не трогаем — консервативно)
- Фаза 4: 2-3 ч
- Фаза 5: 2-3 ч
- **Итого ядро (0-5): ~10-15 ч.** Фаза 6 — отдельно.

## Решения пользователя (зафиксировано 2026-06-02)
1. ✅ **variant ОБЯЗАТЕЛЕН** для категорий с уровнем 3 (content, social-proof, trust, pricing, forms). `variant: null` допустим ТОЛЬКО для категорий без уровня 3. Тест Фазы 1 это enforce'ит.
2. ✅ **cta-блоки (22) — УДАЛИТЬ.** CTA не отдельный блок (функционал, встраивается в hero/формы/footer). Вся папка `block-library/cta/` удаляется в Фазе 3.
3. ✅ **gallery-блоки (7) — УДАЛИТЬ.** Папка `block-library/gallery/` удаляется в Фазе 3.
4. ✅ **team (1) — в Контент** (`category: content`, variant по эвристике: about→о продукте, либо cases если кейс команды).
5. ✅ **Чистка КОНСЕРВАТИВНАЯ.** Дубли по `(category, variant, layout_pattern)` НЕ схлопываем агрессивно — оставляем больше вариантов. Удаляем только cta+gallery (решения 2,3) и team-переезд. `find-block-duplicates.py` остаётся диагностическим (показывает, но не удаляет).
6. ✅ **Слаги `marquee`, `content`, `forms` — ОК.**

**Влияние на объём:** после удаления cta(22)+gallery(7) остаётся **154 блока** для переразметки (183 − 29). team(1) переезжает в content.

## Контроль качества (Wiki Auto-Sync)
`taxonomy.yaml` и `block-library/*/*/meta.yaml` — источники wiki. После изменений: `bash scripts/check-wiki-sync.sh` или дать post-commit хуку пересобрать.

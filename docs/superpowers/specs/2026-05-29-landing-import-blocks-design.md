# landing-import-blocks — Скил импорта блоков в block-library

**Дата:** 2026-05-29
**Статус:** approved
**Slash-команда:** `/landing-import-blocks`

---

## Цель

Автоматически добавлять новые блоки в `block-library/` из скриншота или URL. Проверять уникальность по layout-сигнатуре, добавлять только структурно уникальные блоки с правильной таксономией и нейтральным template.html (без стилей).

---

## Флоу

```
Вход: URL или скриншот из чата
         ↓
[1] Получить изображение
    • URL → take-page-screenshot.py
    • скриншот из чата → wizard-save-images.py (читает JSONL сессии)
         ↓
[2] Codex vision → structure.json
    Для каждого видимого блока:
    • category (Level 1: Navigation, Hero, Content, ...)
    • type (Level 2: hero, features, testimonials, ...)
    • layout_pattern (split|centered|grid-2|grid-3|grid-4|stacked|bento|sidebar|cards|timeline|multi-step)
    • slots[] (name + type: text|image|icon|cta|form)
    • has_bg_image (bool)
    • display_name_ru (формат: "Тип: элемент + элемент")
         ↓
[3] Вычислить сигнатуру каждого блока:
    "{type}|{layout_pattern}|{slots_sorted}|bg:{has_bg_image}"
    Пример: "hero|split|[cta,headline,image,subhead]|bg:true"
         ↓
[4] Сравнить с existing_signatures из catalog.yaml
    • Нет совпадения → добавить автоматически
    • Есть совпадение → показать сравнение и спросить подтверждение:
      "⚠️ Похожий блок уже есть: hero-003
         Существующий: split | headline + image + cta | фон: нет
         Новый:        split | headline + image + cta | фон: есть
         Добавить как hero-004? (yes/no)"
         ↓
[5] Для подтверждённых блоков:
    a. Присвоить id: {type}-{NNN} где NNN = max+1 по типу
    b. generate-blocks.py → template.html БЕЗ стилей
       (нейтральные серые цвета, system-ui, только структура)
    c. Записать meta.yaml
         ↓
[6] update-catalog.py → добавить в catalog.yaml
         ↓
[7] render-gallery.py → перегенерировать gallery.html
         ↓
Вывод в чат:
    "✅ Добавлено N блоков: hero-004, features-012, ...
     ⏭ Пропущено M дублей: hero-003 (уже есть)
     Открой: block-library/gallery.html"
```

---

## Таксономия (двухуровневая)

### Level 1 — Категории (фильтр галереи)

| Категория | Типы (Level 2) |
|---|---|
| Navigation | header, menu |
| Hero | hero |
| Content | features, characteristics, about, problem-solution, process, demo |
| Social Proof | testimonials, logos, stats, case-study, media-mentions |
| Trust | guarantees, comparison, integrations |
| Conversion | cta, banner, urgency, lead-form |
| Pricing | pricing |
| FAQ | faq |
| Gallery | gallery, team |
| Footer | footer, contacts |

### Level 2 — Типы блоков

Итого **23 типа**. Новые типы добавляются в `block-library/taxonomy.yaml` — единый источник истины.

---

## Формат блока

### Структура папки

```
block-library/
  hero/
    hero-001/
      meta.yaml       — описание, сигнатура, слоты
      template.html   — чистая HTML-структура БЕЗ стилей
```

### meta.yaml

```yaml
id: hero-001
type: hero              # level-2: конкретный тип блока
category: Hero          # level-1: группа для фильтра в галерее
layout_pattern: split
display_name_ru: "Hero: фото справа + заголовок + CTA"
slots:
  - {name: headline, type: text, required: true, max_chars: 80}
  - {name: subhead, type: text, required: false, max_chars: 160}
  - {name: image, type: image, required: true}
  - {name: primary-cta, type: cta, required: true}
has_bg_image: false
signature: "hero|split|[cta,headline,image,subhead]|bg:false"
source: import          # manual | import
source_url: https://...
created: 2026-05-29
```

### template.html — требования

- **Без цветов** — только `#f5f5f5`, `#e8e8e8`, `#d0d0d0`, `#333`, `#999`
- **Без шрифтов** — только `font-family: system-ui`
- **Без теней, border-radius декоративных** — только структурные
- **Слоты** — `data-slot="headline"` атрибут на каждом элементе
- **Фоновые изображения** — `background-color: #d0d0d0` с текстом `[BG PHOTO]`
- **Иконки** — серые квадраты `[ICON]`
- **Изображения** — серые прямоугольники `[IMAGE]` нужных пропорций
- Layout (grid, flex, позиционирование) — **сохраняется полностью**

---

## Промпт для Codex (изменения vs текущий)

Текущий промпт возвращает `description` с цветами и стилями. Новый промпт:

1. `type` из нового enum 23 типов (не старых 9)
2. `display_name_ru` — только структура: `"Тип: элемент + элемент"`
3. `has_bg_image` — bool
4. `slots` — явный список с типами
5. **Запрет** упоминать цвета, шрифты, стили в любых полях

---

## Проверка дублей

Сигнатура: `"{type}|{layout_pattern}|{slots_sorted}|bg:{has_bg_image}"`

Сортировка слотов по имени — гарантирует одинаковый результат независимо от порядка в промпте.

Пример:
```
"hero|split|[cta,headline,image,subhead]|bg:false"
```

Совпадение = полное строковое равенство. При совпадении — интерактивный вопрос.

---

## Генерация template.html

Codex получает промпт с:
- Скриншот блока (кроп из полного скриншота страницы)
- Список слотов из structure.json
- Требования к нейтральному стилю (серые тона, system-ui)
- Запрет копировать цвета/шрифты из скриншота

Выход: один `<section>` с нейтральным CSS и `data-slot` атрибутами.

---

## Затронутые файлы

**Создать:**
- `skills/landing-import-blocks/SKILL.md`
- `skills/landing-import-blocks/scripts/import-blocks.py` — главный оркестратор
- `skills/landing-import-blocks/scripts/check-duplicates.py` — проверка сигнатур
- `skills/landing-import-blocks/prompts/structure-analysis.md` — новый промпт
- `skills/landing-import-blocks/prompts/block-generation.md` — промпт генерации без стилей
- `block-library/taxonomy.yaml` — единый источник истины таксономии

**Изменить:**
- `scripts/import-blocks/codex-analyze-structure.sh` — обновить промпт
- `scripts/import-blocks/generate-blocks.py` — генерация без стилей
- `scripts/import-blocks/update-catalog.py` — новые поля meta
- `skills/prototype-import/scripts/validate-prototype.py` — новые типы блоков

**Не трогать:**
- `skills/block-library-management/scripts/render-gallery.py` — уже работает
- Существующие блоки в `block-library/` — чистка отдельная задача (B34)

---

## Что НЕ входит в этот спек

- Чистка существующих 190 блоков (B34)
- Переименование старых блоков
- Обновление wireframe под новую таксономию (B35)
- Визуальный стандарт премиальности (B33)

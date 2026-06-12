# Block Library Cleanup — массовая чистка 190 блоков

**Дата:** 2026-05-29
**Статус:** approved
**Зависит от:** B34 (taxonomy.yaml, check_duplicates.py, block-generation.md промпт)

---

## Цель

Привести существующие 190 блоков `block-library/` к единому стандарту:
1. Текст → плейсхолдеры `[SLOT: name]` (язык лендинга любой).
2. Стили → нейтральные серые тона + system-ui (lo-fi).
3. Полные дубли по layout-сигнатуре — удалить (с подтверждением).
4. Переименовать в `тип-NNN`, `display_name_ru` без цветов.
5. Перенести в новую таксономию (27 типов из `taxonomy.yaml`).

Изображения и иконки — часть блока, остаются как `[SLOT: image]` / `[SLOT: icon]`.

---

## Поток (3 фазы)

### Фаза 1 — Чистка через Codex (пер-блок)

```
Для каждого из 190 блоков:
  [1] Прочитать assets/template.html + meta.yaml
  [2] Codex (промпт block-generation.md + classify-инструкция):
        • классифицировать type + category по taxonomy.yaml
        • восстановить ПОЛНЫЙ список slots из HTML (не только meta.heading)
        • выдать чистый template.html: [SLOT: name] плейсхолдеры, нейтральный стиль
        • display_name_ru без цветов ("Тип: элемент + элемент")
        • has_bg_image (bool)
  [3] compute_signature(block)
  [4] Записать в .cleanup-staging/<old_slug>.json:
        {old_path, old_id, type, category, slots, signature,
         clean_html, display_name_ru, has_bg_image, status}
        status = "ok" | "needs_manual" (если Codex не вернул валидный HTML)
```

**Оригиналы `block-library/` НЕ трогаются в фазе 1.**

Чекпойнт-коммит после фазы 1.

### Фаза 2 — Дедупликация (с подтверждением)

```
  [5] Загрузить все staging-блоки, сгруппировать по signature
  [6] Группы где >1 блок → dedup-report.html:
        • заголовок группы = сигнатура
        • для каждого блока: lo-fi превью (clean_html) + old_id + чекбокс "удалить"
        • по умолчанию отмечены на удаление все кроме первого в группе
  [7] Пользователь правит чекбоксы, жмёт "Скачать keep-list" → keep-list.yaml
        keep-list.yaml: {removed: [old_id, ...], kept: [old_id, ...]}
```

Чекпойнт-коммит после фазы 2 (с keep-list.yaml).

### Фаза 3 — Пересборка библиотеки

```
  [8] Удалить блоки из keep-list.removed
  [9] Сквозная нумерация: сгруппировать оставшиеся по type,
      отсортировать (ru-* первыми для стабильности), присвоить type-001, type-002...
      Блоки со status="needs_manual" НЕ переименовываются и НЕ удаляются —
      остаются в старой папке с пометкой, выводятся в финальном отчёте для ручной доработки.
  [10] Создать новую структуру: block-library/<category>/<type-NNN>/
        ├── meta.yaml      (новые поля: id, type, category, layout_pattern,
        │                    display_name_ru, slots, has_bg_image, signature, source)
        └── assets/template.html  (clean_html)
        Старые папки удалить.
  [11] Перезаписать catalog.yaml (v3) + перегенерировать gallery.html
        Записать migration-map.yaml: {old_id: new_id} — для отладки
```

Чекпойнт-коммит после фазы 3.

---

## Безопасность

- **Git-ветка** `block-library-cleanup` (не `mvp-internal-test`). Провал → выбросить ветку.
- **Staging** `.cleanup-staging/` — Codex пишет туда, оригиналы целы до фазы 3.
- **Чекпойнты** — коммит после каждой фазы, откат на любой.
- **Codex-фейлы** — блок помечается `needs_manual`, оригинал сохраняется, в финале отчёт сколько ok / failed.

---

## Классификация (Codex решает сам)

Промпт классификации передаёт Codex:
- текущий `template.html`
- список 27 типов из `taxonomy.yaml` с label_ru
- инструкцию: определи type по СОДЕРЖИМОМУ, не по старому имени

Маппинг старых→новых для справки (Codex может переопределить):
- `trust` → manifesto / stats / guarantees / partners
- `quiz` → lead-form (или остаётся quiz если multi-step воронка)
- `contacts` → contacts (Footer) или lead-form
- `social-proof` → testimonials / logos / stats / case-study / media-mentions
- остальные → одноимённый тип

---

## Затронутые файлы

**Создать:**
- `skills/block-library-management/scripts/cleanup_blocks.py` — оркестратор 3 фаз
- `skills/block-library-management/scripts/dedup_report.py` — генератор dedup-report.html
- `skills/block-library-management/prompts/cleanup-classify.md` — промпт чистки+классификации
- `tests/block-library/test_cleanup.py` — тесты group_duplicates, renumber, build_new_structure

**Переиспользовать:**
- `skills/landing-import-blocks/scripts/check_duplicates.py` — compute_signature
- `skills/landing-import-blocks/prompts/block-generation.md` — база промпта (placeholders only)
- `block-library/taxonomy.yaml` — 27 типов
- `skills/block-library-management/scripts/render-gallery.py` — финальная галерея

**Артефакты (gitignore или временные):**
- `.cleanup-staging/*.json` — промежуточные результаты
- `block-library/migration-map.yaml` — old_id → new_id (коммитится, для отладки)

---

## Тестируемость

Чистые функции с unit-тестами (без Codex):
- `group_duplicates(blocks: list) -> dict[signature, list[block]]`
- `renumber(blocks: list) -> dict[old_id, new_id]` — сквозная нумерация по типу, ru-* первыми
- `build_new_structure(blocks, keep_list) -> list[actions]` — что куда переместить

Codex-вызовы мокаются (как в импортёре).

---

## Что НЕ входит

- Изменение wireframe/composer под новую таксономию (B35)
- Добавление новых блоков (это импортёр B34)
- Визуальный стандарт премиальности (B33)
- Заполнение пустых новых типов (problem-solution, comparison и т.д.) — отдельная задача

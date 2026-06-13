# Block Library Cleanup — СТАТУС (пауза 2026-05-29)

Связано: [spec](2026-05-29-block-library-cleanup-design.md), [plan](2026-05-29-block-library-cleanup-plan.md)

## Где мы

**Ветка:** `block-library-cleanup` (НЕ смержена в mvp-internal-test)

**Код (Task 0-5):** ✅ ГОТОВ, закоммичен, 13 тестов зелёные
- `skills/block-library-management/scripts/cleanup_lib.py` — group_duplicates, renumber, build_new_structure
- `skills/block-library-management/scripts/cleanup_blocks.py` — оркестратор 3 фаз + rebuild_catalog
- `skills/block-library-management/scripts/dedup_report.py` — dedup-report.html генератор
- `skills/block-library-management/prompts/cleanup-classify.md` — промпт чистки
- `tests/block-library/test_cleanup.py` — 13 тестов

**Фаза 1 (чистка, Task 6):** 🔄 **45 / 190** блоков очищено в `.cleanup-staging/*.json`
- Первые 15 — через Codex CLI (брошено, медленно ~40с/блок)
- Блоки 16-45 — через Claude-субагентов (пачки по 10, параллельно по 2)
- Все status=ok

## Решение по подходу

**Чистим через Claude-субагентов, НЕ через Codex** (Codex слишком медленный, ~3ч на 190).
- Пачка = 10 блоков на субагента, запускаем по 2 параллельно.
- Субагент пишет staging через `cleanup_blocks.build_staging_record` (чтобы сигнатура совпадала).
- Чистый HTML субагент сначала пишет в `d:/tmp/clean_<old_id>.html`, потом читает (избегает экранирования).
- Идемпотентность: блоки уже в `.cleanup-staging/` пропускаются.

## Качество (подтверждено)

- ✅ Чистые плейсхолдеры `[SLOT: name]`, реального текста нет
- ✅ Переклассификация по содержимому (cta→lead-form/banner/urgency где есть формы/счётчики)
- ✅ Нейтральный стиль (#f5f5f5/#e8e8e8/#d0d0d0/#333/#999, system-ui)

## Артефакты-косяки для финальной зачистки

1. `cta-brutalist-split-sskrusgun-ru-3` — содержит `...` вне слотов (Codex-артефакт), поправить.
2. Один блок имеет `type: '<one type>'` (Codex скопировал плейсхолдер промпта дословно) — найти и переклассифицировать. Найти: `grep -l '"<one type>"' .cleanup-staging/*.json`

## Осталось (145 блоков)

`.cleanup-todo.json` — полный список 175 исходно-оставшихся (id, path).
Текущий остаток вычислить: блоки из catalog.yaml, которых нет в `.cleanup-staging/`.

```python
python -c "import json,glob,os; todo=json.load(open('.cleanup-todo.json',encoding='utf-8')); done={os.path.basename(f)[:-5] for f in glob.glob('.cleanup-staging/*.json')}; rest=[(i,p) for i,p in todo if i not in done]; print('осталось',len(rest)); [print(i,':',p) for i,p in rest]"
```

Категории в очереди: остаток features, footer(9), gallery(7), header(10), hero(21), pricing(11), process(12), quiz(13), social-proof(17), team(1), trust(20).

## Дальше (после завершения фазы 1)

- **Task 7 (Фаза 2):** `python skills/block-library-management/scripts/cleanup_blocks.py --phase 2 --library block-library`
  → генерит `block-library/dedup-report.html`. Пользователь открывает, отмечает дубли, скачивает `keep-list.yaml` в корень.
- **Task 8 (Фаза 3):** `python skills/block-library-management/scripts/cleanup_blocks.py --phase 3 --library block-library --keep-list keep-list.yaml`
  → переносит в `block-library/<Category>/<type-NNN>/`, пишет migration-map.yaml + catalog.yaml v3.
  Затем: `python skills/block-library-management/scripts/render-gallery.py --library block-library --output block-library/gallery.html`
- **Task 9:** сводка + merge ветки через finishing-a-development-branch.

## ВАЖНО

Галерея `gallery.html` ПОКА показывает старые 190 блоков — staging-блоки в неё не попадают до фазы 3. Чтобы посмотреть результат чистки до фазы 3 — нужен отдельный preview из `.cleanup-staging/`.

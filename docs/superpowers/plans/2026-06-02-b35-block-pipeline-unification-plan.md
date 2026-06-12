# B35 — Унификация пайплайна блоков (плейсхолдеры + жизненный цикл)

**Дата:** 2026-06-02
**Статус:** PLAN (ожидает утверждения)
**Связано:** B31 (плейсхолдеры), B34 (таксономия), docs/BACKLOG.md

## Проблема (что наблюдаем)

В превью галереи блоки показывают `[HEADLINE: преимущества]`, `[Вопрос 1]` —
видимый русский текст внутри плейсхолдеров. Это вскрыло, что библиотека держит
**три параллельных стандарта**, и пайплайн добавления блоков не нормализует их:

| Расхождение | Сколько | Эталон (куда приводим) |
|---|---|---|
| Формат плейсхолдера: `data-slot="x">[рус]` vs `{{slot:x}}` | 48 ru-* (data-slot) / 93 ({{slot}}) | **`{{slot:name}}`** (язык-нейтральный) |
| Полный `<!DOCTYPE html>` vs фрагмент `<style>+<section>` | 56 ru-* (full doc) / остальные (фрагмент) | **фрагмент** |
| Имена слотов в meta.yaml ≠ имена в template | напр. contacts-001 | **синхронны** |
| Генератор НОВЫХ блоков пишет `data-slot/[SLOT:]` | block-generation.md | **`{{slot}}`** |
| Два gallery-генератора (`render-gallery.py` + `generate-gallery.py`) | 2 | **один** |

> `inject-content.py` УЖЕ поддерживает оба формата плейсхолдера, поэтому
> переход на `{{slot}}` ничего не ломает во флоу compose/wireframe.

## Цель

1. Единый формат плейсхолдера во всех блоках: `{{slot:name}}`.
2. Генератор НОВЫХ блоков (из скриншота) сразу выдаёт `{{slot}}` + фрагмент.
3. Один канонический gallery-генератор.
4. Список команд жизненного цикла блока — задокументирован и согласован.
5. Превью галереи можно прогнать через inject-content с демо-контентом
   (опционально — чтобы блоки выглядели «как настоящие», без `{{slot}}` в кадре).

## Решения (требуют подтверждения — см. вопросы в конце)

- **Р1.** *(УТВЕРЖДЕНО: убрать data-slot.)* В ru-* блоках убираем атрибут
  `data-slot` и заменяем внутренний `[текст]` на `{{slot:<имя из data-slot>}}`.
  Единый формат с импортированными блоками. inject-content обработает через
  `{{slot}}`-путь.
- **Р2.** Полные `<!DOCTYPE html>` ru-* шаблоны ужимаем до фрагмента
  (`<style>…</style>` + корневой `<section>`), отбрасывая `<html>/<head>/<body>`.
- **Р3.** Канонический gallery-генератор — `scripts/generate-gallery.py`
  (B34-aware: variant, folder, русские метки, модалка). `render-gallery.py`
  из скилла — удалить, все вызовы переключить на canonical.
- **Р4.** Демо-контент для превью — отдельный YAML-словарь
  `block-library/_preview-content.yaml` (slot-name → демо-значение), один на
  библиотеку; generate-gallery подставляет его через inject-content.

## Фазы

### Фаза 0 — Стандарт формата блока (док + валидатор)
- `docs/standards/block-template-format.md` — канон: фрагмент, `{{slot:name}}`,
  inline `<style>` с префиксом `lp-`, имена слотов = meta.yaml::slots.
- `tests/block-library/test_block_format.py` — каждый template.html:
  - не содержит `<!DOCTYPE html>`/`<html>` (фрагмент),
  - не содержит `[Рус-плейсхолдер]` (только `{{slot:}}` или чистый текст),
  - имена `{{slot:X}}` ⊆ meta.yaml::slots[].name (или naming-схема item-N).
- Тест сначала КРАСНЫЙ (48 блоков нарушают) — фиксирует объём.

### Фаза 1 — Конвертер существующих блоков
- `scripts/normalize-block-templates.py [--dry-run]`:
  1. для каждого template.html с `data-slot`: заменить внутренний текст
     элемента на `{{slot:<data-slot>}}` (Р1),
  2. если документ полный — вырезать фрагмент `<style>+<section>` (Р2),
  3. синхронизировать meta.yaml::slots с найденными слотами (добавить
     недостающие, type: text),
  4. отчёт: что изменено, что требует ручного взгляда.
- TDD: `test_normalize_block_templates.py` на фикстурах (data-slot→slot,
  full-doc→fragment, meta-sync).
- Прогон на 48 ru-* → Фаза 0 тест зеленеет.

### Фаза 2 — Генератор новых блоков пишет {{slot}}
- `skills/landing-import-blocks/prompts/block-generation.md`: заменить
  требование `data-slot/[SLOT:]` на `{{slot:name}}` + фрагмент.
- `scripts/import-blocks/generate-blocks.py`: убедиться, что парсер сохраняет
  `{{slot}}`, meta.yaml::slots заполняется из найденных слотов (а не `content`).
- Тест на фикстуре codex-ответа (мок): на выходе фрагмент c `{{slot}}`,
  meta.slots синхронны.

### Фаза 3 — Один gallery-генератор
- Удалить `skills/block-library-management/scripts/render-gallery.py`.
- Переключить вызовы (import_blocks.py:250, reclassify-blocks-taxonomy.py:272)
  на `scripts/generate-gallery.py`.
- Тест: import-flow зовёт canonical generate-gallery.

### Фаза 4 — Превью с демо-контентом (опционально, Р4)
- `block-library/_preview-content.yaml` — словарь slot→демо.
- `generate-gallery.py`: перед srcdoc прогнать template через inject-content
  с демо-словарём → в превью нет `{{slot}}`, блоки выглядят настоящими.
- Тест: в gallery.html нет `{{slot:` в srcdoc карточек.

### Фаза 5 — Команды жизненного цикла (док)
- `docs/standards/block-lifecycle.md` — единый список:
  - `/landing-import-blocks` — из URL/скриншота: структура → дубли → генерация
    ({{slot}}) → catalog → gallery.
  - `scaffold-block.py` — пустой блок из эталон-шаблона ({{slot}}).
  - `normalize-block-templates.py` — привести старые блоки к стандарту.
  - `find-block-duplicates.py` — диагностика дублей по (category,variant,layout).
  - `generate-catalog.py` / `generate-gallery.py` — пересборка артефактов.
  - валидаторы: `validate-meta.py`, `test_block_format.py`, `test_meta_taxonomy.py`.
- Обновить CLAUDE.md «Block Library» секцию ссылкой на стандарты.

## Порядок и коммиты
Фаза 0 → 1 → 2 → 3 → (4) → 5. Один коммит на фазу. TDD на каждой.
После Фаз 1/3 — регенерация catalog+gallery. Wiki-sync в конце.

## Риски
- **Конвертер ломает вёрстку**, если текст-плейсхолдер был не в листовом
  элементе. Митигация: заменять только если элемент с data-slot не содержит
  дочерних тегов (текст-лист); иначе — в отчёт «ручная проверка».
- **Имена слотов в meta ≠ template** (contacts-001): синхронизация может
  переписать meta. Митигация: meta берёт имена ИЗ template (template — истина
  вёрстки), фиксируем в Фазе 1 отчётом.
- **Полные html→фрагмент** может потерять `<head>`-зависимый CSS. Митигация:
  переносим весь `<style>` из head в начало фрагмента.

## Решения подтверждены (2026-06-02)
1. Р1: **убрать data-slot**, оставить только `{{slot:name}}`.
2. Р2: **ужимать** full-doc ru-* до фрагмента (56 блоков).
3. Р4: **делать сейчас** (демо-превью, Фаза 4).

# Жизненный цикл блока block-library (B35)

Единый список команд и скриптов для работы с блоками. Формат блока задаёт
[`block-template-format.md`](block-template-format.md): фрагмент, `{{slot:name}}`,
inline `<style>` с префиксом `lp-`, слоты синхронны с `meta.yaml`.

## Артефакты блока

```
block-library/<folder>/<id>/
├── meta.yaml                 # id, category, variant, layout_pattern, slots[], signature
├── assets/
│   ├── template.html         # фрагмент со {{slot}} (desktop)
│   └── template-mobile.html  # опционально
└── index.html                # опционально — готовый рендер для превью
```

`catalog.yaml` и `gallery.html` — производные, регенерируются скриптами.

## Команды и скрипты

### Добавить блок(и)
| Команда / скрипт | Что делает |
|---|---|
| `/landing-import-blocks <url\|screenshot>` | Скриншот → codex-анализ структуры → дедуп по сигнатуре → генерация `template.html` со `{{slot}}` → запись `meta.yaml` (slots из реального html) → обновление `catalog.yaml` → регенерация `gallery.html`. Промпт: `skills/landing-import-blocks/prompts/block-generation.md`. |
| `scaffold-block.py --id <id> --category <cat> --template-source <path>` | Пустой блок из эталон-шаблона. `skills/block-library-management/scripts/`. |

### Привести старые блоки к стандарту
| Скрипт | Что делает |
|---|---|
| `scripts/normalize-block-templates.py [--dry-run]` | `data-slot`/`[плейсхолдеры]` → `{{slot}}`; full-doc → фрагмент; синхронизация `meta.yaml::slots`. Идемпотентно. |
| `scripts/fix-display-names.py [--dry-run]` | `display_name_ru` → `<id> (<layout>)`. |

### Диагностика / валидация
| Скрипт | Что делает |
|---|---|
| `check_duplicates.py` (`compute_signature`) | Сигнатура `type\|layout\|[slots]\|bg` для дедупа при импорте. |
| `tests/block-library/test_block_format.py` | Фрагмент, только `{{slot}}`, слоты ⊆ meta. |
| `tests/block-library/test_meta_taxonomy.py` | `category`/`variant` валидны по `taxonomy.yaml`. |

### Регенерация артефактов
| Скрипт | Что делает |
|---|---|
| `scripts/generate-catalog.py --library block-library --output block-library/catalog.yaml` | Пересобрать `catalog.yaml` (category/variant/folder из meta). |
| `scripts/generate-gallery.py --library block-library --output block-library/gallery.html` | **Единственный** генератор галереи: 2 комбобокса category→variant (рус. метки), превью с демо-контентом, модалка «Просмотр». |

> Удалены legacy-дубли `render-gallery.py`/`.js` (B35 Фаза 3). Канон —
> `scripts/generate-gallery.py`.

## Типовой порядок при ручном добавлении/правке
1. Создать/поправить `template.html` по стандарту (`{{slot}}`, фрагмент).
2. `python scripts/normalize-block-templates.py` — добить формат + синк meta.
3. `python scripts/generate-catalog.py …` и `python scripts/generate-gallery.py …`.
4. `pytest tests/block-library/` — формат, таксономия, каталог, галерея зелёные.
5. Коммит (wiki-хук пересоберёт `wiki/`).

## Подстановка контента (флоу проекта)
`skills/block-composition/scripts/inject-content.py` подставляет реальные тексты
из `prototype.yaml` в `{{slot}}` (и legacy `data-slot`, если встретится) на
этапах 07a wireframe и 07b compose. Имена слотов резолвятся через `SLOT_MAPPING`
и item-схему (`feature-N-title`, `card-N-text` → `items[]`).

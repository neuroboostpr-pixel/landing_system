---
type: script
name: generate-wp-blocks
language: python
sources: ["scripts/generate-wp-blocks.py.doc.md", "scripts/generate-wp-blocks.py"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "wp-theme-assembler", "wp-gutenberg-block-builder", "08-kod"]
tags: ["python", "stage-08", "wordpress", "codegen", "orchestrator"]
---

# generate-wp-blocks.py — Оркестратор сборки WP-темы

## Что делает
Запускает пять генераторов этапа 08 строго в порядке зависимостей: от scaffold WordPress-темы до готовой разметки Gutenberg. Один вызов — полная сборка темы без ручных шагов.

## Когда вызывать / в каком этапе
Этап **08 (Код)**. Запускается после того, как `08_КОД/block-spec.yaml` уже создан (агентом [[wp-builder]] или вручную). Поддерживает флаг `--dry-run` для проверки без записи файлов.

```bash
python scripts/generate-wp-blocks.py --project <путь-к-проекту>
python scripts/generate-wp-blocks.py --project <путь-к-проекту> --dry-run
```

## Что на вход / на выход

**Вход:**
- `--project <path>` — путь к папке проекта (позиционный аргумент для шага 1, `--project` для шагов 2–5)
- `08_КОД/block-spec.yaml` — спецификация блоков (обязательна для шагов 2–5)

**Выход (по шагам):**
| Шаг | Генератор | Артефакт |
|-----|-----------|----------|
| 1 | `generate-theme.py` | `style.css`, `functions.php`, `blocks/`, `assets/css/main.css` |
| 2 | `generate-lzb-templates.py` | `theme/blocks/lazyblock-<slug>/block.php` на каждый блок |
| 3 | `generate-lzb-registration.py` | `add_block()` в `functions.php` |
| 4 | `generate-css-patches.py` | `display:contents` правила в `main.css` |
| 5 | `generate-page-content.py` | `08_КОД/page-content.html` с разметкой Gutenberg |

## Связанные концепты
- [[wp-builder]] — агент этапа 08, который вызывает этот оркестратор для сборки темы
- [[wp-theme-assembler]] — скилл сборки WP-scaffold (шаг 1 pipeline)
- [[wp-gutenberg-block-builder]] — скилл генерации Lazy Blocks и block.php (шаги 2–3)
- [[08-kod]] — этап pipeline, к которому принадлежит скрипт

## Источник
- `scripts/generate-wp-blocks.py`
- `scripts/generate-wp-blocks.py.doc.md`
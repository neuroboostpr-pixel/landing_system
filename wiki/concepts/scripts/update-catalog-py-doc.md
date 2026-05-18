---
type: rule
name: update-catalog
sources: ["scripts/import-blocks/update-catalog.py", "scripts/import-blocks/update-catalog.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "landing-import-blocks"]
tags: ["script", "python", "block-library", "catalog", "import"]
---

# update-catalog — обновление каталога блоков

## Что делает

Python-скрипт, который после импорта новых блоков добавляет их записи в `block-library/catalog.yaml`. Читает список только что добавленных блоков и вписывает в каталог те, которых там ещё нет (по `id`/`slug`).

## Когда вызывать / в каком этапе

Вызывается автоматически в конце команды `/landing-import-blocks` после того, как новые блоки физически скопированы в `block-library/`. Не предназначен для ручного запуска в обычном workflow — это служебный шаг импорта.

Запуск вручную:
```bash
python3 scripts/import-blocks/update-catalog.py \
  --library block-library/ \
  --added-from /tmp/added-blocks.json
```

## Что на вход / на выход

**Вход:**
- `--library` — путь к корню `block-library/` (там же лежит `catalog.yaml`)
- `--added-from` — путь к JSON-файлу со списком добавленных блоков; каждый объект содержит поля `slug`, `path`, `category`

**Выход:**
- Обновлённый `block-library/catalog.yaml` — новые записи вида `{id, path, category}` дописаны в список `blocks[]; уже существующие по `id` пропускаются (идемпотентный)
- Сообщение в stdout: `Catalog обновлён: <путь> (+N)`

**Зависимость:** требует `pyyaml` (`pip install pyyaml`); при отсутствии завершается с `exit 2`.

## Связанные концепты

- [[block-library-management]] — владеет структурой и политиками `block-library/catalog.yaml`
- [[landing-import-blocks]] — команда, которая оркестрирует весь импорт и вызывает этот скрипт последним шагом

## Источник

- `scripts/import-blocks/update-catalog.py`
- `scripts/import-blocks/update-catalog.py.doc.md`
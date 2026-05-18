---
type: rule
name: hash-cache
sources: ["scripts/wiki/hash_cache.py", "scripts/wiki/hash_cache.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wiki"]
tags: ["wiki", "performance", "cache", "python"]
---

# hash_cache.py — SHA256-кэш для пропуска неизменённых файлов

## Что делает
Вычисляет SHA256-хэш для каждого source-файла и сохраняет результат в JSON-кэш. При следующем запуске compile.py файлы, которые не изменились, пропускаются — это делает пересборку wiki практически мгновенной.

## Когда вызывать / в каком этапе
Используется внутри `compile.py` (wiki-компайлер) автоматически — при каждом запуске `python -m scripts.wiki.compile`. Вручную не вызывается. Активируется через post-commit хук (`.githooks/post-commit`), который запускается после каждого коммита, затрагивающего source-файлы wiki.

## Что на вход / на выход

**Вход:**
- `path: Path` — путь к source-файлу (агент, скилл, команда и т.д.)
- `cache_path: Path` — путь к JSON-файлу кэша (`{relative_path: sha256}`)

**Выход:**
- `bool` из `is_changed()` — `True` если файл новый или изменился (нужна перегенерация wiki-страницы), `False` — пропустить
- Обновлённый JSON-кэш на диске после `save_cache()`

**Публичный API (4 функции):**
- `compute_hash(path)` — возвращает hex-строку sha256 содержимого файла
- `load_cache(cache_path)` — читает JSON `{relative_path: sha256}`, при отсутствии/ошибке возвращает `{}`
- `save_cache(cache_path, data)` — пишет JSON атомарно, создаёт директории при необходимости
- `is_changed(path, key, cache)` — проверяет, изменился ли файл относительно записи в кэше

## Связанные концепты
- [[wiki]] — главная wiki-папка, для которой этот кэш и работает

## Источник
- `scripts/wiki/hash_cache.py`
- `scripts/wiki/hash_cache.py.doc.md`
---
type: script
name: system_compiler
language: python
sources: ["scripts/wiki/system_compiler.py"]
updated: 2026-05-18
---

# system_compiler.py

Компилит landing-system в landing-system/wiki/.

Алгоритм:
1. Обходим SYSTEM_SOURCES (glob-паттерны).
2. Для каждого файла — проверяем sha256 против .cache.json.
3. Изменённые → SDK → wiki/concepts/<concept_dir>/<slug>.md.
4. После всех — генерируем wiki/index.md через SDK.
5. Аппендим запись в wiki/log.md.

## Источник

- `scripts/wiki/system_compiler.py`

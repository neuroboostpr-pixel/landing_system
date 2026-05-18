---
type: rule
name: system-compiler
sources: ["scripts/wiki/system_compiler.py", "scripts/wiki/system_compiler.py.doc.md"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["wiki", "stage-gates"]
tags: ["wiki", "compilation", "automation", "scripts"]
---

# system-compiler — компилятор системной wiki

## Что делает

Автоматически собирает wiki landing-system из всех исходников (агенты, скиллы, команды, блоки, правила) и записывает результат в `landing-system/wiki/`. Запускается после каждого `git commit` через post-commit хук, чтобы wiki всегда была актуальной.

## Когда вызывать / в каком этапе

Скрипт запускается автоматически через `.githooks/post-commit` — вручную вызывать не нужно. Ручной запуск только при рассинхроне wiki с исходниками:
```bash
python3 -m scripts.wiki.compile --source-mode=system
```
Проверить синхрон: `bash scripts/check-wiki-sync.sh` (exit 0 = ок, exit 1 = нужна пересборка).

## Что на вход / на выход

**Вход:**
- Все файлы из `SYSTEM_SOURCES` (glob-паттерны): `agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, `template/*/README.md`, `docs/standards/*.md`, `block-library/*/*/meta.yaml` и другие источники системы.
- `.cache.json` — хэш-кэш sha256 для скипа неизменённых файлов.

**Выход:**
- `wiki/concepts/<concept_dir>/<slug>.md` — страница для каждого изменённого концепта.
- `wiki/index.md` — обновлённый главный индекс wiki со всеми концептами по категориям.
- `wiki/log.md` — запись о каждом прогоне (timestamp, количество обновлённых файлов).

## Алгоритм работы

1. Обходит все файлы по `SYSTEM_SOURCES`.
2. Сравнивает sha256 каждого файла с `.cache.json` — пропускает неизменённые (~0 сек).
3. Для изменённых файлов вызывает SDK (Claude) → генерирует wiki-страницу → сохраняет в `wiki/concepts/`.
4. Обновляет `wiki/index.md` через SDK.
5. Дописывает запись в `wiki/log.md`.
6. Post-commit хук, если wiki обновилась → автоматический `chore(wiki)` коммит без `--verify`.

## Связанные концепты

- [[wiki]] — папка проектной wiki, которую этот скрипт обновляет
- [[stage-gates]] — правила pipeline, которые компилируются в wiki как правила
- [[memory]] — рядом расположенный механизм памяти проекта

## Источник

- `scripts/wiki/system_compiler.py`
- `scripts/wiki/system_compiler.py.doc.md`
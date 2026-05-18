---
type: rule
name: install-git-hooks
sources: ["scripts/install-git-hooks.sh", "scripts/install-git-hooks.sh.doc.md", ".githooks/post-commit"]
updated: 2026-05-18
triggers: ["установить git hooks", "настроить wiki авто-синхрон", "после клонирования репо", "хук не установлен"]
stage: ""
uses: ["wiki", "stage-gates", "landing-onboarding", "system-setup"]
tags: ["pr-g", "git", "wiki-sync", "automation", "bash"]
---

# install-git-hooks — Установка git-хуков wiki-авто-синхрона

## Что делает

Подключает папку `.githooks/` как источник git-хуков репозитория. После установки каждый `git commit`, затрагивающий исходники системы, автоматически пересобирает `wiki/` и создаёт коммит `chore(wiki)`.

## Когда вызывать / в каком этапе

Запускается **один раз** после клонирования репозитория или в процессе onboarding'а (`/landing-setup`). Если хук не установлен — wiki разойдётся с исходниками при первом же коммите в `agents/`, `skills/`, `commands/`, `template/` и т.д.

```bash
bash scripts/install-git-hooks.sh
```

Идемпотентен: повторный запуск безопасен.

## Что на вход / на выход

**Вход:**
- Репозиторий с папкой `.githooks/` (содержит `post-commit`)

**Выход:**
- `git config core.hooksPath .githooks` — прописан в локальном `.git/config`
- Все файлы в `.githooks/` получают бит `+x`
- Вывод в консоль: список активных хуков

**Что делает установленный `post-commit`:**
1. Определяет, затронул ли коммит источники wiki (`agents/`, `skills/`, `commands/`, `template/`, `docs/standards/`, `block-library/`, `config/`, `scripts/*.doc.md` и др.).
2. Если да — запускает `python3 -m scripts.wiki.compile --source-mode=system`.
3. Если `wiki/` обновилась — автоматически коммитит с сообщением `chore(wiki): авто-обновление после изменений системы` (флаг `--no-verify`, защита от рекурсии).
4. При падении компилятора — **не блокирует** коммит, выводит предупреждение.

## Связанные концепты

- [[wiki]] — правило wiki-авто-синхрона, которое этот скрипт обеспечивает технически
- [[system-setup]] — агент onboarding'а, вызывающий этот скрипт при первичной настройке
- [[landing-onboarding]] — wizard, в котором упоминается установка хуков
- [[stage-gates]] — аналогичный принцип «не пропускай автоматику»

## Источник

- `scripts/install-git-hooks.sh`
- `scripts/install-git-hooks.sh.doc.md`
- `.githooks/post-commit`
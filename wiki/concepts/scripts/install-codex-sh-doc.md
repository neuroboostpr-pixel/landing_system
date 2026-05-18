---
type: rule
name: install-codex
sources: ["scripts/install-codex.sh"]
updated: 2026-05-18
triggers: ["установить codex", "проверить codex cli", "codex не найден", "настроить codex"]
stage: ""
uses: ["visual-generation", "icon-generator", "infographic-builder", "landing-visuals"]
tags: ["bash", "cli", "codex", "setup", "install"]
---

# install-codex.sh — установка Codex CLI

## Что делает

Проверяет, установлен ли Codex CLI в системе. Если нет — устанавливает его через `npm`. После установки предлагает пройти авторизацию (`codex login`).

## Когда вызывать / в каком этапе

Вызывается один раз при настройке рабочей среды — до запуска любых команд, связанных с генерацией визуалов: `/landing-visuals`, `/landing-go`. Без Codex CLI невозможны этапы 07d (иконки и инфографика через `image_gen`).

Также упоминается в онбординге (`/landing-start`) как обязательная предустановка.

```bash
bash scripts/install-codex.sh            # проверить + установить если нет + логин
bash scripts/install-codex.sh --check   # только отчёт, без установки
bash scripts/install-codex.sh --dry-run # показать что произойдёт, не делать
```

## Что на вход / на выход

**Вход:** нет обязательных аргументов. Опциональные флаги: `--check`, `--dry-run`.

**Выход:**
- Сообщение о статусе Codex CLI (установлен / не установлен / версия).
- При отсутствии — автоматическая установка через `npm install -g @openai/codex`.
- Предложение выполнить `codex login` для авторизации.
- Exit code `0` при успехе, ненулевой при ошибке.

## Связанные концепты

- [[visual-generation]] — скилл, который вызывает Codex CLI для генерации PNG иконок и инфографики
- [[icon-generator]] — агент, использует `codex image_gen` под капотом
- [[infographic-builder]] — агент, использует `codex image_gen` под капотом
- [[landing-visuals]] — команда этапа 07d, требует Codex CLI
- [[landing-go]] — мастер-команда, запускает этапы с visual-generation

## Источник

- `scripts/install-codex.sh`
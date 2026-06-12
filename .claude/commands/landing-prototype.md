---
description: Stage 07 — import user-provided prototype (PDF or MD) from <project>/07_ПРОТОТИП/source/, normalize to prototype.{md,yaml}, write import-log.md.
---

# /landing-prototype

Запускает этап **07_ПРОТОТИП** — импорт пользовательского прототипа.

## Что делает

1. Проверяет, что текущая папка — проект-лендинг (есть `00_БРИФ/brief.md` или `.landing-state.yaml`).
2. Проверяет, что в `07_ПРОТОТИП/source/` существует `prototype.pdf` или `prototype.md`.
3. Передаёт работу агенту `prototype-importer`.
4. После завершения работы агента запускает валидатор:
   ```bash
   python3 skills/prototype-import/scripts/validate-prototype.py 07_ПРОТОТИП/prototype.yaml
   ```
5. Сообщает summary + предлагает запустить `/landing-go`.

## Артефакты после выполнения

- `07_ПРОТОТИП/prototype.md`
- `07_ПРОТОТИП/prototype.yaml`
- `07_ПРОТОТИП/import-log.md`

## Условия запуска

- Текущая папка — проект-лендинг
- В `07_ПРОТОТИП/source/` лежит `prototype.pdf` или `prototype.md`

## После одобрения

Запускай `/landing-go`.

## Запуск

Автоматически через `/landing-go` (рекомендуется) или вручную этой командой. Этап интегрирован со `scripts/gate-check.sh` и `.landing-state.yaml`; порядок этапов enforce'ит `landing-orchestrator`.

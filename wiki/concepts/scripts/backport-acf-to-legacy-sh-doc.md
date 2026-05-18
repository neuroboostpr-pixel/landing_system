---
type: rule
name: backport-acf-to-legacy
sources: ["scripts/backport-acf-to-legacy.sh"]
updated: 2026-05-18
triggers: ["обновить старый проект до ACF/Gutenberg", "перенести артефакты этапа 08 на legacy-проект", "регенерировать acf-fields.json"]
stage: "08"
uses: ["08-kod", "wp-builder", "stage-gates", "landing-orchestrator"]
tags: ["bash", "script", "stage-08", "acf", "gutenberg", "legacy", "backport"]
---

# backport-acf-to-legacy — откат артефактов этапа 08 на старый проект

## Что делает

Переносит (бэкпортирует) артефакты этапа 08 — ACF-поля и Gutenberg-блоки — на существующий «легаси» проект, у которого эти файлы ещё не сгенерированы или устарели. Создаёт резервную копию перед изменениями, проверяет gate-08 и снимает метку `legacy: true` из `.landing-state.yaml`.

## Когда вызывать / в каком этапе

Применяется на этапе **08 (КОД)** для проектов, созданных до автоматической генерации ACF/Gutenberg, или когда нужно перегенерировать `acf-fields.json` принудительно. Вызывается вручную:

```bash
bash scripts/backport-acf-to-legacy.sh <путь-к-проекту> [--dry-run] [--force]
```

- **без флагов** — безопасный прогон с проверкой gate-08;
- `--dry-run` — только предпросмотр через `generate-wp-blocks.py --dry-run`, без записи файлов;
- `--force` — перезаписать `acf-fields.json` даже если он существует, пропустить финальную проверку gate.

Скрипт **отказывает** запуску, если `acf-fields.json` уже существует и не передан `--force`.

## Что на вход / на выход

**Вход:**
- `<project>/07_КОНТЕНТ/final-copy.md` — финальный контент (проходит валидацию через `content_parser.py`).
- `<project>/08_КОД/wp-theme/functions.php` — существующая тема (копируется в backup).
- `<project>/.landing-state.yaml` — стейт-файл проекта.

**Выход:**
- `<project>/08_КОД/acf-fields.json` — сгенерированные ACF-поля.
- Обновлённые блоки через `generate-wp-blocks.py`.
- `<project>/.backport-backup-<timestamp>/` — резервная копия изменённых файлов.
- `.landing-state.yaml` — удалена строка `legacy: true`.

## Связанные концепты

- [[08-kod]] — этап, для которого генерируются артефакты
- [[wp-builder]] — агент, создающий те же артефакты в основном pipeline
- [[stage-gates]] — `gate-check.sh --stage 08_build` запускается для валидации результата
- [[landing-orchestrator]] — основной оркестратор; этот скрипт — ручной аналог для legacy-случаев

## Источник

- `scripts/backport-acf-to-legacy.sh`
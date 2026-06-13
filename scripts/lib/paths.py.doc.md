---
type: script
name: paths
language: python
sources: ["scripts/lib/paths.py"]
updated: 2026-05-18
---

# paths.py

Общий помощник для путей и кодировки.

Назначение:
  - Найти корневую папку с лендингами (LANDINGS_ROOT) кросс-платформенно.
  - Принудительно включить UTF-8 для stdout/stderr на любой ОС.

Использование в Python-скриптах:
    from scripts.lib.paths import LANDINGS_ROOT, REPO_ROOT, project_dir
    state = LANDINGS_ROOT / "my-landing" / ".landing-state.yaml"
    # или:
    state = project_dir("my-landing") / ".landing-state.yaml"

Импорт этого модуля сам по себе включает UTF-8 для вывода — никакой
дополнительной настройки в скриптах делать не нужно.

## Источник

- `scripts/lib/paths.py`

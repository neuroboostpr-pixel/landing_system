---
type: script
name: wizard-save-images
language: python
sources: ["scripts/wizard-save-images.py"]
updated: 2026-05-18
---

# wizard-save-images.py

Извлекает все base64 изображения из JSONL транскрипта текущей сессии.

Использование:
    python scripts/wizard-save-images.py --dst <папка> [--session <session_id>] [--prefix ref]

Находит последний JSONL текущей сессии в ~/.claude/projects/<project>/,
извлекает все image-блоки из user-сообщений, сохраняет как ref-01.jpg, ref-02.jpg, ...

Возвращает JSON-список сохранённых файлов в stdout.

## Источник

- `scripts/wizard-save-images.py`

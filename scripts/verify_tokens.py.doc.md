---
type: script
name: verify_tokens
language: python
sources: ["scripts/verify_tokens.py"]
updated: 2026-05-18
---

# verify_tokens.py

C3 — проверка токенизации цветов (спека reference-driven flow §4.3).

Прямые цвета (#hex / rgb() / rgba() / hsl() / hsla()) допустимы ТОЛЬКО:
  - внутри определения токенов `:root { ... }`;
  - в whitelist бренд-цветов (мессенджеры, точка «онлайн»);
  - в `<meta name="theme-color">` (там переменные не работают);
  - на строке с маркером `/* token-exempt */`.

Любой другой прямой цвет «протекает» при переключении палитры → ошибка сборки.

Usage: verify_tokens.py <file.html|file.css> [...]
Exit: 0 PASS · 1 FAIL · 2 нет файлов.

## Источник

- `scripts/verify_tokens.py`

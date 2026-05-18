---
description: Финальная авто-проверка всего лендинга — bundle всех verify-скриптов системы перед деплоем.
---

# /landing-final-check

Запускает все проверки качества проекта перед деплоем. Bundle:

- Wiki sync (опц.)
- Composed premium (13 фич)
- Content preserved (текст прототипа)
- Photo pipeline (фото в processed/, no placeholders, hero no-crop)
- Identity preserved (manifest без violations)
- Visual QA (опц.)

## Использование

```
/landing-final-check <project>
```

## Output

- stdout: краткая сводка
- `<project>/10_QA/final-check-report.md`: детальный отчёт по каждой проверке
- exit 0 — все обязательные pass; exit 1 — хоть одна fail

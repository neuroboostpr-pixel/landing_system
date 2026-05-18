---
type: rule
name: build-patterns-library
sources: ["scripts/extract-effects/build-patterns-library.py"]
updated: 2026-05-18
triggers: []
stage: ""
uses: ["block-library-management", "visual-qa"]
tags: ["scripts", "patterns", "block-library", "css", "html"]
---

# build-patterns-library — сборщик библиотеки паттернов эффектов

## Что делает

Преобразует сырые данные об извлечённых визуальных эффектах (`findings.json`) в готовые переиспользуемые HTML+CSS сниппеты. Каждый паттерн сохраняется как отдельная папка в `block-library/_patterns/` с демо-страницей, стилями и метаданными.

## Когда вызывать / в каком этапе

Запускается вручную после того, как скрипт-экстрактор собрал `findings.json` с описанием визуальных паттернов из существующих страниц или референсов. Используется при пополнении или обновлении библиотеки блоков новыми анимационными и стилевыми эффектами.

Два способа запуска:

```bash
python build-patterns-library.py findings.json
# или через stdin
cat findings.json | python build-patterns-library.py
```

## Что на вход / на выход

**Вход:**
- `findings.json` — JSON-файл с описанием найденных паттернов (передаётся аргументом или через `stdin`)
- Переменная окружения `PATTERNS_DIR_OVERRIDE` — опциональный кастомный путь до `_patterns/`; если не задана, используется `block-library/_patterns/`

**Выход:**
- Папки в `block-library/_patterns/` — по одной на каждый паттерн
- `index.html` внутри каждой папки — живое демо эффекта
- `styles.css` — изолированные стили паттерна
- `meta.yaml` — метаданные паттерна (имя, теги, источник)

## Связанные концепты

- [[block-library-management]] — управление общей библиотекой блоков, куда попадают собранные паттерны
- [[visual-qa]] — визуальная проверка качества сгенерированных сниппетов
- [[visual-curator]] — агент, который может использовать паттерны при сборке composed.html

## Источник

- `scripts/extract-effects/build-patterns-library.py`
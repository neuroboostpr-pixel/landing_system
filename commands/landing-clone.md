---
description: Клонировать существующий сегмент в новый — byte-by-byte копия страниц с одного поддомена на другой внутри одной multisite-сети. Использует skills/wp-multisite/scripts/clone-subsite.sh.
allowed-tools: Bash, Read
---

# /landing-clone

Клонирует контент существующего сегмента целевой аудитории в новый сегмент.
Использует multisite-модель: оба сегмента — subsites одной WordPress-сети.

## Использование

```
/landing-clone <source-slug> <dest-slug>
```

Пример: `/landing-clone russian russian-experiment`

## Что делаю

1. Проверяю что source-сегмент существует в `.landing-state.yaml`.
2. Создаю dest-сегмент (через `/landing-segment` под капотом).
3. Копирую все страницы source → dest (по одной через `wp post get` + `wp post create`).
4. Переношу `show_on_front` / `page_on_front` если они стояли.

## Когда использовать

- Тестирование изменений на копии без риска основному сегменту.
- Создание варианта существующего сегмента для A/B-сплита.

## Когда НЕ использовать

- Для создания **нового** сегмента целевой аудитории (с другим брифом и контентом) →
  используйте `/landing-segment` (он создаёт пустой skeleton под новый контент).

## Скрипт

`skills/wp-multisite/scripts/clone-subsite.sh <project-dir> <source-slug> <dest-slug>`

## Legacy

Старая команда `/landing-clone <new-slug>` для filesystem-клонирования проекта
(модель «N независимых WP инстансов») переехала в
`skills/landing-versioning-and-cloning/scripts/clone-landing.sh`
и помечена deprecated. Использовать только для legacy single-site проектов
без multisite-миграции.

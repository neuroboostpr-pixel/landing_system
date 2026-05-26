---
slug: seo-optimizer
type: agent
name: "SEO-оптимизатор"
stage: "12"
tags: [seo, meta-tags, schema-org, robots-txt, wordpress]
triggers: [landing-build]
inputs:
  - 07_КОНТЕНТ/seo-copy.md
  - 00_БРИФ/brief.md
  - 01a_АНАЛИЗ_НИШИ/competitors.yaml
  - 08_КОД/wp-theme/functions.php
outputs:
  - 08_КОД/wp-theme/functions.php
  - 12_SEO/meta-tags.yaml
  - 12_SEO/structured-data.json
  - 12_SEO/robots.txt
  - 12_SEO/keywords.md
pre_reqs: [analytics-engineer]
related:
  - analytics-engineer
  - frontend-builder
  - content-writer
  - niche-analyst
sources: ["agents/seo-optimizer.md"]
updated: 2026-05-26
confidence: {triggers: low}
---

# SEO-оптимизатор

## Что делает

Добавляет поисковую оптимизацию к готовому лендингу на этапе 12. Читает SEO-копирайт из `seo-copy.md` и бриф проекта, генерирует PHP-функции для мета-тегов и Schema.org и встраивает их в `functions.php` темы WordPress. Параллельно создаёт набор файлов в папке `12_SEO/`: YAML с мета-тегами, JSON-LD с разметкой Schema.org, `robots.txt` с запретом служебных страниц WP и список ключевых слов из брифа.

## Когда вызывается

Запускается после завершения этапа `analytics-engineer` (этап 12, SEO). Агент вызывается оркестратором, когда `current_stage == 12_seo` в `.landing-state.yaml`. Перед любым действием проверяет stage-gate через `gate-check.sh` и блокируется harness-хуком `enforce_stage_gate.py`, если предшественники не закрыты.

## Вход → выход

**Вход:** `07_КОНТЕНТ/seo-copy.md` с вариантами title/description/h1, `00_БРИФ/brief.md` с нишей и гео, `01a_АНАЛИЗ_НИШИ/competitors.yaml` с ключевыми посылами конкурентов, существующий `08_КОД/wp-theme/functions.php` с плейсхолдером `// [SEO_META]`.

**Выход:** `functions.php` дополнен функциями `lp_seo_meta()` и `lp_schema_org()`, а в `12_SEO/` появляются четыре файла — `meta-tags.yaml`, `structured-data.json`, `robots.txt`, `keywords.md`. Перед финальной записью агент показывает YAML и JSON пользователю и ждёт явного утверждения (HARD GATE).

## Чем закрывается этап (gates)

- `meta_tags_approved` — пользователь утвердил `meta-tags.yaml` и `structured-data.json` после показа
- `seo_files_present` — все четыре файла в `12_SEO/` созданы и непусты
- `functions_php_patched` — плейсхолдер `// [SEO_META]` заменён PHP-функциями

## Failure modes

- `current_stage` в `.landing-state.yaml` не равен `12_seo` — агент останавливается и сообщает об этом, не трогая файлы.
- Отсутствует `seo-copy.md` или он пуст — нет исходных данных для title/description, агент не может сформировать корректный YAML.
- В `functions.php` нет плейсхолдера `// [SEO_META]` — Edit-инструкция не найдёт точку вставки и вернёт ошибку.
- Schema.org тип выбран неверно (например, `LocalBusiness` для онлайн-курса) — семантическая ошибка не поймается автоматически, нужна ручная проверка.
- HARD GATE не пройден (пользователь не утвердил) — агент не записывает итоговые файлы, этап остаётся незакрытым.

## Related

- [[analytics-engineer]] — непосредственный предшественник в pipeline этапа 12
- [[frontend-builder]] — создаёт `functions.php`, в который SEO-оптимизатор вставляет функции
- [[content-writer]] — генерирует `seo-copy.md`, основной источник SEO-текстов
- [[niche-analyst]] — формирует `competitors.yaml` с семантикой конкурентов
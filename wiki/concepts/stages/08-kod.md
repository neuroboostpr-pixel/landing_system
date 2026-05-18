---
type: stage
name: 08-kod
sources: ["template/08_КОД/README.md"]
updated: 2026-05-15
triggers: []
stage: "08"
uses: ["wp-builder", "landing-build"]
tags: ["wordpress", "theme", "gutenberg", "build", "auto"]
---

# 08_КОД — Сборка WordPress-темы

## Что делает
Хранит готовый код WordPress-темы: PHP-шаблоны, CSS, JS, Gutenberg-блоки и конфиг полей ACF. Всё это генерируется автоматически агентом `wp-builder` после утверждения контента и дизайна.

## Когда вызывать / в каком этапе
Этап 08 запускается автоматически командой `/landing-build` после завершения этапов контента (07) и дизайна (05). Пользователь не создаёт файлы вручную — папка заполняется агентом.

## Что на вход / на выход

**Вход:**
- Утверждённый `DESIGN.md` с токенами и wireframe
- `final-copy.md` и `seo-copy.md` от `content-writer`
- `tokens.json` с дизайн-токенами

**Выход:**
- `wp-theme/` — полная WordPress-тема (PHP-темплейты, CSS, JS)
- `gutenberg-blocks/` — JSON-конфиги Gutenberg-блоков
- `acf-fields.json` — конфиг Advanced Custom Fields

## Связанные концепты
- [[wp-builder]] — агент, который генерирует все файлы этого этапа
- [[landing-build]] — команда, запускающая этап 08
- [[design-system-generator]] — поставляет `DESIGN.md` и `tokens.json` как входные данные
- [[content-writer]] — поставляет тексты (`final-copy.md`) как входные данные
- [[wp-deployer]] — следующий этап: берёт собранную тему и деплоит на Бегет

## Источник
- `template/08_КОД/README.md`
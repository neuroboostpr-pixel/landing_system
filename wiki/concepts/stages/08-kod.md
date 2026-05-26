---
slug: 08-kod
type: stage
name: "08_КОД — WordPress-код лендинга"
stage: "08"
tags: [build, wordpress, theme, gutenberg, acf, auto]
triggers: [landing-build]
inputs:
  - 07-kontent
  - 05-dizayn-sistema
  - 06-stek
outputs:
  - 08-kod
gates:
  - theme_files_present
  - blocks_registered
pre_reqs:
  - 07-kontent
  - 05-dizayn-sistema
  - 06-stek
related:
  - landing-build
  - wp-builder
  - wp-gutenberg-block-builder
  - frontend-builder
  - landing-style
  - landing-deploy
sources:
  - "template/08_КОД/README.md"
updated: 2026-05-26
confidence:
  gates: low
  inputs: low
---

# 08_КОД — WordPress-код лендинга

## Что делает

Этап генерирует полный WordPress-код лендинга: PHP-тему, Gutenberg-блоки и конфигурацию полей ACF. На выходе появляется папка `wp-theme/` с темплейтами, CSS и JS, папка `gutenberg-blocks/` с JSON-конфигами блоков и файл `acf-fields.json`. Этап выполняется автоматически агентом `wp-builder`, без ручного вмешательства пользователя.

## Когда вызывается

Запускается командой `/landing-build` после того, как утверждены контент (этап 07), дизайн-система (этап 05) и стек (этап 06). В рамках `/landing-go` вызывается оркестратором автоматически при достижении этапа 08.

## Вход → выход

**Вход:** утверждённые артефакты этапов 05 (дизайн-токены), 06 (стек), 07 (контент). Должен существовать `composed.html` из этапа 07b.

**Выход:** `08_КОД/wp-theme/` — полноценная WordPress-тема; `08_КОД/gutenberg-blocks/` — Gutenberg-блоки; `08_КОД/acf-fields.json` — конфигурация Advanced Custom Fields / Lazy Blocks.

## Чем закрывается этап (gates)

- theme_files_present — в `wp-theme/` присутствуют минимально необходимые файлы темы (functions.php, style.css, index.php)
- blocks_registered — все блоки из `composed.html` имеют соответствующие JSON-конфиги в `gutenberg-blocks/`

## Failure modes

- Агент пропускает блоки из `composed.html` — часть страницы не рендерится в WordPress без явной регистрации блоков.
- Дизайн-токены не подтянуты в CSS — тема игнорирует цвета и шрифты из этапа 05; визуал расходится с утверждённым.
- ACF/Lazy Blocks версия не совпадает со стеком из этапа 06 — плагин не активирует поля, блоки не показывают данные.
- Сгенерированный код не проходит `stage-08-spec-lint` — несоответствие между `composed.html` и зарегистрированными блоками.
- Отсутствует `wp-theme/functions.php` с подключением ассетов — CSS и JS не загружаются на фронте.

## Related

- [[landing-build]] — команда, инициирующая этот этап
- [[wp-builder]] — агент, создающий всё содержимое папки
- [[wp-gutenberg-block-builder]] — скилл сборки блоков Gutenberg
- [[frontend-builder]] — связанная роль по генерации фронтенда
- [[landing-style]] — этап 08b, стилизация блоков после build
- [[landing-deploy]] — следующий этап: деплой кода на Бегет
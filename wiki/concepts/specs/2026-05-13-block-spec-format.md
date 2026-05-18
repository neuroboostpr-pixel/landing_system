---
type: rule
name: block-spec-format
sources: ["docs/superpowers/specs/2026-05-13-block-spec-format.md"]
updated: 2026-05-18
triggers: []
stage: "08"
uses: ["wp-builder", "landing-content", "frontend-builder", "landing-build"]
tags: ["block-spec", "lazy-blocks", "wordpress", "stage-08", "yaml"]
---

# block-spec.yaml — формат спецификации блоков (stage-08)

## Что делает

Описывает структуру файла `block-spec.yaml` — центрального входного артефакта восьмого этапа сборки лендинга. В нём перечислены все Gutenberg-блоки страницы: их типы, контролы, дефолтные значения и seed-разметка. Четыре генератора читают этот файл и автоматически создают PHP-шаблоны, CSS-патчи и разметку страницы WordPress.

## Когда вызывать / в каком этапе

Файл создаётся на этапе **08 (Код)** — заполняется менеджером или скиллом `/landing-content` после утверждения контента. Расположение: `<project>/08_КОД/block-spec.yaml`. Генераторы (`generate-lzb-registration.py`, `generate-lzb-templates.py`, `generate-css-patches.py`, `generate-page-content.py`) запускаются агентом [[wp-builder]] при сборке темы.

## Что на вход / на выход

**Вход:**
- Утверждённый контент лендинга (этапы 07/07b)
- Список блоков с заголовками, иконками и контролами
- Пути к изображениям в `08_КОД/wp-theme/assets/img/`

**Выход:**
- `block-spec.yaml` версии `1` с полной схемой блоков
- Используется четырьмя Python-генераторами для авто-создания WordPress-кода

**Ключевые поля верхнего уровня:**
- `version: 1` — обязательно
- `page.title`, `page.slug` — мета страницы WP
- `blocks[]` — массив блоков двух типов: `single` и `section-card`

**Типы блоков:**
- `single` — одиночный блок (без `card:` и `section_grid_class`)
- `section-card` — секция с дочерними карточками (обязательны `card:` и `section_grid_class`)

**Типы контролов (22 типа Lazy Blocks Free):** `text`, `textarea`, `rich-text`, `image`, `gallery`, `repeater`, `select`, `toggle`, `color`, `date-time` и другие.

**Зарезервированные имена контролов** (нельзя использовать): `anchor`, `lazyblock`, `className`, `blockId`, `blockUniqueClass`, `ghostkitSpacings`, `ghostkitSR`.

**Главные правила валидации:**
- Каждый `slug` блока уникален, kebab-case
- `child_of` ссылается только на существующий `repeater`-контрол
- Nested repeaters (repeater внутри repeater) — запрещены; нужно разбить на `section-card`
- Для `image`-контролов `default` — путь относительно `assets/img/`; файл авто-импортируется в Media Library при деплое

Эталонный пример: `template/08_КОД/block-spec.example.yaml`.

## Связанные концепты

- [[wp-builder]] — читает `block-spec.yaml` и генерирует PHP-шаблоны Lazy Blocks
- [[frontend-builder]] — дорабатывает CSS на основе `section_grid_class` из спеки
- [[landing-content]] — скилл/команда, заполняющая `block-spec.yaml` по утверждённому контенту
- [[landing-build]] — команда, запускающая весь pipeline stage-08
- [[08-kod]] — этап, которому принадлежит этот артефакт

## Источник

- `docs/superpowers/specs/2026-05-13-block-spec-format.md`
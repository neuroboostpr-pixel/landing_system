---
type: block
name: features-technical-grid-2-portfolio-kdm1-ru-8
sources: ["block-library/features/features-technical-grid-2-portfolio-kdm1-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: ""
uses:
  - block-library-management
tags: ["features", "grid-2", "technical", "ru-market", "education", "services", "b2b-saas", "tech"]
---

# Features Technical Grid-2 — Секция сопровождения с текстовыми колонками

## Что делает
Отображает раздел «Преимущества» / «Что вы получаете» в виде двухколоночной сетки с техническим стилем. Акцент на системную поддержку: несколько текстовых колонок, чёткая структура без анимаций.

## Когда вызывать / в каком этапе
Используется на этапе **07a (wireframe)** и **07b (compose)** при подборе блоков из библиотеки. Подходит, когда в прототипе есть секция «Что входит», «Как мы поддерживаем» или «Из чего состоит курс». Целевой рынок — Россия (`ru_market: true`).

Подходящие ниши: онлайн-образование, B2B-сервисы, SaaS, технологические компании.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок секции.

**Выход:**
- HTML-блок в стиле `technical`, паттерн `grid-2` (двухколоночная сетка).
- Без анимации (`has_animation: false`).

**Импорт:**
- Источник: PDF-портфолио `portfolio.kdm1.ru` (онлайн-школа Дмитрия Выходцева).
- Метод генерации: `codex-block-generation`, дата: 2026-05-16.

## Связанные концепты
- [[block-library-management]] — скилл управления библиотекой блоков, в которую входит этот блок.

## Источник
- `block-library/features/features-technical-grid-2-portfolio-kdm1-ru-8/meta.yaml`
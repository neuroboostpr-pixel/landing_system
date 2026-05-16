---
type: block
name: faq-minimal-stacked-project21993216-tild-11
sources: ["block-library/faq/faq-minimal-stacked-project21993216-tild-11/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["faq", "minimal", "stacked", "accordion", "ru-market", "services", "ecommerce", "education", "medical"]
---

# FAQ: Аккордеон вопросов в белых строках

## Что делает

Отображает блок часто задаваемых вопросов в виде аккордеона: каждый вопрос — белая строка с иконкой раскрытия справа. При клике строка раскрывается и показывает ответ. Без анимации, в минималистичном стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при сборке wireframe.html через `ux-composer`. Агент выбирает блок из библиотеки, если в prototype.yaml есть секция FAQ. Подходит для ниш: услуги, e-commerce, образование, медицина. Оптимизирован для русского рынка (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` (text, required) — заголовок секции FAQ, обязательный слот
- Контент вопросов и ответов из prototype.yaml (подставляется при composing)

**Выход:**
- HTML-блок аккордеона в составе wireframe.html (этап 07a)
- После `/landing-compose` — вставляется в composed.html с реальными текстами из прототипа и токенами дизайна из tokens.json

## Особенности блока

- **Стиль:** `minimal` — чистый, без лишних декоративных элементов
- **Раскладка:** `stacked` — строки друг под другом
- **Анимация:** отсутствует (`has_animation: false`)
- **Иконки раскрытия:** расположены справа от текста вопроса
- **Импортирован:** с Tilda (project21993216) методом `codex-block-generation` 16 мая 2026

## Связанные концепты

- [[ux-composer]] — агент, который выбирает и рендерит этот блок в wireframe.html на этапе 07a
- [[block-composition]] — скилл, подставляющий design-tokens и тексты прототипа в блок на этапе 07b
- [[block-library-management]] — скилл управления библиотекой блоков, откуда берётся этот блок
- [[wireframe-rendering]] — скилл рендеринга итогового wireframe.html с вариантами блоков

## Источник

- `block-library/faq/faq-minimal-stacked-project21993216-tild-11/meta.yaml`
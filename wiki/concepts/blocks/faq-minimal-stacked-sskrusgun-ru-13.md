---
type: block
name: faq-minimal-stacked-sskrusgun-ru-13
sources: ["block-library/faq/faq-minimal-stacked-sskrusgun-ru-13/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["faq", "accordion", "minimal", "stacked", "ru-market", "services", "education", "ecommerce"]
---

# FAQ: Аккордеон на светлом фоне (minimal stacked)

## Что делает
Блок вопросов-ответов в виде аккордеона — компактные строки на светлом фоне с иконками раскрытия (плюс/шеврон). Пользователь кликает на вопрос — раскрывается ответ, остальные сворачиваются. Без анимации, только чистая типографика и структура.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке wireframe.html — `ux-composer` подбирает блок из библиотеки под секцию FAQ прототипа. На этапе **07b (Compose)** — `block-composer` инжектирует дизайн-токены и подставляет тексты из prototype.yaml. Подходит для проектов в нишах **услуг, образования и e-commerce**, где нужен лаконичный блок часто задаваемых вопросов без визуальных отвлечений.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции FAQ
- Пары вопрос/ответ берутся из `prototype.yaml` (секция faq)
- Дизайн-токены из `tokens.json` (цвет фона, типографика, отступы)

**Выход:**
- HTML-фрагмент аккордеона с семантической разметкой
- Вписывается в `composed.html` как самостоятельная секция
- Без JS-анимаций: раскрытие через CSS `details/summary` или checkbox-паттерн

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при генерации wireframe
- [[block-composer]] — инжектирует токены и тексты в composed.html
- [[wireframe-rendering]] — скилл, в рамках которого блок рендерится интерактивно
- [[block-composition]] — скилл финальной сборки composed.html со всеми блоками
- [[block-library-management]] — управление библиотекой блоков, к которой принадлежит этот блок

## Источник
- `block-library/faq/faq-minimal-stacked-sskrusgun-ru-13/meta.yaml`
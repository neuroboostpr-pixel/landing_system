---
type: block
name: hero-corporate-split-project21993216-tild-1
sources: ["block-library/hero/hero-corporate-split-project21993216-tild-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "corporate", "split", "ru_market", "ecommerce", "services", "education"]
---

# Первый экран: крупный заголовок + фото слева + форма заявки справа

## Что делает

Блок первого экрана (hero) с двухколоночной компоновкой: слева — фото продукта, справа — крупный заголовок и форма заявки с акцентом на выгоду. Подходит для коммерческих лендингов в корпоративном стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)**, когда [[ux-composer]] подбирает блоки из библиотеки под прототип. Активируется автоматически, если прототип предполагает hero-секцию с раздельной (split) компоновкой. Также задействован на этапе **07b (Compose)** агентом [[block-composer]], который подставляет токены и тексты из `prototype.yaml`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текст заголовка (слот `heading`, обязательный)
- `tokens.json` — цвета и шрифты из дизайн-системы
- Фото продукта — визуальный слот (placeholder до этапа [[07c-photos]])

**Выход:**
- HTML-фрагмент hero-секции, встраиваемый в `wireframe.html` (07a) и `composed.html` (07b)
- Placeholder `[SLOT: hero-photo]` для фото, заполняется в [[07c-photos]]
- Форма заявки — заглушка, финально подключается [[integrations-engineer]] на этапе 08

## Дополнительные характеристики

| Параметр | Значение |
|---|---|
| Категория | hero |
| Стиль | corporate |
| Паттерн компоновки | split (двухколоночный) |
| Анимация | нет |
| Рынок | ru_market |
| Подходящие ниши | ecommerce, services, education |
| Источник | Tilda (codex-block-generation, 2026-05-16) |

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки на этапе 07a, если прототип содержит split-hero
- [[block-composer]] — рендерит финальный composed.html с подставленными токенами и текстами (07b)
- [[wireframe-rendering]] — скилл, используемый при генерации wireframe.html с кандидатами блоков
- [[block-composition]] — скилл этапа 07b, инжектирует design-tokens в шаблон блока
- [[photo-curator]] — заполняет визуальный слот фото продукта на этапе 07c
- [[block-library-management]] — скилл управления библиотекой, в которой хранится этот блок

## Источник

- `block-library/hero/hero-corporate-split-project21993216-tild-1/meta.yaml`
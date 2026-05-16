---
type: block
name: header-minimal-split-portfolio-kdm1-ru-0
sources: ["block-library/header/header-minimal-split-portfolio-kdm1-ru-0/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["header", "minimal", "split", "ru-market", "ecommerce", "services", "b2b-saas"]
---

# Тонкая верхняя панель с логотипом, навигацией и контактами

## Что делает

Минималистичная шапка сайта в стиле «split»: логотип слева, навигация по центру, телефон и иконки действий справа. Подходит для сдержанного делового стиля без анимации.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при подборе вариантов шапки, и на **07b (Compose)** при финальной сборке. Агент [[ux-composer]] выбирает этот блок, если прототип требует заголовок в минималистичном split-раскладе для ниш ecommerce, services или b2b-saas. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Обязательный текстовый слот `heading` — текст заголовка / названия компании (тип `text`, required).
- Токены дизайна из `tokens.json` (цвета, шрифты) — инжектируются автоматически на этапе 07b.

**Выход:**
- HTML-разметка блока с классами Lazy Blocks, готовая к встраиванию в `wireframe.html` и `composed.html`.
- Плейсхолдеры для логотипа (визуальный слот, заполняется на этапах PR-B/PR-C).

## Технические характеристики

| Параметр | Значение |
|---|---|
| Категория | `header` |
| Паттерн | `split` |
| Настроение | `minimal` |
| Анимация | нет |
| Российский рынок | да |
| Подходящие ниши | ecommerce, services, b2b-saas |
| Импортирован | 2026-05-16, метод `codex-block-generation` |

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe.html
- [[block-composer]] — инжектирует дизайн-токены и подставляет тексты на этапе 07b
- [[wireframe-rendering]] — скилл, в рамках которого блок рендерится с 2–3 вариантами
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управляет библиотекой, в которой хранится этот блок

## Источник

- `block-library/header/header-minimal-split-portfolio-kdm1-ru-0/meta.yaml`
- Оригинал: [portfolio.kdm1.ru — LCase.pdf](https://portfolio.kdm1.ru/upload/iblock/f94/slk0g7ub4mnpodwty9jl8iyrq4zk33uv/LCase.pdf)
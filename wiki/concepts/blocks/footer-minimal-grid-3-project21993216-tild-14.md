---
type: block
name: footer-minimal-grid-3
sources: ["block-library/footer/footer-minimal-grid-3-project21993216-tild-14/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags: ["footer", "minimal", "grid-3", "ru_market", "services", "ecommerce", "b2b-saas"]
---

# Footer Minimal Grid-3 — Нижний блок с колонками и служебной строкой

## Что делает
Отрисовывает подвал лендинга в минималистичном стиле: краткое описание компании, контактные колонки (три колонки), кнопка действия и служебная строка (копирайт, политика конфиденциальности). Подходит для российского рынка.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при сборке wireframe.html, и на этапе **07b (Compose)** при финальной компоновке composed.html. Агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип содержит секцию «футер» с паттерном трёх колонок. Агент [[block-composer]] инжектирует дизайн-токены и подставляет тексты из prototype.yaml.

Анимация у блока **отсутствует** (`has_animation: false`), поэтому он подходит для быстрых и лёгких лендингов без GSAP.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текстовый контент для слотов (обязателен слот `heading`)
- `tokens.json` — цвета и типографика из design-system
- Опционально: логотип из `04_БРЕНД/logos/`

**Выход:**
- HTML-фрагмент блока, встроенный в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Слот `heading` (type: text, required: true) — должен быть заполнен перед финальной сборкой

## Ниши применения
- **services** — сервисные компании, агентства
- **ecommerce** — интернет-магазины
- **b2b-saas** — B2B сервисы и SaaS-продукты

## Технические характеристики
| Параметр | Значение |
|---|---|
| Категория | footer |
| Layout | grid-3 |
| Стиль | minimal |
| Анимация | нет |
| RU-рынок | да |
| Источник | Tilda project21993216 |
| Метод импорта | codex-block-generation |

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при генерации wireframe
- [[block-composer]] — инжектирует токены и тексты в этапе 07b
- [[wireframe-rendering]] — скилл, который рендерит wireframe.html с этим блоком
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управляет каталогом блоков, включая этот

## Источник
- `block-library/footer/footer-minimal-grid-3-project21993216-tild-14/meta.yaml`
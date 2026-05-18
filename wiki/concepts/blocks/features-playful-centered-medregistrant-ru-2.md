---
type: block
name: features-playful-centered-medregistrant-ru-2
sources: ["block-library/features/features-playful-centered-medregistrant-ru-2/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["features", "playful", "centered", "ru-market", "medical", "services", "tech", "education"]
---

# Features Playful Centered — блок с центральным персонажем и выносками

## Что делает

Секция «фичи» с большим центральным визуальным персонажем (иллюстрация, фото или иконка) в центре и поясняющими выносками (callout-карточками) вокруг него. Создаёт игривое, дружелюбное ощущение — хорошо подходит для продуктов, которые хотят казаться доступными и понятными.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** при подборе блока-секции фичей для ниш с тёплой или игровой подачей. `ux-composer` выбирает блок из библиотеки на основе `prototype.yaml`; затем на этапе **07b (Compose)** `block-composer` инжектирует токены дизайна и текст из прототипа.

Подходит для ниш: **медицина, сервисы, технологии, образование**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — контент секции (заголовок, описания фич)
- `tokens.json` — цвета и шрифты из бренд-кита
- Слот `heading` (обязательный, тип `text`) — главный заголовок секции

**Выход:**
- HTML-блок в составе `wireframe.html` (этап 07a) с CSS-only вариантами
- HTML-блок в составе `composed.html` (этап 07b) с подставленными токенами и текстами
- Слоты под визуальный контент (иконки / инфографика) передаются в этапы **07c** (фото) и **07d** (генерация иконок)

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-composer]] — инжектирует design-tokens и текст прототипа в compose-этапе
- [[wireframe-rendering]] — скилл, в рамках которого блок появляется в wireframe.html
- [[block-composition]] — скилл этапа 07b, финальная сборка с токенами
- [[block-library-management]] — управление реестром таких блоков
- [[visual-curator]] — заполняет иконочные/инфографические placeholders внутри блока на этапе 07d

## Источник

- `block-library/features/features-playful-centered-medregistrant-ru-2/meta.yaml`
- Импортирован с [medregistrant.ru](https://medregistrant.ru/) · 2026-05-16 · метод: `codex-block-generation`
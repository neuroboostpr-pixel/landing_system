---
type: block
name: ru-social-proof-07-logo-ticker
sources: ["block-library/social-proof/ru-social-proof-07-logo-ticker/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a / 07b"
uses: ["block-composer", "ux-composer", "block-composition", "block-library-management"]
tags: ["social-proof", "ticker", "animation", "css-only", "ru-market", "b2c", "local", "services"]
---

# Тикер клиентов — бегущая строка с названиями

## Что делает

Отображает горизонтальную бегущую строку с именами клиентов или партнёров. Слева — лейбл с пульсирующей точкой (сигнал «мы работаем»), справа — анимированный тикер с названиями. Анимация полностью на CSS, без JavaScript. Создаёт быстрый визуальный сигнал доверия без громоздкого раздела с отзывами.

## Когда вызывать / в каком этапе

Используется на этапах **07a (wireframe)** и **07b (compose)**. `ux-composer` выбирает блок из библиотеки при построении wireframe, `block-composer` инжектирует дизайн-токены и реальные тексты при сборке `composed.html`. Рекомендуется размещать **между hero и features** — там блок работает как быстрый якорь доверия до основного контента.

Подходит для рынков: **services, b2c, local**. Оптимален для стилей Editorial & Magazine, Minimalism & Swiss Style, Flat Design 2.0.

## Что на вход / на выход

**Вход (слоты):**

| Слот | Тип | Обязательный | Ограничение |
|---|---|---|---|
| `ticker-label` | text | да | до 40 символов |
| `ticker-sub` | text | нет | до 40 символов |
| `client-1` | text | да | до 40 символов |
| `client-2` … `client-8` | text | нет | до 40 символов каждый |

Для бесшовного зацикливания имена клиентов дублируются в HTML-разметке — это норма, не ошибка.

**Выход:**
Готовый HTML-блок с CSS-анимацией тикера и пульсирующей точкой. На мобильных переходит в вертикальный стек (лейбл сверху, тикер снизу).

## Связанные концепты

- [[block-composer]] — инжектирует токены и тексты в блок при сборке 07b
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe 07a
- [[block-composition]] — скилл, описывающий процесс сборки composed.html
- [[block-library-management]] — скилл управления библиотекой блоков, включает этот блок

## Источник

- `block-library/social-proof/ru-social-proof-07-logo-ticker/meta.yaml`
- Адаптирован из [github.com/nexu-io/open-design](https://github.com/nexu-io/open-design): `design-templates/open-design-landing` (лицензия Apache-2.0)
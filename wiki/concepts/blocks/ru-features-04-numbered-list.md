---
type: block
name: ru-features-04-numbered-list
sources: ["block-library/features/ru-features-04-numbered-list/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a / 07b"
uses: ["ux-composer", "block-composer", "block-composition"]
tags: ["features", "ru-market", "b2c", "services", "local", "minimalism", "saas", "opendesign"]
---

# Нумерованные преимущества — 3 колонки, монопространство

## Что делает
Показывает три ключевых преимущества компании в равных колонках: крупный номер (01–03) моноширинным шрифтом с акцентным цветом, заголовок и описание. Создаёт ощущение порядка и последовательности — хорошо воспринимается в B2C и tech-услугах.

## Когда вызывать / в каком этапе
Используется на этапах **07a** (wireframe) и **07b** (compose). Подключается агентом [[ux-composer]] при выборе блока для секции «Преимущества» и наполняется реальным контентом агентом [[block-composer]].

Рекомендован для проектов со стилем:
- Minimalism & Swiss Style
- Flat Design 2.0
- Corporate Clean

Подходит для ниш: **услуги, B2C, локальный бизнес**.

## Что на вход / на выход

**Вход (слоты):**
| Слот | Обязателен | Макс. символов |
|---|---|---|
| `section-label` | нет | 50 |
| `feat-1-num` / `feat-2-num` / `feat-3-num` | нет | 4 |
| `feat-1-title` / `feat-2-title` / `feat-3-title` | **да** | 45 |
| `feat-1-desc` / `feat-2-desc` / `feat-3-desc` | **да** | 180 |

Номера генерируются автоматически (01, 02, 03) — слоты `feat-*-num` можно не заполнять.

**Выход:** HTML-блок с тремя колонками на белом фоне, верхней и нижней границами. На мобильном — вертикальный стек с разделителями.

**Conversion tip:** Описания должны быть измеримыми — не «мы быстрые», а «доставка за 2 дня». Белый фон с серыми границами визуально отделяет блок от hero.

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composer]] — наполняет слоты текстом из prototype.yaml на этапе 07b
- [[block-composition]] — скилл, управляющий сборкой composed.html
- [[wireframe-rendering]] — скилл этапа 07a, куда встраивается этот блок

## Источник
- `block-library/features/ru-features-04-numbered-list/meta.yaml`
- Базируется на: `github.com/nexu-io/open-design: design-templates/saas-landing (Apache-2.0)`
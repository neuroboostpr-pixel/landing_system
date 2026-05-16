---
type: block
name: ru-testimonials-02-text-photo
sources: ["block-library/social-proof/ru-testimonials-02-text-photo/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: []
tags: [social-proof, testimonials, ru-market, photo, b2c, services, local]
---

# 💬 4 карточки отзывов с фото 2×2

## Что делает
Отображает четыре отзыва клиентов в сетке 2×2: каждая карточка содержит квадратное фото клиента, длинную цитату с конкретным результатом (до 200 символов), имя и роль. На мобильных устройствах карточки выстраиваются в одну колонку.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — агент [[block-composer]] вставляет блок в `composed.html`, когда прототип требует раздела с социальными доказательствами. Подходит для услуг, B2C и локального бизнеса на российском рынке.

## Что на вход / на выход

**Обязательные слоты (required):**
| Слот | Тип | Лимит |
|---|---|---|
| `headline` | text | 60 символов |
| `testimonial-1-photo` | photo 1:1 | — |
| `testimonial-1-quote` | text | 200 символов |
| `testimonial-1-name` | text | 30 символов |
| `testimonial-2-photo` | photo 1:1 | — |
| `testimonial-2-quote` | text | 200 символов |
| `testimonial-2-name` | text | 30 символов |

**Опциональные слоты:** `testimonial-N-role` для всех 4 карточек; карточки 3 и 4 целиком опциональны (фото + цитата + имя + роль).

**Выход:** HTML-блок внутри `composed.html` с заполненными текстами и `[PHOTO SLOT: testimonial-N-photo]` — заглушками для фотографий, которые заменяются на этапе 07c.

## Связанные концепты
Нет явных ссылок на другие концепты в исходнике.

## Источник
- `block-library/social-proof/ru-testimonials-02-text-photo/meta.yaml`
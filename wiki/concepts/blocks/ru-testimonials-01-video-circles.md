---
type: block
name: ru-testimonials-01-video-circles
sources: ["block-library/social-proof/ru-testimonials-01-video-circles/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "photo-curator", "photo-classifier"]
tags: ["social-proof", "testimonials", "ru-market", "b2c", "services", "local", "reels", "stories"]
---

# Отзывы в круглых кружках (Reels-стиль)

## Что делает
Показывает до пяти отзывов клиентов в формате круглых аватарок — как Stories или Reels в Instagram. Под каждым кружком — имя и короткая цитата. Визуальный язык, привычный для российской аудитории, повышает доверие и конверсию.

## Когда вызывать / в каком этапе
Блок используется на этапе **07a (UX Wireframe)** — агент [[ux-composer]] выбирает его из библиотеки, когда прототип требует секцию с отзывами для услуг, B2C или локального бизнеса. На этапе **07b (Compose)** агент [[block-composer]] подставляет реальные тексты и токены дизайна. Фото заполняются на этапе **07c (Photos)** через [[photo-curator]].

## Что на вход / на выход

**Вход (слоты):**
| Слот | Тип | Макс. символов | Обязательный |
|---|---|---|---|
| `headline` | текст | 60 | да |
| `testimonial-1-photo` | фото 1:1 | — | да |
| `testimonial-1-name` | текст | 30 | да |
| `testimonial-1-quote` | текст | 100 | да |
| `testimonial-2-*` | фото + текст | — | да |
| `testimonial-3-*` | фото + текст | — | да |
| `testimonial-4-*` | фото + текст | — | нет |
| `testimonial-5-*` | фото + текст | — | нет |

Минимально работающий вариант — 3 отзыва (1–3 обязательны). Четвёртый и пятый добавляются при наличии материала.

**Выход:**
- Секция HTML с пятью (или тремя) круглыми фото, именами и цитатами.
- Placeholders `[SLOT: testimonial-N-photo]` до прохождения этапа 07c.

## Конверсионные заметки
Реальные лица клиентов в круглом кадрировании — формат, который аудитория воспринимает как «знакомый» (Stories/Reels). По данным атрибуции блока, реальные лица повышают конверсию на **20–35%**. Настоятельно рекомендуется использовать клиентские фото, а не AI-генерацию — identity-safe правила [[photo-curator]] это поддерживают.

## Связанные концепты
- [[ux-composer]] — выбирает блок при рендеринге wireframe.html
- [[block-composer]] — подставляет тексты и дизайн-токены в composed.html
- [[photo-curator]] — заполняет фото-слоты на этапе 07c
- [[photo-classifier]] — тегирует клиентские фото и проверяет ratio 1:1
- [[photo-matcher]] — ранжирует кандидатов для каждого `testimonial-N-photo` слота

## Источник
- `block-library/social-proof/ru-testimonials-01-video-circles/meta.yaml`
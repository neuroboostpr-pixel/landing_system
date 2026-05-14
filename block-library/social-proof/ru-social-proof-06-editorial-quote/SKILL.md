---
name: ru-social-proof-06-editorial-quote
description: Редакционная засечная цитата с аватаром-инициалом, именем автора и блоком логотипов/имён партнёров. Адаптирован из open-design-landing testimonial (Apache-2.0).
---

# ru-social-proof-06-editorial-quote

## Когда применять

Блок отзывов для **premium и B2B** сегментов. Засечный шрифт и редакционная нумерация создают доверие. Хорошо работает в связке с разделом "О нас".

## Slots

- `quote` (text, ≤280 char) — цитата. Используйте кавычки-ёлочки «».
- `author-initial` (text, ≤3 char) — первая буква имени для аватара.
- `author-name`, `author-role` — имя и должность.
- `partner-{1,2,3}` — названия компаний-партнёров.
- `testimonial-image` (photo, 4:5) — фото автора справа (скрывается на mobile).

## Mobile considerations

Изображение скрывается, цитата + автор + партнёры вертикально. Ширина 375px.

---
type: block
name: social-proof-luxury-cards-romanmelnikov-tilda-12
sources: ["block-library/social-proof/social-proof-luxury-cards-romanmelnikov-tilda-12/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "wireframe-rendering", "block-composition"]
tags: ["social-proof", "luxury", "cards", "отзывы", "ru-market"]
---

# Отзывы — тёмные контурные карточки с золотыми деталями

## Что делает
Отображает блок отзывов клиентов в виде тёмных контурных карточек с круглыми аватарами и золотыми акцентами. Подходит для люкс-сегмента и premium-услуг, где важно передать статусность и доверие через визуальный стиль.

## Когда вызывать / в каком этапе
Используется на **этапе 07a** (wireframe) при выборе блока социального доказательства. `ux-composer` подбирает этот блок автоматически, если в `prototype.yaml` есть секция `social-proof` или `reviews`, а в `brand-kit.md` задан стиль `luxury`. Также активируется через `/landing-wireframe` при нише `services`, `luxury` или `education`.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — заголовок секции отзывов
- Данные отзывов из `prototype.yaml` (имя клиента, аватар, текст отзыва)
- Токены брендинга из `tokens.json` (цвета, типографика)

**Выход:**
- HTML-блок с карточками отзывов в тёмной теме с золотыми деталями
- Встраивается в `07a_WIREFRAME/wireframe.html` как один из вариантов блока
- После `/landing-compose` — в `07b_COMPOSED/composed.html` с реальными текстами и placeholders для аватаров

## Особенности блока
- **Стиль:** `luxury` — тёмный фон, контурные карточки, золотые акценты
- **Раскладка:** `cards` — горизонтальный или сеточный ряд карточек
- **Анимация:** отсутствует (`has_animation: false`)
- **Рынок:** адаптирован под русскоязычную аудиторию (`ru_market: true`)
- **Источник:** импортирован с [romanmelnikov.tilda.ws](https://romanmelnikov.tilda.ws/) методом `codex-block-generation`

## Связанные концепты
- [[ux-composer]] — выбирает этот блок при сборке wireframe по нише и стилю
- [[wireframe-rendering]] — рендерит блок в интерактивный wireframe.html
- [[block-composition]] — инжектирует токены и тексты на этапе 07b
- [[photo-curator]] — заполняет слоты аватаров клиентскими фотографиями
- [[block-library-management]] — управляет каталогом всех блоков включая этот

## Источник
- `block-library/social-proof/social-proof-luxury-cards-romanmelnikov-tilda-12/meta.yaml`
---
type: block
name: social-proof-playful-grid-2-opt-ecowash-ru-9
sources: ["block-library/social-proof/social-proof-playful-grid-2-opt-ecowash-ru-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["social-proof", "playful", "grid-2", "отзывы", "ecommerce", "services", "education", "ru-market"]
---

# Раздел отзывов — Playful Grid 2 (EcoWash)

## Что делает
Отображает раздел отзывов клиентов: крупный заголовок и сетка из двух колонок с белыми карточками под пользовательские отзывы. Карточки изначально пустые — контент подставляется из прототипа на этапе compose.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** при подборе блоков для landing-страницы. `ux-composer` выбирает блок из библиотеки, если в прототипе есть раздел социального доказательства (отзывы, рейтинги). На этапе **07b (Compose)** `block-composer` инжектирует заголовок и тексты отзывов из `prototype.yaml`.

Подходит для проектов в нишах:
- **ecommerce** — магазины, маркетплейсы
- **services** — сервисные бизнесы (клининг, авто, доставка)
- **education** — онлайн-курсы, школы

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок раздела отзывов, например «Что говорят наши клиенты»
- Контент карточек отзывов берётся из прототипа (имя, текст, рейтинг)

**Выход:**
- HTML-блок с крупным заголовком и двухколоночной сеткой белых карточек
- Стиль `playful`: скруглённые карточки, лёгкие тени, игривая типографика
- Без анимации (`has_animation: false`) — статичная верстка, не нагружает браузер
- Адаптирован под российский рынок (`ru_market: true`)

## Технические детали
- **Layout:** `grid-2` — две колонки на десктопе, одна на мобиле
- **Источник:** импортирован с [opt.ecowash.ru](https://opt.ecowash.ru/) методом `codex-block-generation` (16.05.2026)
- **Категория:** `social-proof`
- **Анимация:** нет

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — инжектирует токены и тексты прототипа в compose-фазе
- [[wireframe-rendering]] — рендерит блок как один из вариантов в wireframe.html
- [[block-composition]] — скилл compose-этапа, заменяет placeholders реальным контентом
- [[block-library-management]] — управляет каталогом блоков, в котором живёт этот блок
- [[prototype-import]] — источник текстового контента для слота heading и карточек

## Источник
- `block-library/social-proof/social-proof-playful-grid-2-opt-ecowash-ru-9/meta.yaml`
---
type: block
name: gallery-cinematic-grid-4-sskrusgun-ru-12
sources: ["block-library/gallery/gallery-cinematic-grid-4-sskrusgun-ru-12/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["gallery", "cinematic", "grid", "ru-market", "services", "education"]
---

# Gallery Cinematic Grid-4 — фотоколлаж в плотной сетке

## Что делает
Отображает атмосферные фотографии процесса в плотной сетке из 4 колонок (grid-4) в кинематографическом стиле. Помогает передать живую динамику работы через реальные кадры — без анимации, акцент на визуальной плотности и насыщенности.

## Когда вызывать / в каком этапе
Используется на **этапе 07b (Compose)** — когда [[block-composer]] собирает `composed.html` из выбранных блоков прототипа. [[ux-composer]] может предложить этот блок как кандидат на wireframe-этапе (07a) для секций «галерея», «портфолио», «как мы работаем».

Подходит для российского рынка (`ru_market: true`). Рекомендован для ниш:
- **services** — демонстрация процесса оказания услуг
- **education** — показ учебного процесса, занятий, мастерских

## Что на вход / на выход

**Вход:**
- Слот `heading` (тип: `text`, обязательный) — заголовок секции галереи
- Фотографии для сетки (заполняются через [[photo-curator]] на этапе 07c)

**Выход:**
- HTML-блок с плотной 4-колонной сеткой фотографий
- Стиль `cinematic` — тёмные тона, киношная атмосфера, без анимационных переходов

**Особенности:**
- `has_animation: false` — нет GSAP/CSS-анимаций, блок статичный
- `layout_pattern: grid-4` — равномерная сетка из 4 колонок
- Импортирован с [sskrusgun.ru](https://sskrusgun.ru/) методом `codex-block-generation`

## Связанные концепты
- [[block-composer]] — использует этот блок при сборке `composed.html` на этапе 07b
- [[ux-composer]] — может выбрать блок как вариант для wireframe галереи
- [[block-composition]] — скилл, управляющий сборкой блоков с токенами и контентом
- [[photo-curator]] — заполняет фото-слоты блока реальными снимками клиента на этапе 07c
- [[block-library-management]] — скилл, отвечающий за каталог и обновление block-library

## Источник
- `block-library/gallery/gallery-cinematic-grid-4-sskrusgun-ru-12/meta.yaml`
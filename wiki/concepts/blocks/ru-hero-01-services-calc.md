---
type: block
name: ru-hero-01-services-calc
sources: ["block-library/hero/ru-hero-01-services-calc/meta.yaml"]
updated: 2026-05-12
triggers: []
stage: "07b"
uses: [ux-composer, block-composer, wireframe-rendering, block-composition]
tags: [hero, ru-market, services, photo, cta, price-tag, calculator]
---

# RU Hero — Услуги: фото фона + расчёт стоимости

## Что делает
Полноэкранный hero-блок для сервисных компаний: фоновое фото объекта, оффер с подзаголовком слева, плашка «от X ₽» и кнопка «Рассчитать стоимость». На мобильном — вертикальный stack. Создан для российского рынка услуг.

## Когда вызывать / в каком этапе
Используется на этапе **07a** (wireframe) при подборе hero-блока для сервисного лендинга. Финально рендерится на этапе **07b** (compose) агентом [[block-composer]] с инжектом design-токенов и текстов из `prototype.yaml`. Рекомендован для ниш: строительство, ремонт, проектирование, любые услуги с ценовым порогом входа.

## Что на вход / на выход

**Слоты (вход):**

| Слот | Тип | Ограничение | Обязателен |
|---|---|---|---|
| `hero-bg` | фото | 16:9 desktop / 9:16 mobile | да |
| `headline` | текст | макс. 60 символов | да |
| `subhead` | текст | макс. 120 символов | нет |
| `price-tag` | текст | макс. 12 символов (пример: «от 3 500 ₽») | нет |
| `primary-cta` | кнопка | по умолчанию «Рассчитать стоимость» | да |

**Выход:**
- HTML-секция `<section id="hero">` в `composed.html` с bg-фото, оффером, плашкой цены и sticky CTA после скролла за hero.

**Требования по конверсии:**
- Контраст CTA — минимум 7:1.
- Плашка «от X ₽»: правый угол на desktop, под subhead на mobile.
- Sticky CTA активируется при скролле за пределы hero.

**Рекомендуемые стили:** Minimalism & Swiss Style, Flat Design 2.0.

## Связанные концепты
- [[ux-composer]] — выбирает этот блок из библиотеки при рендере wireframe.html
- [[block-composer]] — инжектирует tokens и prototype-тексты в слоты блока на этапе 07b
- [[wireframe-rendering]] — скилл, который отрисовывает кандидатов блоков (включая этот)
- [[block-composition]] — скилл финальной сборки composed.html
- [[photo-curator]] — заполняет слот `hero-bg` клиентским фото или AI-fallback
- [[block-library-management]] — скилл управления и обновления библиотеки блоков

## Источник
- `block-library/hero/ru-hero-01-services-calc/meta.yaml`
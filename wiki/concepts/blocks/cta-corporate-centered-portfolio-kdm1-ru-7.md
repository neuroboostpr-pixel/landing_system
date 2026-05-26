---
type: block
name: cta-corporate-centered-portfolio-kdm1-ru-7
sources: ["block-library/cta/cta-corporate-centered-portfolio-kdm1-ru-7/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: "07b"
uses: []
tags: ["cta", "corporate", "centered", "ru-market", "form", "services", "ecommerce", "b2b-saas"]
---

# Финальный CTA с центрированным заголовком и формой заявки

## Что делает
Завершающий блок призыва к действию: крупный центрированный заголовок, форма заявки и декоративная линейка персонажей снизу. Создаёт убедительное финальное касание с посетителем перед уходом со страницы.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** при сборке `composed.html`. Подходит как финальный CTA-блок для корпоративных лендингов в нишах услуг, e-commerce и B2B-SaaS. Ориентирован на русскоязычный рынок (`ru_market: true`). Анимации не предусмотрены (`has_animation: false`), что делает блок быстрым и стабильным для любых устройств.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок секции CTA.
- Опционально: данные формы (поля заявки задаются в composed.html).

**Выход:**
- Готовый HTML-фрагмент блока с центрированным макетом (`layout_pattern: centered`), стилем `corporate` и декоративным элементом внизу.
- Вписывается в `composed.html` на место соответствующего прототипного блока.

## Связанные концепты
Связи явно не указаны в исходнике.

## Метаданные импорта
- **Источник:** [portfolio.kdm1.ru — Спецодежда Сити (PDF)](https://portfolio.kdm1.ru/upload/iblock/c4c/ejaxky0hmu17f3t0aymzbkm7osq54n8x/Spetsodezhda-Siti.pdf)
- **Дата импорта:** 2026-05-16
- **Метод:** `codex-block-generation`

## Источник
- `block-library/cta/cta-corporate-centered-portfolio-kdm1-ru-7/meta.yaml`
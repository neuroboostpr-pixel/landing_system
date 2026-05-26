---
type: block
name: contacts-corporate-split-portfolio-kdm1-ru-16
sources: ["block-library/contacts/contacts-corporate-split-portfolio-kdm1-ru-16/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["contacts", "corporate", "split", "ru-market", "services", "education", "b2b-saas"]
---

# Финальный контактный экран с формой выбора времени

## Что делает
Завершающий блок лендинга: крупный заголовок, форма выбора удобного времени для звонка и яркая CTA-кнопка. Подходит для корпоративного стиля с чётким разделением на две колонки (split-раскладка).

## Когда вызывать / в каком этапе
Используется на этапе **07b Compose** при сборке `composed.html` как финальный контактный экран. Подходит для ниш: услуги (services), образование (education), B2B SaaS. Ориентирован на русскоязычный рынок (`ru_market: true`). Выбирается в wireframe-раскладке, когда нужен корпоративный (corporate) стиль и split-компоновка без анимаций.

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — крупный заголовок секции контактов.

**Выход:**
- Готовый HTML-блок контактного экрана с заголовком, формой выбора времени и кнопкой, вписанный в `composed.html`.

## Дополнительные характеристики
| Параметр | Значение |
|---|---|
| Категория | contacts |
| Раскладка | split |
| Стиль | corporate |
| Анимация | нет |
| Ru-рынок | да |
| Метод импорта | codex-block-generation |
| Источник | portfolio.kdm1.ru (онлайн-школа Дм. Выходцева, 2026-05-16) |

## Связанные концепты
- [[landing-wireframe]] — блок выбирается пользователем через интерактивный wireframe.html на этапе 07a
- [[landing-compose]] — блок встраивается в composed.html на этапе 07b
- [[landing-design]] — стиль corporate согласуется с design-system проекта (этап 05)

## Источник
- `block-library/contacts/contacts-corporate-split-portfolio-kdm1-ru-16/meta.yaml`
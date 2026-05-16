---
type: block
name: cta-minimal-split-portfolio-kdm1-ru-8
sources: ["block-library/cta/cta-minimal-split-portfolio-kdm1-ru-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition"]
tags: ["cta", "minimal", "split", "ru-market", "ecommerce", "services", "education"]
---

# CTA — Контактная форма с lifestyle-фото (минимализм, split)

## Что делает
Блок призыва к действию: контактная форма в светлой карточке расположена рядом с lifestyle-фотографией. Справа — заметная кнопка отправки. Стиль — чистый минимализм без анимаций.

## Когда вызывать / в каком этапе
Используется на этапе **07b (Compose)** — агент [[block-composer]] выбирает этот блок из библиотеки, если прототип содержит CTA-секцию с формой обратной связи. Подходит для ниш: интернет-магазины (`ecommerce`), услуги (`services`), образование (`education`). Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (text, обязательный) — заголовок над формой.
- Lifestyle-фотография клиента (фото-слот, подставляется из результатов [[photo-curator]] на этапе 07c).

**Выход:**
- HTML-блок с разметкой split-layout: карточка формы слева / фото справа (или наоборот в зависимости от tokens).
- Встраивается в `07b_COMPOSED/composed.html` с подставленными design-tokens (цвета, шрифты из `tokens.json`).

## Ключевые характеристики
| Параметр | Значение |
|---|---|
| Категория | `cta` |
| Настроение | `minimal` |
| Раскладка | `split` |
| Анимация | нет |
| Рынок | Россия |
| Импорт | codex-block-generation, 2026-05-16 |

## Связанные концепты
- [[block-composer]] — агент, который рендерит блок в `composed.html` на этапе 07b
- [[block-composition]] — скилл, управляющий подбором и инъекцией блоков
- [[ux-composer]] — агент, который включает блок в `wireframe.html` на этапе 07a
- [[photo-curator]] — поставляет lifestyle-фото для визуального слота
- [[design-tokens-generation]] — генерирует `tokens.json`, из которого берутся цвета и шрифты блока

## Источник
- `block-library/cta/cta-minimal-split-portfolio-kdm1-ru-8/meta.yaml`
---
type: block
name: cta-brutalist-split-sskrusgun-ru-3
sources: ["block-library/cta/cta-brutalist-split-sskrusgun-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "brutalist", "split", "ru-market", "services", "education"]
---

# CTA — Брутальный сплит-блок с вертикальным фоном (sskrusgun-ru-3)

## Что делает

Широкий промо-блок с вертикальным предметным фоном справа и крупным рубленым призывом к действию слева. Создаёт сильный визуальный акцент за счёт жёсткого брутального стиля и контрастного split-макета — изображение и текст делят пространство пополам.

## Когда вызывать / в каком этапе

Используется на этапе **07a (Wireframe)** и **07b (Compose)** как вариант CTA-секции. Подходит для ниш **услуг** и **образования**, где нужен прямой, без украшений призыв к действию. Выбирается через `selections.yaml` после просмотра `wireframe.html`. Анимации отсутствуют — подходит для проектов с упором на скорость загрузки.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — главный рубленый заголовок/призыв
- Фоновое изображение для вертикальной правой колонки (photo-слот, через photo-curator)
- `tokens.json` — цвета и типографика бренда (инжектируются block-composer)

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` (этап 07a) и `composed.html` (этап 07b)
- При деплое — Lazy Block (`block.php`) через wp-builder

## Связанные концепты

- [[ux-composer]] — подбирает этот блок как кандидат CTA-секции при рендере wireframe
- [[block-composer]] — инжектирует design-токены и текст прототипа в блок на этапе 07b
- [[wireframe-rendering]] — скилл, в рамках которого блок попадает в wireframe.html
- [[block-composition]] — скилл этапа 07b, финальная сборка composed.html
- [[wp-builder]] — конвертирует блок в Lazy Block для WordPress на этапе 08
- [[photo-curator]] — поставляет фото для вертикального фонового слота (07c)

## Источник

- `block-library/cta/cta-brutalist-split-sskrusgun-ru-3/meta.yaml`
- Импортирован с [sskrusgun.ru](https://sskrusgun.ru/) · 2026-05-16 · метод: codex-block-generation
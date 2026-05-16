---
type: block
name: social-proof-cinematic-split-antidiler-karpov-ru-3
sources: ["block-library/social-proof/social-proof-cinematic-split-antidiler-karpov-ru-3/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["block-composition", "ux-composer", "wireframe-rendering"]
tags: ["social-proof", "cinematic", "split", "premium-auto", "luxury", "ru-market"]
---

# Крупный кейс — сплит с фото у авто и диагональной типографикой

## Что делает
Блок социального доказательства в кинематографическом стиле: крупное фото клиента у автомобиля слева, диагональная типографика с текстом отзыва и кнопка CTA справа. Создаёт эффект дорогого авто-контента и усиливает доверие к бренду.

## Когда вызывать / в каком этапе
Используется на этапе **07a (Wireframe)** — `ux-composer` выбирает блок из библиотеки при построении wireframe.html. Также задействуется на этапе **07b (Compose)** агентом `block-composer` для финальной сборки composed.html с подстановкой токенов и текста прототипа.

Подходит для ниш: **premium-auto**, **services**, **luxury**. Оптимален для российского рынка (`ru_market: true`). Анимации нет — блок статичный.

## Что на вход / на выход

**Вход:**
- Слот `heading` (текст, обязательный) — заголовок кейса или цитата клиента
- Фото клиента у автомобиля (photo-slot, заполняется агентом `photo-curator` на этапе 07c)
- Токены дизайна из `tokens.json` (цвета, шрифты)
- CTA-текст и ссылка из `prototype.yaml`

**Выход:**
- HTML-блок в составе `wireframe.html` (07a) или `composed.html` (07b)
- Диагональная сплит-раскладка с типографикой в cinematic-стиле

## Связанные концепты
- [[block-composition]] — агент 07b инжектирует токены и текст в этот блок при финальной сборке
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe на этапе 07a
- [[wireframe-rendering]] — скилл отрисовки интерактивного wireframe.html с вариантами блоков
- [[photo-curator]] — заполняет фото-слот (клиент у авто) на этапе 07c
- [[block-library-management]] — отвечает за хранение и индексацию всех блоков библиотеки

## Источник
- `block-library/social-proof/social-proof-cinematic-split-antidiler-karpov-ru-3/meta.yaml`
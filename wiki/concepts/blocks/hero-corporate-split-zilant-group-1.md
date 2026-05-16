---
type: block
name: hero-corporate-split-zilant-group-1
sources: ["block-library/hero/hero-corporate-split-zilant-group-1/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["hero", "corporate", "split", "ru-market", "no-animation", "services", "luxury", "premium-auto", "education"]
---

# Hero Corporate Split — Zilant Group 1

## Что делает

Большой первый экран (hero) в светло-бирюзовой палитре: крупный заголовок слева, деловая фотокомпозиция справа, кнопка CTA. Создаёт сильное корпоративное первое впечатление без анимаций — акцент на доверие и статус.

## Когда вызывать / в каком этапе

Используется на этапе **07a (UX Wireframe)** — агент [[ux-composer]] выбирает блок из библиотеки, когда прототип требует hero-блок с split-раскладкой и корпоративным настроением. Финально применяется на этапе **07b (Block Compose)** через скилл [[block-composition]].

Подходит для ниш: **услуги, премиум-авто, люкс, образование**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Слот `heading` (текст, обязательный) — главный заголовок первого экрана
- Дизайн-токены проекта (цвета, шрифты из `tokens.json`)
- Фотокомпозиция (деловое фото) — визуальный placeholder до этапа [[07c-photos]]

**Выход:**
- HTML-разметка hero-блока с split-раскладкой, встроенная в `wireframe.html` (этап 07a) или `composed.html` (этап 07b)

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[block-composition]] — инжектирует токены и тексты прототипа в блок на этапе 07b
- [[wireframe-rendering]] — рендерит блок как один из кандидатов в интерактивном wireframe.html
- [[block-library-management]] — управляет каталогом блоков, в котором хранится этот блок
- [[07c-photos]] — на этом этапе placeholder фотокомпозиции заменяется реальным клиентским фото

## Источник

- `block-library/hero/hero-corporate-split-zilant-group-1/meta.yaml`
- Импортирован с [zilant.group](https://zilant.group/) 2026-05-16 методом `codex-block-generation`
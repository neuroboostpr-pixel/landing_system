---
type: block
name: social-proof-corporate-cards-medregistrant-ru-6
sources: ["block-library/social-proof/social-proof-corporate-cards-medregistrant-ru-6/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07b"
uses: ["block-composer", "ux-composer", "block-composition", "wireframe-rendering"]
tags: ["social-proof", "corporate", "cards", "carousel", "animation", "ru-market", "b2b", "medical", "services"]
---

# Карусель карточек клиентов с логотипами и кнопками действия

## Что делает

Показывает клиентов или партнёров компании в виде карусели карточек: логотип, краткое описание и кнопка действия на каждой карточке. Подходит для B2B, медицины и сервисных компаний — убеждает новых посетителей через социальное доказательство в корпоративном стиле.

## Когда вызывать / в каком этапе

Используется на этапе **07b (Block Compose)** — агент [[block-composer]] вставляет блок в `composed.html`, когда в прототипе обозначен раздел «клиенты», «партнёры» или «кейсы». Агент [[ux-composer]] может предложить блок как вариант для слота `social-proof` на этапе **07a (Wireframe)**.

Подходит для ниш: **услуги**, **медицина**, **B2B SaaS**. Ориентирован на российский рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- Обязательный слот `heading` (тип `text`) — заголовок секции (например, «Нам доверяют»).
- Опционально: логотипы клиентов, краткие тексты-описания, ссылки для кнопок действия (передаются через `prototype.yaml` или заполняются вручную в `composed.html`).

**Выход:**
- HTML-блок карусели карточек, встроенный в `07b_COMPOSED/composed.html`.
- Анимация включена (`has_animation: true`) — карусель переключается автоматически или по клику.

## Связанные концепты

- [[block-composer]] — агент, который собирает composed.html и вставляет этот блок на нужное место
- [[ux-composer]] — агент этапа 07a, выбирает блок из библиотеки для wireframe
- [[block-composition]] — скилл, описывающий логику сборки блоков с токенами и текстами
- [[wireframe-rendering]] — скилл этапа 07a, где блок впервые становится кандидатом для слота
- [[block-library-management]] — скилл управления библиотекой, в которой хранится этот блок

## Источник

- `block-library/social-proof/social-proof-corporate-cards-medregistrant-ru-6/meta.yaml`
- Импортирован с [medregistrant.ru](https://medregistrant.ru/) методом `codex-block-generation` (2026-05-16)
---
type: block
name: cta-corporate-centered-zilant-group-9
sources: ["block-library/cta/cta-corporate-centered-zilant-group-9/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "corporate", "centered", "premium-auto", "luxury", "services", "education", "ru-market"]
---

# CTA Corporate Centered — Zilant Group 9

## Что делает

Финальный блок призыва к действию с крупным заголовком, коротким текстом, красной кнопкой и размытым фоновым изображением. Используется в конце лендинга, чтобы подтолкнуть посетителя к целевому действию (звонок, заявка, запись).

## Когда вызывать / в каком этапе

Блок выбирается на этапе **07a (UX Wireframe)** агентом [[ux-composer]] при сборке wireframe.html из prototype.yaml. Финально рендерится на этапе **07b (Block Compose)** агентом [[block-composer]] через скилл [[block-composition]]. Подходит для проектов в нишах: услуги, премиум-авто, люкс, образование — ориентирован на российский рынок.

## Что на вход / на выход

**Вход:**
- `heading` (text, обязательный) — крупный заголовок призыва к действию
- Фоновый образ (размытый) — заполняется через слот визуального контента (PR-B/PR-C)

**Выход:**
- HTML-блок CTA с центрированной компоновкой, красной кнопкой и фоновым изображением с blur-эффектом
- Встраивается в wireframe.html / composed.html

## Особенности

| Параметр | Значение |
|---|---|
| Категория | `cta` |
| Стиль / настроение | `corporate` |
| Компоновка | `centered` |
| Анимация | нет |
| Российский рынок | да |
| Источник | [zilant.group](https://zilant.group/) |
| Метод импорта | codex-block-generation |

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe
- [[block-composer]] — рендерит блок в composed.html с токенами и текстами
- [[wireframe-rendering]] — скилл, управляющий этапом 07a
- [[block-composition]] — скилл, управляющий этапом 07b
- [[block-library-management]] — управление всей библиотекой блоков

## Источник

- `block-library/cta/cta-corporate-centered-zilant-group-9/meta.yaml`
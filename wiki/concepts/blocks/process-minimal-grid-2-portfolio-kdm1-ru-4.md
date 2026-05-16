---
type: block
name: process-minimal-grid-2-portfolio-kdm1-ru-4
sources: ["block-library/process/process-minimal-grid-2-portfolio-kdm1-ru-4/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-library-management", "wireframe-rendering"]
tags: ["process", "minimal", "grid-2", "ru-market", "icons", "education", "services", "b2b-saas", "ecommerce"]
---

# Два информационных блока с иконками — сценарии продаж (process-minimal-grid-2)

## Что делает
Показывает два параллельных сценария продаж через отдельные каналы — каждый в своей карточке с иконкой и текстом. Подходит для объяснения «как это работает» в минималистичном стиле без лишних деталей.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** — агент [[ux-composer]] выбирает этот блок из библиотеки, когда прототип содержит секцию «процесс» или «как мы работаем» с двумя параллельными потоками. Подходит для ниш: образование, услуги, B2B SaaS, e-commerce. Блок ориентирован на российский рынок (`ru_market: true`). Анимации нет — рендерится статично.

## Что на вход / на выход

**Вход:**
- `heading` — обязательный текстовый слот (заголовок секции)
- Контент берётся из `prototype.yaml` на этапе подстановки (stage 07b)
- Иконки — из слотов типа `icon`, заполняемых агентом [[visual-curator]] на этапе 07d

**Выход:**
- HTML-блок в составе `wireframe.html` (07a) и `composed.html` (07b)
- Сетка 2 колонки (`grid-2`), стиль `minimal`
- Без анимации

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при сборке wireframe.html
- [[block-composer]] — инжектирует design-tokens и тексты прототипа в этот блок на этапе 07b
- [[block-library-management]] — скилл, управляющий реестром блоков и метаданными
- [[wireframe-rendering]] — скилл, рендерящий wireframe.html с кандидатами блоков
- [[visual-curator]] — заполняет иконочные слоты блока на этапе 07d

## Источник
- `block-library/process/process-minimal-grid-2-portfolio-kdm1-ru-4/meta.yaml`
- Импортирован: 2026-05-16, метод: `codex-block-generation`, источник: [portfolio.kdm1.ru / LCase.pdf](https://portfolio.kdm1.ru/upload/iblock/f94/slk0g7ub4mnpodwty9jl8iyrq4zk33uv/LCase.pdf)
---
type: block
name: trust-editorial-stacked-portfolio-kdm1-ru-12
sources: ["block-library/trust/trust-editorial-stacked-portfolio-kdm1-ru-12/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["trust", "editorial", "stacked", "ru-market", "b2b-saas", "education", "services"]
---

# Контрастный доверительный блок (editorial stacked)

## Что делает
Формирует зону доверия на лендинге: крупный заголовок на тёмном фоне, светлая вставка-врезка и компактные текстовые аргументы, уложенные стопкой. Визуальный контраст сразу фиксирует внимание и создаёт ощущение авторитетности бренда.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** при сборке wireframe.html агентом [[ux-composer]]. Подходит для посадочных страниц в нишах **услуги**, **онлайн-образование** и **b2b-saas**, когда нужно закрыть возражения и укрепить доверие до призыва к действию. Адаптирован для **российского рынка** (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `heading` (text, required) — главный заголовок блока; единственный обязательный слот.

**Выход:**
- HTML-фрагмент блока, встраиваемый в `wireframe.html` или `composed.html` агентом [[block-composer]] на этапе 07b.

Анимация **отсутствует** (`has_animation: false`), что упрощает интеграцию и ускоряет загрузку.

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — вставляет токены дизайна и тексты прототипа в блок на этапе 07b
- [[wireframe-rendering]] — скилл, в рамках которого блок рендерится как кандидат
- [[block-composition]] — скилл сборки composed.html, куда блок попадает после выбора
- [[block-library-management]] — управляет реестром блоков, включая этот

## Источник
- `block-library/trust/trust-editorial-stacked-portfolio-kdm1-ru-12/meta.yaml`
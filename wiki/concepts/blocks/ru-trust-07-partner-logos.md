---
type: block
name: ru-trust-07-partner-logos
sources: ["block-library/trust/ru-trust-07-partner-logos/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a"
uses:
  - ux-composer
  - block-composer
  - wireframe-rendering
  - block-composition
tags:
  - trust
  - proof
  - logos
  - ru-market
  - b2c
  - services
  - local
---

# Полоса логотипов — компании-клиенты в ряд

## Что делает

Показывает горизонтальный ряд логотипов клиентов или партнёров с коротким лейблом сверху. Логотипы текстовые (не SVG и не изображения), отображаются с прозрачностью 55% — выглядят как нейтральный факт, а не реклама.

## Когда вызывать / в каком этапе

Используется на этапе **07a (wireframe)** при формировании секции социального доказательства (trust/proof). Рекомендуется размещать между блоком Hero и блоком Features. Подходит для услуг, B2C и локального бизнеса. Агент `ux-composer` выбирает этот блок из библиотеки, когда в прототипе есть упоминание клиентов, партнёров или кейсов. На этапе **07b (compose)** агент `block-composer` заполняет слоты реальными названиями компаний.

## Что на вход / на выход

**Вход:**
- `section-label` — подпись над полосой (не обязательно, макс. 60 символов), например «Нам доверяют»
- `logo-1` — название первой компании (обязательно, макс. 40 символов)
- `logo-2` … `logo-5` — названия остальных компаний (не обязательны)

**Выход:**
- Секция HTML с центрированной полосой; на мобильных логотипы переносятся на несколько строк (flex-wrap)

## Особенности реализации

- Стиль логотипов — текст с `opacity: 0.55`; не требует SVG-файлов, что упрощает интеграцию клиентских материалов
- Рекомендованные стили оформления: Minimalism & Swiss Style, Corporate Clean, Flat Design 2.0
- Источник шаблона: `github.com/nexu-io/open-design` (Apache-2.0), атрибуция обязательна

## Связанные концепты

- [[ux-composer]] — выбирает блок при построении wireframe из prototype.yaml
- [[block-composer]] — подставляет тексты и токены при compose
- [[wireframe-rendering]] — скилл, рендерящий интерактивный wireframe.html с этим блоком
- [[block-composition]] — скилл этапа 07b, инжектирует design-tokens и прототипный текст
- [[block-library-management]] — управляет реестром блоков, включая этот

## Источник

- `block-library/trust/ru-trust-07-partner-logos/meta.yaml`
- Исходник: `github.com/nexu-io/open-design: design-templates/saas-landing` (Apache-2.0)
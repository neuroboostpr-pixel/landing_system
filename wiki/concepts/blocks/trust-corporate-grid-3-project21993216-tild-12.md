---
type: block
name: trust-corporate-grid-3-project21993216-tild-12
sources: ["block-library/trust/trust-corporate-grid-3-project21993216-tild-12/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["trust", "corporate", "grid-3", "certificates", "ru-market"]
---

# Trust Corporate Grid-3 — Секция сертификатов (три карточки)

## Что делает

Отображает секцию доверия с тремя карточками сертификатов на светло-голубом фоне. Используется для демонстрации документов, лицензий и наград — чтобы потенциальный клиент убедился в легитимности компании.

## Когда вызывать / в каком этапе

Подключается на этапе **07a (Wireframe)** при сборке wireframe.html агентом [[ux-composer]]. Выбирается из библиотеки блоков категории `trust`, когда прототип предполагает блок с документами, лицензиями или сертификатами. Подходит для ниш: медицина, услуги, e-commerce, IT/tech.

Также задействуется на этапе **07b (Compose)** через скилл [[block-composition]], где в слот `heading` подставляется реальный текст из `prototype.yaml`.

## Что на вход / на выход

**Вход:**
- `prototype.yaml` с заполненным слотом `heading` (обязательный текстовый слот — заголовок секции)
- `tokens.json` с дизайн-токенами (цвета, типографика) — для инъекции стиля

**Выход:**
- HTML-фрагмент блока внутри `wireframe.html` (этап 07a) или `composed.html` (этап 07b)
- Три карточки с placeholder-контентом (иконки/изображения сертификатов) — визуальный контент заполняется на этапах PR-B / PR-C

**Параметры блока:**
- `style_mood`: corporate
- `layout_pattern`: grid-3
- `has_animation`: false (статичный блок, без GSAP/CSS-анимаций)
- `ru_market`: true (оптимизирован для российского рынка)

## Связанные концепты

- [[ux-composer]] — выбирает блок из библиотеки при рендере wireframe.html
- [[block-composition]] — инжектирует tokens и prototype-тексты в слот `heading`
- [[block-library-management]] — управляет регистрацией и обновлением блоков в библиотеке
- [[wireframe-rendering]] — скилл, в рамках которого блок попадает в итоговый wireframe

## Источник

- `block-library/trust/trust-corporate-grid-3-project21993216-tild-12/meta.yaml`
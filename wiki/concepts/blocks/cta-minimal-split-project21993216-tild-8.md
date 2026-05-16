---
type: block
name: cta-minimal-split-project21993216-tild-8
sources: ["block-library/cta/cta-minimal-split-project21993216-tild-8/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["cta", "minimal", "split", "ru-market", "services", "b2b-saas", "education"]
---

# CTA Minimal Split — Короткий подтверждающий баннер

## Что делает
Отображает лаконичный баннер с одной кнопкой призыва к действию на спокойном фоне. Подходит для финального подтверждающего экрана — когда нужно ненавязчиво, без лишнего шума, подтолкнуть пользователя к следующему шагу.

## Когда вызывать / в каком этапе
Используется на этапе **07a (UX Wireframe)** при подборе блоков из библиотеки через [[ux-composer]]. Выбирается, когда прототип содержит короткую CTA-секцию в минималистичном стиле без анимации. На этапе **07b (Block Compose)** рендерится через [[block-composer]] с подстановкой токенов и текстов из `prototype.yaml`.

Подходит для ниш: **услуги**, **B2B SaaS**, **образование**. Ориентирован на русскоязычный рынок (`ru_market: true`).

## Что на вход / на выход

**Вход:**
- `prototype.yaml` — текст заголовка (слот `heading`, обязательный)
- `tokens.json` — цвета, шрифты, отступы бренда
- `selections.yaml` — выбор этого блока в wireframe-сессии

**Выход:**
- HTML-фрагмент блока внутри `07b_COMPOSED/composed.html`
- Слот `heading` заполнен текстом прототипа
- Визуальных плейсхолдеров нет (блок текстово-кнопочный, без фото и иконок)

## Особенности блока

| Параметр | Значение |
|---|---|
| Категория | `cta` |
| Стиль | `minimal` |
| Раскладка | `split` |
| Анимация | нет |
| Обязательных слотов | 1 (`heading`) |
| Источник | Tilda project21993216, импорт 2026-05-16 |

## Связанные концепты
- [[ux-composer]] — выбирает блок из библиотеки при построении wireframe
- [[block-composer]] — рендерит блок в composed.html с токенами и текстами
- [[wireframe-rendering]] — скилл, управляющий выбором блоков на этапе 07a
- [[block-composition]] — скилл, управляющий сборкой composed.html на этапе 07b
- [[block-library-management]] — поддерживает библиотеку блоков, куда входит этот блок

## Источник
- `block-library/cta/cta-minimal-split-project21993216-tild-8/meta.yaml`
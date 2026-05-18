---
type: block
name: hover-effect-09-item-9
sources: ["block-library/_patterns/hover-effect-09-item-9/meta.yaml", "block-library/_patterns/hover-effect-09-item-9/styles.css", "block-library/_patterns/hover-effect-09-item-9/index.html"]
updated: 2026-05-16
triggers: []
stage: ""
uses: []
tags: ["pattern", "hover", "css", "animation", "block-library"]
---

# Hover 9 — CSS-паттерн эффекта при наведении

## Что делает

Добавляет плавный эффект при наведении курсора на элемент карточки или блока: фон меняется через CSS-переменную `--t396-bgcolor-hover-color` за 0.3 секунды. Паттерн извлечён с реального сайта методом css-pattern-extraction.

## Когда вызывать / в каком этапе

Используется в этапе 07b (block-composition / composed.html) и 08 (wp-builder), когда дизайнер или оркестратор выбирает интерактивный hover-эффект для карточек, фич, иконок или любых повторяющихся элементов блока. Подключается вручную через класс `.item-9` на нужный DOM-элемент.

## Что на вход / на выход

**Вход:**
- HTML-элемент с классом `.item-9` (любой тег: `div`, `li`, `article`)
- CSS-переменные из `tokens.json`: `--t396-bgcolor-hover-color`, `--t396-bgcolor-color` (если не заданы — фон прозрачный)

**Выход:**
- Плавный переход `transition: all 0.3s ease` при наведении
- Смена фона через CSS custom property (брендовый цвет из design-tokens)
- Совместимость с Tilda-стилевыми переменными (`--t396-*`)

## Технические детали

```css
.item-9 {
  transition: all 0.3s ease;
}
.item-9:hover {
  background-color: var(--t396-bgcolor-hover-color,
    var(--t396-bgcolor-color, transparent));
}
```

HTML-разметка минимальна:
```html
<div class="item-9">Hover me</div>
```

Паттерн импортирован `2026-05-16` методом `css-pattern-extraction` из реального сайта. Tilda-специфичный селектор `#rec1232321881 .tn-elem[...]` в styles.css — артефакт извлечения, при интеграции его следует убрать или перенести в блочный CSS.

## Связанные концепты

- [[block-composition]] — паттерн подключается на этапе сборки composed.html
- [[design-tokens-generation]] — CSS-переменные `--t396-bgcolor-hover-color` берутся из tokens.json
- [[wp-gutenberg-block-builder]] — класс `.item-9` может применяться в block.php шаблонах

## Источник

- `block-library/_patterns/hover-effect-09-item-9/meta.yaml`
- `block-library/_patterns/hover-effect-09-item-9/styles.css`
- `block-library/_patterns/hover-effect-09-item-9/index.html`
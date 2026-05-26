---
type: block
name: animation-08-iconbackgroundtransform
sources: ["block-library/_patterns/animation-08-iconbackgroundtransform/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["animation", "keyframe", "css-pattern", "icon", "transform"]
---

# Animation: iconBackgroundTransform

## Что делает
CSS-анимация на основе keyframes, которая трансформирует фоновый элемент за иконкой — создаёт эффект движения или пульсации подложки иконки без JavaScript.

## Когда вызывать / в каком этапе
Используется при сборке блоков на этапе 07b (Compose) и 08 (Build), когда нужно оживить иконку декоративным фоновым движением. Подключается как CSS-паттерн к любому блоку, содержащему иконку с фоновым элементом (`<span class="icon-bg">` или аналог).

## Что на вход / на выход
**Вход:** CSS-класс на оборачивающем элементе иконки; паттерн не требует дополнительных параметров.

**Выход:** Готовый `@keyframes iconBackgroundTransform` с соответствующим CSS-правилом `.icon-bg` (или целевым селектором). Анимация зациклена и запускается автоматически при загрузке страницы.

## Связанные концепты
Нет явных связей, указанных в исходнике.

## Источник
- `block-library/_patterns/animation-08-iconbackgroundtransform/meta.yaml`
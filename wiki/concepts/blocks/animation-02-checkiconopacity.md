---
type: block
name: animation-02-checkiconopacity
sources: ["block-library/_patterns/animation-02-checkiconopacity/meta.yaml"]
updated: 2026-05-25
triggers: []
stage: ""
uses: []
tags: ["animation", "css", "keyframe", "pattern", "icon"]
---

# Animation checkIconOpacity

## Что делает
CSS-паттерн, реализующий keyframe-анимацию прозрачности иконки галочки (checkmark). Позволяет плавно проявлять или скрывать иконку подтверждения через изменение opacity.

## Когда вызывать / в каком этапе
Применяется на этапе 07b (Compose) и 08 (Build) при вёрстке блоков, где нужна анимированная индикация успеха, подтверждения или выполненного действия — например, в формах после отправки, в списках преимуществ или в чекбоксах.

## Что на вход / на выход
- **Вход:** CSS-класс или keyframe-правило подключается к нужному HTML-элементу с иконкой галочки.
- **Выход:** Анимация `checkIconOpacity` — плавное изменение прозрачности иконки, управляемое через CSS `animation` property.

## Связанные концепты
Нет явно указанных связей в исходнике.

## Источник
- `block-library/_patterns/animation-02-checkiconopacity/meta.yaml`
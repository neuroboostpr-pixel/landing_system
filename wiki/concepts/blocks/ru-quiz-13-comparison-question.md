---
type: block
name: ru-quiz-13-comparison-question
sources: ["block-library/quiz/ru-quiz-13-comparison-question/meta.yaml"]
updated: 2026-05-16
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composition", "wireframe-rendering"]
tags: ["quiz", "comparison", "b2c", "services", "local", "ru-market", "css-only"]
---

# ⚖️ Квиз — вопрос-сравнение «А или Б»

## Что делает
Показывает пользователю два крупных варианта на весь экран и просит выбрать приоритет — например, «цена» или «качество». Выбор фиксируется через radio CSS без JavaScript, помогает сегментировать клиента ещё в квизе.

## Когда вызывать / в каком этапе
Используется на этапе **07a (wireframe)** при сборке квиза для B2C-услуг или локального бизнеса, когда нужно выявить ключевой приоритет клиента. Подходит для случаев, когда оффер делится по двум полярным характеристикам (цена vs качество, скорость vs надёжность). Вставляется агентом [[ux-composer]] или вручную через [[block-composition]] при компоновке `composed.html`.

## Что на вход / на выход

**Вход (слоты):**
| Слот | Макс. символов | Обязательный |
|---|---|---|
| `question-text` | 120 | да |
| `option-a-title` | 50 | да |
| `option-a-description` | 100 | нет |
| `option-b-title` | 50 | да |
| `option-b-description` | 100 | нет |
| `question-comment` | 80 | нет |
| `progress-label` | 60 | нет |

**Выход:** HTML-блок с двумя карточками (карточка А / карточка Б), заголовок + иконка + описание, CSS-only radio без JS. Встраивается в `wireframe.html` или `composed.html`.

## Конверсионная логика
Бинарный выбор сразу разделяет аудиторию по приоритету — дальнейшие вопросы квиза и итоговое предложение можно персонализировать под выбранный вектор. Паттерн взят из практики Marquiz (подбор по параметрам для отстройки от конкурентов).

## Связанные концепты
- [[ux-composer]] — вставляет блок в wireframe при сборке квиза
- [[block-composition]] — инжектирует токены и текст при компоновке composed.html
- [[wireframe-rendering]] — рендерит интерактивный HTML с CSS-only переключением вариантов
- [[prototype-import]] — прототип квиза, из которого берутся тексты для слотов

## Источник
- `block-library/quiz/ru-quiz-13-comparison-question/meta.yaml`
- Атрибуция: [marquiz.ru/blog/kak-otstroitsya-ot-konkurentov](https://marquiz.ru/blog/kak-otstroitsya-ot-konkurentov)
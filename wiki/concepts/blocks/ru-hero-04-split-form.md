---
type: block
name: ru-hero-04-split-form
sources: ["block-library/hero/ru-hero-04-split-form/meta.yaml"]
updated: 2026-05-13
triggers: []
stage: "07a"
uses: ["ux-composer", "block-composer", "wireframe-rendering", "block-composition"]
tags: ["hero", "ru-market", "services", "b2c", "lead-form", "split-layout", "conversion"]
---

# ru-hero-04-split-form — Текст слева + лид-форма справа

## Что делает

Hero-блок с разбивкой 60/40: слева — заголовок и три буллета с галочками, справа — встроенная форма захвата лида (поле телефона + выбор канала связи: Telegram / Max / Звонок). Фотографий нет — форма сама служит главным визуальным элементом первого экрана.

## Когда вызывать / в каком этапе

Используется на **этапе 07a (UX Wireframe)** при подборе блоков библиотеки через [[ux-composer]]. Подходит для проектов сферы услуг и B2C, где главная цель — немедленный сбор контакта без лишнего скролла. Рекомендован при стилях «Minimalism & Swiss Style» и «Corporate Professional».

Не подходит, если нужна продуктовая фотография или визуальный акцент на команде/товаре — для таких случаев используй hero-блоки с фотослотами.

## Что на вход / на выход

**Слоты (входные данные из prototype.yaml):**

| Слот | Тип | Обязателен | Лимит |
|---|---|---|---|
| `headline` | text | да | 60 символов |
| `bullet-1-text` | text | да | 80 символов |
| `bullet-2-text` | text | да | 80 символов |
| `bullet-3-text` | text | нет | 80 символов |
| `primary-cta` | cta | да | default: «Узнать стоимость» |
| `lead-phone-input` | text | да | 20 символов |
| `lead-submit-cta` | cta | да | default: «Отправить заявку» |

**Выход:** wireframe-блок в `wireframe.html` (этап 07a) или assembled-фрагмент в `composed.html` (этап 07b) с подставленными текстами и токенами дизайна.

**Mobile:** форма перемещается под текст (stack в одну колонку).

**Конверсионные особенности:** форма видна без скролла на первом экране; радиогруппа Telegram / Max / Звонок не включает запрещённые мессенджеры; буллеты с ✓ повышают доверие до отправки формы.

## Связанные концепты

- [[ux-composer]] — выбирает этот блок из библиотеки при построении wireframe.html
- [[block-composer]] — инжектирует design-tokens и текст прототипа в слоты блока
- [[wireframe-rendering]] — скилл, рендерящий блок в интерактивный HTML с вариантами
- [[block-composition]] — скилл финальной сборки composed.html
- [[block-library-management]] — управляет каталогом, в котором зарегистрирован блок

## Источник

- `block-library/hero/ru-hero-04-split-form/meta.yaml`